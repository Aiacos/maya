from zoo.core.util import env
from zoo.libs.command import base
from zoovendor import six


class ExecutorMeta(type):
    """Executor meta class singleton to hot swap the class type depending on which environment
    we're in. For Example if we're in maya the zoo.libs.maya.mayacommand.mayaexecutor.MayaExecutor will be
    created
    """
    _instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            if env.isMaya():
                from zoo.libs.maya.mayacommand import mayaexecutor
                cls._instance = type.__call__(mayaexecutor.MayaExecutor, *args, **kwargs)
            else:
                cls._instance = type.__call__(base.ExecutorBase, *args, **kwargs)
        return cls._instance


@six.add_metaclass(ExecutorMeta)
class Executor(object):
    pass


def execute(executeId, **kwargs):
    """ Helper to execute zoo commands by id

    :param executeId: ID To execute
    :type executeId: basestring
    :return: Returns the executor and anything from exe execute
    """
    exe = Executor()
    return exe.execute(executeId, **kwargs)
