"""Module which handles all preset naming configurations.

Example  preset in raw data form.

.. code-block:: json

    {
        "name": "ZooToolsPro",
        "configs": [
            {
                "name": "zootoolsProGlobalConfig",
                "hiveType": "global"
            }
        ]
    }

"""

import json.decoder
import os
import tempfile

from zoo.core.util import zlogging, filesystem, modules
from zoo.libs.hive.constants import (
    CONFIG_EXT,
    PRESET_EXT,
    ZOO_PRESET,
    ZOOTOOLS_GLOBAL_CONFIG,
)
from zoo.libs.naming import naming
from zoo.preferences.interfaces import hiveinterfaces

logger = zlogging.getLogger(__name__)


class MissingPresetPath(Exception):
    """Called when the preset doesn't have a file path."""

    def __init__(self, preset):
        message = "Preset missing file Path, {}".format(preset.filePath)
        super(MissingPresetPath, self).__init__(message)


class PresetManager(object):
    """Managers all naming presets and configurations for Hive

    ..Note: This class is not meant to be instantiated directly.
    ..Note: This Class initializes all presets and configs once at first init,
    Any Modification to the hierarchy or config will be reflected on all hive rig instances.
    """

    # Environment variable name for all naming preset files.
    ENV_VAR = "HIVE_NAME_PRESET_PATH"

    @staticmethod
    def savePreset(preset):
        """Saves the given preset onto disk.

        ..note:: The preset must have a file path specified.

        :param preset: The preset instance to save.
        :type preset: :class:`Preset`
        :return: Whether the file successfully saved.
        :rtype: bool
        :raise MissingPresetPath: When the Provided Preset file path has no value
        """
        outputPath = preset.filePath
        if not outputPath:
            raise MissingPresetPath(preset)
        logger.debug("Saving Preset: {}, path: {}".format(preset, outputPath))
        data = preset.serialize()
        filesystem.ensureFolderExists(os.path.dirname(outputPath))
        filesystem.saveJson(data, outputPath)
        return True

    def __init__(self):
        # hive preferences interface instance.
        self.prefInterface = hiveinterfaces.hiveInterface()
        # full list of preset instances.
        self.presets = []  # type: list[Preset]
        # The root preset defined by a hierarchy.
        self.rootPreset = None  # type: Preset or None
        # A dict which contains all naming configurations.
        self.namingConfigs = {}  # type: dict[str, naming.NameManager]
        self._availableConfigTypes = set()  # set[str]

    def availableConfigTypes(self):
        """Returns all currently available naming configuration hive Types.

        :rtype: set[str]
        """
        return self._availableConfigTypes

    def updateAvailableConfigTypes(self, types):
        """Updates the currently available config types, when a class instance is first
        created the list will update from the found preset configuration.

        :type types: list[str] or set[str]
        """
        self._availableConfigTypes.update(set(types))

    def containsPath(self, filePath):
        """Whether the file path has already been loaded.

        :param filePath: The file path to search for.
        :type filePath: str
        :return:
        :rtype: bool
        """
        normPath = os.path.normpath(filePath)
        for preset in self.presets:
            if preset.filePath == normPath:
                return True
        return False

    def findPreset(self, name):
        """Return the preset by the name, None if not found.

        :param name: The preset name to search for
        :type name: str
        :rtype: :class:`Preset` or None
        """
        for preset in self.presets:
            if preset.name == name:
                return preset

    def createPreset(self, name, directory, parent=None):
        """Creates but does not save to disk a new preset instance.

        Call :meth:`PresetManager.savePreset` to save the preset to disk.

        :param name: The name for the preset.
        :type name: str
        :param directory: The directory where the preset will be created.
        :type directory: str
        :param parent: The parent Preset for the new preset
        :type parent: :class:`Preset`
        :return: The newly created preset.
        :rtype: :class:`Preset`
        """
        outputName = os.path.join(directory, os.path.extsep.join((name, PRESET_EXT)))
        newPreset = Preset(name, outputName, parent=parent, presetManager=self)
        if parent is not None:
            parent.children.append(newPreset)
        self.presets.append(newPreset)
        return newPreset

    def removePreset(self, presetName):
        """Remove the preset by name and returns whether deletion was successfully.

        This Method only remove's the preset from memory but doesn't delete it on disk.
        You should call :meth:`PresetManager.deletePreset`

        ..note: This method will also modify the parent preset.

        :param presetName: The preset name to search for
        :type presetName: str
        :rtype: bool
        """
        currentPreset = self.findPreset(presetName)
        if currentPreset is None:
            return False
        parentPreset = currentPreset.parent
        if parentPreset is not None:
            parentPreset.children.remove(currentPreset)
        self.presets.remove(currentPreset)

        return True

    def deletePreset(self, preset, configs=True):
        """Removes the given preset from the manager and deletes the preset file as well as any attached
        configurations.

        :param preset: The preset instance to delete from disk.
        :type preset: :class:`Preset`
        :param configs: If True then the Preset configs will also be deleted from disk.
        :type configs: bool
        :rtype: bool
        """
        if preset.exists():
            logger.debug("Deleting Preset file: {}".format(preset.filePath))
            os.remove(preset.filePath)
        if configs:
            for config in preset.configs:
                manager = config.config
                if not manager:
                    continue
                filePath = manager.configPath

                if os.path.exists(filePath):
                    logger.debug("Deleting Configuration file: {}".format(filePath))
                    os.remove(filePath)
        return self.removePreset(preset.name)

    def duplicatePreset(self, preset):
        """Duplicates the preset and it's hierarchy on presets and configs.

        :note: This method doesn't save to disk the Duplicate presets and configs..

        :param preset: The preset instance to Duplicate
        :type preset: :class:`Preset`
        :return: The duplicated preset in an unsaved state.
        :rtype: :class:`Preset`
        """
        createdPresetsMap = {}  # contains orig presetName to new preset
        presetDuplicate = self.createPreset(
            preset.name + "_COPY",
            self.prefInterface.namingPresetSavePath(),
            parent=preset.parent,
        )
        createdPresetsMap[preset.name] = presetDuplicate
        for config in preset.configs:
            cfgData = presetDuplicate.createConfig(name="", hiveType=config.hiveType)
            genName = cfgData.name
            cfgData.config.copyFromConfigData(config.config.serialize())
            cfgData.config.name = genName

        stack = [i for i in preset.children]
        while stack:
            child = stack.pop()
            childPreset = self.createPreset(
                child.name + "_COPY",
                self.prefInterface.namingPresetSavePath(),
                parent=createdPresetsMap[child.parent.name],
            )
            createdPresetsMap[child.name] = childPreset
            for config in child.configs:
                cfgData = childPreset.createConfig(name="", hiveType=config.hiveType)
                genName = cfgData.name
                cfgData.config.copyFromConfigData(config.config.serialize())
                cfgData.config.name = genName
            stack.extend(child.children)

        return presetDuplicate

    def configSaveFolder(self):
        """The current folder which all new presets get saved too.

        :rtype: str
        """
        return self.prefInterface.namingPresetSavePath()

    def saveConfig(self, config):
        """Saves the given config instance to disk.

        :param config: The config instance to save.
        :type config: :class:`naming.NameManager`
        :return: Whether the file successfully saved.
        :rtype: bool
        """
        if not config.configPath:
            folder = self.configSaveFolder()
            filePath = os.path.join(
                folder, os.path.extsep.join([config.name, CONFIG_EXT])
            )
            config.configPath = filePath
        else:
            folder = os.path.dirname(config.configPath)
        logger.debug("Saving Naming configuration: {}".format(config.configPath))
        filesystem.ensureFolderExists(folder)
        filesystem.saveJson(config.serialize(), config.configPath)

        return True

    def loadFromEnv(self, hierarchy):
        """Loads all presets and constructs the preset hierarchy from the preset environment variable.

        .. note::

            Calling this method will clear the cache which stores all presets and configs.

        :param hierarchy:
        :type hierarchy: dict
        """
        self.namingConfigs.clear()
        self.presets = []
        self.rootPreset = None
        self._availableConfigTypes.clear()

        paths = os.getenv(self.ENV_VAR, "").split(os.pathsep)
        prefPaths = self.prefInterface.namingPresetPaths()
        visited = set()
        for path in paths + prefPaths:
            path = os.path.normpath(path)
            if path in visited:
                continue
            elif not os.path.exists(path):
                logger.warning(
                    "Invalid naming Preset path will be ignored: {}".format(path)
                )
                continue
            visited.add(path)
            if self.containsPath(path):
                continue
            elif os.path.isdir(path):
                self.loadFromDirectoryPath(path)
            elif os.path.isfile(path):
                self.loadFromFile(path)

        self._loadPresetHierarchy(hierarchy)

    def loadFromFile(self, path):
        """Loads the provided file path which is either a preset or naming configuration.

        :param path: The file path to load, must be either file format . ".namingcfg" or ".namingpreset"
        :type path: str
        """
        baseName = os.path.basename(path)
        if baseName.startswith(modules.MODULE_EXCLUDE_PREFIXES):
            return
        path = os.path.normpath(path)
        if baseName.endswith("." + PRESET_EXT):
            for preset in self.presets:
                if preset.filePath.lower() == path.lower():
                    return
            preset = Preset.loadFromPath(path, presetManager=self)
            if preset is not None:
                self.presets.append(preset)
                for config in preset.configs:
                    self._availableConfigTypes.add(config.hiveType)
                return preset
        elif baseName.endswith("." + CONFIG_EXT):
            cfg = naming.NameManager.fromPath(path)
            if cfg.name in self.namingConfigs:
                return
            self.namingConfigs[cfg.name] = cfg
            hiveType = cfg.originalConfig.get("hiveType")
            if hiveType:
                self._availableConfigTypes.add(hiveType)

    def loadFromDirectoryPath(self, path):
        """Recursively loads all naming presets or configs from the provided folder

        :param path: Absolute file path to the naming preset of config to load
        :type path: str
        """
        for root, dirs, files in os.walk(path):
            for f in files:
                fullPath = os.path.join(root, f)
                self.loadFromFile(fullPath)

    def hierarchyData(self):
        """Returns the current hierarchy raw data from the current preset hierarchy.


        .. code-block:: python

            data = preset.hierarchyData()
            # {"name": "ZooToolsPro",
            # "children": [{"name": "UE5Manniquin"}]
            # }

        :rtype: dict

        """

        def serializeHierarchy(preset):
            """Recursively serializes the preset

            :param preset: The preset to serialize
            :type preset: :class:`Preset`
            :rtype: dict
            """
            return {
                "name": preset.name,
                "children": [serializeHierarchy(i) for i in preset.children],
            }

        if not self.rootPreset:
            return {}
        return serializeHierarchy(self.rootPreset)

    def printHierarchy(self):
        """Prints the current preset hierarchy to console.
        """
        _pprintTree(self.rootPreset)

    def _loadPresetHierarchy(self, data):
        currentPresets = {i.name: i for i in self.presets}

        globalCfg = self.namingConfigs[ZOOTOOLS_GLOBAL_CONFIG]

        def _processChild(childData, parent):
            """

            :type childData: dict
            :type parent: :class:`Preset` or None
            :rtype: :class:`preset`
            """
            name = childData["name"]
            try:
                childPreset = currentPresets[name]
            except KeyError:
                logger.warning("Missing naming Configuration Preset: {}".format(name))
                return
            if parent:
                parent.children.append(childPreset)
            childPreset.parent = parent
            globalCfgOverride = (
                childPreset.findNamingConfigForType("global") or globalCfg
            )
            for childConfig in childPreset.configs:
                cfg = self.namingConfigs.get(childConfig.name)
                if cfg is None:
                    childConfig.config = globalCfg
                    continue
                childConfig.config = cfg
                parentConfig = (
                    globalCfgOverride if childConfig.hiveType != "global" else None
                )
                if parent is not None:
                    parentConfig = parent.findNamingConfigForType(childConfig.hiveType)
                cfg.parentConfig = parentConfig

            for child in childData.get("children", []):
                _processChild(child, parent=childPreset)

            return childPreset

        if data:
            root = _processChild(data, parent=None)
        else:
            root = self.findPreset(ZOO_PRESET)
        # ensure all presets even dangling presets at least have a parent
        for preset in self.presets:
            if preset.parent is None and preset != root:
                preset.parent = root
                root.children.append(preset)
        # ensure all configs even dangling configs at least have a parent
        for config in self.namingConfigs.values():
            if config.parentConfig is None and config != globalCfg:
                config.parentConfig = globalCfg
        self.rootPreset = root

    def findConfigsByType(self, hiveType):
        """Returns all naming configurations by the hive type.

        :param hiveType: The hive component type.
        :type hiveType: str
        :rtype: list[:class:`naming.NameManager`]
        """
        return [
            i
            for i in self.namingConfigs.values()
            if i.originalConfig.get("hiveType", "") == hiveType
        ]


