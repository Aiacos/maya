"""AbstractCheck is a class every model validation check will inherit from. holding logic shared by all checks. """

import os
import traceback

from arise.external_modules import six

from arise.pyside.QtGui import QIcon, QColor
from arise.pyside.QtCore import QObject, Signal

import maya.cmds as mc

ROOT_FOLDER = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

STATE_ICON = {
    "none": QIcon(os.path.join(ROOT_FOLDER, "resources", "none_icon.png")),
    "warning": QIcon(os.path.join(ROOT_FOLDER, "resources", "warning_icon.png")),
    "minor_warning": QIcon(os.path.join(ROOT_FOLDER, "resources", "minor_warning_icon.png")),
    "error": QIcon(os.path.join(ROOT_FOLDER, "resources", "error_icon.png")),
    "success": QIcon(os.path.join(ROOT_FOLDER, "resources", "success_icon.png")),
}

BG_COLOR = {
    "none": QColor(45, 45, 45),
    "warning": QColor(130, 130, 60),
    "minor_warning": QColor(100, 100, 60),
    "error": QColor(130, 60, 60),
    "success": QColor(60, 140, 60),
}

VALID_CHILDREN = ["mesh", "nurbsCurve", "nurbsSurface", "transform"]


def undo_chunk_dec(func):
    """Decorator to run the function in an Maya undo chunk and catch errors. """
    def wrapper(*args, **kwargs):
        result = None
        mc.undoInfo(openChunk=True)
        try:
            result = func(*args, **kwargs)
        except:  # pass error to log but don't stop code execution.
            print("")
            print("#"*50)  # keep.
            print("##### error executing: '{0}' #####".format(func.__name__))  # keep.
            print("")
            traceback.print_exc()
            print("#"*50)  # keep.
            print("")
        finally:
            mc.undoInfo(closeChunk=True)

        return result

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__

    return wrapper


