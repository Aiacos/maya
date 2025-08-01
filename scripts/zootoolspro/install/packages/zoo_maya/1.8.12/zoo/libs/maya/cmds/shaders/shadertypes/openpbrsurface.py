"""This module creates and manages Maya's openPBRSurface shader.

This class is a subclass of shaderbase and inherits all functionality where applicable.

Example use:

.. code-block:: python

    from zoo.libs.maya.cmds.shaders.shadertypes import mayaopenPBRSurface
    shadInst = mayaopenPBRSurface.OpenPBRSurface("shaderName", create=True)  # creates a new shader

    shadInst.setDiffuse([0.0, 0.0, 1.0])  # sets diffuse color to blue
    shadInst.setDiffuseWeight(1.0)

    shadInst.setMetalness(1.0)  # sets metalness to be on

    shadInst.setSpecWeight(1.0)
    shadInst.setSpecColor([1, 1, 1])
    shadInst.setSpecRoughness(1.0)
    shadInst.setSpecIOR(1.3)

    shadInst.setCoatWeight(0.0)
    shadInst.setCoatIOR(1.5)
    shadInst.setCoatRoughness(.1)
    shadInst.setCoatColor([1, 1, 1])

    shadInst2 = openPBRSurface.OpenPBRSurface("rocketShader", ingest=True)  # Loads existing "rocketShader" as instance

    shadInst2.assignSelected()

    shadInst2.setShaderName("newNameY")
    print(shadInst2.shaderName())

"""
from maya import cmds

from zoo.libs.maya import zapi

from zoo.libs.utils import color

from zoo.libs.maya.cmds.shaders import shdmultconstants
from zoo.libs.maya.cmds.shaders.shadertypes import shaderbase

NODE_TYPE = "openPBRSurface"
SHADER_SUFFIX = "PBR"
DIFFUSE_WEIGHT_ATTR = "baseWeight"
DIFFUSE_COLOR_ATTR = "baseColor"
DIFFUSE_ROUGHNESS_ATTR = "baseDiffuseRoughness"
METALNESS_ATTR = "baseMetalness"
SPECULAR_WEIGHT_ATTR = "specularWeight"
SPECULAR_COLOR_ATTR = "specularColor"
SPECULAR_ROUGHNESS_ATTR = "specularRoughness"
SPECULAR_IOR_ATTR = "specularIOR"
COAT_WEIGHT_ATTR = "coatWeight"
COAT_COLOR_ATTR = "coatColor"
COAT_ROUGHNESS_ATTR = "coatRoughness"
COAT_IOR_ATTR = "coatIOR"
EMISSION_ATTR = "emissionColor"
EMISSION_WEIGHT_ATTR = "emissionLuminance"
NORMAL_ATTR = "normalCamera"
BUMP_ATTR = "normalCamera"

OUT_COLOR = "outColor"