class Preset(object):
    """Naming Preset class which managers configurations.

    A Preset data is in the form of

    .. code-block:: json

        {
            "name": "ZooToolsPro",
            "configs": [
            {
                "name": "zootoolsProGlobalConfig",
                "hiveType": "global"
            }]
        }

    :param name: The preset name
    :type name: str
    :param filePath: The file path for the preset, note. it doesn't need to exist.
    :type filePath: str
    :param parent: The parent preset.
    :type parent: :class:`Preset`
    :param presetManager: The current Preset Manager instance.
    :type presetManager: :class:`PresetManager`
    """

    @classmethod
    def loadFromPath(cls, path, presetManager):
        """Loads the preset from a valid file path, must be valid json data.

        :param path: The preset json file path to load.
        :type path: str
        :return: The new loaded preset.
        :rtype: :class:`Preset`
        """
        try:
            logger.debug("Loading Preset from path: {}".format(path))
            data = filesystem.loadJson(path)
        except json.decoder.JSONDecodeError:
            logger.error("Failed to Loaded Json file: {}".format(path), exc_info=True)
            return
        return cls.loadFromData(data, path, presetManager)

    @classmethod
    def loadFromData(cls, data, filePath, presetManager, parent=None):
        """Loads the preset from the provided data.

        :param data: The raw preset data to load.
        :type data: dict
        :param filePath: The file path for the preset.
        :type filePath: str
        :param parent: The parent preset instance
        :type parent: :class:`Preset`
        :return: The newly loaded preset instance.
        :rtype: :class:`Preset`
        """
        name = data.get("name")
        newPreset = cls(name, filePath, parent, presetManager)
        for config in data.get("configs", []):
            hiveType = config["hiveType"]
            configType = NameConfigData(config["name"], hiveType)
            newPreset.configs.append(configType)
        return newPreset

    def __init__(self, name, filePath, parent, presetManager):
        self.name = name
        self.filePath = filePath
        self.presetManager = presetManager
        self.configs = []  # type: list[NameConfigData]
        self.children = []  # type: list[Preset]
        self.parent = parent  # type: Preset

    def __repr__(self):
        return "Preset(name={})".format(self.name)

    def serialize(self):
        """Returns the raw dict representing this preset.

        :rtype: dict
        """
        return {"name": self.name, "configs": [i.serialize() for i in self.configs]}

    def exists(self):
        """Whether this preset exists on disk.

        :rtype: bool
        """
        return os.path.exists(self.filePath)

    def createConfig(self, name, hiveType, fields=None, rules=None):
        """Creates but doesn't save to disk a new name configuration and adds it
        to the preset.

        :param name: The Configuration name to use.
        :type name: str
        :param hiveType: The hive component type to link too.
        :type hiveType: str
        :param fields: The fields to set on the newly created config.
        :type fields: list[dict]
        :param rules: The rules to set on the newly created config.
        :type rules: list[dict]
        :rtype: :class:`NameConfigData`
        """
        name = name or _generateUidConfigName(
            hiveType, directory=os.path.dirname(self.filePath)
        )
        config = naming.NameManager(
            {"name": name, "fields": fields or [], "rules": rules or []}
        )
        configData = NameConfigData(name, hiveType)
        parent = self.findNamingConfigForType(hiveType)
        config.parentConfig = parent
        configData.config = config
        self.configs.append(configData)
        logger.debug("Created Configuration: {}, hiveType: {}".format(name, hiveType))
        return configData

    def removeConfigByName(self, name):
        """Removes the configuration by name from the preset however doesn't delete the config off.
        disk.

        :param name: The name of the configuration to remove.
        :type name: str
        :return: Whether removal was successful.
        :rtype: bool
        """
        for config in self.configs:
            if config.name == name:
                logger.debug(
                    "Removing configuration: {} from preset:{}".format(
                        config.name, self.name
                    )
                )
                self.configs.remove(config)
                return True
        return False

    def removeConfigByHiveType(self, hiveType):
        """Removes The config by the hive type however doesn't delete the config off.

        :param hiveType: The hive component type search for.
        :type hiveType: str
        :return: Whether removal was successful.
        :rtype: bool
        """
        for config in self.configs:
            if config.hiveType == hiveType:
                logger.debug(
                    "Removing configuration: {} from preset:{}".format(
                        config.name, self.name
                    )
                )
                self.configs.remove(config)
                return True
        return False

    def deleteAllConfigs(self):
        """Deletes all configuration instances from disk.

        :return: Whether deletion was successful.
        :rtype: bool
        """
        deleted = False
        for config in self.configs:
            if self.deleteConfig(config.config):
                deleted = True
        return deleted

    def deleteConfig(self, config):
        """Deletes the configuration instance from disk

        :param config: The naming configuration instance to delete.
        :type config: :class:`naming.NameManager`
        :return: Whether deletion was successful.
        :rtype:  bool
        """
        filePath = config.configPath
        self.removeConfigByName(config.name)
        if os.path.exists(filePath):
            logger.debug("Deleting configuration: {}".format(filePath))
            os.remove(filePath)
            return True
        return False

    def findConfigDataByHiveType(self, hiveType, recursive=True):
        """Returns the configuration Data instance stored on the preset.

        :param hiveType: The component hive type.
        :type hiveType: str
        :rtype: :class:`NameConfigData`
        """
        for i in self.configs:
            if i.hiveType == hiveType:
                return i

        if self.parent is not None and recursive:
            return self.parent.findConfigDataByHiveType(hiveType)
        # no parent found so we search for a config outside the preset but only return one
        # if there's only one. This is useful for user component cfgs or new ones
        elif self.parent is None:
            globalCfgs = self.presetManager.findConfigsByType(hiveType)
            if len(globalCfgs) != 1:
                return
            data = NameConfigData(globalCfgs[0], hiveType)
            data.config = globalCfgs[0]
            return data

    def findNamingConfigByName(self, name, recursive=True):
        """Returns the naming configuration instance by name.

        :param name: The name of the configuration to find.
        :type name: str
        :rtype: :class:`naming.NameManager`
        """
        for i in self.configs:
            if i.name == name:
                return i
        if self.parent is not None and recursive:
            return self.parent.findNamingConfigByName(name)

    def findNamingConfigForType(self, hiveType, recursive=True):
        """Finds and returns the naming convention config for the hive Type.

        The Hive Type is one of three keys either "rig", "global" or the component Type.

        :param hiveType: The Hive Type to search for, ie. componentType, "rig" or "global"
        :type hiveType: str
        :return: The naming configuration Manager instance
        :rtype: :class:`zoo.libs.naming.naming.NameManager`
        """
        presetConfigData = self.findConfigDataByHiveType(hiveType, recursive)
        if presetConfigData is None:
            return self.findConfigDataByHiveType("global").config
        return presetConfigData.config


