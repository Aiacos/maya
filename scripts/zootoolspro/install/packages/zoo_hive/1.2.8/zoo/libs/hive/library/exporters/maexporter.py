
import ast
import os
import logging
import pprint

import maya.mel as mel
from maya import cmds

from zoo.core.util import zlogging

from zoo.libs.maya import zapi
from zoo.libs.maya.utils import files, general
from zoo.libs.maya.cmds.filemanage import saveexportimport
from zoo.libs.hive import api


from zoo.libs.utils import output, filesystem

logger = zlogging.getLogger(__name__)




class ExportSettings(object):
    """Handles All Currently available fbx export settings
    """

    def __init__(self):
        self.outputPath = ""


    def pprint(self):
        pprint.pprint({"outputPath": self.outputPath})


class MaExporterPlugin(api.ExporterPlugin):
    """

    .. code-block:: python
        from zoo.libs.hive import api as hiveapi
        rigInstance = r.rig()
        rigInstance.startSession("rig")
        exporter = hiveapi.Configuration().exportPluginForId("maExport")()
        settings = exporter.exportSettings()  # type: zoo.libs.hive.library.exporters.fbxexporter
        settings.outputPath = outputPath
        exporter.execute(rigInstance, settings)
    """
    id = "maExport"

    def exportSettings(self):
        return ExportSettings()

    def export(self, rig, exportOptions):
        """

        :param rig:
        :type rig: :class:`zoo.libs.hive.base.rig.Rig`
        :param exportOptions:
        :type exportOptions: :class:`ExportSettings`
        :return:
        :rtype:
        """

        self.onProgressCallbackFunc(50, "Exporting to .ma")
        if not rig.exists():
            output.displayError("Rig does not exist")
            return

        transform = rig.rootTransform()
        metaNode = rig.meta
        zapi.select([transform, metaNode])

        cmds.file(exportOptions.outputPath,
                  force=True,
                  options="v=0;",
                  type="mayaAscii",
                  preserveReferences=True,
                  exportSelected=True)






