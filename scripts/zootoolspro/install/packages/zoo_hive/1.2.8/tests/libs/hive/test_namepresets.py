import os

from zoo.libs.maya.utils import mayatestutils
from zoo.libs.hive import api
from zoo.libs.hive.base import namingpresets


class TestNamingPresets(mayatestutils.BaseMayaTest):
    newSceneAfterTest = False
    _createdPresets = []

    def tearDown(self):
        self.presetManager = api.namingpresets.PresetManager()
        for preset in self._createdPresets:
            self.presetManager.deletePreset(preset)

    def setUp(self):
        self.presetManager = api.namingpresets.PresetManager()
        hierarchy = self.presetManager.prefInterface.namingPresetHierarchy()
        self.presetManager.loadFromEnv(hierarchy)

    def test_createPreset(self):
        folderPath = self.presetManager.prefInterface.namingPresetSavePath()
        newPreset = self.presetManager.createPreset("testTempPreset", folderPath)
        self._createdPresets.append(newPreset)
        outputName = os.path.join(
            folderPath, os.path.extsep.join((newPreset.name, namingpresets.PRESET_EXT))
        )
        self.assertFalse(
            os.path.exists(newPreset.filePath),
            "Creating Preset shouldn't create a file",
        )
        self.assertEqual(newPreset.name, "testTempPreset")
        self.assertEqual(newPreset.filePath, outputName)
        self.presetManager.savePreset(newPreset)
        self.assertTrue(
            os.path.exists(newPreset.filePath),
            "Saving file didn't create the file : {}".format(newPreset.filePath),
        )
        self.presetManager.deletePreset(newPreset)
        self.assertFalse(
            os.path.exists(newPreset.filePath),
            "Deleting Preset didn't delete the file : {}".format(newPreset.filePath),
        )

    def test_duplicatePreset(self):
        folderPath = self.presetManager.prefInterface.namingPresetSavePath()
        rootPreset = self.presetManager.createPreset("testTempPreset", folderPath,
                                                     parent=self.presetManager.rootPreset)
        childPreset = self.presetManager.createPreset(
            "testTempPreset", folderPath, parent=rootPreset
        )
        self._createdPresets.append(rootPreset)
        self._createdPresets.append(childPreset)
        self.presetManager.printHierarchy()
        childCfg = childPreset.createConfig(name="", hiveType="global")
        rootCfg = rootPreset.createConfig(name="", hiveType="global",
                                          )
        self.presetManager.saveConfig(childCfg.config)
        self.presetManager.saveConfig(rootCfg.config)
        self.presetManager.savePreset(rootPreset)
        self.presetManager.savePreset(childPreset)

        # duplicate and validate child presets and configs were copied correctly.
        newDuplicate = self.presetManager.duplicatePreset(rootPreset)
        self.assertTrue(newDuplicate.name.startswith(rootPreset.name + "_COPY"))
        self.assertEqual(len(newDuplicate.children), 1)
        self.assertEqual(newDuplicate.parent, rootPreset.parent)
        # ensure we're copies not a ref
        for i, inst in enumerate(newDuplicate.children):
            self.assertNotEqual(inst, rootPreset.children[i])

    def test_allRulesHaveValidExampleFields(self):
        for n, config in self.presetManager.namingConfigs.items():
            for rule in config.rules(False):
                expressionFields = rule.fields()
                exampleFields = rule.exampleFields
                self.assertTrue(
                    all(i in exampleFields for i in expressionFields),
                    "Missing exampleFields for rule {}".format(rule.name),
                )
