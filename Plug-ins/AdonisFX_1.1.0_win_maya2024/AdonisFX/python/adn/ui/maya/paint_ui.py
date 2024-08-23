import maya.cmds as cmds
import maya.mel as mel

from PySide2 import QtCore, QtGui, QtWidgets

from adn.ui.widgets.base import BaseWidget
from adn.utils import path
from adn.utils.constants import UiConstants

from adn.ui.widgets.dialogs import msg_box
from adn.ui.maya.window import main_window
from adn.utils.maya.undo_stack import undo_chunk


class PaintToolUI(BaseWidget):
    """Class to implement the paint brush tool.

    Args:
        deformer (str): Deformer node name.
        node_type (str): Node type name.
        paintable_attributes (list): List of paintable attributes.
        multi_infl_attr (list): List of multi influence paintable
            attributes.
        mesh_node (str): Mesh node being painted.
        dcc_tool (Auxiliar methods): Methods not related to the UI but to the paint tool.
        parent (:obj:`BaseWidget`): Parent class of the current tool class.
        *args: Argument list.
        **kwargs: Keyword argument list.
    """
    TOOL_PAINT = "AdnPaintToolContext"
    PICKER_PAINT_CTX = "AdnPaintToolPickContext"
    # Empty paint tool to disable painting while showing visual feedback to the user.
    PAINT_TOOL_DISABLED = "AdnPaintToolInvalidTool"
    # Last selected tool button from Maya tool section.
    TOOL_BUTTON = "ToolBox|MainToolboxLayout|frameLayout5|flowLayout2|lastNonSacredTool"

    def __init__(self, deformer, node_type, paintable_attributes, multi_infl_attr, 
                 mesh_node, dcc_tool, parent, *args, **kwargs):
        super(PaintToolUI, self).__init__("Paint Tool",
                                          parent,
                                          width=360,
                                          height=300)
        self.deformer = deformer
        self.node_type = node_type
        self.paintable_attrib_list = paintable_attributes
        self.multi_infl_attr = multi_infl_attr
        self.deformer_influences = list()
        self.ui_influences_names = list()
        self.ui_influences_long_names = list()
        self.entering_ui = False
        self.pick_error = False

        # Gather the influences names from the deformer
        self._update_influences_names()

        self.dcc_tool = dcc_tool
        self.mesh_node = mesh_node
        self.mesh = ""
        mesh_transform = cmds.listRelatives(mesh_node, parent=True, fullPath=True) or []
        if mesh_transform:
            self.mesh = mesh_transform[0]
        self.colors_active = False

        # Shading node cached variables
        self._shading_group_uuid = ""

        # Current stored poly option. This is necessary to remove the specular component of the painting 
        # for the current custom paint tool. We trigger "none" when activating the paint tool and
        # we restore the previous poly option when disabled
        self._poly_option = "none"

        # Node debug cached variables
        self._debug_flag = False
        self._debug_feature = -1

        # Select the current paintable mesh so the paint context only allows to paint on the active mesh.
        cmds.select(self.mesh)

        self.button_not_active = "background-color: none; border: none;"
        self.button_active = "background-color: #5285A6; border: none;"

        self._build_ui()
        self._connect_signals()

        if not cmds.artAttrTool(exists=self.PAINT_TOOL_DISABLED):
            cmds.artAttrTool(add=self.PAINT_TOOL_DISABLED)

        if not cmds.artUserPaintCtx(self.TOOL_PAINT, exists=True):
            cmds.artUserPaintCtx(self.TOOL_PAINT)
        
        tool_setup_cmd = self.dcc_tool.create_mel_procedure(
            self._paint_ctx_setup_procedure,
            [('string', 'toolContext')])
        tool_cleanup_cmd = self.dcc_tool.create_mel_procedure(
            self._paint_ctx_cleanup_procedure, 
            [('string', 'toolContext')])

        # Setup the paint context using the custom callbacks
        cmds.artUserPaintCtx(
            self.TOOL_PAINT,
            edit=True,
            toolSetupCmd=tool_setup_cmd,
            toolCleanupCmd=tool_cleanup_cmd,
            initializeCmd="AdnPaintInitializeCommand",
            finalizeCmd="AdnPaintFinalizeCommand",
            setValueCommand="AdnPaintSetValueCommand",
            getValueCommand="AdnPaintGetValueCommand",
            colorfeedback=False,
            whichTool="userPaint",
            fullpaths=True,
            image1="adn_paint_tool.png")

        cmds.select(self.mesh)

        self.attr_combo.blockSignals(True)
        self.attr_combo.setCurrentIndex(0)
        self.attr_combo.blockSignals(False)
        self._attr_changed()
        paint_mode = cmds.artUserPaintCtx(self.TOOL_PAINT, query=True, selectedattroper=True)
        self._change_weight_mode(paint_mode)

        if (self.attr_combo.currentText() not in self.multi_infl_attr or
                (self.ui_influences_names and self.ui_influences_long_names)):
            self._paint_ctx_setup_procedure()
            # Select multi-influence object if we are in a multi-influence atttribute.
            # This must be done outside _paint_ctx_setup_procedure to avoid selecting meshes
            # when enabling the paint context from the tool box.
            selected_indices = [item.row() for item in self.influences_list.selectedIndexes()]
            if self.attr_combo.currentText() in self.multi_infl_attr and selected_indices:
                selected_item = self.ui_influences_names[selected_indices[0]]
                self.dcc_tool.select_multi_influence_obj(selected_item)

    def _build_ui(self):
        """Builds the UI for the paint tool.
        """
        vertical_layout = QtWidgets.QVBoxLayout()

        # Button Layout
        form_layout = QtWidgets.QFormLayout()
        form_layout.setFormAlignment(QtCore.Qt.AlignHCenter)
        buttons_layout = QtWidgets.QHBoxLayout()
        vertical_layout.addLayout(form_layout)
        
        # Refresh Context Button
        self.refresh_ctx_button = QtWidgets.QPushButton("Refresh From Selection")
        self.refresh_ctx_button.setMaximumWidth(200)
        self.refresh_ctx_button.setMinimumWidth(200)

        buttons_layout.addWidget(self.refresh_ctx_button)
        form_layout.addRow(buttons_layout)

        # Paint Attributes
        paint_group = QtWidgets.QGroupBox("Paint Attributes")
        form_layout = QtWidgets.QFormLayout()
        paint_group.setLayout(form_layout)
        vertical_layout.addWidget(paint_group)

        # Attribute Selection Dropdown
        label = QtWidgets.QLabel("Attribute:")
        self.attr_combo = QtWidgets.QComboBox()
        self.attr_combo.setMinimumWidth(250)
        self.attr_combo.addItems(self.paintable_attrib_list)
        self.attr_combo.setCurrentIndex(0)
        self.attr_combo.setMaximumWidth(250)

        form_layout.addRow(label, self.attr_combo)

        # Influences names dropdown
        self.influences_label = QtWidgets.QLabel("Influences:")
        self.influences_list = QtWidgets.QListWidget()
        self.influences_list.setSortingEnabled(False)
        self.influences_list.setMinimumHeight(self.influences_list.sizeHintForColumn(0))
        self.influences_list.setMinimumWidth(250)
        self.influences_list.setCurrentRow(0)

        self.influences_label.hide()
        self.influences_list.hide()

        form_layout.addRow(self.influences_label, self.influences_list)

        # Paint Context Value
        label = QtWidgets.QLabel("Value:")
        horizontal_layout = QtWidgets.QHBoxLayout()
        self.value_spin = QtWidgets.QDoubleSpinBox()
        self.value_spin.setDecimals(4)
        self.value_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.value_spin.setMinimum(0.0)
        self.value_spin.setMaximum(1.0)
        self.value_spin.setMaximumWidth(65)
        self.value_spin.setMinimumWidth(65)
        self.value_slider = QtWidgets.QSlider()
        self.value_slider.setOrientation(QtCore.Qt.Horizontal)
        self.value_slider.setSingleStep(1)
        self.value_slider.setMinimum(0)
        self.value_slider.setMaximum(10000)
        self.value_slider.setMaximumWidth(148)
        self.value_slider.setMinimumWidth(148)
        
        # Pick Button
        icon_size = 14
        button_size = 20
        self._picker_icon_path = ":/colorPickIcon.png"
        self._picker_pixmap = QtGui.QPixmap(self._picker_icon_path)
        picker_scaled = self._picker_pixmap.scaledToHeight(icon_size, QtCore.Qt.SmoothTransformation)
        self._picker_icon = QtGui.QIcon(picker_scaled)

        self.pick_button = QtWidgets.QPushButton('')
        self.pick_button.setIcon(self._picker_icon)
        self.pick_button.setIconSize(QtCore.QSize(icon_size, icon_size))
        self.pick_button.setToolTip("Value picker")
        self.pick_button.setMaximumWidth(button_size)
        self.pick_button.setMinimumWidth(button_size)
        self.pick_button.setMaximumHeight(button_size)
        self.pick_button.setMaximumHeight(button_size)

        horizontal_layout.addWidget(self.value_spin)
        horizontal_layout.addWidget(self.value_slider)
        horizontal_layout.addWidget(self.pick_button)
        form_layout.addRow(label, horizontal_layout)

        # Brush Style 
        brush_group = QtWidgets.QGroupBox("Brush")
        form_layout = QtWidgets.QFormLayout()
        brush_group.setLayout(form_layout)
        vertical_layout.addWidget(brush_group)

        # Weight Operation
        label = QtWidgets.QLabel("Paint operation:")
        weight_operation_layout = QtWidgets.QHBoxLayout()
        self.weight_absolute = QtWidgets.QRadioButton("Replace")
        self.weight_additive = QtWidgets.QRadioButton("Add")
        self.weight_scale = QtWidgets.QRadioButton("Scale")
        self.weight_smooth = QtWidgets.QRadioButton("Smooth")

        weight_operation_layout.addWidget(self.weight_absolute)
        weight_operation_layout.addWidget(self.weight_additive)
        weight_operation_layout.addWidget(self.weight_scale)
        weight_operation_layout.addWidget(self.weight_smooth)
        
        form_layout.addRow(label, weight_operation_layout)
        
        # Radius (U)
        label = QtWidgets.QLabel("Radius(U):")
        horizontal_layout = QtWidgets.QHBoxLayout()
        self.radius_spin = QtWidgets.QDoubleSpinBox()
        self.radius_spin.setDecimals(4)
        self.radius_spin.setMinimum(0.0)
        self.radius_spin.setMaximum(500.0)
        self.radius_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.radius_spin.setMaximumWidth(65)
        self.radius_spin.setMinimumWidth(65)
        self.radius_slider = QtWidgets.QSlider()
        self.radius_slider.setOrientation(QtCore.Qt.Horizontal)
        self.radius_slider.setSingleStep(1)
        self.radius_slider.setMinimum(0)
        self.radius_slider.setMaximum(50000)
        self.radius_slider.setMaximumWidth(150)
        self.radius_slider.setMinimumWidth(150)
        
        horizontal_layout.addWidget(self.radius_spin)
        horizontal_layout.addWidget(self.radius_slider)
        form_layout.addRow(label, horizontal_layout)
        
        # LowerRadius (L)
        label = QtWidgets.QLabel("Radius(L):")
        horizontal_layout = QtWidgets.QHBoxLayout()
        self.lower_radius_spin = QtWidgets.QDoubleSpinBox()
        self.lower_radius_spin.setDecimals(4)
        self.lower_radius_spin.setMinimum(0.0)
        self.lower_radius_spin.setMaximum(500.0)
        self.lower_radius_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.lower_radius_spin.setMaximumWidth(65)
        self.lower_radius_spin.setMinimumWidth(65)
        self.lower_radius_slider = QtWidgets.QSlider()
        self.lower_radius_slider.setOrientation(QtCore.Qt.Horizontal)
        self.lower_radius_slider.setSingleStep(1)
        self.lower_radius_slider.setMinimum(0)
        self.lower_radius_slider.setMaximum(50000)
        self.lower_radius_slider.setMaximumWidth(150)
        self.lower_radius_slider.setMinimumWidth(150)
        
        horizontal_layout.addWidget(self.lower_radius_spin)
        horizontal_layout.addWidget(self.lower_radius_slider)
        form_layout.addRow(label, horizontal_layout)
        
        # Opacity
        label = QtWidgets.QLabel("Opacity:")
        horizontal_layout = QtWidgets.QHBoxLayout()
        self.opacity_spin = QtWidgets.QDoubleSpinBox()
        self.opacity_spin.setDecimals(4)
        self.opacity_spin.setMinimum(0.0)
        self.opacity_spin.setMaximum(1.0)
        self.opacity_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.opacity_spin.setMaximumWidth(65)
        self.opacity_spin.setMinimumWidth(65)
        self.opacity_slider = QtWidgets.QSlider()
        self.opacity_slider.setOrientation(QtCore.Qt.Horizontal)
        self.opacity_slider.setSingleStep(1)
        self.opacity_slider.setMinimum(0)
        self.opacity_slider.setMaximum(10000) 
        self.opacity_slider.setMaximumWidth(150)
        self.opacity_slider.setMinimumWidth(150)
        
        horizontal_layout.addWidget(self.opacity_spin)
        horizontal_layout.addWidget(self.opacity_slider)
        form_layout.addRow(label, horizontal_layout)

        # Brush Shape
        label = QtWidgets.QLabel("Profile:")
        shape_layout = QtWidgets.QHBoxLayout()
        shape_layout.setSpacing(2)

        icon_size = 30
        button_size = 40

        self._square_icon_path = path.get_icon_path("adn_square_32px.png")
        self._square_pixmap = QtGui.QPixmap(self._square_icon_path)
        square_scaled = self._square_pixmap.scaledToHeight(icon_size, QtCore.Qt.SmoothTransformation)
        self._square_icon = QtGui.QIcon(square_scaled)
        self._solid_icon_path = path.get_icon_path("adn_solid_32px.png") 
        self._solid_pixmap = QtGui.QPixmap(self._solid_icon_path)
        solid_scaled = self._solid_pixmap.scaledToHeight(icon_size, QtCore.Qt.SmoothTransformation)
        self._solid_icon = QtGui.QIcon(solid_scaled)
        self._poly_icon_path = path.get_icon_path("adn_poly_32px.png")
        self._poly_pixmap = QtGui.QPixmap(self._poly_icon_path)
        poly_scaled = self._poly_pixmap.scaledToHeight(icon_size, QtCore.Qt.SmoothTransformation)
        self._poly_icon = QtGui.QIcon(poly_scaled)
        self._gauss_icon_path = path.get_icon_path("adn_gauss_32px.png")
        self._gauss_pixmap = QtGui.QPixmap(self._gauss_icon_path)
        gauss_scaled = self._gauss_pixmap.scaledToHeight(icon_size, QtCore.Qt.SmoothTransformation)
        self._gauss_icon = QtGui.QIcon(gauss_scaled)

        self.brush_gauss = QtWidgets.QPushButton("")
        self.brush_gauss.setIcon(self._gauss_icon)
        self.brush_gauss.setIconSize(QtCore.QSize(icon_size, icon_size))
        self.brush_gauss.setToolTip("Gauss brush")
        self.brush_gauss.setCheckable(True)
        self.brush_gauss.setStyleSheet(self.button_not_active)

        self.brush_poly = QtWidgets.QPushButton("")
        self.brush_poly.setIcon(self._poly_icon)
        self.brush_poly.setIconSize(QtCore.QSize(icon_size, icon_size))
        self.brush_poly.setToolTip("Soft brush")
        self.brush_poly.setCheckable(True)
        self.brush_poly.setStyleSheet(self.button_not_active)

        self.brush_solid = QtWidgets.QPushButton("")
        self.brush_solid.setIcon(self._solid_icon)
        self.brush_solid.setIconSize(QtCore.QSize(icon_size, icon_size))
        self.brush_solid.setToolTip("Solid brush")
        self.brush_solid.setCheckable(True)
        self.brush_solid.setStyleSheet(self.button_not_active)

        self.brush_square = QtWidgets.QPushButton("")
        self.brush_square.setIcon(self._square_icon)
        self.brush_square.setIconSize(QtCore.QSize(icon_size, icon_size))
        self.brush_square.setToolTip("Square brush")
        self.brush_square.setCheckable(True)
        self.brush_square.setStyleSheet(self.button_not_active)
        
        self.brush_square.setFixedSize(button_size, button_size)
        self.brush_solid.setFixedSize(button_size, button_size)
        self.brush_poly.setFixedSize(button_size, button_size)
        self.brush_gauss.setFixedSize(button_size, button_size) 
        shape_layout.addWidget(self.brush_gauss)
        shape_layout.addWidget(self.brush_poly)
        shape_layout.addWidget(self.brush_solid)
        shape_layout.addWidget(self.brush_square)
        
        form_layout.addRow(label, shape_layout)

        # Brush Style 
        stroke_group = QtWidgets.QGroupBox("Stroke")
        form_layout = QtWidgets.QFormLayout()
        stroke_group.setLayout(form_layout)
        vertical_layout.addWidget(stroke_group)

        # Screen projection
        self.screen_proj = QtWidgets.QCheckBox("Screen projection")
        form_layout.addRow("", self.screen_proj)
        self.screen_proj.setChecked(False)
        self.screen_proj.setTristate(False)

        # Reflection
        self.reflection = QtWidgets.QCheckBox("Reflection")
        form_layout.addRow("", self.reflection)
        self.reflection.setTristate(False)

        # Reflection about origin
        self.reflection_origin = QtWidgets.QCheckBox("Reflection about origin")
        form_layout.addRow("", self.reflection_origin)
        self.reflection_origin.setTristate(False)
        self.reflection_origin.setEnabled(False)

        # Reflection axis
        label = QtWidgets.QLabel("Reflection axis:")
        reflection_axis_layout = QtWidgets.QHBoxLayout()
        self.reflection_x = QtWidgets.QRadioButton("X")
        self.reflection_y = QtWidgets.QRadioButton("Y")
        self.reflection_z = QtWidgets.QRadioButton("Z")
        self.reflection_x.setEnabled(False)
        self.reflection_y.setEnabled(False)
        self.reflection_z.setEnabled(False)

        reflection_axis_layout.addWidget(self.reflection_x)
        reflection_axis_layout.addWidget(self.reflection_y)
        reflection_axis_layout.addWidget(self.reflection_z)
        
        form_layout.addRow(label, reflection_axis_layout)

        # Stamp spacing
        label = QtWidgets.QLabel("Stamp spacing:")
        horizontal_layout = QtWidgets.QHBoxLayout()
        self.spacing_spin = QtWidgets.QDoubleSpinBox()
        self.spacing_spin.setDecimals(4)
        self.spacing_spin.setMinimum(0.01)
        self.spacing_spin.setMaximum(10.0)
        self.spacing_spin.setButtonSymbols(QtWidgets.QAbstractSpinBox.NoButtons)
        self.spacing_spin.setMaximumWidth(65)
        self.spacing_spin.setMinimumWidth(65)
        self.spacing_slider = QtWidgets.QSlider()
        self.spacing_slider.setOrientation(QtCore.Qt.Horizontal)
        self.spacing_slider.setSingleStep(1)
        self.spacing_slider.setMinimum(1)
        self.spacing_slider.setMaximum(1000)
        self.spacing_slider.setMaximumWidth(155)
        self.spacing_slider.setMinimumWidth(155)
        
        horizontal_layout.addWidget(self.spacing_spin)
        horizontal_layout.addWidget(self.spacing_slider)
        form_layout.addRow(label, horizontal_layout)

        # Button Layout
        button_group = QtWidgets.QGroupBox("")
        form_layout = QtWidgets.QFormLayout()
        form_layout.setFormAlignment(QtCore.Qt.AlignHCenter)
        buttons_layout = QtWidgets.QHBoxLayout()
        button_group.setLayout(form_layout)
        vertical_layout.addWidget(button_group)

        # Flood Button
        self.flood_button = QtWidgets.QPushButton("Flood")
        self.flood_button.setMaximumWidth(160)
        self.flood_button.setMinimumWidth(160)
        
        buttons_layout.addWidget(self.flood_button)
        form_layout.addRow(buttons_layout)

        self._main_layout.addLayout(vertical_layout)
        self._main_layout.addStretch()

        # Menu bar
        menu_bar = self.menuBar()
        self._edit_menu = QtWidgets.QMenu("&Edit", self)
        self._reset_action = QtWidgets.QAction("&Reset tool", self, triggered=self._reset)   
        self._edit_menu.addAction(self._reset_action)
        menu_bar.insertMenu(self._help_menu.menuAction(), self._edit_menu)

    def _connect_signals(self):
        """Connect signals to all of the components of the UI.
        The shortcuts are connected too.
        """
        # Connect signals
        self.attr_combo.currentIndexChanged.connect(self._attr_changed)
        self.influences_list.itemSelectionChanged.connect(self._influence_changed)
        self.value_spin.valueChanged.connect(self._value_spin_changed)
        self.value_slider.valueChanged.connect(self._value_slider_changed)
        self.radius_spin.valueChanged.connect(self._radius_spin_changed)
        self.radius_slider.valueChanged.connect(self._radius_slider_changed)
        self.lower_radius_spin.valueChanged.connect(self._lower_radius_spin_changed)
        self.lower_radius_slider.valueChanged.connect(self._lower_radius_slider_changed)
        self.opacity_spin.valueChanged.connect(self._opacity_spin_changed)
        self.opacity_slider.valueChanged.connect(self._opacity_slider_changed)

        # Change the weight operation
        self.weight_absolute.clicked.connect(lambda: self._weight_mode_changed(self.dcc_tool.PaintToolMode.ABSOLUTE))
        self.weight_additive.clicked.connect(lambda: self._weight_mode_changed(self.dcc_tool.PaintToolMode.ADDITIVE))
        self.weight_scale.clicked.connect(lambda: self._weight_mode_changed(self.dcc_tool.PaintToolMode.SCALE))
        self.weight_smooth.clicked.connect(lambda: self._weight_mode_changed(self.dcc_tool.PaintToolMode.SMOOTH))

        # Change the brush style
        self.brush_square.clicked.connect(lambda: self._stamp_profile_changed(self.dcc_tool.PaintToolBrush.SQUARE))
        self.brush_solid.clicked.connect(lambda: self._stamp_profile_changed(self.dcc_tool.PaintToolBrush.SOLID))
        self.brush_poly.clicked.connect(lambda: self._stamp_profile_changed(self.dcc_tool.PaintToolBrush.POLY))
        self.brush_gauss.clicked.connect(lambda: self._stamp_profile_changed(self.dcc_tool.PaintToolBrush.GAUSS))

        # Stroke parameters
        self.screen_proj.stateChanged.connect(self._projection_changed)
        self.reflection.stateChanged.connect(self._reflection_changed)
        self.reflection_origin.stateChanged.connect(self._reflection_origin_changed)
        self.reflection_x.clicked.connect(lambda: self._reflection_axis_changed(self.dcc_tool.PaintToolReflectionAxis.X))
        self.reflection_y.clicked.connect(lambda: self._reflection_axis_changed(self.dcc_tool.PaintToolReflectionAxis.Y))
        self.reflection_z.clicked.connect(lambda: self._reflection_axis_changed(self.dcc_tool.PaintToolReflectionAxis.Z)) 

        self.flood_button.clicked.connect(self._flood_weights)
        self.refresh_ctx_button.clicked.connect(self._paint)
        self.pick_button.clicked.connect(self._pick_value)

        self.spacing_spin.valueChanged.connect(self._spacing_spin_changed)
        self.spacing_slider.valueChanged.connect(self._spacing_slider_changed)

        # Shortcuts
        self.flood_sc = QtWidgets.QShortcut(QtGui.QKeySequence("Alt+F"), self, 
                                            context=QtCore.Qt.ApplicationShortcut)
        self.flood_sc.activated.connect(self._flood_weights)
        self.color_feedback_sc = QtWidgets.QShortcut(QtGui.QKeySequence("Alt+C"), self, 
                                                     context=QtCore.Qt.ApplicationShortcut)
        self.color_feedback_sc.activated.connect(self._color_feedback_sc_changed)
        self.reflection_sc = QtWidgets.QShortcut(QtGui.QKeySequence("Alt+R"), self, 
                                                 context=QtCore.Qt.ApplicationShortcut)
        self.reflection_sc.activated.connect(self._reflection_sc_changed)

    def _reset(self):
        """Resets all fields to the default ones. Updates the context
        and commands. Usually called from the menu Edit->Reset.
        """
        self.value_spin.setValue(self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("intensity"))
        self._value_spin_changed()

        self._change_upper_radius()          
        
        self.lower_radius_spin.setValue(self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("lower_radius"))
        self._lower_radius_spin_changed()
 
        self.opacity_spin.setValue(self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("opacity"))
        self._opacity_spin_changed()

        self._change_weight_mode(self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("paint_mode"))
        self._weight_mode_changed(self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("paint_mode"))

        self._stamp_profile_changed(self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("brush_shape"))

        self.screen_proj.setChecked(self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("screen_proj"))
        self._projection_changed(self.screen_proj.checkState())

        self.reflection.setChecked(self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("reflection"))
        self._reflection_changed(self.reflection.checkState())

        self.reflection_origin.setChecked(self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("reflection_origin"))
        self._reflection_origin_changed(self.reflection_origin.checkState())

        self._change_reflection_axis(self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("reflection_axis"))
        self._reflection_axis_changed(self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("reflection_axis"))

        self.spacing_spin.setValue(self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("stamp_spacing"))
        self._spacing_spin_changed()

    def _change_upper_radius(self):
        """Change the upper radius to the default value. It changes both modes (with screen projection and 
        without screen projection). This method ignores the lower_radius being the minimum value.
        """
        # Upper radius current mode
        self.radius_spin.blockSignals(True)
        self.radius_slider.blockSignals(True)
        self.radius_spin.setValue(self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("upper_radius"))
        self.radius_slider.setValue(self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("upper_radius") * 1000)
        cmds.artUserPaintCtx(self.TOOL_PAINT, edit=True, 
                             radius=self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("upper_radius"))
        self.radius_spin.blockSignals(False)
        self.radius_slider.blockSignals(False)
        
        # Change the projection mode
        cmds.artUserPaintCtx(self.TOOL_PAINT, edit=True, projective=not self.screen_proj.isChecked())

        # Upper radius opposite of current mode
        self.radius_spin.blockSignals(True)
        self.radius_slider.blockSignals(True)
        self.radius_spin.setValue(self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("upper_radius"))
        self.radius_slider.setValue(self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("upper_radius") * 1000)
        cmds.artUserPaintCtx(self.TOOL_PAINT, edit=True, 
                             radius=self.dcc_tool.PaintToolSettings.DEFAULT_PRESET.get("upper_radius"))
        self.radius_spin.blockSignals(False)
        self.radius_slider.blockSignals(False)

    @staticmethod
    def _update_context_value(value):
        """Change the value/intensity of the paint tool. Called from spin, slider or shortcut.

        Args:
            value (float): New intensity to assign to the paint context. From 0.0 to 1.0.
        """
        cmds.AdnPaintDataCommand(edit=True, uiValue=value)

    def _update_context_radius(self, radius):
        """Change the upper radius of the paint tool. Called from spin, slider or shortcut.

        Args:
            radius (float): New upper radius to assign to the paint context.
        """
        if cmds.artUserPaintCtx(self.TOOL_PAINT, exists=True):
            cmds.artUserPaintCtx(self.TOOL_PAINT, edit=True, radius=radius)

    def _update_context_lower_radius(self, radius):
        """Change the lower radius of the paint tool. Called from spin, slider or shortcut.

        Args:
            radius (float): New lower radius to assign to the paint context.
        """
        if cmds.artUserPaintCtx(self.TOOL_PAINT, exists=True):
            cmds.artUserPaintCtx(self.TOOL_PAINT, edit=True, lowerradius=radius)

    def _update_context_opacity(self, opacity):
        """Change the opacity of the paint tool. Called from spin or slider.

        Args:
            opacity (float): New opacity to assign to the paint context.
                From 0.0 to 1.0.
        """
        cmds.AdnPaintDataCommand(edit=True, uiOpacity=opacity)
        if cmds.artUserPaintCtx(self.TOOL_PAINT, exists=True):
            cmds.artUserPaintCtx(self.TOOL_PAINT, edit=True, opacity=opacity)

    def _attr_changed(self):
        """Change paint attribute. Updates the weight being displayed using the 
        AdnPaintDataCommand. It also updates the influences list in the UI.
        """
        if not self.deformer or not cmds.objExists(self.deformer):
            cmds.setToolTo("selectSuperContext")
            return

        # Make sure to set the data correctly to the deformer before querying below.
        attribute = self.attr_combo.currentText()
        cmds.AdnPaintDataCommand(edit=True, deformer=self.deformer, 
                                 weight=attribute)

        # Only update the influences names if the attributes is
        # set to multi influence.
        if attribute in self.multi_infl_attr:
            self._update_influences_names()
        else:
            del self.ui_influences_names[:]
            del self.ui_influences_long_names[:]
        
        # Update the influences list in the UI (hide/show/update)
        self._update_influences_list()

        # Only update the selected influence if the attribute is set to
        # multi influence.
        if attribute in self.multi_infl_attr:
            # NOTE: Default to the first influence in case there are several
            # multi-influence attributes in the deformer
            self._default_influence()
            self._select_current_influence()

        # Disable or not the paint tool paint context if we have a valid paintable
        # attribute selected
        if (attribute not in self.multi_infl_attr or
                (self.ui_influences_names and self.ui_influences_long_names)):
            cmds.setToolTo(self.TOOL_PAINT)
        else:
            cmds.setToolTo("selectSuperContext")

    def _value_spin_changed(self):
        """Change the spin value. Updates the value slider accordingly and calls 
        the value update context.
        """
        paint_value = self.value_spin.value()
        self._update_context_value(paint_value) 
        self.value_slider.blockSignals(True)
        self.value_slider.setValue(paint_value * 10000)
        self.value_slider.blockSignals(False)

    def _value_slider_changed(self):
        """Change the value slider. Updates the value spin accordingly and calls 
        the value update context.
        """
        paint_value = self.value_slider.value() * 0.0001
        self._update_context_value(paint_value) 
        self.value_spin.blockSignals(True)
        self.value_spin.setValue(paint_value)
        self.value_spin.blockSignals(False)

    def _radius_spin_changed(self):
        """Change the upper radius spin. Updates the upper radius slider accordingly 
        and calls the upper radius update context. Might update the lower radius to
        be greater or equal.
        """
        if self.radius_spin.value() < self.lower_radius_spin.value():
            self.radius_spin.blockSignals(True)
            self.radius_spin.setValue(self.lower_radius_spin.value())
            self.radius_spin.blockSignals(False)
        paint_radius = self.radius_spin.value()
        self._update_context_radius(paint_radius)
        self.radius_slider.blockSignals(True)
        self.radius_slider.setValue(paint_radius * 1000)
        self.radius_slider.blockSignals(False)

    def _radius_slider_changed(self):
        """Change the radius slider. Updates the upper radius spin accordingly 
        and calls the upper radius update context. Might update the lower radius to
        be greater or equal.
        """
        if self.radius_slider.value() < self.lower_radius_slider.value():
            self.radius_slider.blockSignals(True)
            self.radius_slider.setValue(self.lower_radius_slider.value())
            self.radius_slider.blockSignals(False)            
        paint_radius = self.radius_slider.value() * 0.001
        self._update_context_radius(paint_radius)
        self.radius_spin.blockSignals(True)
        self.radius_spin.setValue(paint_radius)
        self.radius_spin.blockSignals(False)

    def _lower_radius_spin_changed(self):
        """Change the lower radius spin. Updates the lower radius slider accordingly 
        and calls the lower radius update context. Might update the upper radius to
        be greater or equal.
        """
        if self.lower_radius_spin.value() > self.radius_spin.value():
            self.lower_radius_spin.blockSignals(True)
            self.lower_radius_spin.setValue(self.radius_spin.value())
            self.lower_radius_spin.blockSignals(False)
        paint_lower_radius = self.lower_radius_spin.value()
        self._update_context_lower_radius(paint_lower_radius)
        self.lower_radius_slider.blockSignals(True)
        self.lower_radius_slider.setValue(paint_lower_radius * 1000)
        self.lower_radius_slider.blockSignals(False)

    def _lower_radius_slider_changed(self):
        """Change the lower radius slider. Updates the lower radius spin accordingly 
        and calls the lower radius update context. Might update the upper radius to
        be less or equal.
        """
        if self.lower_radius_slider.value() > self.radius_slider.value():
            self.lower_radius_slider.blockSignals(True)
            self.lower_radius_slider.setValue(self.radius_slider.value())
            self.lower_radius_slider.blockSignals(False)  
        paint_lower_radius = self.lower_radius_slider.value() * 0.001
        self._update_context_lower_radius(paint_lower_radius)
        self.lower_radius_spin.blockSignals(True)
        self.lower_radius_spin.setValue(paint_lower_radius)
        self.lower_radius_spin.blockSignals(False)

    def _opacity_spin_changed(self):
        """Change the spin opacity. Updates the opacity slider accordingly 
        and calls the opacity update context.
        """
        paint_opacity = self.opacity_spin.value()
        self._update_context_opacity(paint_opacity)
        self.opacity_slider.blockSignals(True)
        self.opacity_slider.setValue(paint_opacity * 10000)
        self.opacity_slider.blockSignals(False)

    def _opacity_slider_changed(self):
        """Change the opacity slider. Updates the opacity spin accordingly 
        and calls the opacity update context.
        """
        paint_opacity = self.opacity_slider.value() * 0.0001
        self._update_context_opacity(paint_opacity)
        self.opacity_spin.blockSignals(True)
        self.opacity_spin.setValue(paint_opacity)
        self.opacity_spin.blockSignals(False)

    def _change_stamp_profile(self, value):
        """Change stamp profile. Highlights the button based on the sent stamp.

        Args:
            value (str): Brush selected.
        """
        # Uncheck and check
        self.brush_gauss.setChecked(False)
        self.brush_gauss.setStyleSheet(self.button_not_active)
        self.brush_poly.setChecked(False)
        self.brush_poly.setStyleSheet(self.button_not_active)
        self.brush_solid.setChecked(False)
        self.brush_solid.setStyleSheet(self.button_not_active)
        self.brush_square.setChecked(False)
        self.brush_square.setStyleSheet(self.button_not_active)

        if value == self.dcc_tool.PaintToolBrush.GAUSS:
            self.brush_gauss.setChecked(True)
            self.brush_gauss.setStyleSheet(self.button_active)
        elif value == self.dcc_tool.PaintToolBrush.POLY:
            self.brush_poly.setChecked(True)
            self.brush_poly.setStyleSheet(self.button_active)
        elif value == self.dcc_tool.PaintToolBrush.SOLID:
            self.brush_solid.setChecked(True)
            self.brush_solid.setStyleSheet(self.button_active)
        else:
            self.brush_square.setChecked(True)
            self.brush_square.setStyleSheet(self.button_active)
            
    def _stamp_profile_changed(self, value):
        """Stamp profile changed. Highlights the current selected stamp. Updates the
        paint context with the current stamp profile.

        Args:
            value (str): Brush selected.
        """
        self._change_stamp_profile(value)
        if cmds.artUserPaintCtx(self.TOOL_PAINT, exists=True):
            cmds.artUserPaintCtx(self.TOOL_PAINT, edit=True, stampProfile=value)
    
    def _change_weight_mode(self, value):
        """Change weight profile. Checks in the UI the weight mode sent.

        Args:
            value (str): Paint operation mode selected.
        """
        if value == self.dcc_tool.PaintToolMode.SMOOTH:
            self.weight_smooth.setChecked(True)
        elif value == self.dcc_tool.PaintToolMode.ADDITIVE:
            self.weight_additive.setChecked(True)
        elif value == self.dcc_tool.PaintToolMode.SCALE:
            self.weight_scale.setChecked(True)
        else:
            self.weight_absolute.setChecked(True)

    def _weight_mode_changed(self, value):
        """Weight profile changed. Updates the paint operation with the current selected one.

        Args:
            value (str): Paint operation mode selected.
        """
        if value not in self.dcc_tool.PaintToolMode.paint_mode:
            print("{0} Unrecognized paint mode. Paint mode was not updated.".format(UiConstants.LOG_PREFIX))
            return

        enable_flood_button = self.attr_combo.currentText() != "Fibers"
        if self.weight_smooth.isChecked():
            self.flood_button.setEnabled(True)
        else:
            self.flood_button.setEnabled(enable_flood_button)

        cmds.AdnPaintDataCommand(edit=True, paintMode=self.dcc_tool.PaintToolMode.paint_mode[value])
        if cmds.artUserPaintCtx(self.TOOL_PAINT, exists=True):
            cmds.artUserPaintCtx(self.TOOL_PAINT, edit=True, selectedattroper=value)

    def _projection_changed(self, value):
        """Reflection mode changed. Changes the projection (screen projection or not) of the 
        paint context.

        Args:
            value (`QtCore.Qt.CheckState`): Check state of the checkbox related to the projection.
        """        
        if cmds.artUserPaintCtx(self.TOOL_PAINT, exists=True):
            cmds.artUserPaintCtx(self.TOOL_PAINT, edit=True, projective=value == QtCore.Qt.Checked)

            # Update radius
            self.radius_spin.blockSignals(True)
            self.radius_slider.blockSignals(True)
            radius = cmds.artUserPaintCtx(self.TOOL_PAINT, query=True, radius=True)
            self.radius_spin.setValue(radius)
            self.radius_slider.setValue(radius * 1000)
            self.radius_spin.blockSignals(False)
            self.radius_slider.blockSignals(False)

    def _reflection_changed(self, value, edit_context=True):
        """Reflection mode changed. Enables or disables reflection. At the same time enables or
        disables UI elements.

        Args:
            value (`QtCore.Qt.CheckState` or bool): Check state of the checkbox related to the reflection
                mode.
            edit_context (bool, optional): Flag to edit or not the reflection attribute at the paint
                context. Defaults to True.
        """
        checked = False
        if type(value) == bool:
            checked = value
        else:
            checked = value == QtCore.Qt.Checked

        if cmds.artUserPaintCtx(self.TOOL_PAINT, exists=True) and edit_context:
            cmds.artUserPaintCtx(self.TOOL_PAINT, edit=True, reflection=checked)

        self.reflection_origin.setEnabled(checked)
        self.reflection_x.setEnabled(checked)
        self.reflection_y.setEnabled(checked)
        self.reflection_z.setEnabled(checked)

    def _reflection_sc_changed(self):
        """Reflection shortcut changed. Shortcut that changes the current reflection mode (of the 
        paint context) to the opposite. Enable -> Disable, Disable -> Enable.
        """
        # Skip updating reflection widgets status if not in the right context
        if cmds.currentCtx() != self.TOOL_PAINT:
            return

        refl_opposite = QtCore.Qt.Checked
        if cmds.artUserPaintCtx(self.TOOL_PAINT, query=True, reflection=True):
            refl_opposite = QtCore.Qt.Unchecked
            self.reflection.setChecked(False)
        else:
            self.reflection.setChecked(True)

        self._reflection_changed(value=refl_opposite)
    
    def _reflection_origin_changed(self, value):
        """Reflection origin changed. Changes if the reflection is based on the origin.

        Args:
            value (`QtCore.Qt.CheckState`): Check state of the checkbox related to the reflection 
        """        
        if cmds.artUserPaintCtx(self.TOOL_PAINT, exists=True):
            cmds.artUserPaintCtx(self.TOOL_PAINT, edit=True, reflectionaboutorigin=value == QtCore.Qt.Checked)
    
    def _change_reflection_axis(self, value):
        """Change reflection axis. Updates the UI based on the reflection axis sent.

        Args:
            value (str): Reflection axis which the paint stroke will be reflected.
        """
        if value == self.dcc_tool.PaintToolReflectionAxis.X:
            self.reflection_x.setChecked(True)
        elif value == self.dcc_tool.PaintToolReflectionAxis.Y:
            self.reflection_y.setChecked(True)
        else:
            self.reflection_z.setChecked(True)

    def _reflection_axis_changed(self, value):
        """Reflection axis changed. Changes the axis of the reflection based on the current selection.

        Args:
            value (str): Reflection axis which the paint stroke will be reflected.
        """
        if cmds.artUserPaintCtx(self.TOOL_PAINT, exists=True):
            cmds.artUserPaintCtx(self.TOOL_PAINT, edit=True, reflectionaxis=value)
    
    def _spacing_spin_changed(self):
        """Change the spin spacing. Changes how often the stamps of the stroke are being
        computed. Updates stamp slider accordingly.
        """
        paint_spacing = self.spacing_spin.value()
        self.spacing_slider.blockSignals(True)
        self.spacing_slider.setValue(paint_spacing * 100)
        self.spacing_slider.blockSignals(False)

        if cmds.artUserPaintCtx(self.TOOL_PAINT, exists=True):
            cmds.artUserPaintCtx(self.TOOL_PAINT, edit=True, stampSpacing=paint_spacing)

    def _spacing_slider_changed(self):
        """Change the spacing slider. Changes how often the stamps of the stroke are being
        computed. Updates stamp spin accordingly.
        """
        paint_spacing = self.spacing_slider.value() * 0.01
        self.spacing_spin.blockSignals(True)
        self.spacing_spin.setValue(paint_spacing)
        self.spacing_spin.blockSignals(False)

        if cmds.artUserPaintCtx(self.TOOL_PAINT, exists=True):
            cmds.artUserPaintCtx(self.TOOL_PAINT, edit=True, stampSpacing=paint_spacing)

    def _paint(self):
        """Setup the paint tool context. If the paint context does not exist, creates it.
        Creates the custom mel-python commands and edits the paint context. The context by
        default will be reset and the maya context is changed to the paint one.
        """
        result, deformer, node_type, paint_attr, multi_infl_attr, mesh_node = \
            self.dcc_tool.setup_paint_tool(self)
        if not result:
            return

        new_index = self.attr_combo.currentIndex() if node_type == self.node_type else 0

        self._paint_ctx_cleanup_procedure()
        self._refresh_cache(deformer, node_type, paint_attr,
                            multi_infl_attr, mesh_node)

        # Select the current paintable mesh so the paint context only allows to paint on the active mesh.
        cmds.select(self.mesh)

        self.attr_combo.blockSignals(True)
        self.attr_combo.setCurrentIndex(new_index)
        self.attr_combo.blockSignals(False)
        self._attr_changed()
        paint_mode = cmds.artUserPaintCtx(self.TOOL_PAINT, query=True, selectedattroper=True)
        self._change_weight_mode(paint_mode)

        if (self.attr_combo.currentText() not in self.multi_infl_attr or
                self.ui_influences_names):
            self._paint_ctx_setup_procedure()
            # Select multi-influence object if we are in paint context.
            selected_indices = [item.row() for item in self.influences_list.selectedIndexes()]
            if self.attr_combo.currentText() in self.multi_infl_attr and selected_indices:
                selected_item = self.ui_influences_names[selected_indices[0]]
                self.dcc_tool.select_multi_influence_obj(selected_item)
    
    @undo_chunk
    def _flood_weights(self):
        """Flood the whole geometry with the current selected value. Based also on the paint operation,
        opacity and brush shape.
        """
        if cmds.currentCtx() != self.TOOL_PAINT or not self.flood_button.isEnabled():
            return
        try:
            cmds.AdnPaintDataCommand(edit=True, deformer=self.deformer)
            cmds.AdnPaintFloodCommand()
            cmds.AdnPaintFinalizeCommand(flood=True)
        except RuntimeError as err:
            print(err)

    def _pick_value_press_command(self):
        """Gets the paint tool value based on the selection. Method called when we click meanwhile
        self.PICKER_PAINT_CTX is active.
        """
        if cmds.currentCtx() != self.PICKER_PAINT_CTX:
            return

        # Get closest vertex
        closest_vertex = self.dcc_tool.get_closest_index_dragger_context(self.PICKER_PAINT_CTX,
                                                                         self.deformer,
                                                                         self.mesh_node)
        if closest_vertex == -1:
            self.pick_error = True
            return

        try:
            # Get the weight and update the art context
            value = cmds.AdnPaintGetWeightCommand(vertex=closest_vertex)
            self.value_spin.setValue(value)
            self._value_spin_changed()
        except:
            self.pick_error = True
        return

    def _pick_value_release_command(self):
        """Method called when, during the self.PICKER_PAINT_CTX, mouse releases. Paint context has to be
        restored here.
        """
        if self.pick_error:
            msg_box(main_window(), "error",
                    "Could not pick a value from the current context. Wrong selection or vertex not found in weight map.")

        cmds.select(self.mesh)
        cmds.setToolTo(self.TOOL_PAINT)
        return

    def _pick_value(self):
        """Process to get the value of the selected vertex based on the ray thrown by the selection.
        """
        if cmds.currentCtx() != self.TOOL_PAINT:
            return

        # Define draggerContext
        if cmds.draggerContext(self.PICKER_PAINT_CTX, exists=True):
            # Dragger context has to be created everytime since references to UI might change
            cmds.deleteUI(self.PICKER_PAINT_CTX)

        cmds.draggerContext(self.PICKER_PAINT_CTX, pressCommand=self._pick_value_press_command,
                            releaseCommand=self._pick_value_release_command, cursor='crossHair')
        self.pick_error = False

        # When context changes weights are hidden and material is restored
        cmds.setToolTo(self.PICKER_PAINT_CTX)
        self._show_paint_weights()

    def _refresh_cache(self, deformer, node_type, paint_attr, multi_infl_attr,
                       mesh_node):
        """Update cached data with the input values to ensure that posterior
        command queries and interaction with the paint context are consistent.

        Args:
            deformer (str): Name of the deformer node.
            node_type (str): Node type name.
            paint_attr (list): List of paintable attributes.
            multi_infl_attr (list): List of multi influence paintable attributes.
            mesh_node (str): Mesh node of the selection.
        """
        self.deformer = deformer
        self.node_type = node_type
        self.paintable_attrib_list = paint_attr
        self.multi_infl_attr = multi_infl_attr
        self.attr_combo.blockSignals(True)
        self.attr_combo.clear()
        self.attr_combo.addItems(self.paintable_attrib_list)
        self.attr_combo.blockSignals(False)
        self.mesh_node = mesh_node
        self.mesh = ""
        mesh_transform = cmds.listRelatives(mesh_node, parent=True,
                                            fullPath=True) or []
        if mesh_transform:
            self.mesh = mesh_transform[0]

    @undo_chunk
    def _paint_ctx_setup_procedure(self, toolContext=None):
        """Setup the paint context. Gathers nodes, the paintable attributes, and enables
        the vertex coloring for the mesh.

        Args:
            toolContext (str, optional): Name of the tool paint context.
                Should be `self.TOOL_PAINT`.
        """
        result, deformer, node_type, paint_attr, multi_infl_attr, mesh_node = \
            self.dcc_tool.setup_paint_tool(self)
        if not result:
            return

        if deformer != self.deformer:
            self._refresh_cache(deformer, node_type, paint_attr,
                                multi_infl_attr, mesh_node)

        # Change "Last selected tool" double click behavior
        from adn.ui.maya.launchers import show_paint_tool
        cmds.toolButton(self.TOOL_BUTTON, edit=True, doubleClickCommand=show_paint_tool)

        if cmds.artUserPaintCtx(self.TOOL_PAINT, exists=True):
            cmds.artUserPaintCtx(self.TOOL_PAINT, edit=True, whichTool="userPaint")

        current_selection = cmds.ls(selection=True, long=True)
        selection_check = current_selection and (self.deformer in current_selection or self.mesh in current_selection)
        attribute_check = (self.attr_combo.currentText() not in self.multi_infl_attr or
                           self.ui_influences_names and self.ui_influences_long_names)
        if selection_check and attribute_check:
            """
            A and B, where:
            A: current selection is not empty and selects the last deformer or mesh painted.
            B: attribute that is being painted is allowed to be painted.
            """
            self._show_paint_weights()
            cmds.select(self.mesh)

            if self.attr_combo.currentText() == "Fibers":
                # Display fibers while combing.
                self._debug_flag, self._debug_feature = self.dcc_tool.debug_fibers_on_painting(
                    self.deformer)
                self._toggle_operations_during_combing(False)
            else:
                # Painting maps. Restore previous debug settings.
                self.dcc_tool.restore_debug_attributes(self.deformer,
                                                       self._debug_flag,
                                                       self._debug_feature)
                self._debug_flag = None
                self._debug_feature = -1
                self._toggle_operations_during_combing(True)

        elif cmds.artUserPaintCtx(self.TOOL_PAINT, exists=True):
            # Wrong selection. Change to an empty tool that will display visual feedback to the user.
            cmds.artUserPaintCtx(self.TOOL_PAINT, edit=True, whichTool=self.PAINT_TOOL_DISABLED)

        # Changing reflection attributes outside of paint context might introduce undefined
        # behaviours. Widgets are enabled when entering context.
        self.reflection.setEnabled(True)
        if cmds.artUserPaintCtx(self.TOOL_PAINT, exists=True):
            checked = cmds.artUserPaintCtx(self.TOOL_PAINT, query=True, reflection=True)
            self._reflection_changed(checked, edit_context=False)

        # Make sure to set the data correctly to the deformer before querying below.
        attribute = self.attr_combo.currentText()
        cmds.AdnPaintDataCommand(edit=True, deformer=self.deformer,
                                 weight=attribute)

    @undo_chunk
    def _paint_ctx_cleanup_procedure(self, toolContext=None):
        """Cleanup the paint context. Disables the vertex coloring and resets the deform and mesh 
        value.

        Args:
            toolContext (str, optional): Name of the tool paint context. Should be `self.TOOL_PAINT`.
        """
        # Restore previous debug settings.
        self.dcc_tool.restore_debug_attributes(self.deformer,
                                               self._debug_flag,
                                               self._debug_feature)
        self._debug_flag = None
        self._debug_feature = -1
        # Restore "Last selected tool" double click behavior to open again the Settings Tool Window from Maya
        mel.eval("toolButton -e -dcc \"toolPropertyWindow\" \"{0}\"".format(self.TOOL_BUTTON))
        self._hide_paint_weights()

        # Changing reflection attributes outside of paint context might introduce undefined
        # behaviours. Widgets are disabled when exiting context.
        self.reflection.setEnabled(False)
        self._reflection_changed(False, edit_context=False)

        # Check that the current selection contains the currently painted mesh.
        current_selection = cmds.ls(selection=True, long=True)
        _, _, _, mesh_node, _= self.dcc_tool.collect_paint_tool_nodes(current_selection)
        if cmds.objExists(self.mesh) and self.mesh_node == mesh_node:
            # Selection is reset when leaving context, multi-influence objects might be selected.
            cmds.select(self.mesh)

    def _show_paint_weights(self):
        """Show painted weights. Called by the paint context or by the shortcut.
        """
        if not self.mesh_node or self.colors_active:
            return
        self._shading_group_uuid, self._poly_option = self.dcc_tool.display_paint(self.mesh_node, True,
                                                                                  self._shading_group_uuid,
                                                                                  self._poly_option)
        self.colors_active = True
    
    def _hide_paint_weights(self):
        """Hide painted weights. Called by the paint context or by the shortcut.
        """
        if not self.mesh_node or not self.colors_active:
            return
        self.dcc_tool.display_paint(self.mesh_node, False, self._shading_group_uuid, self._poly_option)
        self._shading_group_uuid = ""
        self._poly_option = "none"
        self.colors_active = False

    def _color_feedback_sc_changed(self):
        """Turn on/off the colors using the shortcut based on the current state.
        """
        if self.colors_active:
            self._hide_paint_weights()
        else:
            self._show_paint_weights()

    def _update_ui_based_on_ctx(self):
        """Updates the UI based on the paint context values.
        """
        if not cmds.artUserPaintCtx(self.TOOL_PAINT, exists=True):
            return
        
        # Paint parameteres
        paint_value = cmds.AdnPaintDataCommand(query=True, uiValue=True)
        self.value_spin.setValue(paint_value)

        # Paint operations
        paint_mode = cmds.artUserPaintCtx(self.TOOL_PAINT, query=True, selectedattroper=True)
        self._change_weight_mode(paint_mode)
        
        upper_radius = cmds.artUserPaintCtx(self.TOOL_PAINT, query=True, radius=True)
        self.radius_spin.setValue(upper_radius)

        lower_radius = cmds.artUserPaintCtx(self.TOOL_PAINT, query=True, lowerradius=True)
        self.lower_radius_spin.setValue(lower_radius)

        opacity = cmds.artUserPaintCtx(self.TOOL_PAINT, query=True, opacity=True)
        self.opacity_spin.setValue(opacity)

        stamp_profile = cmds.artUserPaintCtx(self.TOOL_PAINT, query=True, stampProfile=True)
        self._change_stamp_profile(stamp_profile)

        # Stroke
        screen_proj = cmds.artUserPaintCtx(self.TOOL_PAINT, query=True, projective=True)
        self.screen_proj.setChecked(screen_proj)

        # Update the status of reflection widgets only if current context is self tool context to
        # avoid undefined behaviour
        if cmds.currentCtx() == self.TOOL_PAINT:
            reflection = cmds.artUserPaintCtx(self.TOOL_PAINT, query=True, reflection=True)
            self.reflection.setChecked(reflection)
            self._reflection_changed(reflection)

            reflection_origin = cmds.artUserPaintCtx(self.TOOL_PAINT, query=True, reflectionaboutorigin=True)
            self.reflection_origin.setChecked(reflection_origin)

            refl_axis = cmds.artUserPaintCtx(self.TOOL_PAINT, query=True, reflectionaxis=True)
            self._change_reflection_axis(refl_axis)

        stamp_spacing = cmds.artUserPaintCtx(self.TOOL_PAINT, query=True, stampSpacing=True)
        self.spacing_spin.setValue(stamp_spacing)

    def _update_influences_names(self):
        """Update the influences names for multi influece paintable attributes.
        """
        if not self.deformer or not cmds.objExists(self.deformer):
            del self.ui_influences_names[:]
            del self.ui_influences_long_names[:]
            cmds.setToolTo("selectSuperContext")
            return
        # Get the influences from the deformer. 
        # Eg: [AdnMuscle1.attachmentConstraintsList[0].attachmentMatrix, ...]
        self.deformer_influences = cmds.AdnPaintDataCommand(self.deformer, query=True,
                                                            influences=True) or []

        # Handle multiple entries for one compound attribute to expose them to the UI
        compound_attribute_entry = dict()
        for influence in self.deformer_influences:
            # AdnMuscle1.attachmentConstraintsList[0].attachmentMatrix...
            compound_attribute = influence.split(".")
            # Skip invalid compound attribute entries
            if len(compound_attribute) < 3:
                continue
            compound_attribute = compound_attribute[1]
            if compound_attribute not in compound_attribute_entry.keys():
                compound_attribute_entry[compound_attribute] = list()
            # Accumulate clashes of compound attribute entries
            compound_attribute_entry[compound_attribute].append(influence)

        # Find the long name of the influences.
        del self.ui_influences_names[:]
        del self.ui_influences_long_names[:]
        # Iterate over the compound attribute entries clashes to form the pairs if needed
        for key, value in compound_attribute_entry.items():
            long_name_list = []
            nice_name_list = []
            for plug in value:
                connection = cmds.listConnections(plug)
                if not connection:
                    continue
                long_name_query = cmds.ls(connection[0], long=True)
                nice_name_query = cmds.ls(long_name_query, shortNames=True)
                long_name_list.append(long_name_query[0] if long_name_query else "N/A")
                nice_name_list.append(nice_name_query[0] if nice_name_query else "N/A")
            self.ui_influences_names.append(" - ".join(nice_name_list) if nice_name_list else "N/A")
            self.ui_influences_long_names.append(" - ".join(long_name_list) if long_name_list else "N/A")

    def _update_influences_list(self):
        """Update the influences list (UI) for multi influece paintable attributes. 
        """
        if not self.deformer or not cmds.objExists(self.deformer):
            self.influences_label.hide()
            self.influences_list.hide()
            cmds.setToolTo("selectSuperContext")
            return
        # Show the influences list with refreshed data when a multi influence
        # attribute has been selected. If not default the current influence to 0
        # and hide the influence list in the UI.
        if self.attr_combo.currentText() in self.multi_infl_attr:
            self.influences_list.clear()
            current_influence = cmds.AdnPaintDataCommand(self.deformer, query=True, 
                                                         currentInfluence=True)
            if not self.ui_influences_names or not self.ui_influences_long_names:
                self.influences_label.hide()
                self.influences_list.hide()
                # Set the current influence to -1 as no attachments have been provided.
                if current_influence != -1:
                    cmds.AdnPaintDataCommand(edit=True, deformer=self.deformer, 
                                             currentInfluence=-1)
            else:
                self.influences_list.addItems(self.ui_influences_names)
                # Add tooltips with long names.
                for idx in range(self.influences_list.count()):
                    self.influences_list.item(idx).setToolTip(self.ui_influences_long_names[idx])
                self.influences_label.show()
                self.influences_list.show()
                # Default to multi-influence item 0 when switching between attributes.
                if current_influence < 0:
                    cmds.AdnPaintDataCommand(edit=True, deformer=self.deformer,
                                             currentInfluence=0)
        else:
            self.influences_label.hide()
            self.influences_list.hide()
            # NOTE: Avoid setting values to the deformer if we are entering the UI.
            # The UI is set to the current influence in the deformer on enter.
            # Because the QListWidget has a connect behaviour set it will invoke this
            # method too which would update the painted values array during a stroke
            # introducing an incorrect painting to the system.
            if self.entering_ui:
                return
            cmds.AdnPaintDataCommand(edit=True, deformer=self.deformer, 
                                     currentInfluence=0)

    def _influence_changed(self):
        """Update the current influence in the deformer when a different
        influence has been selected. 
        """
        if not self.deformer or not cmds.objExists(self.deformer):
            self.influences_label.hide()
            self.influences_list.hide()
            cmds.setToolTo("selectSuperContext")
            return
        # NOTE: Avoid setting values to the deformer if we are entering the UI.
        # The UI is set to the current influence in the deformer on enter.
        # Because the QListWidget has a connect behaviour set it will invoke this
        # method too which would update the painted values array during a stroke
        # introducing an incorrect painting to the system.
        if self.entering_ui:
            return
        selected_items = self.influences_list.selectedIndexes()
        selected_indices = [item.row() for item in selected_items]

        if not selected_indices:
            return

        # Set the first selected influence.
        cmds.AdnPaintDataCommand(edit=True, deformer=self.deformer, 
                                 currentInfluence=selected_indices[0])

        # Select multi-influence object
        selected_item = self.ui_influences_names[selected_indices[0]]
        self.dcc_tool.select_multi_influence_obj(selected_item)

    def _default_influence(self):
        """Default the influence to be the one with index 0. 
        """
        if not self.deformer or not cmds.objExists(self.deformer):
            cmds.setToolTo("selectSuperContext")
            return
        if self.influences_list.count() >= 1:
            self.influences_list.item(0).setSelected(True)
        cmds.AdnPaintDataCommand(edit=True, deformer=self.deformer, 
                                 currentInfluence=0)
    
    def _select_current_influence(self):
        """Set the current influence to be the one queried
        from the deformer. 
        """
        if not self.deformer or not cmds.objExists(self.deformer):
            cmds.setToolTo("selectSuperContext")
            return
        current_influence = cmds.AdnPaintDataCommand(self.deformer, query=True, 
                                                     currentInfluence=True)
        for i in range(0, self.influences_list.count()):
            if i == current_influence:
                self.influences_list.item(i).setSelected(True)
            else:
                self.influences_list.item(i).setSelected(False)

        # Select multi-influence object if we are in paint context.
        selected_indices = [item.row() for item in self.influences_list.selectedIndexes()]
        if cmds.currentCtx() == self.TOOL_PAINT and selected_indices:
            selected_item = self.ui_influences_names[selected_indices[0]]
            self.dcc_tool.select_multi_influence_obj(selected_item)

    def _toggle_operations_during_combing(self, enable):
        """Changes the availability of paint widgets depending on the flag sent.
        The widgets are disabled as they are not necessary during the combing.

        Args:
            enable (bool): flag that defines if widgets should be enabled or not.
                It is true if not combing fibers.
        """
        self.value_slider.setEnabled(enable)
        self.value_spin.setEnabled(enable)
        self.pick_button.setEnabled(enable)
        self.opacity_slider.setEnabled(enable)
        self.opacity_spin.setEnabled(enable)
        self.brush_square.setEnabled(enable)
        self.brush_solid.setEnabled(enable)
        self.brush_poly.setEnabled(enable)
        self.brush_gauss.setEnabled(enable)
        self.weight_additive.setEnabled(enable)
        self.weight_scale.setEnabled(enable)

        # If combing fibers, additive and scale modes are not supported
        # Defaults to Replace
        if not enable and (self.weight_additive.isChecked() or self.weight_scale.isChecked()):
            self._change_weight_mode(self.dcc_tool.PaintToolMode.ABSOLUTE)
            self._weight_mode_changed(self.dcc_tool.PaintToolMode.ABSOLUTE)

        if self.weight_smooth.isChecked():
            # Smooth flood supported in fiber combing and attribute paint.
            self.flood_button.setEnabled(True)
        else:
            # Other paint operations supported in attribute paint.
            # But not on fiber combing.
            self.flood_button.setEnabled(enable)

    @undo_chunk
    def closeEvent(self, event):
        """Change the maya context when closing the tool.

        Args:
            event (`QCloseEvent`): Event that is emit every time the user press 'X' on the
            title bar menu.
        """
        self._paint_ctx_cleanup_procedure()
        cmds.setToolTo("selectSuperContext")
        cmds.AdnPaintDataCommand(edit=True, clear=True)
        self.dcc_tool.remove_all_weights_display_nodes()
        event.accept()

    def enterEvent(self, event):
        """When mouse enters the window app calls self._update_ui_based_on_ctx() 

        Args:
            event (`QEnterEvent`): Event that happens every time the mouse enters a
            window/widget.
        """
        self.entering_ui = True
        attribute = self.attr_combo.currentText()

        if (attribute not in self.multi_infl_attr
            or (self.ui_influences_names and self.ui_influences_long_names)):
            self._update_ui_based_on_ctx()

        # Only update the influences names if the attributes is
        # set to multi influence.
        if attribute in self.multi_infl_attr:
            self._update_influences_names()

        self._update_influences_list()

        # Set the selected influence from the deformer to the UI.
        if attribute in self.multi_infl_attr:
            self._select_current_influence()
        self.entering_ui = False