class AbstractCheck(QObject):
    """A class every model validation check will inherit from. holding logic shared by all checks.

    Args:
        namespace (str or None): str namespace to run checks on or None to search everything in the scene
    """

    state_change_signal = Signal()

    def __init__(self, namespace=False):
        QObject.__init__(self)

        self.namespace = namespace
        self._state = "none"
        self._check_type = "error"
        self._can_select = True
        self._can_fix = True
        self._name = ""
        self._one_line = ""
        self._explanation = ""
        self._position = 100000

    def __str__(self):
        """String representation of this class. """
        if self.name:
            return self.name

        return self.__class__.__name__

    @property
    def state(self):
        """Return the str name of the current state. """
        return self._state[:]

    def reset(self):
        """Reset check state to none. """
        self._update_state(is_success=None)

    def _update_state(self, is_success):
        """Set the state based on check result and 'is_error'.

        Args:
            is_success (bool or None): True if check passed successfully False if failed, None to reset check.
        """
        if is_success is None:
            self._state = "none"
            self.state_change_signal.emit()
            return

        if is_success is True:
            self._state = "success"
            self.state_change_signal.emit()
            return

        self._state = self.check_type
        self.state_change_signal.emit()

    @property
    def icon(self):
        """Return the QIcon for matching the current state. """
        return STATE_ICON[self.state]

    @property
    def color(self):
        """Return the QColor for background based on current state. """
        return BG_COLOR[self.state]

    @property
    def check_type(self):
        """Return str the type of check this is 'error', 'warning', 'minor_warning'. """
        return self._check_type

    @check_type.setter
    def check_type(self, value):
        """Set this check to either 'error' or 'warning', or 'minor_warning'.

        Args:
            value (str): 'error' or 'warning', or 'minor_warning'
        """
        if value not in ['error', 'warning', 'minor_warning']:
            raise ValueError("[check_type] must be ['error', 'warning', 'minor_warning']. got: {0}".format(value))

        self._check_type = value

    @property
    def position(self):
        """Return int number dictating where in the list this check will be. """
        return self._position

    @position.setter
    def position(self, value):
        """Set the position in the list this check will be in. low numbers appear first high numbers last.

        Args:
            value (int): position index
        """
        if not isinstance(value, int):
            raise ValueError("[position] value must be an int. got '{0}'".format(value))

        self._position = value

    @property
    def name(self):
        """return name of check. """
        return self._name

    @name.setter
    def name(self, value):
        """Set the name of this check.

        Args:
            value (str): name of check
        """
        if not isinstance(value, six.string_types):
            raise ValueError("[name] provided name must be a str. got: '{0}'".format(value))

        self._name = value

    @property
    def one_line(self):
        """return one line explanation of check. """
        return self._one_line

    @one_line.setter
    def one_line(self, value):
        """Set the one line explanation of check.

        Args:
            value (str): text of one line explanation
        """
        if not isinstance(value, six.string_types):
            raise ValueError("[one_line] provided name must be a str. got: '{0}'".format(value))

        self._one_line = value

    @property
    def explanation(self):
        """return long explanation of this check. """
        return self._explanation

    @explanation.setter
    def explanation(self, value):
        """Set long explanation of this check.

        Args:
            value (str): text of long explanation
        """
        if not isinstance(value, six.string_types):
            raise ValueError("[explanation] must be a str. got: '{0}'".format(value))

        self._explanation = value

    @property
    def can_fix(self):
        """Return True if this check can has a fix. """
        return self._can_fix

    @can_fix.setter
    def can_fix(self, value):
        """True to enable this check fix option. """
        if not isinstance(value, bool):
            raise ValueError("[can_fix] must be passed a bool. got: '{0}'".format(value))

        self._can_fix = value

    @property
    def can_select(self):
        """Return True if this check can select objects in Maya after check has run. """
        return self._can_select

    @can_select.setter
    def can_select(self, value):
        """True to enable this check select option. """
        if not isinstance(value, bool):
            raise ValueError("[can_select] must be passed a bool. got: '{0}'".format(value))

        self._can_select = value

    def namespace_str(self):
        """Return str for searching in a namespace used when searching objects using mc.ls(). """
        return "{0}::*".format(self.namespace if self.namespace else "")

    @undo_chunk_dec
    def do_run_check(self):
        """Called by other methods. it runs 'run_check' and update the state. """
        result = self.run_check()
        self._update_state(result)

    @undo_chunk_dec
    def do_run_fix(self):
        """Called by other methods. it runs 'run_fix' and re-runs the check to validate it was fixed. """
        self.run_fix()
        self.do_run_check()

    @undo_chunk_dec
    def do_run_select(self):
        """Calls on run_select but with undo_chunk decorator. """
        self.run_select()

    def run_check(self):
        """This method run the check on the scene. if this method returns True the check passed.
            returns False means the check failed. subclasses will reimplement this method.
        """
        return

    def run_select(self):
        """This method should select objects in Maya that failed the test. subclasses will reimplement this. """
        return

    def run_fix(self):
        """This method will fix objects in the scene so the check will pass. subclasses will reimplement this. """
        return

    def get_all_meshes(self, skip_intermediate=False):
        """Return a list of long names of all 'mesh' nodes.

        Args:
            skip_intermediate (bool): True to skip shapes with intermediateObject on
        """
        shapes = mc.ls(self.namespace_str(), type="mesh", long=True)

        if skip_intermediate:
            shapes = [shape for shape in shapes if not mc.getAttr("{0}.intermediateObject".format(shape))]

        return shapes

    def get_all_curves(self, skip_intermediate=False):
        """Return a list of long names of all 'nurbsCurve' nodes.

        Args:
            skip_intermediate (bool): True to skip shapes with intermediateObject on
        """
        shapes = mc.ls(self.namespace_str(), type="nurbsCurve", long=True)

        if skip_intermediate:
            shapes = [shape for shape in shapes if not mc.getAttr("{0}.intermediateObject".format(shape))]

        return shapes

    def get_all_surfaces(self, skip_intermediate=False):
        """Return a list of long names of all 'nurbsSurface' nodes.

        Args:
            skip_intermediate (bool): True to skip shapes with intermediateObject on
        """
        shapes = mc.ls(self.namespace_str(), type="nurbsSurface", long=True)

        if skip_intermediate:
            shapes = [shape for shape in shapes if not mc.getAttr("{0}.intermediateObject".format(shape))]

        return shapes

    def get_all_deformables(self, skip_intermediate=False):
        """Return a list of long names of all 'mesh', 'nurbsCurve', and 'nurbsSurface' nodes.

        Args:
            skip_intermediate (bool): True to skip shapes with intermediateObject on
        """
        skip = skip_intermediate
        return self.get_all_meshes(skip) + self.get_all_curves(skip) + self.get_all_surfaces(skip)

    def get_all_deformables_transforms(self):
        """Return a list of long names of 'mesh', 'nurbsCurve', and 'nurbsSurface' transform parents. """
        parent_transforms = []
        for obj in self.get_all_deformables(True):
            parent = mc.listRelatives(obj, parent=True, fullPath=True, type="transform") or []

            if parent:
                parent_transforms.append(parent[0])

        return list(set(parent_transforms))

    def get_all_transforms(self):
        """Return a list of long names of all 'transform' nodes. """
        return mc.ls(self.namespace_str(), type="transform", long=True)

    def get_deformable_and_empty_transforms(self):
        """Return the transforms of 'mesh', 'nurbsCurves', 'nurbsSurface', and empty transforms. """
        valid_transforms = []

        transforms = [trans for trans in self.get_all_transforms() if mc.nodeType(trans) == "transform"]
        for transform in transforms:
            if not mc.listRelatives(transform, children=True):
                valid_transforms.append(transform)
                continue

            # Maya bug workaround for some node types (like greasePencil)
            for shape in mc.listRelatives(transform, children=True, fullPath=True, type=VALID_CHILDREN) or []:
                if mc.objectType(shape) in VALID_CHILDREN:
                    valid_transforms.append(transform)
                    continue

        return valid_transforms
