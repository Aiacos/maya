__LEGAL__ = """
# -----------------------------------------------------------------------------
#  Arise Rigging System 2026. All Rights Reserved.
#
#  This file is part of a proprietary software product. Unauthorized copying,
#  modification, distribution, decompiling, or use of this file, via any medium,
#  is strictly prohibited without explicit written permission from the copyright owner.
#
#  For licensing info, contact: info@ariserigging.com
# -----------------------------------------------------------------------------
"""

"""Check for near-zero-length edges and near-zero-area faces."""

import maya.api.OpenMaya as om
import maya.cmds as mc

from .abstract_check.abstract_check import AbstractCheck

EDGE_LENGTH_TOLERANCE = 1e-8
FACE_AREA_TOLERANCE = 1e-12


def mesh_dag_path(mesh):
    """Return the API DAG path for a mesh's full path."""
    selection = om.MSelectionList()
    selection.add(mesh)
    return selection.getDagPath(0)


class DegenerateGeometryCheck(AbstractCheck):
    """Identify degenerate components in non-intermediate meshes."""

    def __init__(self, namespace):
        AbstractCheck.__init__(self, namespace)
        self.position = 10800
        self.check_type = "warning"
        self.name = "Degenerate Faces and Edges"
        self.one_line = "Checks for near-zero-area faces and near-zero-length edges"
        self.explanation = (
            "Checks non-intermediate meshes in object space for edges no longer than\n"
            "1e-8 cm and faces with an area no greater than 1e-12 square cm.\n"
            "'Select' - selects the affected edges and faces.\n"
            "Review and repair the geometry manually."
        )
        self.can_select = True
        self.can_fix = False
        self.selection_list = []

    def run_check(self):
        """Find degenerate components."""
        self.selection_list = self._get_degenerate_components()
        return not self.selection_list

    def _get_degenerate_components(self):
        """Return full component paths for degenerate edges and faces."""
        components = []
        for mesh in self.get_all_meshes(True):
            path = mesh_dag_path(mesh)
            edges = om.MItMeshEdge(path)
            while not edges.isDone():
                if edges.length(om.MSpace.kObject) <= EDGE_LENGTH_TOLERANCE:
                    components.append("{0}.e[{1}]".format(mesh, edges.index()))
                edges.next()

            faces = om.MItMeshPolygon(path)
            while not faces.isDone():
                if faces.getArea(om.MSpace.kObject) <= FACE_AREA_TOLERANCE:
                    components.append("{0}.f[{1}]".format(mesh, faces.index()))
                faces.next()

        return components

    def run_select(self):
        """Select the affected edges and faces."""
        self.selection_list = self._get_degenerate_components()
        mc.selectMode(component=True)
        mc.selectType(polymeshEdge=True, polymeshFace=True)
        mc.select(self.selection_list, replace=True)
        print("[{0}] selected: <{1}> {2}".format(self, len(self.selection_list), self.selection_list))
