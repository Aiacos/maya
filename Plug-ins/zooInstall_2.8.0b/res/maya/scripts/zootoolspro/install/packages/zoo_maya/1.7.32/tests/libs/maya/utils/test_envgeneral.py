from zoo.libs.maya.utils import mayatestutils
from zoo.libs.maya.utils import general


class TestEnvGeneral(mayatestutils.BaseMayaTest):
    keepPluginsLoaded = True
    def test_pluginQuery(self):
        self.loadPlugin("zooundo.py")
        self.assertTrue(general.isPluginLoaded("zooundo.py"))
