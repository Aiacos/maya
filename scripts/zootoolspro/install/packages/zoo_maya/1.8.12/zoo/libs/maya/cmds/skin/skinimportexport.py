"""Import Export Skin Weights

Currently supports weightBlended weights only.

from zoo.libs.maya.cmds.skin import skinimportexport
blendWeightsDict = skinimportexport.dqWeightBlended("skinCluster1")

from zoo.libs.maya.cmds.skin import skinimportexport
skinCluster = "natBody_geo_skin"
path = r"D:\Dropbox\3dC3dC\_hiveRigs\natalieHive\data\dqBlendWeights\natDqWeights.json"
skinimportexport.saveDqWeightBlendedPath(skinCluster, path)

from zoo.libs.maya.cmds.skin import skinimportexport
skinCluster = "natBody_geo_skin"
path = r"D:\Dropbox\3dC3dC\_hiveRigs\natalieHive\data\dqBlendWeights\natDqWeights.json"
skinimportexport.loadDqWeightBlendedPath(skinCluster, path)

"""

from zoo.libs.maya import zapi
from zoo.libs.utils import filesystem


def dqWeightBlended(skinCluster):
    """ Serializes the dual quaternion blend weights of the skin cluster to a dictionary.

    Vert numbers and weights are stored in a dictionary.

    DICT = {67: 0.07964204251766205, 68: 0.1235511302947998}

    :return: The dictionary of the blend weights, keys are the vertex indices and values are the blend weight values.
    :rtype: dict
    """
    node = zapi.nodeByName(skinCluster)
    blendWeights = {}
    for i in node.blendWeights:
        vertex = i.logicalIndex()
        value = i.value()
        blendWeights[vertex] = value
    return blendWeights


def setDqWeightBlended(skinCluster, blendWeightsDict):
    """ Sets the dual quaternion blend weights of the skin cluster from a dictionary.

    Vert numbers and weights in dictionary.

    DICT = {67: 0.07964204251766205, 68: 0.1235511302947998}

    :param skinCluster: The skin cluster to set the blend weights on.
    :type skinCluster: str
    :param blendWeightsDict: The dictionary of the blend weights, keys are the vertex indices and values are the blend weight values.
    :type blendWeightsDict: dict
    """
    node = zapi.nodeByName(skinCluster)
    for vertex, value in blendWeightsDict.items():
        node.blendWeights[vertex].set(value)


def loadDqWeightBlendedPath(skinCluster, path):
    """ Loads the dual quaternion blend weights of the skin cluster from a file.

    JSON = {"67": 0.07964204251766205, "68": 0.1235511302947998}
    string keys must be converted to integers
    DICT = {67: 0.07964204251766205, 68: 0.1235511302947998}

    :param skinCluster: The skin cluster to set the blend weights on.
    :type skinCluster: str
    :param path: The path to the file to load the blend weights from.
    :type path: str
    """
    blendWeightsDict = filesystem.loadJson(path)
    blendWeightsDict = {int(k): v for k, v in blendWeightsDict.items()}  # keys must be integers, not strings
    setDqWeightBlended(skinCluster, blendWeightsDict)


def saveDqWeightBlendedPath(skinCluster, path):
    """ Saves the dual quaternion blend weights of the skin cluster to a file.

    Keys are converted into strings for JSON.
    JSON = {"67": 0.07964204251766205, "68": 0.1235511302947998}

    :param skinCluster: The skin cluster to set the blend weights on.
    :type skinCluster: str
    :param path: The path to the file to save the blend weights to.
    :type path: str
    """
    blendWeightsDict = dqWeightBlended(skinCluster)
    filesystem.saveJson(blendWeightsDict, path)
