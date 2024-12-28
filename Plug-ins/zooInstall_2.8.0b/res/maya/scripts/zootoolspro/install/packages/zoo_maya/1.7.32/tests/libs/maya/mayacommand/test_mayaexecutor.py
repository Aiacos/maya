import os
from maya import cmds
from maya.api import OpenMaya as om2

from zoo.libs.maya.utils import mayatestutils
from zoo.libs.command import executor


class TestMayaCommandExecutor(mayatestutils.BaseMayaTest):
    @classmethod
    def setUpClass(cls):
        super(TestMayaCommandExecutor, cls).setUpClass()
        os.environ["TESTDATA"] = os.pathsep.join(["tests.testdata.mayacommanddata.testmayacommand",
                                                  "tests.testdata.commanddata.testcommands"])

    def setUp(self):
        self.executor = executor.Executor()
        self.executor.flush()
        self.env = "TESTDATA"
        self.executor.registry.registerByEnv(self.env)

    def testCommandExecutes(self):
        result = self.executor.execute("test.mayaSimpleCommand")
        self.assertEqual(result, "hello world")

    # standalone based commands need to be tested in maya as well
    def testCommandFailsArguments(self):
        with self.assertRaises(ValueError) as context:
            self.executor.execute("Test.mayaTestCommandFailsOnResolveArgs", value="helloWorld")

    def testUndoLast(self):
        result = om2.MObjectHandle(self.executor.execute("test.mayaTestCreateNodeCommand"))
        self.assertTrue(result.isAlive() and result.isValid())
        cmds.undo()
        self.assertFalse(result.isAlive() and result.isValid())
        cmds.redo()
        self.assertTrue(result.isAlive() and result.isValid())

    def testUndoSkips(self):
        result = self.executor.execute("test.mayaNotUndoableCommand")
        self.assertEqual(result, "hello world")
        result = self.executor.undoLast()
        self.assertFalse(result)
