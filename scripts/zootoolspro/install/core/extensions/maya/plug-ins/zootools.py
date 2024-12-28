import logging
import cProfile
import os
import sys
from functools import wraps
from maya import OpenMayaMPx
from maya import OpenMaya

logger = logging.getLogger(__name__)
if not len(logger.handlers):
    logger.addHandler(logging.StreamHandler())
# set the level, we do this for the plugin since this module usually gets executed before zootools is initialized
if os.getenv("ZOO_LOG_LEVEL", "INFO") == "DEBUG":
    logger.setLevel(logging.DEBUG)


def _embedPaths():
    """This ensures zootools python paths have been setup correctly"""
    rootPath = os.getenv("ZOOTOOLS_PRO_ROOT", "")
    rootPythonPath = os.path.join(rootPath, "python")
    rootPythonPath = os.path.abspath(rootPythonPath)

    if rootPythonPath is None:
        msg = """Zootools is missing the 'ZOOTOOLS_PRO_ROOT' environment variable
                in the maya mod file.
                """
        raise ValueError(msg)
    elif not os.path.exists(rootPythonPath):
        raise ValueError("Failed to find valid zootools python folder, incorrect .mod state")
    if rootPythonPath not in sys.path:
        sys.path.append(rootPythonPath)


def loadZoo():
    rootPath = os.getenv("ZOOTOOLS_PRO_ROOT", "")
    rootPath = os.path.abspath(rootPath)

    if rootPath is None:
        msg = """Zoo Tools PRO is missing the 'ZOOTOOLS_PRO_ROOT' environment variable
        in the maya mod file.
        """
        raise ValueError(msg)

    from zoo.core import api
    from zoo.core import engine
    from zoo.core.util import zlogging
    from maya import utils

    manager = zlogging.CentralLogManager()
    manager.removeHandlers(zlogging.CENTRAL_LOGGER_NAME)
    manager.addHandler(zlogging.CENTRAL_LOGGER_NAME, utils.MayaGuiLogHandler())

    existingPackageEnv = os.getenv(api.constants.ZOO_PACKAGE_VERSION_FILE)
    if not existingPackageEnv:
        os.environ[api.constants.ZOO_PACKAGE_VERSION_FILE] = "package_version_maya.config"

    import zoomayaengine
    currentInstance = api.currentConfig()
    if currentInstance is None:
        coreConfig = api.zooFromPath(rootPath)
        engine.startEngine(coreConfig, zoomayaengine.MayaEngine, "maya")


def profileIt(func):
    """cProfile decorator to profile said function, must pass in a filename to write the information out to
    use RunSnakeRun to run the output

    :return: Function
    """
    profileFlag = int(os.environ.get("ZOO_PROFILE", "0"))
    profileExportPath = os.path.expandvars(os.path.expanduser(os.environ.get("ZOO_PROFILE_PATH", "")))
    shouldProfile = False
    if profileFlag and profileExportPath:
        shouldProfile = True

    @wraps(func)
    def inner():
        if shouldProfile:
            logger.debug("Running CProfile output to : {}".format(profileExportPath))
            prof = cProfile.Profile()
            retval = prof.runcall(func)
            # Note use of name from outer scope
            prof.dump_stats(profileExportPath)
            return retval
        else:
            return func()

    return inner


@profileIt
def create():
    OpenMaya.MGlobal.displayInfo("Loading Zoo Tools PRO, please wait!")
    logger.debug("Loading Zoo Tools PRO")
    _embedPaths()
    loadZoo()


def initializePlugin(obj):
    OpenMayaMPx.MFnPlugin(obj, "David Sparrow", "1.0")

    try:
        create()
    except Exception as er:
        logger.error("Unhandled Exception occurred during Zoo tools startup", exc_info=True)
        OpenMaya.MGlobal.displayError("Unknown zoo tools startup failure: \n{}".format(er))


def uninitializePlugin(obj):
    OpenMayaMPx.MFnPlugin(obj)
    try:
        from zoo.core import api
        cfg = api.currentConfig()
        if cfg is not None:
            cfg.shutdown()
    except Exception as er:
        logger.error("Unhandled Exception occurred during Zoo tools shutdown", exc_info=True)
        OpenMaya.MGlobal.displayError("Unknown zoo tools shutdown failure: \n{}".format(er))