class NameConfigData(object):
    """Data class which stores the config name, hiveType and linked name Manager
    configuration on a preset.
    """

    def __init__(self, name, hiveType):
        self.name = name
        self.hiveType = hiveType
        self.config = None  # type: naming.NameManager or None

    def serialize(self):
        """Returns the raw representation of the configuration which only contains the
        Name and hiveType keys.

        :rtype: dict
        """
        return {"name": self.name, "hiveType": self.hiveType}

    def __eq__(self, other):
        if not isinstance(other, NameConfigData):
            return False
        return self.name == other.name and self.hiveType == other.hiveType

    def __ne__(self, other):
        if not isinstance(other, NameConfigData):
            return True
        return self.name != other.name or self.hiveType != other.hiveType

    def __repr__(self):
        return "NameConfigData(name={}, hiveType={})".format(self.name, self.hiveType)


def _generateUidConfigName(hiveType, directory):
    """Generates a unique name for hive naming configurations.

    .. code-block:: python

        name = _generateUidConfigName("aimcomponent", "C:/Users")
        # aimcomponent_mzf6w3tt


    :param hiveType: The hive component type.
    :type hiveType: str
    :param directory: The directory which will be used as a filter location.
    :type directory: str
    :return: The unique name.
    :rtype: str
    """
    return os.path.basename(tempfile.mktemp(prefix=hiveType + "_", dir=directory))


def surroundTextAsField(text):
    """Returns the text with the field syntax added.

    .. code-block:: python

        text = surroundTextAsField("myField")
        # "{text}"

    :param text: The text to surround
    :type text: str
    :rtype: str
    """
    return "{" + text + "}"


def _pprintTree(item, _prefix="", _last=True):
    treeSep = "`- " if _last else "|- "

    values = [_prefix]
    if isinstance(item, Preset):
        values += [treeSep, "Preset: ", item.name, " Path: ", item.filePath]
    else:
        values += ["|   Config: ", item.name, " Path: ", item.configPath]
    msg = "".join(values)
    print(msg)
    _prefix += "   " if _last else "|  "
    childCount = 0
    children = []
    if isinstance(item, Preset):
        children = [i.config for i in item.configs] + item.children
        childCount = len(children)
    for i, child in enumerate(children):
        _last = i == (childCount - 1)
        _pprintTree(child, _prefix, _last)