class OpenPBRSurface(shaderbase.ShaderBase):
    """Manages the creation and set/get attribute values for the OpenPBRSurface shader.
    """
    nodetype = NODE_TYPE
    suffix = SHADER_SUFFIX

    outColorAttr = OUT_COLOR

    diffuseWeightAttr = DIFFUSE_WEIGHT_ATTR
    diffuseColorAttr = DIFFUSE_COLOR_ATTR
    diffuseRoughnessAttr = DIFFUSE_ROUGHNESS_ATTR
    metalnessAttr = METALNESS_ATTR
    specularWeightAttr = SPECULAR_WEIGHT_ATTR
    specularColorAttr = SPECULAR_COLOR_ATTR
    specularRoughnessAttr = SPECULAR_ROUGHNESS_ATTR
    specularIorAttr = SPECULAR_IOR_ATTR
    coatWeightAttr = COAT_WEIGHT_ATTR
    coatcolorAttr = COAT_COLOR_ATTR
    coatRoughnessAttr = COAT_ROUGHNESS_ATTR
    coatIorAttr = COAT_IOR_ATTR
    emissionAttr = EMISSION_ATTR
    emissionWeightAttr = EMISSION_WEIGHT_ATTR
    normalAttr = NORMAL_ATTR
    bumpAttr = BUMP_ATTR

    def __init__(self, shaderName="", node=None, genAttrDict=None, create=False, ingest=False, suffixName=False,
                 message=True):
        """Either loads a shader or creates it.

        To create a new shader:
            create=True and node=False to create a new shader

        To load a shader by zapiNode name
            node="zapiNode" (should be a shader node) and ingest=True

        To load a shader by string:
            shaderName="shaderName" and ingest=True

        :param shaderName: The name of the shader to load or create
        :type shaderName: str
        :param node: A zapi node as an object
        :type node: zoo.libs.maya.zapi.base.DGNode
        :param genAttrDict: The generic attribute dictionary with attribute values to set only if creating
        :type genAttrDict: dict(str)
        :param create: If True then create a new shader False will load the shader and nodes in the instance
        :type create: bool
        :param ingest: If True then shaders should be passed in as a string name (shaderName) or zapi node (node).
        :type ingest: bool
        :param message: Report a message to the user only if creating
        :type message: bool
        """
        super(OpenPBRSurface, self).__init__(shaderName=shaderName,
                                              node=node,
                                              genAttrDict=genAttrDict,
                                              create=create,
                                              ingest=ingest,
                                              suffixName=suffixName,
                                              message=message)

    def knownShader(self):
        """Returns True as this shader is supported by Zoo Tools"""
        return True

    def renderer(self):
        """Returns the current renderer as a string"""
        return shdmultconstants.MAYA

    def setFromDict(self, genAttrDict, apply=True, noneIsDefault=True, colorsAreSrgb=False):
        """Sets the shader from a generic attribute dictionary. Values as attribute values.
        Fix Clear Coat issues where openPBRSurface can apply as grey color, should always be white 100% bright

        Colors are linear by default, use the colorsAreSrgb flag if SRGB.

        Handles None-values in the dictionary and also missing keys.

        None-values and missing keys can either pass or be replaced with default values.

        :param genAttrDict: The generic attribute dictionary with values as attribute values
        :type genAttrDict: dict(str)
        :param apply: Will apply the dict to the current shader, must exist
        :type apply: bool
        :param noneIsDefault: Will apply defaults if the value of the key is None
        :type noneIsDefault: bool
        :param colorsAreSrgb: Set to True if the incoming colors are SRGB such as from a UI.
        :type colorsAreSrgb: bool
        """
        # Fix if color is not 100% bright, multiply it by weight and set color to be full bright.
        if shdmultconstants.COATCOLOR in genAttrDict.keys():  # Fix if coat color is included.
            coatColor = genAttrDict[shdmultconstants.COATCOLOR]
            coatHsv = color.convertRgbToHsv(coatColor)
            colorBrightness = float(coatHsv[2])
            if colorBrightness < 0.99:
                coatHsv[2] = 1.0
                genAttrDict[shdmultconstants.COATCOLOR] = color.convertHsvToRgb(coatHsv)
                genAttrDict[shdmultconstants.COATWEIGHT] *= colorBrightness
        super(OpenPBRSurface, self).setFromDict(genAttrDict,
                                                 apply=apply,
                                                 noneIsDefault=noneIsDefault,
                                                 colorsAreSrgb=colorsAreSrgb)

    # -------------------
    # Create Assign Delete
    # -------------------

    def createShader(self, message=True):
        """Creates a aiSurfaceStandard node network and loads the nodes as class variables

        Overridden method.

        :param message: Report a message to the user when the shader is created
        :type message: bool
        """
        shaderName = cmds.shadingNode(NODE_TYPE, asShader=True, name=self.shaderNameVal)
        self.node = zapi.nodeByName(shaderName)
        self.shaderNameVal = shaderName
        self.applyCurrentSettings()

    # -------------------
    # Setters Getters - Attributes
    # -------------------

    def setDiffuseWeight(self, value):
        """Sets the diffuse weight

        :param value: The diffuse weight value 0.0-1.0
        :type value: float
        """
        if self.setAttrScalar(DIFFUSE_WEIGHT_ATTR, value) is None:  # None is not settable/textured
            return
        self.diffuseWeightVal = value

    def diffuseWeight(self):
        """Returns the current diffuse weight

        :return value: The diffuse weight value 0-1.0, None if textured/connected
        :rtype value: float
        """
        color = self.getAttrScalar(DIFFUSE_WEIGHT_ATTR)
        if color is not None:
            self.diffuseWeightVal = color
        return color

    def setDiffuse(self, color):
        """Sets the diffuse color

        :param color: The diffuse color as rendering space float color, (0.5, 1.0, 0.0)
        :type color: list(float)
        """
        if self.setAttrColor(DIFFUSE_COLOR_ATTR, color) is None:  # None is not settable/textured
            return
        self.diffuseVal = color

    def diffuse(self):
        """Returns the diffuse color

        :return value: The diffuse color as rendering space float rgb (0.1, 0.5, 1.0), None if textured/connected
        :rtype value: list(float)
        """
        color = self.getAttrColor(DIFFUSE_COLOR_ATTR)
        if color is not None:
            self.diffuseVal = color
        return color

    def setDiffuseRoughness(self, value):
        """Sets the diffuse weight

        :param value: The diffuse weight value 0.0-1.0
        :type value: float
        """
        if self.setAttrScalar(DIFFUSE_ROUGHNESS_ATTR, value) is None:  # None is not settable/textured
            return
        self.diffuseRoughnessVal = value

    def diffuseRoughness(self):
        """Returns the current diffuse weight

        :return value: The diffuse weight value 0-1.0, None if textured/connected
        :rtype value: float
        """
        value = self.getAttrScalar(DIFFUSE_ROUGHNESS_ATTR)
        if value is not None:
            self.diffuseRoughnessVal = value
        return value

    def setMetalness(self, value):
        """Sets the metalness value

        :param value: The metalness value 0-1.0
        :type value: float
        """
        if self.setAttrScalar(METALNESS_ATTR, value) is None:  # None is not settable/textured
            return
        self.metalnessVal = value

    def metalness(self):
        """Returns the metalness value

        :return value: The metalness value 0-1.0, None if textured/connected
        :rtype value: float
        """
        color = self.getAttrScalar(METALNESS_ATTR)
        if color is not None:
            self.metalnessVal = color
        return color

    def setSpecWeight(self, value):
        """Sets the specular weight value

        :param value: Specular Weight value 0-1.0
        :type value: float
        """
        if self.setAttrScalar(SPECULAR_WEIGHT_ATTR, value) is None:  # None is not settable/textured
            return
        self.specWeightVal = value

    def specWeight(self):
        """Returns the specular weight value

        :return value:  Specular Weight value 0-1.0, None if textured/connected
        :rtype value: float
        """
        color = self.getAttrScalar(SPECULAR_WEIGHT_ATTR)
        if color is not None:
            self.specWeightVal = color
        return color

    def setSpecColor(self, color):
        """Sets the specular color

        :param color: Specular color as rendering space float rgb (0.5, 1.0, 0.0)
        :type color: list(float)
        """
        if self.setAttrColor(SPECULAR_COLOR_ATTR, color) is None:  # None is not settable/textured
            return
        self.specColorVal = color

    def specColor(self):
        """Returns the specular color

        :return color: Specular color as rendering space float rgb (0.5, 1.0, 0.0), None if textured/connected
        :rtype color: list(float)
        """
        color = self.getAttrColor(SPECULAR_COLOR_ATTR)
        if color is not None:
            self.specColorVal = color
        return color

    def setSpecRoughness(self, value):
        """Sets the specular roughness value

        :param value: The specular roughness value 0-1.0
        :type value: float
        """
        if value < 0.0:
            value = 0.0
        if self.setAttrScalar(SPECULAR_ROUGHNESS_ATTR, value) is None:  # None is not settable/textured
            return
        self.specRoughnessVal = value

    def specRoughness(self):
        """Returns the specular roughness value

        :return value: The specular roughness value 0-1.0, None if textured/connected
        :rtype value: float
        """
        color = self.getAttrScalar(SPECULAR_ROUGHNESS_ATTR)
        if color is not None:
            self.specRoughnessVal = color
        return color

    def setSpecIOR(self, value):
        """Sets the specular IOR value

        :param value: The specular IOR value, 1.0 - 20.0
        :type value: float
        """
        if self.setAttrScalar(SPECULAR_IOR_ATTR, value) is None:  # None is not settable/textured
            return
        self.specIORVal = value

    def specIOR(self):
        """Sets the specular IOR

        :return value: The specular IOR value, 1.0 - 20.0, None if textured/connected
        :rtype value: float
        """
        color = self.getAttrScalar(SPECULAR_IOR_ATTR)
        if color is not None:
            self.specIORVal = color
        return color

    def setCoatWeight(self, value):
        """Sets the clear coat weight

        :param value: The clear coat weight value 0-1.0
        :type value: float
        """
        if self.setAttrScalar(COAT_WEIGHT_ATTR, value) is None:  # None is not settable/textured
            return
        self.coatWeightVal = value

    def coatWeight(self):
        """Returns the clear coat weight

        :return value: The clear coat weight value 0-1.0, None if textured/connected
        :rtype value: float
        """
        color = self.getAttrScalar(COAT_WEIGHT_ATTR)
        if color is not None:
            self.coatWeightVal = color
        return color

    def setCoatColor(self, color):
        """Sets the clear coat color

        :param color: Clear coat color as rendering space float rgb (0.5, 1.0, 0.0)
        :type color: list(float)
        """
        if self.setAttrColor(COAT_COLOR_ATTR, color) is None:  # None is not settable/textured
            return
        self.coatColorVal = color

    def coatColor(self):
        """Returns the clear coat color

        :return color: Clear coat color as rendering space float rgb (0.5, 1.0, 0.0), None if textured/connected
        :rtype color: list(float)
        """
        color = self.getAttrColor(COAT_COLOR_ATTR)
        if color is not None:
            self.coatColorVal = color
        return color

    def setCoatRoughness(self, value):
        """Sets the clear coat roughness value

        :param value: The clear coat roughness value 0 -1.0
        :type value: float
        """
        if self.setAttrScalar(COAT_ROUGHNESS_ATTR, value) is None:  # None is not settable/textured
            return
        self.coatRoughnessVal = value

    def coatRoughness(self):
        """Returns the clear coat roughness value

        :return value: The clear coat roughness value 0 -1.0, None if textured/connected
        :rtype value: float
        """
        color = self.getAttrScalar(COAT_ROUGHNESS_ATTR)
        if color is not None:
            self.coatRoughnessVal = color
        return color

    def setCoatIOR(self, value):
        """Sets the clear coat IOR value

        :param value: The clear coat IOR value, 1.0 - 20.0
        :type value: float
        """
        if self.setAttrScalar(COAT_IOR_ATTR, value) is None:  # None is not settable/textured
            return
        self.coatIORVal = value

    def coatIOR(self):
        """Returns the clear coat IOR value

        :return value: The clear coat IOR value, 1.0 - 20.0, None if textured/connected
        :rtype value: float
        """
        color = self.getAttrScalar(COAT_IOR_ATTR)
        if color is not None:
            self.coatIORVal = color
        return color

    def setEmission(self, color):
        """Sets the emission (self illumination) color

        :param color: Emission color as rendering space float rgb (0.5, 1.0, 0.0)
        :type color: list(float)
        """
        if self.setAttrColor(EMISSION_ATTR, color) is None:  # None is not settable/textured
            return
        self.emissionVal = color

    def emission(self):
        """Returns the emission (self illumination) color

        :return color: Emission color as rendering space float rgb (0.5, 1.0, 0.0), None if textured/connected
        :rtype color: list(float)
        """
        color = self.getAttrColor(EMISSION_ATTR)
        if color is not None:
            self.emissionVal = color
        return color

    def setEmissionWeight(self, value):
        """Sets the emission weight value

        :param value: Emission weight value, 1.0 and above
        :type value: float
        """
        if self.setAttrScalar(EMISSION_WEIGHT_ATTR, value) is None:  # None is not settable/textured
            return
        self.emissionWeightVal = value

    def emissionWeight(self):
        """Returns the emission weight value

        :return value: Emission weight value, 1.0 and above, None if textured/connected
        :rtype value: float
        """
        value = self.getAttrScalar(EMISSION_WEIGHT_ATTR)
        if value is not None:
            self.emissionWeightVal = value
        return value
