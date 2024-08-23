"""CalamariRigAction exports a rig that removes skinning and converts it to parenting by slicing the meshes. """

import os

import maya.cmds as mc
from maya import mel

from arise.utils.decorators_utils import simple_catch_error_dec
from arise.utils.tagging_utils import get_maya_nodes_with_tag, get_all_tagged_ctrl_item, MODELS_GRP_NAME

CATEGORY = "arise_base_main_ctrl_tag"


class CalamariRigAction(object):
    """Export rig that removes skinning and converts it to parenting by slicing the meshes. """
    def __init__(self):
        self.name = "Calamari Rig"
        self.info = (
            "Exports a rig that slices skinned meshes to segments and parent under joints.\n"
            "Used as a fast animation rig."
        )
        self.position = 1200
        self.is_checked = False
        self.post_action = True

    @staticmethod
    @simple_catch_error_dec
    def run_action(save_path):
        """Run slice skinned meshes.

        save_path (str): full save path
        """
        print("\n#########################################################")
        print("############ Action: 'Calamari Rig' START. ##############")
        print("#########################################################\n")

        path, ext = os.path.abspath(save_path).rsplit(".", 1)
        calamari_path = "{0}_calamari.{1}".format(path, ext)

        for ctrl in get_all_tagged_ctrl_item():

            if not mc.listAttr(ctrl, category=CATEGORY):
                continue

            attr = "{0}.joints_visibility".format(ctrl)

            if not mc.objExists(attr):
                    continue

            if mc.getAttr(attr, lock=True):
                continue

            if mc.listConnections(attr, source=True, destination=False):
                continue

            mc.setAttr(attr, 1)

        geo_grp = get_maya_nodes_with_tag(MODELS_GRP_NAME)

        if not geo_grp or not mc.objExists(geo_grp[0]):
            return "Cannot find 'geometry_grp' folder. Aborting"

        for mesh in mc.listRelatives(geo_grp[0], allDescendents=True, fullPath=True, type="transform") or []:
            skin_cluster = mel.eval('findRelatedSkinCluster {0}'.format(mesh)) or None
            if not skin_cluster:
                continue

            if not mc.listRelatives(mesh, children=True, noIntermediate=True, shapes=True, type="mesh"):
                continue

            joints_index = mc.skinPercent(skin_cluster, "{0}.vtx[:]".format(mesh), transform=None, q=True)
            joints_dict = {jnt: [] for jnt in joints_index}

            for face in mc.ls("{0}.f[:]".format(mesh), fl=True):
                face_verts = mc.ls(mc.polyListComponentConversion(face, fromFace=True, toVertex=True), fl=True)

                values = []
                for vert in face_verts:
                    values.append(mc.skinPercent(skin_cluster, vert, q=True, value=True))

                values_sum = [sum(val) for val in zip(*values)]

                joints_dict[joints_index[values_sum.index(max(values_sum))]].append(face.rsplit(".", 1)[-1])

            for joint, faces in joints_dict.items():
                if not faces:
                    continue

                shape = mc.listRelatives(mesh, children=True, noIntermediate=True, shapes=True, type="mesh")[0]
                dup_mesh = mc.duplicate(
                    [mesh, shape],
                    inputConnections=False,
                    name="{0}_{1}_calamari_geo".format(mesh.rsplit("|", 1)[-1], joint.rsplit("|", 1)[-1]),
                    parentOnly=True,
                )[0]
                mc.delete(dup_mesh, constructionHistory=True)

                for attr in ["translate", "rotate", "scale"]:
                    for axis in "XYZ":
                        mc.setAttr("{0}.{1}{2}".format(dup_mesh, attr, axis), lock=False)

                faces_list = []
                for face in faces:
                    faces_list.append("{0}.{1}".format(dup_mesh, face))

                mc.select(faces_list)
                mc.select("{0}.f[:]".format(dup_mesh), toggle=True)

                if mc.ls(sl=True):
                    mc.delete()

                mc.delete(dup_mesh, constructionHistory=True)
                mc.parent(dup_mesh, joint)

        mc.delete(geo_grp[0])

        mc.file(rename=calamari_path)
        mc.file(
            save=True,
            type='mayaAscii' if calamari_path.endswith((".ma", ".MA")) else "mayaBinary",
            force=True,
            executeScriptNodes=False,
        )

        print("calamari rig exported to: '{0}'".format(calamari_path))

        return "Action successful"
