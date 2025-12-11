"""CtrlsShape allows to manually modify the controls CVs of the node. """
import logging

import maya.cmds as mc
import maya.api.OpenMaya as om

from arise.utils.decorators_utils import reset_issue_indicator
from arise.utils.io_nodes.io_track_node import IoTrackNode
from arise.data_types.attachment_data import AttachmentData
from arise.utils import tagging_utils


LOGGER = logging.getLogger("node_rig_logger")

MAYA_VERSION = 2016
AUTHOR = "Etay Herz"
RIG_TYPE = "Ctrls"
RIG_CATEGORY = "Post"
TAGS = ["ctrls", "control", "cv", "offset", "store"]
TOOL_TIP = "CtrlsShape allows you to modify the shape of ctrls manually."


class CtrlsShape(AttachmentData):
    """Here we will reimplement methods to 1) create attributes on the attachment
    2) create guides in the template module and 3) the rig method where the rig will be built.
    """
    sort_priority = 200

    def __init__(self, parent, icon, docs, module_dict):
        AttachmentData.__init__(
            self,
            parent=parent,
            icon=icon,
            docs=docs,
            module_dict=module_dict
        )

    @property
    def category(self):  # REIMPLEMENTED!
        """Returns the category number. 1-'build', 2-'finalize', 3-'post'. """
        return 3

    @staticmethod
    def attachment_permissions(node):
        """Return True or False if attachment allowed on node.

        Arguments:
            node {node_ptr} -- node to check permission with

        Returns:
            [bool] -- True if allowed or False if not
        """
        if list(node.node_data.ctrls_manager):
            return True

        module = __file__.rsplit("\\", 1)[-1].rsplit("/", 1)[-1].rsplit(".", 1)[0]
        LOGGER.warning(
            "Cannot add attachment '%s' to node '%s'. Node has no ctrls to operate on.",
            module, node.name,
        )
        return False

    @staticmethod
    def support_copy_settings():  # REIMPLEMENTED!
        """Return True if this attachment supports copying settings between nodes of same module.
        Reimplemented by subclasses that do support copy settings to return True. default is to return False.
        """
        return True

    def attributes_creation(self):  # REIMPLEMENTED!
        """Here you add the attributes. """
        self.add_separator(title="Settings")
        self.add_button(
            buttons=[
                (
                    self.store_modifications,
                    "resources/icons/attachments/modify_ctrl_cvs.png",
                    "Save Modifications",
                    "Save manual modifications done to this node's ctrls shapes",
                ),
                (
                    self.remove_stored_ctrls_modifications,
                    "resources/icons/attachments/reset_ctrl_cvs.png",
                    "Clear Modifications",
                    "Remove stored modifications done to this node's ctrls shapes",
                ),
            ],
        )
        self.custom_shapes_checkbox = self.add_boolean_attribute(
            name="Store Full Curve Data",
            default_value=False,
            annotation=(
                "Allows editing ctrls beyond moving existing CVs.\n"
                "Stores full NURBS Curve data under each ctrl's transform node.\n"
                "Supports replacing shapes with custom ones.\n"
                "Increases build time and file size."
            ),
        )

    @reset_issue_indicator
    def store_modifications(self):
        """Store the modifications to this node ctrls shapes. """
        if self.top_node_data.state_manager.state in ["None", "Template"]:
            LOGGER.warning("['%s'] can only store ctrls modifications in 'Build' state", self.long_name)
            return False

        ctrls_trans = tagging_utils.get_node_tagged_ctrl_item(tag=self.top_node_data.uuid.hex)

        if not ctrls_trans:
            LOGGER.warning("['%s'] cannot find ctrls in Maya scene", self.long_name)
            return False

        if self.custom_shapes_checkbox.value:
            return self.store_custom_shapes_data(ctrls_trans)

        else:
            return self.store_ctrls_cvs_offsets(ctrls_trans)

    def store_ctrls_cvs_offsets(self, ctrls_trans):
        """Store only the CVs positions of the ctrl shapes. OLD METHOD.

        Arguments:
            ctrls_trans {list} -- list of ctrl transform nodes
        """

        database = {}
        for ctrl in ctrls_trans:
            ctrl_type, default_name = mc.getAttr("{0}.{1}".format(ctrl, tagging_utils.CTRL_ITEM)).split("| ")
            shapes = self.get_ctrl_shapes(ctrl)

            if not shapes:
                continue

            shapes_data = {}
            for shape in shapes:

                if not mc.objExists("{0}.{1}".format(shape, tagging_utils.CTRL_ITEM)):
                    continue

                index = mc.getAttr("{0}.{1}".format(shape, tagging_utils.CTRL_ITEM))

                sel = om.MSelectionList()
                sel.add(shape)
                dag = sel.getDagPath(0)
                mfn = om.MFnNurbsCurve(dag)

                cvs = [mfn.cvPosition(i, om.MSpace.kObject) for i in range(mfn.numCVs)]
                cvs_positions = [list(cv) for cv in cvs]

                shapes_data[str(index)] = cvs_positions

            database[str(default_name)] = {
                "type": str(ctrl_type),
                "shapes": shapes_data,
            }

        self.internal_database = database
        LOGGER.info("['%s'] Ctrls shapes offsets Saved", self.long_name)
        return True

    def store_custom_shapes_data(self, ctrls_trans):
        """Store the full NurbsCurve data of the ctrl shapes.

        Arguments:
            ctrls_trans {list} -- list of ctrl transform nodes
        """
        database = {}
        for ctrl in ctrls_trans:
            _, default_name = mc.getAttr("{0}.{1}".format(ctrl, tagging_utils.CTRL_ITEM)).split("| ")
            shapes = mc.listRelatives(ctrl, shapes=True, type="nurbsCurve", fullPath=True) or []

            if not shapes:
                continue

            shapes_data = {}
            for index, shape in enumerate(shapes):
                sel = om.MSelectionList()
                sel.add(shape)
                dag = sel.getDagPath(0)
                mfn = om.MFnNurbsCurve(dag)

                degree = mfn.degree
                form = mfn.form  # 0=open, 1=closed, 2=periodic
                spans = mfn.numSpans
                cvs = [mfn.cvPosition(i, om.MSpace.kObject) for i in range(mfn.numCVs)]
                cvs = [list(cv) for cv in cvs]
                knots = list(mfn.knots())

                if degree + 1 > len(cvs):  # To avoid error when recreating curve with insufficient CVs.
                    LOGGER.warning("[%s] Skipping save. Insufficient CVs for shape: '%s'", self.module_type, shape)
                    return False

                shapes_data[str(index)] = {
                    "degree": degree,
                    "form": form,
                    "spans": spans,
                    "cvs": cvs,
                    "knots": knots,
                }

            database[str(default_name)] = {
                "type": "__custom__",  # To support backwards compatibility custom shapes stored as type __custom__
                "shapes": shapes_data,
            }

        self.internal_database = database
        LOGGER.info("['%s'] Saved full NURB curves data", self.long_name)
        return True

    @reset_issue_indicator
    def remove_stored_ctrls_modifications(self):
        """Simply removes any stored modification data. """
        self.internal_database = {}
        LOGGER.info("['%s'] Removed Stored Modifications", self.long_name)

    @staticmethod
    def get_ctrl_shapes(ctrl_long_name):
        """Return list of ctrl shapes long names that are tagged as ctrls.

        Arguments:
            ctrl_long_name {str} -- long name of ctrl
        """
        shapes = mc.listRelatives(ctrl_long_name, fullPath=True, shapes=True)
        return [shape for shape in shapes if mc.listAttr(ctrl_long_name, ct=tagging_utils.CTRL_ITEM)]

    def attachment_creation(self):
        """Search for ctrl nodes in scene and apply offsets on their shapes. """

        if not self.internal_database:
            return "No stored modifications. Skipping attachment."

        ctrls_effected = []
        for ctrl in self.top_node_data.ctrls_manager.io_ctrls_list:
            stored_data = self.internal_database.get(ctrl.default_name, None)

            if stored_data is None:
                continue

            if stored_data["type"] not in [ctrl.info.shape, "__custom__"]:
                continue

            if stored_data["type"] == "__custom__":
                self.create_custom_shape(ctrl, stored_data)

            else:  # Support old method of storing only CVs positions offsets.
                self.apply_stored_shape_offsets(ctrl, stored_data)

            ctrls_effected.append(ctrl)

        if not ctrls_effected:
            return "No ctrls modified."

        return True

    def apply_stored_shape_offsets(self, ctrl, stored_data):
        for shape in ctrl.transform.shapes_list:
            if not mc.listAttr(shape, ct=tagging_utils.CTRL_ITEM):
                continue

            index = mc.getAttr("{0}.{1}".format(shape, tagging_utils.CTRL_ITEM))
            offsets = stored_data["shapes"].get(str(index), None)

            if not offsets:
                continue

            self.set_curve_cvs_local(shape, offsets)

    def set_curve_cvs_local(self, curve, positions):
        """
        Sets each CV of the given NURBS curve to specific positions in object (local) space.

        Arguments:
            curve {str} -- The name of the NURBS curve shape node.
            positions {list} -- A list of positions (tuples/lists) for each CV.
        """
        selection_list = om.MGlobal.getSelectionListByName(str(curve))
        mfn = om.MFnNurbsCurve(selection_list.getDagPath(0))

        if len(positions) != mfn.numCVs:
            LOGGER.warning("[%s] Skipping curve. CV count mismatch for curve '%s'.", self.module_type, curve)
            return

        cvs = [om.MPoint(p) for p in positions]
        mfn.setCVPositions(cvs, om.MSpace.kObject)
        mfn.updateCurve()

    def create_custom_shape(self, ctrl, stored_data):
        """Recreate custom shape(s) for ctrl based on stored data.

        Arguments:
            ctrl {CtrlData} -- ctrl data object
            stored_data {dict} -- stored shape data from internal_database
        """
        transform_name = ctrl.transform.long_name

        driver = None
        for shape in ctrl.transform.shapes_list:
            driver = mc.listConnections("{0}.visibility".format(shape), source=True, destination=False, plugs=True)

            if driver:
                driver = driver[0]
                break

        if ctrl.transform.shapes_list:
            mc.delete(ctrl.transform.shapes_list)

        ctrl.transform.shapes_list = []

        shapes_data = stored_data.get("shapes", {})

        for index_str, shape_data in shapes_data.items():
            mfn_curve = om.MFnNurbsCurve()
            new_curve_obj = mfn_curve.create(
                [om.MPoint(*p) for p in shape_data["cvs"]],
                shape_data["knots"],
                shape_data["degree"],
                shape_data["form"],
                False,  # not rational
                False,  # not 2D
                om.MObject.kNullObj
            )

            shape_transform = om.MFnDagNode(new_curve_obj).fullPathName()
            shape_name = mc.listRelatives(shape_transform, shapes=True, fullPath=True)[0]
            shape = IoTrackNode(shape_name)

            mc.parent(shape_name, transform_name, shape=True, relative=True)

            if mc.objExists(shape_transform):
                mc.delete(shape_transform)

            short_name = transform_name.rsplit("|", 1)[-1]
            final_shape_name = mc.rename(shape, "{0}Shape".format(short_name))

            tagging_utils.tag_as_ctrl_item(final_shape_name, index_str)
            ctrl.transform.shapes_list.append(shape)

            mc.setAttr("{0}.overrideEnabled".format(final_shape_name), 1)
            mc.setAttr("{0}.overrideRGBColors".format(final_shape_name), 1)
            mc.setAttr("{0}.overrideColorRGB".format(final_shape_name), *ctrl.info.color, type="double3")

            mc.setAttr("{0}.lineWidth".format(final_shape_name), ctrl.info.line_width)

            if driver:  # If visibility was driven before, reconnect it.
                mc.connectAttr(driver, "{0}.visibility".format(final_shape_name), force=True)
