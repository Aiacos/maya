
from zoo.libs.command import command
from maya import cmds
from zoo.libs.command.errors import UserCancel
import logging

logger = logging.getLogger(__name__)


class ZooCommandMaya(command.ZooCommand):

    def disableUndoQueue(self, disable):
        """ Disable Undo Queue

        :param disable: Disable undo queue
        :type disable: bool
        :return:
        """
        cmds.undoInfo(stateWithoutFlush=not disable)

    def isQueueDisabled(self):
        """ Check if it is disabled or not

        :return:
        :rtype: type
        """
        return not cmds.undoInfo(stateWithoutFlush=1, q=1)

    def runArguments(self, **arguments):
        """ Parses the arguments then runs the command

        :param arguments: key, value pairs that correspond to the DoIt method
        :type arguments:
        :return:
        :rtype:
        """
        orig = self.isQueueDisabled()

        if self.useUndoChunk:
            cmds.undoInfo(openChunk=True)
        self.disableUndoQueue(self.disableQueue)

        try:
            self.parseArguments(arguments)
            ret = self.runIt()
        except UserCancel:
            raise
        except Exception:
            raise
        finally:
            self.disableUndoQueue(orig)
            if self.useUndoChunk:
                cmds.undoInfo(closeChunk=True)

        return ret
