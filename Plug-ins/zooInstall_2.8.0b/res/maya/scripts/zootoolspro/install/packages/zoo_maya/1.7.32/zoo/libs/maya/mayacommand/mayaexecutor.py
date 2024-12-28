# @note if the executed command is not maya based its still going to be part of maya internal undo stack
# which could be bad but maybe not :D
import traceback

import sys
from maya import cmds
from maya.api import OpenMaya as om2
from zoo.libs.command import base
from zoo.libs.command import errors
from zoo.libs.maya.mayacommand import command
from zoo.libs.maya.utils import general
from zoo.libs.utils import output
from zoo.core.util import zlogging


logger = zlogging.getLogger(__name__)


class MayaExecutor(base.ExecutorBase):
    """Maya Executor class for safely injecting zoo commands into the maya undo stack via MPXCommands.
    Always call executor.execute() method when executing commands
    """

    def __init__(self):
        super(MayaExecutor, self).__init__(interface=[command.ZooCommandMaya], registerEnv="ZOO_COMMAND_LIB")
        om2._COMMANDEXECUTOR = self
        general.loadPlugin("zooundo.py")

    def execute(self, commandName, **kwargs):
        """Function to execute Zoo commands which lightly wrap maya MPXCommands.
        Deals with prepping the Zoo plugin with the command instance. Safely opens and closes the undo chunks via
        maya commands (cmds.undoInfo)

        :param commandName: The command.id value
        :type commandName: str
        :param kwargs: A dict of command instance arguments, should much the signature of the command.doit() method
        :type kwargs: dict
        :return: The command instance returns arguments, up to the command developer
        """
        logger.debug("Executing command: {}".format(commandName))
        cmdObj = self.findCommand(commandName)
        if cmdObj is None:
            raise ValueError("No command by the name: {} exists within the registry!".format(commandName))
        if om2._COMMANDEXECUTOR is None:
            om2._COMMANDEXECUTOR = self
        cmd = cmdObj()
        if not cmd.isEnabled:
            return
        try:
            cmd.parseArguments(kwargs)
            if cmd.requiresWarning():
                output.displayWarning(cmd.warningMessage())
                return
        except errors.UserCancel:
            raise
        except Exception:
            raise
        exc_tb, exc_type, exc_value = None, None, None
        cmd.stats = base.CommandStats(cmd)
        try:
            if cmd.isUndoable and cmd.useUndoChunk:
                cmds.undoInfo(openChunk=True, chunkName=cmd.id)
            om2._ZOOCOMMAND = cmd
            cmds.zooAPIUndo(commandId=cmd.id)
            if cmd.returnStatus == command.command.RETURN_STATE_ERROR:
                exc_type, exc_value, exc_tb = sys.exc_info()
                message = "Command failed to execute: {}".format(cmd.id)
                raise errors.CommandExecutionError(message)
            return cmd._returnResult

        finally:
            tb = None
            if exc_type and exc_value and exc_tb:
                tb = traceback.format_exception(exc_type, exc_value, exc_tb)
            if cmd.isUndoable and cmd.useUndoChunk:
                cmds.undoInfo(closeChunk=True)
            cmd.stats.finish(tb)
            logger.debug("Finished executing command: {}".format(commandName))

    def flush(self):
        super(MayaExecutor, self).flush()
        cmds.flushUndo()