import os
from abc import ABCMeta, abstractmethod

from zoo.libs.command import errors
from zoovendor import six

try:
    from inspect import getfullargspec
except ImportError:
    from inspect import getargspec as getfullargspec

RETURN_STATE_SUCCESS = 0
RETURN_STATE_ERROR = 1


@six.add_metaclass(ABCMeta)
class CommandInterface(object):
    """The standard ZooCommand metaclass interface. Each command must implement doIt, id, creator, isUndoable, description

    """
    uiData = {"icon": "",
              "tooltip": "",
              "label": "",
              "color": "",
              "backgroundColor": ""
              }

    def __init__(self, stats=None):
        self.stats = stats
        self.arguments = ArgumentParser()
        self._returnResult = None
        self._warning = ""
        self._errors = ""
        self.returnStatus = RETURN_STATE_SUCCESS
        self.initialize()

    def initialize(self):
        """Intended for overriding by the subclasses, intention here is if the subclass needs __init__ functionality
        then this function should be used instead to avoid any mishaps in any uncalled data.

        """
        pass

    @abstractmethod
    def doIt(self, **kwargs):
        """Main method to implemented the command operation. all subclasses must have a doIt method
        The DoIt method only support Kwargs meaning that every argument must have a default, this is by design to
        maintain clarity in people implementation.

        :param kwargs: key value pairs, values can be any type , we are not restricted by types including custom \
        objects or DCC dependent objects eg.MObjects.
        :param kwargs: dict

        :return This method should if desired by the developer return a value, this value can be anything \
        including maya api MObject etc.

        :Example:

            # correct
            doIt(source=None, target=None, translate=True)
            # incorrect
            doIt(source, target=None, translate=True)

        """

        pass

    def undoIt(self):
        """If this command instance is set to undoable then this method needs to be implemented, by design you do the
        inverse operation of the doIt method

        :return:
        :rtype:

        """
        pass

    def runIt(self):
        """ Runs `doIt` with the current arguments

        :return: The result from doIt
        """
        return self.doIt(**self.arguments)

    def runArguments(self, **arguments):
        """ Parses the arguments then runs the command

        :param arguments: key, value pairs that correspond to the DoIt method
        :type arguments:
        :return:
        :rtype:
        """
        self.parseArguments(arguments)
        return self.runIt()

    def resolveArguments(self, arguments):
        """Method which allows the developer to pre doIt validate the incoming arguments. This method get executed before
        any operation on the command.

        :param arguments: key, value pairs that correspond to the DoIt method
        :type arguments: dict
        :return: Should always return a dict with the same key value pairs as the arguments param
        :rtype: dict

        """
        return arguments

    @property
    @abstractmethod
    def id(self):
        """Returns the command id which is used to call the command and should be unique

        :return: the Command id
        :rtype: str

        """
        pass

    @property
    @abstractmethod
    def creator(self):
        """Returns the developer name of this command

        :rtype: str

        """
        pass

    @property
    @abstractmethod
    def isUndoable(self):
        """Returns whether this command is undoable or not

        :return: Defaults to False
        :rtype: bool

        """
        return False

    def commandUi(self):
        """Method to launch dialogs for this command instance, When a command is run the client can specify 
        if the ui is required
        """
        pass


class ZooCommand(CommandInterface):
    isEnabled = True
    useUndoChunk = True  # Chunk all operations in doIt()
    disableQueue = False  # If true, disable the undo queue in doIt()

    def initialize(self):
        self.prepareCommand()

    def description(self):
        return self.__doc__

    def requiresWarning(self):
        if self._warning:
            return True
        return False

    def displayWarning(self, message):
        self._warning = message

    def warningMessage(self):
        return self._warning

    def cancel(self, msg=None):
        """Raises the UserCancel error, useful when validating arguments

        :param msg: The Error message to display
        :type msg: str
        :raise: :class:`errors.UserCancel`
        """

        raise errors.UserCancel(msg)

    def hasArgument(self, name):
        return name in self.arguments

    def parseArguments(self, arguments):
        """ Parse the arguments and get it ready for the command to use

        :param arguments: dictionary
        :type arguments: duct
        :return:
        :rtype: bool
        """
        kwargs = self.arguments
        kwargs.update(arguments)
        results = self.resolveArguments(ArgumentParser(**kwargs)) or {}

        kwargs.update(results)
        return True

    def prepareCommand(self):
        funcArgs = getfullargspec(self.doIt)
        args = funcArgs.args[1:]
        defaults = funcArgs.defaults or tuple()
        if len(args) != len(defaults):
            raise ValueError("The command doIt function({}) must use keyword argwords".format(self.id))
        elif args and defaults:
            arguments = ArgumentParser(zip(args, defaults))
            self.arguments = arguments
            return arguments
        return ArgumentParser()

    @classmethod
    def commandAction(cls, uiType, parent=None, optionBox=False):
        # import locally due to avoid qt dependencies by default
        from zoo.libs.command import commandui

        if uiType == 0:
            widget = commandui.CommandAction(cls)
        else:
            widget = commandui.MenuItem(cls)
        widget.create(parent=parent, optionBox=optionBox)
        return widget


class ArgumentParser(dict):
    def __getattr__(self, item):
        result = self.get(item)
        if result:
            return result
        return super(ArgumentParser, self).__getAttribute__(item)


def generateCommandTemplate(className, id, doItContent, undoItContent, filePath,
                            creator, doitArgs):
    """Function to Generate a ZooCommand template.

    :param className: the command class Name
    :type className: str
    :param id: the command Id
    :type id: str
    :param doItContent: The python code for the doIt method
    :type doItContent: str
    :param undoItContent: The python code for the undoIt method
    :type undoItContent: str
    :param filePath: The file location to create this command
    :type filePath: str
    :param creator: the command developers name
    :type creator: str
    :param doitArgs: The doIt arguments
    :type doitArgs: dict
    :return:
    :rtype:

    """
    code = """
from zoo.libs.command import command


class {className}(command.ZooCommand):
    id = "{id}"
    creator = "{creator}"
    isUndoable = {isUndoable}
    isEnabled = True

    def doIt(self, {doItArgs}):
        {doItContent}
        
    def undoIt(self):
        {undoItContent}

""".format(className=className, id=id, isUndoable=True if undoItContent else False,
           doItArgs=", ".join(doitArgs), doItContent=doItContent or "pass",
           undoItContent=undoItContent or "pass", creator=creator)
    if os.path.exists(filePath):
        with open(filePath, "a") as f:
            f.write(code)
        return True
    with open(os.path.realpath(filePath), "w") as f:
        f.write(code)
    return True
