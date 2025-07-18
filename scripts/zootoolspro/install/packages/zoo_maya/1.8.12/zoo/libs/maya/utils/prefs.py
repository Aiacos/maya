from maya import cmds

def isControllerPrepopulateActive():
    """
    This method returns True if the controllers are set to prepopulate the
    graph, False otherwise.
    """

    return cmds.optionVar(q="prepopulateController")


def setControllerPrepopulateActive(state):
    """
    This method activates or deactivates the controller prepopulation of the
    graph.
    """

    cmds.optionVar(iv=("prepopulateController", state))