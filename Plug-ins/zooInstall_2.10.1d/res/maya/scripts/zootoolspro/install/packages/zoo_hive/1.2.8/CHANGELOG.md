=========
ChangeLog
=========


1.2.8 (2025-06-27)
------------------

Bug
~~~

- (Godnode) Fix godNode failing to build in py2 environment.
- (Spaceswitch) Fix space switch failing when a driver expression path isn't invalid anymore.

Change
~~~~~~

- (Ikfk) Replaced maya constraints with matrix constraint.
- (Jaw) Replaced maya constraints with matrix constraint.
- (Reversefoot) Replaced lookdevkit float condition nodes with maya default condition node.


1.2.7 (2025-06-24)
------------------

Bug
~~~

- (Eyes) Fix Eye scale incorrect taking parent component scale into account.


1.2.6 (2025-06-23)
------------------

Added
~~~~~

- (Components) Added Joint Color setting.
- (Components) Added joint colors, radius and jointDraw mode to component configuration.
- (Configuration) Added Global joint size to configuration.
- (Fkchain) Option to remove controls from fk chain component, note joints will not be driven by anything in this case.
- (Rigconfig) Added Deform and Non-Deform joint radius settings.

Bug
~~~

- (Brows) Fix Mirror and apply symmetry not always correctly mirroring the curve.
- (Eye) Fix idMapping returning ids which don't exist due to user settings.
- (Guidemirroring) Fix mirroring core code not taking into account offsetParentMatrix current value.
- (Mouth) Fix Alignment of guides not correctly taking ctrlCount into account, meaning extra ctrls added will not be aligned previously.
- (Mouth) Fix DeleteGuideCurve(lips) not deleting math node networks at the same time.
- (Mouth) Fix guides Not aligning at all due to transform attrs not being unlocked beforehand.
- (Mouth) Fix joint alignment not being relative to root guide orientation.
- (Mouth) Fix lip mirroring scaling issues.
- (Preferences) Fix export plugin preference key using wrong name.
- (Quadleg) Remove upr,mid,ankle deform joints from skeleton selection set when twists/bendy is enabled.

Change
~~~~~~

- (Bendysystem) Small Improvement to build time by remove a few deep data copies.
- (Core) Replaced component Method setupSelectionSet with deformationJointIds() to have better reuse for joint Color, radius and selection sets.


1.2.5 (2025-06-12)
------------------

Bug
~~~

- (Eyelids) Regression fix for Incorrect default values for fleshy attributes.


1.2.4 (2025-06-11)
------------------

Added
~~~~~

- (Godnode) Added option to setup global scale to remove non-uniform scaling support.
- (Markingmenu) Added Guide Annotation visibility option to marking menu.

Bug
~~~

- (Brows) Fix Aligning brows would cause the curve to reset back to original position.
- (Eye) Fix building without non-uniform scale not connecting the eye joint.
- (Limbs) Fix build error due to a maya2026 node type name typo.


1.2.3 (2025-05-28)
------------------

Added
~~~~~

- (Fk) Added Scale mirroring support.

Bug
~~~

- (Eye) Fix non-uniform scaling + eye rotation issues.
- (Godnode) Regression Fix where rootMotion joint didn't respect the rootMotion guide orientation, resulting in unexpected behaviour in Unreal.
- (Quadleg) Regression Fix where old rigs can't be deleted due to now removed rig logic.


1.2.2 (2025-05-21)
------------------

Added
~~~~~

- (Eyes) Added option to set lid Y translation for when lid close is fully active.

Bug
~~~

- (Cheek) Fix spacer attribute being named visibility instead of multipliers.
- (Cheeks) Fix missing naming convention.
- (Core) Fix component to component connections not playing well with maya constraints eg. orient spaceSwitching.
- (Core) Fix Regression where control srts weren't being locked.
- (Ikfk) Fix matching Scale when switch ik to fk.
- (Leg) Fix ikstretch not being affected by foot extra ctrls eg. ballroll.
- (Leg) Fix leg lock not taking into account mirrored components.
- (Leg) Fix quadleg stretch not working with ballroll and segment stretch attrs.
- (Mouth) Fix incorrect default orientation for outer left guides.
- (Mouth) Fix set curve guide multiple times would not update existing curve but create a new one.
- (Quadleg) Fix quadleg lock not taking into account mirrored components.
- (Quadleg) Fix quadleg stretch and segment stretch attrs not working with ballroll.

Change
~~~~~~

- (Mouth) Fix visibility on outer and center tertiary guides.
- (Templates) Updated head_face and biped_face templates with cheeks.


1.2.1 (2025-05-07)
------------------

Added
~~~~~

- (Templates) Added mouth component to biped_face and head_face templates.
- (Selectionset_Face_Buildscript.Py) Added support for the mouth component in the face selection sets.

Bug
~~~

- (Core) Fix Driver meta data failing to load due to empty string not being valid json.
- (Jaw) Fix input nodes having wrong location first time building.
- (Mouth) Fix drivers not being saved to definition.

Change
~~~~~~

- (Templates) Update face templates mouth drivers.


1.2.0 (2025-05-06)
------------------

Bug
~~~

- (Mouth) Fix deleting anim rig causing non default values to propagate to PSD transforms.


1.1.8 (2025-05-06)
------------------

Added
~~~~~

- (Api) Added support for driver definition with current support for direct connections between components.
- (Api) Added support for setting the pivot shape and a guide.
- (Cheekcomponent) Added Cheek Component.
- (Core) Allow Curve and Surface type Guide pivot shape types.
- (Mouthcomponent) Added Mouth Component.

Bug
~~~

- (Core) Ensure display layer current active is turned off while building to avoid runtime errors.
- (Core) Fix Zoo Matrix constraints on deform joints not being deleted between builds.
- (Jaw) Fix output nodes not having their transform set during deform build instead of rig build.

Change
~~~~~~

- (Api) Changed mirroring/symmetry behaviour to allow components to define how to mirror, useful for situation like the mouth which mirror locally instead of to a separate component.
- (Templates) Update head_face template eye lid curve colors to be the same as the default.
- (Templates) Updated human templates to have ik leg align to world by default.

Removed
~~~~~~~

- (Serialization) Removed the need to serialize anim control shapes reduces build time/serialization overhead.


1.1.7 (2025-04-01)
------------------

Bug
~~~

- (Brow) Fix build error when a joint guide is outside the raycast tolerance of the brow curve when detect the closest curve to which the joint belongs.
- (Head) Fix head alignment not maintaining guide position when head guide autoAlign is off and neck->head is not straight up.
- (Head) Fix neck alignment not maintaining guide position when neck guide autoAlign is off.
- (Mirror) Regression Fix due to core mirror changes which created a AttributeError with axisNamesToNegativeVector.
- (Mirrorconstants.Py) Ik legs hips control (baseIk) now mirrors correctly with the mirror tools.


1.1.6 (2025-03-28)
------------------

Bug
~~~

- (Core) Maya 2026 Fixes for multDoubleLinear and addDoubleLinear nodes.


1.1.5 (2025-03-25)
------------------

Added
~~~~~

- (Configuration) Added hideCtrlsDuringPlayback option to configuration.


1.1.4 (2025-03-11)
------------------

Added
~~~~~

- (Selectionset_Allcomponents.Py) Added build script that creates a selection set for every hive component and parents to the all set.
- (Selectionset_Buildfromsaved.Py) Added build script that rebuilds the selection set if saved to the scene with the Zoo Selection Set UI.

Bug
~~~

- (Jaw) Fix Jaw output node not receiving the result of Auto top lip transform.


1.1.3 (2025-03-06)
------------------

Bug
~~~

- (Eyecomponent) Fix inverted rotations when a guide is outside the start or end of the lid curve.


1.1.2 (2025-03-04)
------------------

Bug
~~~

- (2Boneik) Fix hard coding of aimVector when setting up stretch allowing for other axis based on the guides aimVector.
- (Head) Fix twists not outputting their outputNodes, making it not connectable.


1.1.0 (2025-02-28)
------------------

Bug
~~~

- (Autoalign) Default autoAlign(fk) doesn't maintain child guides transform.
- (Fkcomponent) Fix fk custom spaceSwitch drivers being lost between builds.
- (Fkik) Fix switching from ik to fk ignoring scale on arms/legs/vchain.
- (Spaceswitching) Fix renaming a component wouldn't update space switch drivers dependencies for other components.
- (Templates) Fix horse template spine flipping when moving away from world 0.
- (Templates) Fix UE template root joint orientation not matching UE skeleton.

Change
~~~~~~

- (Core) Replaced all uses of floatMath nodes with the equivalent native maya nodes over using lookdevkit builtin plugin.
- (Fbxexport) Added support for exporting takes, If no take is provided as part of the settings then the default take 001 will be updated with the range.
- (Spineik) Added Guide Setting to remove default spaceSwitches allowing users to it themselves.


1.0.47 (2025-01-28)
-------------------

Added
~~~~~

- (Quadleg) Added ikfk result transform to space switch driver objects.
- (Templates) Added face components to Ue5 templates.
- (Vchain) Added ikfk result transform to space switch driver objects.

Bug
~~~

- (Brow) Fix Brow Failing to update curve cvs when auto aligning.

Change
~~~~~~

- (Brow) Unlocked differentiator translate attrs.
- (Core) Allow spaceSwitch internals to connect to tagged nodes not just controls.
- (Eye) Unlocked differentiator translate attrs.
- (Eye) Unlocked translate and rotate attrs for pupil and iris.
- (Jaw) Unlocked differentiator translate attrs.
- (Templates) Update biped templates cog guides to have their autoAlign set to off.


1.0.46 (2025-01-10)
-------------------

Bug
~~~

- (Head) Toggling twist joints From pre zoo version 2.9.4b would error. Guide validation has also been added to inform the user to rebuild the head component in this specific case due to the head guide meta data being deleted from a bug.
- (Quadleg) Fix IkEnd ctrl alignment being inverted when foot is turned off and the quad leg is rotate 90+ degrees.


1.0.45 (2025-01-08)
-------------------

Added
~~~~~

- (Templates) Added UE5 template with Spine IK component.

Change
~~~~~~

- (Docs) Fix findRigInstance function in hive examples.
- (Head) Fix toggling twists on/off causing head joint definition being deleting which results in build errors.
- (Universalrigbuilder) Speed up twist counts change during matching.
- (Natalie_Buildscript.Py) Minor changes to Nat build script, label attr renamed.


1.0.44 (2024-12-11)
-------------------

Bug
~~~

- (Fbx) Fix non-uniform joint scale default values not being exported.
- (Ikfkmatch) Fix Quad ikfk match having a 180 flipped rotations when matching on a mirrored component.

Change
~~~~~~

- (Jaw) Added topLip offset anim attribute.


1.0.43 (2024-11-25)
-------------------

Added
~~~~~

- (Arm) Added option to toggle off building auto rotation into the arm twists.
- (Head) Added option to toggle off building auto rotation into the arm twists.
- (Leg) Added option to toggle off building auto rotation into the arm twists.
- (Markingmenu) Added (un)solo options to marking menu.
- (Quadleg) Added option to toggle off building auto rotation into the arm twists.
- (Biped_Face.Template) Added the build scripts, face selection set and face visibility.
- (Facevisibility_Buildscript.Py) This build script adds a face visibility attribute to the head, or other controls for toggling the face controls on and off.
- (Head_Face.Template) Added the build scripts, face selection set and face visibility.
- (Selectionset_Face_Buildscript.Py) New build script that can be added to any rig with the standard Hive face. Checks if components exists and handles the animator selection sets.

Bug
~~~

- (Eyelid) Fix incorrect Scale(shear) values propagating from eyeCtrl to eyeScale jnt when eye guide is rotated on more than one axis.
- (Mirrorconstants.Py) Eye target mirror has been fixed, translation mirror was broken.

Change
~~~~~~

- (Guides) Xray guides is now a configuration setting and saved as meta data.
- (Jaw) Change jaw mover to use BSDiff output for better consistency.
- (Jaw) Change top-lip to be rotated when bottom lip and/or jaw move up.
- (Jaw) Ported jaw Blendshape Differentiator from the buildscript into the component and force delete the old buildScript from user preferences.
- (Natalie_Buildscript.Py) Removed code related to the custom face which no longer exists. Face sets have been moved to selectionset_face_buildscript.py.


1.0.41 (2024-11-18)
-------------------

Bug
~~~

- (Autopolevector) Fix aimMatrix on auto polevector using default attribute value which is different based on maya version.
- (Bendy) Fix aimMatrices using default attribute value which is different based on maya version which caused some controls to be flipped in 2025.
- (Brow) Fix aimMatrices using default attribute value which is different based on maya version which caused some controls to be flipped in 2025.
- (Eyecomponent) Fix pupil and iris scaling when rotating the parentinput.
- (Eyescale) Fix eyeScale translate, rotate attributes not being locked causing users to use unsupported behaviour.
- (Ikfkmatch) Fix ikfk foot match not resetting extra attrs eg. heelside. Which resulted in a constant shift between matches.
- (Ikfkmatch) Fix ikfk match undo not undoing foot ctrls as well.
- (Spineik) Fix volume attrs not supporting no more than 6 joints.

Change
~~~~~~

- (Eyescale) Defaulted non-uniform scale option to on as it's the most common use.


1.0.38 (2024-11-12)
-------------------

Bug
~~~

- (Brow) Fix mirrored component flipping when parent is rotated.
- (Brows) Fix Rails main not having it transform attributes locked only hidden.
- (Eyelids) Fix differentiator attributes not being visible in channelBox.


1.0.37 (2024-11-11)
-------------------

Added
~~~~~

- (Fk) Added Delete Fk guides Marking menu action, note: not currently undoable due to other hive internal limitations with deletion undo.

Bug
~~~

- (Brows) Fix allows curve to be created with less then 4 vertices.
- (Brows) Fix parameter value for the end joint being over 1.0 causing maya error, solved by clamping the value to 1.0.
- (Core) Fix Delete guides not always deleting annotations.
- (Eyelids) Fix allows curve to be created with less then 4 vertices.
- (Fk) Fix addGuide MM always adding an extra meta entry instead of reusing empty ones resulting incorrect numerical ordering when combined with deletion.
- (Fk) Fix IdMapping not taking into a account of guide changes resulting in edge case errors when using marking menu actions.
- (Fkchain) Fix setParent guide not maintaining position.
- (Fk) Fix Fk MM setParent undo not updating meta data resulting in incorrect behaviour when combined with add guide.
- (Fkchain) Fix set parent not saving state resulting in inconsistent parenting when building.
- (Ik) Fix ikhandle and effector not having the visiblity locked to avoid show all behaviour display ik.

Change
~~~~~~

- (Brow) Added Basic guide validation to ensure brow curve exists before building.
- (Core) Guide id meta attribute is now a proxy attribute.
- (Exporter) Update fbxExporter to validate for non-deformer history.
- (Eyelids) Added Basic guide validation to ensure each pair of the eyelids exists before building.
- (Fkchain) Moved add guide and link fk to fk marking menu options down slightly for better consistency between components.
- (Fkchain) Removed redundant guide srts.


1.0.36 (2024-10-30)
-------------------

Added
~~~~~

- (Biped_Face.Template) Added tongue, teeth and nose to the face template.
- (Head_Face.Template) Added tongue, teeth and nose to the face template.


1.0.35 (2024-10-30)
-------------------

Change
~~~~~~

- (Natalie.Template) Added the brows to the natalie template.


1.0.34 (2024-10-30)
-------------------

Added
~~~~~

- (Biped_Face.Template) Added brows, eye template colors tweaked.
- (Head.Template) Added brows, eye template colors tweaked. Neck controls positioned properly.

Bug
~~~

- (Brows) Ensure guide scale attributes are unlocked before applying uniform scale behaviour.
- (Matchguides.Py) Fixed issues due to the new single glabalScale attribute for guides.

Change
~~~~~~

- (Eyelids) Change lid curve default colors.
- (Eyes.Template) Changed curve colors for clarity, was previously uncolored blue.
- (Eyes_Template.Py) Updated template to match the face template, minus the jaw, head and ears/brow.


1.0.33 (2024-10-30)
-------------------

Bug
~~~

- (Eyelid) Scale value from eyeScale guide wasn't applied to "eyeScale" Joint upon build.


1.0.31 (2024-10-29)
-------------------

Added
~~~~~

- (Brows) Added Primary ctrl X translation to blendshape differentiator.
- (Components) Added a ValidateGuides method to components and subsystems which can be called by the user via the api or UIs which validates components of the current state the scene guides are in.
- (Exporter) Added .ma exporter plugin.
- (Metadata) Added zoo,hive and Maya version as rig meta data and template metaData for easier debugging user files.
- (Validation) Added basic first pass FBX validation.

Bug
~~~

- (Brows) Fix mirrored brow having invert roll for the rail curve.
- (Controls) Transform attrs on srts are now locked to avoid users messing with them.
- (Fbxexporter) Fix Fbx Exporter error when complete if the current scene isn't valid.
- (Guides) Guide Srts are now transform attributes are now locked to avoid users accidentally modifying them which results in unexpected behavior.
- (Serialization) Avoid serializing plugs types which aren't supported.
- (Twists) Twist guides would incorrectly align in 2022 or below due to autodesk changing aimMatrix mode default attribute value in 2023.

Change
~~~~~~

- (Brows) Allow tangents to go into the negative values.
- (Guides) Set Scale Y alias to "globalScale" and no longer allow non-uniform scale except if a component overrides the behaviour e.g. eyeScale.


1.0.30 (2024-10-21)
-------------------

Added
~~~~~

- (Cccharacterbase_Meshpivots.Json) Added universal mesh pivots.
- (Hive.Py) Preferences path to universalmeshes.
- (Skinproxy.Py) Now also deletes the blendshape while importing a Skin Proxy Mesh.
- (Universalmesh.Py) Added support for seting the vertDict to support multiple meshes from a UI.

Bug
~~~

- (Hiveskinproxy_Meshpivots.Json) Added universal mesh pivots.
- (Skinproxy.Py) Fix for multiple imports of the skinproxy mesh with the namespace already in the scene.

Removed
~~~~~~~

- (Umeshconstants.Py) Removed thumb aims for now.


1.0.29 (2024-10-18)
-------------------

Added
~~~~~

- (Umeshconstants.Py) Added locator pivot grps.
- (Universalmesh.Py) Added build template curves and improved organisation with groups and auto-clean setups.
- (Universalmesh.Py) Improved neck auto orient.

Change
~~~~~~

- (Brow) Default brow guide controls adjusted.


1.0.28 (2024-10-17)
-------------------

Added
~~~~~

- (Brow) Added brow Component.
- (Buildskinfromskele.Py) Tool now handles if no skin proxy mesh is present.
- (Skinproxy.Py) Added importSkinProxyMesh() function.
- (Skinproxy_Constants.Py) Added DEFAULT_SKINPROXY_MESH, and DEFAULT_SKINPROXY_SKELETON_ROOT.
- (Umeshconstants.Py) Added LOCATOR_BIPED_DEFAULT, JOINT_NAMES, LRA_JOINTS and MESH_VERT_COUNT.
- (Umeshconstants.Py) Added UI list for the universal mesh to Hive UI.
- (Umeshconstants.Py) Added universal mesh constants for the universalmesh module.
- (Universalmesh.Py) Added numerous functionality ready for Alpha release.
- (Universalmesh.Py) Basic changes to better match a UI.
- (Universalmesh.Py) Builds left pivots, skeleton and a full Hive rig from the Skin Proxy Mesh only.

Bug
~~~

- (Commands) Fix Deletecomponent undo failing due to core api type changes.
- (Core) Fix guide srt name clashing.
- (Core) Fixed createSrtBuffer method set transform rotations incorrectly when handling negative scale.
- (Dggraph) Creation of input/output attributes now support, min/max default and enums.
- (Dggraph) Deleting DGGraphs would fail if a downstream connected attribute was locked.
- (Delete) Fix delete buildRig function name typo.
- (Eye) Fix control srt name clashes.
- (Eye) Fix some DG node names not have component name as prefix.
- (Eye) Fix undoing joint count change error.
- (Fbxexport) Fix upAxis and format ui options not being used. in exporter.
- (Head) Fix head twists default shape.
- (Head) Neck joint shouldn't be included in the selectionSet if twists are active.
- (Head) Regression Fix for head and neck not auto aligning since twists were added to the component.
- (Hive) Failed to load hive commands in maya 2020.
- (Leg) Fix ball and ballRoll name clash.
- (Quadleg) Fix ball and ballRoll name clash.
- (Twists) Fix default guide pivot shape to be a sphere instead of sphere arrow.
- (Twists) Fix twists not having scale constrained when bendy is not built.
- (Buildscript) Fix jaw build script fail if locator doesn't exist on build.
- (Universalmesh.Py) Now cleans up the locators in the scene after building the rig.

Change
~~~~~~

- (Eye) DifferentiatorBS Node visibility now can be turn on via channelBox "showBSDifferentiator".
- (Eyelid) Added EyeScale joint to skin selection set.
- (Eyelids) Added blinkRatio attribute separator to channelBox.
- (Eyelids) Changed outer lids visibility attribute default value to True.
- (Eyelids) Removed BetaVersion tag.
- (Tests) Add more templates builds to tests.

Removed
~~~~~~~

- (Undo) Flushed undo after a build since undo has been unstable.


1.0.27 (2024-08-02)
-------------------

Added
~~~~~

- (Animatortools.Py) Added Biped TPose function.
- (Buildskinfromskele.Py) Checks if the skin proxy mesh or base joint have unique names.
- (Buildskinfromskele.Py) Funciton targetGeoObjectsAsString handles long non unique names.

Bug
~~~

- (Templates) Fix UE5 Template finger control transforms.


1.0.26 (2024-08-01)
-------------------

Added
~~~~~

- (Natalie_Buildscript.Py) Updated build script to match the new natalie eyes and jaw. Selection sets and face vis all working.

Bug
~~~

- (Eye) Fix Eye joints not being effected by the eyeCtrl when non-uniform scale is active.
- (Eye) Fix Eye rotation issues with non-uniform scale active.
- (Eye) Fix differentiatorBS.lwrblinkUpDown attr using incorrect blinkRatio math.
- (Eye) Fix pupil and iris hierarchy being inverted.
- (Eye) Fix Pupil and iris default guide control rotation so it's at 90 degrees.


1.0.25 (2024-07-30)
-------------------

Bug
~~~

- (Core) Fix joint offsetParentMatrix not being reset to identity matrix when rebuilding.
- (Eye) Fix eye,pupil,iris,eyeMain alignment when mirrored.
- (Ikfk) Fix ikfk default setting not being applied to control panel default.


1.0.24 (2024-07-26)
-------------------

Bug
~~~

- (Core) Disconnecting joint transforms would also disconnect downstream connections instead of just the sources. This resulted in user SDKs and the like to be disconnected.
- (Headcomponent) Fix head output node that being scale constrained.


1.0.23 (2024-07-17)
-------------------

Bug
~~~

- (Headcomponent) Fix building components which have new joints but not attached to the skincluster prebindmatrix.
- (Headcomponent) Fix Building Rig with twists which resulted in the wrong offset being applied to the head outputNode.
- (Namingpresets) Fix print hierarchy spacing bug.


1.0.21 (2024-07-10)
-------------------

Added
~~~~~

- (Head) Twists subsystem to head component(neck segment).
- (Namingpresets) Added Duplicate Preset helper method, note UI has yet to support duplicate.

Bug
~~~

- (Eyecomponent) Fix Eye aim twisting when parent component is rotated.
- (Eyecomponent) Fixed Pupil and iris parenting being in the wrong order.
- (Eyelids) Fix Pupil and iris default control shape size being the same.
- (Templates) Fix right Leg twist orientation being flipped.
- (Twists) Fix guide twist Offset control shape defaulting to world zero on creation.
- (Uetemplate) Fix UE default template orientations and spine count.

Change
~~~~~~

- (Headcomponent) Replaced Maya constraints with matrix constraint to clean up the Dag and improve performance, plus consistency.
- (Templates) Natalie, biped templates updated with neck twists.
- (Templates) Updated all templates which contain a head to either have neck twists or not.

Misc
~~~~

- (Biped.Template.Py) Twists now default to 6 rather than 5 for arms and legs. Changed ( biped_face.template ) Twists now default to 6 rather than 5 for arms and legs. Ignore ( buildskinfromskele.py ) Doc & message changes.
- (Buildskinfromskele.Py) Auto adds the proxy mesh and base joint while loading the UI.
- (Buildskinfromskele.Py) Many updates, the major change is that the skin proxy mesh is duplicated to the Hive joints and then skinning is transferred speeding up the skinning of dense meshes. Many other changes including auto detection of the proxy root node and skin proxy geo. More error checks added and better error messages for users.
- (Skinproxy.Mb) Added the Maya file skinProxy.mb that can be imported into scenes for characterization and for building new hive rigs.
- (Skinproxy.Mb) Deleted animation and toughGuy all blendshape that wasn't needed, reduced filesize by 1MB.
- (Skinproxy.Py) Moved this module to zoo_hive, can now import the skinproxy.mb and delete and check if it exists. Added ( skinproxy_constants.py ) Moved the constants to zoo_hive, added the path to the skinproxy.mb file. Added ( buildskinfromskele.py ) Added function to duplicate the shaders of the original skin proxy and offset their colors on the newly created mesh.


1.0.20 (2024-06-20)
-------------------

Added
~~~~~

- (Markingmenu) Added Foot and wrist guide menu for arm,leg and QuadLeg.
- (Buildskinfromskele.Py) More work, rig now builds if a Hive rig from selection.
- (Hiverigexists) Added check if the hive rig exists and will build the rig if not.
- (Matchconstants.Py) Upgrading constants to match with new UI "Build Rig From Skeleton".
- (Matchconstants.Py) Added HIVE_BIPED_FK_IDS for Hive FK spine bipeds. Added more spine support for HIK Accurig etc.
- (Matchguides.Py) Added function to return hive guide selection as a string for the Build Rig From Skeleton UI.
- (Matchguides.Py) Added functions hiveIdDictToList() and skeletonDictToList().
- (Matchguides.Py) Upgrading to sync with the new UI "Build Rig From Skeleton".
- (Matchguides.Py) More tweaks to build and match rigs from a skeleton.

Bug
~~~

- (Bendy) Fix bendy roundness having different results depending on leg size.
- (Bendy) Fixed Duplicate node names.
- (Controllertags) Added controller tag evaulation toggle to default build script to avoid maya freezing during builds.
- (Core) Fix creating SRT on a control which has non-identity offsetParentMatrix would result in a local offset.
- (Godnode) Fix regression of root joint naming.
- (Headcomponent) Fixed Duplicate node names.
- (Naming) Fix global naming config override not being included in the hierarchy when resolving component hierarchy.
- (Namingpreset) UE5 naming preset for upper arm/leg now has up to 6 twist count built in naming overrides.
- (Namingpresets) Fix Duplicate naming preset paths being registered due to case-sensitive.
- (Namingpresets) Fix Redundant naming rule overrides in default ZootoolsPro preset.
- (Namingpresets) Fix namingPresets output folder being all lower case while searching for camelcase.
- (Quadleg) BREAKING change to ensure ik/fk controls are named differently.
- (Quadleg) Fix Quadleg ikfk naming conflicts.
- (Spineik) Changing joint count while child components are pinned results in hive core error.
- (Spineik) Changing spine ik joint count raises AttributeError.
- (Twists) Remove redundant twist server jnt(tempJnt) which causes duplicate naming validation issues.
- (Matchguides.Py) Accounted for the deleted toe in the match hive to skeleton.

Change
~~~~~~

- (Buildskinfromskele.Py) New module for ingesting full rigs into hive including building and skinning.
- (Matchconstants.Py) Cleaning up matchconstants.py.

Misc
~~~~

- (Buildskinfromskele.Py) Broken up the build function so that it can be tracked via a progress bar. Bugfixes and documentation.
- (Buildskinfromskele.Py) Is building from a skin proxy scene, needs a UI now.
- (Buildskinfromskele.Py) Minor update, main build broken into multiple steps for a progress bar in the UI. Added ( matchguides.py ) Added alignFeetControls() and alignWristControls() for marking menus and the auto hive builders. Main BuildMatchGuides() class supports auto finding of the top skeleton and has been broken up further for the progress bar.
- (Buildskinfromskele.Py) Added helper functions for UI and some better error checking. Hides the skin proxy after building the rig.
- (Footwristmatchcommands.Py) Fix for the quadleg foot Align Feet Controls some controls were out. Changed ( footwristmatchcommands.py ) Changed marking menu label to Align Foot/Wrist Controls and the icon change too. Added ( icons ) Added jointKnee_64.png, superhero_64.png and thinMan_64.png icons. Added ( matchguides.py ) Added fix option for the quad leg Align Foot Controls.
- (Matchguides.Py) Doc changes minor.

Removed
~~~~~~~

- (Markingmenu) Removed marking menu from being overridden in templates as we don't support overrides at the user level.


1.0.19 (2024-05-23)
-------------------

Bug
~~~

- (Frameless) Fix OSX file name detection of "._*" which was always a false positive.


1.0.18 (2024-05-23)
-------------------

Added
~~~~~

- (Markingmenu) Added xray guides marking menu option.

Bug
~~~

- (Eyelids) Building the eyeLids with a joint count which doesn't match ctrl count would result in a failure.
- (Eyelids) Fix differentiator_bs output node not receiving values due to node evaluation being skipped.
- (Jaw_Differentiator_Bs) Fix differentiator_bs output node not receiving values due to node evaluation being skipped.

Change
~~~~~~

- (Eyelids) Change method name from blinkRatioParams to blinkJointRatioParams for clarity.
- (Spineik) Fix Fk Ctrl count incorrectly place new guides and fixes error when deleting fkguides.


1.0.17 (2024-05-10)
-------------------

Bug
~~~

- (Core) Fix For duplicate Meta data attrName causing scene corruption in maya 2025.
- (Maya2025) Fix SaveDefinitionData method failing in Maya2025 when accessing component child attribute by child name instead of fullPath.
- (Maya2025) Fix access to child compound attribute would randomly fail.
- (Twoboneik) Fix IkHandle having duplicate name.


1.0.16 (2024-05-03)
-------------------

Added
~~~~~

- (Core) Added addGuideSettings to guideLayerDefinition for faster solution to adding settings in bulk.
- (Core) Added createDisplayLayer to rig meta node.
- (Core) Creating deform joints now pass attributes from the definition.
- (Markingmenu) Added Mirror marking menu tools.
- (Templates) Added biped template with face.
- (Animmirror.Py) Right Click marking menu now with the Mirror marking menu with icons and fully functional.
- (Head_Face.Template) Added template with teh head eyes and ears/jaw.
- (Mirroranim.Py) Support for flipping and center controls WIP.
- (Mirroranimation.Py) Added mirror animation functions.
- (Mirrorconstants.Py) Added full support for aim and eye components, center and mirror.
- (Mirrorconstants.Py) Support for flipping and center axis flipping.

Bug
~~~

- (Bendy) Fix Out tangent guide alignment being inverted after update to use auto polevector.
- (Core) Creating a joint fails if a parent isn't provided.
- (Duplication) Regression fix for component duplication which led to source duplicated component missing it's parent.
- (Jawcomponent) Fix alignGuides failing if auto align is turned off.
- (Legcomponent) Fix foot not being autoAligned, Fixes foot mirror/symmetry.
- (Quadleg) Fixed Ik ctrl not constraining rotations to the ik joint when Foot has been removed.
- (Serialization) Fix zoo constraints being serialized .
- (Uenamingpreset) Fix spine naming for pelvis and godnode.
- (Mirroranim.Py) Fixed issues if the opposite control doesn't exist even though hte component does.

Change
~~~~~~

- (Eyecomponent) Fix default Transform for eyeLid controls.
- (Fkchain) Fk/Finger now support toggling the creation of all joints.
- (Mirroring) Added support for mirroring by scale.
- (Biped_Face.Template) Tweaked template controls curves and face proportions.


1.0.15 (2024-03-07)
-------------------

Bug
~~~

- (Headcomponent) Fix HeadSpace switch have wrong default offset causing switching space to have incorrect transform.


1.0.14 (2024-02-21)
-------------------

Added
~~~~~

- (Buildscript) Added Support to handle build script deletion allowing for buildscripts to cleanup.

Bug
~~~

- (Buildscript) Update tortoise buildscript for new joint constraints.
- (Component) If user attempted to SetParent twice with different drivers the existing constraint and annotation isn't removed.
- (Mirroring) Regression, mirroring parent components would not correctly constrain mirrored child components.
- (Quadleg) AlignIkEnd and AutoAlign settings not being respected in rig build.
- (Quadleg) Changing the endGuide rotation affected the ik control shape incorrectly at rig build time.
- (Quadleg) Hock(ankle) control not receiving alignment matrix when endGuide autoAlign is False.
- (Registries) Handle OSX special files when discovering data files.
- (Ueaddikjoints) UEAddIkJoints build script now deletes joints from the scene if the build script was removed.

Change
~~~~~~

- (Api) Definition class no longer inherits ObjectDict making getitem and setitem no longer supported but easily to understand and document.
- (Assets) Take into account of the global option to avoid copying default assets to user assets.


1.0.13 (2024-01-23)
-------------------

Bug
~~~

- (Bendy) Regression Fix for Bendy auto roundness shifting inverted.
- (Restposecache) Regression Fix for rest Pose cache matrices not being set.


1.0.12 (2024-01-22)
-------------------

Added
~~~~~

- (Bendy) Added Volume Preservation.
- (Customrig.Py) Added customrig module, logic for parenting custom rigs to Hive.

Bug
~~~

- (Componentcore) Relying on hierarchy deletion results in numerous maya errors which have no impact on operation but cluttered log history, this fixes most of these by ensuring NamedGraphs get deleted beforehand.
- (Constraints) Fixes most NonUniform scale issues but not all, specifically if you nonuniform scale the elbow then the fingers will be incorrect but fine if you do the wrist, something to continue looking into.
- (Fbxexport) Fix UEikJoints from being deleted.
- (Fbxexport) Fix joints which are tagged to the rig deformLayer from being delete.
- (Iklock) Fix Ik Lock not taking global uniform scale into account.
- (Legcomponent) Fix ball output node not being connected to ball joint.
- (Natbuildscript) ParentConstraint for faceRig wasn't updated between builds.
- (Setlivelink) Failed when a joint wasn't part of the transform rest pose cache.
- (Spaceswitch) Rig Attributes would be incorrectly inserting at wrong index.
- (Spinefk) Fix newly created guides having it's control shape at world zero.
- (Twists) Fix twist settings not being maintained between builds.
- (Ikstretch) Fix Stretch not taking global uniform scale into account.

Change
~~~~~~

- (Commands) Remove zoo triggers while any hive command is running.
- (Constraints) Switch component connection constraints with matrices.
- (Constraints) Switch most component output->bindJoint constraints to matrices with some exceptions ie. ikfk output is still maya constraints.
- (Deleterig) DeleteRig now has option to avoid deleting deformJoints if they're attached to the root DeformLayer MetaData.
- (Quadleg) Removed Beta Label.
- (Scaling) General Scale fixes and replacement of most maya constraints for joints.


1.0.11 (2023-12-05)
-------------------

Added
~~~~~

- (Configuration) Added isHistoricallyInteresting to Rig Configuration, rig will be updated automatically during polish or when in rig mode, and the user sets the value in the UI.
- (Mirror) Added pre-post mirror methods to component class for better component customization.
- (Buildscriptwidget.Py) Added tooltip for build script widget buttons.
- (Horsetemplate.Py) Added the horse template to hive under animals.
- (Jawdifferentiator_Buildscript.Py) Added a buildscript for the jaw that spits out the rotation differences in the jaw lips chin and head. Useful for blendshape correctives on mouths and jaws.

Bug
~~~

- (Alignguides) Maintain upVec world position between alignments.
- (Definition) Parent always being updated even though it's an internal guide which shouldn't be reparented.
- (Joints) LiveLinking joints to guide with differing hierarchy causes bad transform offsets.
- (Serialization) Loading rig from scene doesn't maintain base definition priority updates.
- (Spine) Fix CogGimbal not always having the same transform as the cog.
- (Symmetry) Fix symmetry not having the same behavior as mirroring, now allows components to handle specific setups via pre-post mirror.
- (Templates) Fix default UE5 template arm orientation having an inverted upVector.
- (Tortoisedemotemplate) Fix buildScript which fails when running preDeleteRig.

Change
~~~~~~

- (Components) Updated jaw component to have better default control shapes, default alignment, chin missing control shape and fixed wrong joints being added to skin selectionSet.
- (Ikguides) Updated VChain, arm, leg and quadleg components to now live orient to the ik plane.


1.0.10 (2023-11-10)
-------------------

Bug
~~~

- (Templates) Fixed full body templates with quad spines so the root control is always up in world.


1.0.9 (2023-11-10)
------------------

Change
~~~~~~

- (Canine) Fixed the root control to align with world.


1.0.8 (2023-11-10)
------------------

Bug
~~~

- (Spineik) Typo fix to spineik definition.
- (Alignment) Improvement to worldUpVec construction plane to align at the endGuide.
- (Spineik) Cog AutoAlign to be turn off by default.
- (Spineik) Update WorldUpVec scale.
- (Worldupvec) Update worldUpVec guide size in component base definition to be larger.


1.0.7 (2023-11-10)
------------------

Change
~~~~~~

- (Spineik) Fix ctrl02 alignment aligning to wrong guide.
- (Template) Turn off auto align for cog guide.


1.0.6 (2023-11-10)
------------------

Change
~~~~~~

- (Spineik) Fix ctrl02 alignment aligning to wrong guide.
- (Template) Turn off auto align for cog guide.


1.0.5 (2023-11-10)
------------------

Added
~~~~~

- (Bendy) Added angle multipliers for auto roundness in the guide settings to help with rig scale.
- (Quad) Added bendy to quad leg.
- (Templates) Added allosaurus template.
- (Templates) Added dino_carnivore, spiderLeg, insect_spider canine templates.
- (Templates) Added canine_legBack, canine_legFront.
- (Templates) Added werewolf.

Bug
~~~

- (Bendy) Bendy subsystem to support more then 2 segments.
- (Bendy) Fix primary bendy guides not having the correct alignment when the linked primary guide alignment changes.
- (Component) Fix vChain,arm,leg components ignore alignToWorld option if the component doesn't support aligning relative.
- (Fkcomponent) Fix FkComponent not correctly constrained if parent component has no joints.
- (Guides) Fix gudie shape transform not maintaining serialized transform.
- (Guides) Twist Guide incorrect scale propagation from wrong parent guide.
- (Quad) Fix twists not being deleted when settings has been changed.
- (Quadspinetemplate) Incorrect default alignment.
- (Reversefoot) Fix min/max values for "sideBank", "heelSideToSide".
- (Rigfromnode) Fix rigFromNode raising an error if the meta Node retrieve isn't a hive node, hive will now search all attached metanodes until the first one is found.
- (Rigfromnode) Fix twoboneiksubsystem failing if the attached component does have a worldUpVec guide.
- (Spineik) Fix cogGimbal being ignore during auto align.
- (Twoboneik) Fix Lock value output not being connected.

Change
~~~~~~

- (Bendy) Bendy AutoAlign now updated to use worldUpVec normal.
- (Components) Updated quad leg default guide.
- (Graphregistry) Cache graph data on first use and reuse from there on.
- (Ik) Updated IK limbs to use worldUpVec guide Y basisVector as plane normal for alignment.
- (Ikplane) Removed now redundant worldUpVecRef from IK Limbs except for spine we now pull the YbasisVector from the worldMatrix of worldUpVec for better stability.
- (Mirror) WorldUpVec mirroring requires special handling after latest changes.

Misc
~~~~

- (Misc) Quad leg updates with bendy.


1.0.4 (2023-10-05)
------------------

Added
~~~~~

- (Dino_Carnivore_Buildscript.Py) Cleans up selection sets on carnivore dinosaurs.
- (Mannequin_Spine_Buildscript.Py) SImplifies the default sontrol visibility for spline spines.

Bug
~~~

- (Autoalign) No longer attempt to predict worldUpVec world rotation during alignment.
- (Reversefoot) Reverse Foot was forced on if any guide setting was changed other than the foot.
- (Reversefoot) Reverse foot joints would be forced to be recreated every other build even though the foot build setting was off.
- (Twists) Twists was forced on if any guide setting was changed other than the twist toggle setting.

Change
~~~~~~

- (Components) Added alignIkEndToWorld to ik limb.


1.0.3 (2023-09-27)
------------------

Bug
~~~

- (Componentregistry) Take into account folders with "." in the name when looking up components.


1.0.2 (2023-09-27)
------------------

Added
~~~~~

- (Unittests) Added unittest for UE5 mannequin build.
- (Mirrorconstants.Py) Quad leg mirror dict added to mirrorconstants.py.

Bug
~~~

- (Armcomponent) Fix an additional twist guide in the base component definition.
- (Autopolevector) Fix maya error message which has no real consequences due to order of operation when PoleVector node graph is generated.
- (Componentlibrary) ComponentDataByPath doesn't treat .py and .pyc as the same, this fixes the comparison.

Change
~~~~~~

- (Quadspine) BaseIK guide shape now deleted from the guides and now uses the Upr Guide shape.
- (Templates) Polished Quad spine template.
- (Unittest) Updated unittests to explicit test twist guides.


1.0.1 (2023-09-27)
------------------

Added
~~~~~

- (Api) Added helper method to return a template by a provided path if available.
- (Templates) Save template now supports providing the folder path to save too.

Bug
~~~

- (Components) Small fix to arm,leg and quad components where the twist segment counts had wrong attribute datatype.
- (Ikfk) Fix Quadleg ankle ikfk matching.
- (Mirror) Regression, Mirroring without duplicating option resulted in components being either unparented or parented to wrong components if the component already existed.
- (Mirror) Regression, mirroring caused parenting to the new mirrored component to be ignored or parented to wrong component.
- (Mirror) Undo mirroring would error.
- (Preferences) Applying preferences doesn't update template paths registry.
- (Preferences) Apply preferences doesn't update Hive artist UI Template library widget.
- (Quadleg) Fix Hip Guide pivot being visible.
- (Selection) Marking menu selection options error during undo.
- (Unreal) Add support for quad leg in UEaddikjoints_buildscript.
- (Unreal) UEaddikjoints_buildscript fails hard if one of the required components don't exist.

Change
~~~~~~

- (Components) Change to component folder hierarchy for a better organization.
- (Components) Depreciated icon variable and replaced with uiData dict, currently only specified with the Python class, this will be supported in the definition later.
- (Templates Misc) Templates re-categorized into folders.


1.0.0b25 (2023-08-22)
---------------------

Added
~~~~~

- (Ue5Template) Added ik hand/foot build script to UEtemplate.
- (Matchconstants.Py) Match constants for Hive guide Ids and various skeletons and third party skeletons. Will add controls later for animation matching.
- (Matchguides.Py) WIP module for matching Hive guides to various skeletons including third party skeletons such as mixamo and accurig.

Bug
~~~

- (Bendy) Incorrect default tangent guide alignment vectors.
- (Bendy) Incorrect tangent distance for first out tangent.
- (Ikfkmatch) Ikfk deletes keys on all nodes disregarding per component state and per frame keys ranges.
- (Ikfkmatch) Ikfk matching occurs on frames which the component is already in the required ikfk state.
- (Namingpresets) Add naming configurations based on its hiveType key allowing for custom configs without modifying core hive.
- (Polevector) Backward compatibility fix for old rigs missing auto pole vector attributes.
- (Uenamingpreset) Fix spine root name being hipsSwing instead of pelvis.
- (Vchain) End Guide alignment is inconsistent with subclasses which have child guides that change order.

Change
~~~~~~

- (Templates) Updated default pole vector distance on various templates.
- (Autopolevector) Change default distance to 20.
- (Fkchain) Simplify Output node constraint code.


1.0.0b24 (2023-08-11)
---------------------

Added
~~~~~

- (Fkutils) Added util function to generate fk guides from specified transforms.
- (Fbxexporter.Py) Added batch fbx export helper functions to fbxexporter. fbxExportHiveRigsSel() fbxExportHiveRigNames(). More helper functions to come including handling multiple time sections.
- (Fbxexporter.Py) Added misc helper UI functions.
- (Fbxexporter.Py) Added save and load UI functions.
- (Fbxexporter.Py) Converted batch exporting to classes and added functionality for exporting time-ranges for cycles. This is fully working now with new naming options too.
- (Fbxexporter.Py) Documentation and many UI related additions and tweaks to the UI functions.
- (Hiverigexportwidget.Py) Added Create Time Slider Bookmarks function, opens the Maya window.

Bug
~~~

- (Controlnode) ControlNode setParent queries for an srt even when not asked for it.
- (Controlnode) Fix srt queries failing when the control has multiple message connections to a HiveLayer.
- (Definition) BaseDefinition Srts should take priority over templates.
- (Definition) Children expanded multiple times during update.
- (Deletion) Fix Component deletion where joints were already created but the guides were deleted causing an AttributeError.
- (Displaylayers) Annotations not added to displayLayer.
- (Fkcomponent) Fix control creation failing if the parent control was yet to be created.
- (Guides) Fix Fk "link fk" command failure to delete annotation.
- (Guides) Fix default pivot shape type for guides which don't override it.
- (Ikfk) Ikfk matching takes into account distance setting from the guides.
- (Jaw) Building rig fails to find jaw guide when parenting due to bad sorting in the definition.
- (Markingmenu) "toggleLra" command fails if there are no guides other than the root.
- (Mirrorutils) Fix mirror currentState data not containing the behaviour value.
- (Natalie) PreDeleteRigLayer fails due to legacy facial setup.
- (Recalculatepolevector) PoleVector distance setting is taken into account.
- (Rename) Rig renaming after the rig has been built at least once fails due to missing selectionSets which were deleted.
- (Rig) Fix Set modification while looping over it.
- (Rig) Fix recreating guides not syncing the current scene before rebuild.
- (Symmetry) Fix Shape being incorrectly mirrored.
- (Ue5Namingpreset) Incorrect thigh twist naming.

Change
~~~~~~

- (Arm) Reduced Guide srts.
- (Bendy) Bendy to use one curve per segment in prep for squash.
- (Bendy) Primary bendy guide pivot is no longer visible by default.
- (Commands) Update commands to latest core changes.
- (Leg) Reduced Guide srts.
- (Transformstofkguides) Added guide scale to transformsToFkGuides function.
- (Vchain) Reduced Guide srts.

Misc
~~~~

- (Misc) Added Interactive PoleVector guides.
- (Misc) Temp fix for component caching. todo: do a real fix.
- (Rename) Root selection set incorrectly named after rig rename.
- (Transformstofkguides) TransformsToFkGuides to also set root guide scale.
- (Transformstofkguides) Fix root guide scale not using the default * guideScale.
- (Ikfkmatch) Better distance handling.


1.0.0b23 (2023-06-23)
---------------------

Bug
~~~

- (Buildstate) Skeleton build state being ignored if guide control build state was on.


1.0.0b22 (2023-06-22)
---------------------

Added
~~~~~

- (Guides) Added helper function for aligning guides along a Plane.

Bug
~~~

- (Buildscripting) Fix default properties not being passed to build scripts on execution.
- (Components) Retrieving the parent component joint will now return the only joint on the component if there's only one joint.
- (Controls) Srt() function would fail if the attached metaNode wasn't the guideLayer or rigLayer, now searches for specific meta types.
- (Filtering) Searching for components from nodes raises error if any node isn't a hive node.
- (Godcomponent) Godnode now supports settings the offset guide as the component parent, allowing for an isolated rootmotion. this is now default.
- (Python) Fix missing namespace pkg setup code in prefs.
- (Spineik) Fix World input from the parent component using the wrong node.
- (Templates) Fix biped template inverted twist joint alignment.
- (Templates) Templates rootmotion now handled.
- (Unittest) Fix unittest error with testing annotations.
- (Vchain) Twist DGGraph had debug nodes being created.

Change
~~~~~~

- (Build) Building Guides which already display control vis will now just hide them.
- (Buildmodes) Added Guide Control visibility build state.
- (Config) Remove redundant singleChainHierarchy settings as this is enforced.
- (Guides) Annotations have been switched out to use maya curves.
- (Template) Biped Templates updated with latest code changes.
- (Vchaincomponent) Update for co-planar iterator changes.


1.0.0b21 (2023-05-11)
---------------------

Bug
~~~

- (Visibility) Fix Visibility attributes being connected but not hidden.


1.0.0b20 (2023-05-11)
---------------------

Added
~~~~~

- (Settings) Added Shapes hidden in outliner configuration option.
- (Animatortools.Py) Added misc animator tools module for Hive.
- (Animatortools.Py) Added toggle control panel nodes selected function. toggleControlPanelNodesSel().

Bug
~~~

- (Bendy) Fix bendy control visiblity being connected but not hidden in channelBox.


1.0.0b19 (2023-05-10)
---------------------

Bug
~~~

- (Naming) Fix Template saving not saving component level naming preset override.
- (Templates) Fix UE template not having the Naming Presets.

Change
~~~~~~

- (Resetattrs) Support network nodes in resetAttrs.


1.0.0b18 (2023-05-03)
---------------------

Added
~~~~~

- (Mirroranimation) Updated mirror animation for bendy.
- (Mirrorbehaviour) Added mirror behaviour types.
- (Mirrorbehaviour) Added mirror behaviour types.
- (Mirrorconstants.Py) Temp Fix for bendy arms and mirroring, will be changed again once the bendy orient fix is pushed.

Bug
~~~

- (Bendy) Fixed default bendy control alignment.
- (Bendy) Fixed default bendy control alignment.
- (Buildscripts) Fix zoomannequin_buildscript using incorrect api calls to change default attribute values.
- (Hiveversion) Fix hiveVersion return None on first call.
- (Mirror) Mirroring doesn't run align guides resulting inconsistent alignment.
- (Mirror) Mirroring doesn't run align guides resulting inconsistent alignment.
- (Serialization) Fix naming preset not being serialized for components.
- (Serialization) Fix naming preset not being serialized for components.
- (Symmetry) Applying symmetry has different behaviour to mirroring due to components not being disconnected in batch.
- (Symmetry) Applying symmetry has different behaviour to mirroring due to components not being disconnected in batch.
- (Templates) Fix natalie templates having old toe guides.
- (Templates) Fix ue5_mannequin template not having naming convention overrides.
- (Templates) Updated Sir_moustache template with arms.

Change
~~~~~~

- (Templates) Change template hive version to 1.0.0b18.

Removed
~~~~~~~

- (Utils) Moved strutils from zoo_core to core.


1.0.0b17 (2023-04-05)
---------------------

Added
~~~~~

- (Templates) Added support updating a rig from a template.
- (Sir_Moustache_Buildscript.Py) Build script supports arms and visibility for amrs, hat and facial geo and controls. Bendy on by default.

Bug
~~~

- (Blackbox) Undoing blackbox would fail.
- (Build) Fix building Guides potentially causing a guide pop in child components under certain situations.
- (Cli) Hive fails to run any hive commands if run in headless maya.
- (Definition) Guide definition doesn't have alignment vector attributes by default.
- (Spaceswitching) Fix default driver not being applied to maya attribute.
- (Spaceswitching) Fix removeSpacesByLabel not actually deleting the space.
- (Spaceswitching) Fix spaceSwitching not saving the template File.
- (Startup) Fix startup file to avoid importing modules before they exist due to later zoo version logic.
- (Templates) UpdateFromTemplate doesn't update component names.
- (Templates) UpdateFromTemplate would fail if the template didn't have the component or the component was renamed, now provides a way to remap components by name.
- (Core) Maya 2024 fixes.

Change
~~~~~~

- (Api) DeformLayer.delete now support arguments "deleteJoints" to allow the deformLayer meta node to be deleted without deleting joints.
- (Core) Split loadFromTemplate code for reuse in updateFromTemplate.
- (Natalie) Update natalie build script face rig scale.
- (Rigcore) Accessing a single component via rig.component() doesn't add component to rig cache.
- (Unittests) Skip unittests which are yet to be implemented.
- (Vchain) Include coPlanar op as part of the alignment batch.
- (Mirrorconstants.Py) Fix for bendy mirroring.


1.0.0b16 (2023-03-23)
---------------------

Bug
~~~

- (Fbxexporter) Fix RuntimeError when export FBX animation without skinning and with meshes.


1.0.0b15 (2023-03-16)
---------------------

Bug
~~~

- (Spaceswitching) Fix custom space switching on FkComponents being deleted.
- (Spaceswitching) FkComponent Loses custom spaces switches when rebuild guides.
- (Twists) Fix new twists not having their mirror attribute set to True.
- (Templates) Fix twist guides not having mirroring set to on.


1.0.0b14 (2023-03-13)
---------------------

Added
~~~~~

- (Zoomannequin_Buildscript) Build script for zoo mannequin that handles visor and foot bendy controls.

Bug
~~~

- (Selectionset_Biped_Buildscript) Arm selection sets were not parenting correctly depending on the rig and the dictionary order.

Change
~~~~~~

- (Legcomponent) Update leg component footbreak default value to 65.


1.0.0b13 (2023-03-13)
---------------------

Bug
~~~

- (Components) Fix aimComponent failing to rebuild.
- (Natalie_Buildscript.Py) Bugs addressed for rebuilding with the face and not only th template.

Change
~~~~~~

- (Selectionset_Biped_Buildscript.Py) ArmFingerClav sets can have any side string variations. Eg "L" or "left" and are no longer hardcoded.


1.0.0b12 (2023-03-09)
---------------------

Bug
~~~

- (Twists) Upr arm/leg twist server node has incorrect rotations causing issues if the rig has non t-pose setup.


1.0.0.b11 (2023-03-08)
----------------------

Bug
~~~

- (Bendy) Maya 2020 tangent rotation graph update to match 2023.


1.0.0.b10 (2023-03-08)
----------------------

Bug
~~~

- (Bendy) MidBendy out tangent has incorrect rotation when mid ctrl has translations.


1.0.0b9 (2023-03-07)
--------------------

Bug
~~~

- (Bendy) Failure when adding bendy back in after removing it.
- (Bendy) Fix ctrl Scale on lowerarm inheriting from wrong output.
- (Bendy) OSX Fix getParamAtPoint causing runtime error, replaced with closestPoint.
- (Fbxexport) Fix Scale issues when exporting FBX.
- (Head) Fix worldSpace scale being applied to joints.
- (Joints) Deactivated scale compensation across all components to have better support for scale.
- (Spine) Fix worldSpace scale being applied to joints.
- (Spine) Swapped non-uniform scale to uniform scale to support game engines universally.
- (Twists) Failure when adding Twists back in after removing it.
- (Twists) Removing twists leaves unused DG nodes in the scene.
- (Twists) Twists flip when rotating globally i.e godnode.

Change
~~~~~~

- (Bendysubsystem.Py) Tweaked the bendy multiplier amount to 0.4 for a more rounded auto-bendy.


1.0.0b8 (2023-03-02)
--------------------

Added
~~~~~

- (Buildscript) Added support for Buildscript property tooltips.
- (Hive Templates Misc) All templates upgraded to have limb world up vectors.
- (Hive Templates Misc) Bendy added to Natalie and biped templates, still zoo_mannequin and sir_moustache to go.
- (Hive Templates Misc) Bendy added to zoo_mannequin and sir_moustache rig templates.
- (Mirrorconstants.Py) Added bendy control mirror anim support.
- (Natalie_Buildscript.Py) Minor tweaks, proxy attributes for hair vis now on the head and hips.
- (Selectionset_Biped_Buildscript.Py) Added icons and hide sets from the selection set marking menu.
- (Sir_Moustache_Buildscript.Py) Sir Moustache build script for selection sets added.
- (Tortoise_Buildscript.Py) New selections sets are now fully working for Tortoise Toon.

Bug
~~~

- (Alignguides) AlignGuides doesn't disconnect child components.
- (Components) Edge case where Live link fails when adding new array indices.
- (Components) Updating guide settings doesn't maintain connections.
- (Fbxexporter) Failure to export with geometry due to TypeErrors.
- (Mayacallbacks) Fix maya internal callbacks with attributeEditor erroring, we do this by removing the current selection before building.
- (Nodeeditor) Temporarily disable nodeEditor while building.
- (Resetcontrols) Reset Marking menu doesn't reset all attributes.
- (Resetcontrols) Reset all below marking menu doesn't reset child components.
- (Templates) Templates not saving build script property state.
- (Vchain) Fix Global scale not being accounted for.
- (Vchaincomponent) VChainComponent AlignGuides end guide doesn't handle the shapeNode resulting in a possible difference.

Change
~~~~~~

- (Armcomponent) Update base arm component control shapes to match templates.
- (Checkbox) Checkbox widget to allow label as a kwarg.
- (Guides) Rebuilding guides will now delete the guides beforehand reducing errors because of a metaData change between hive versions.
- (Naming) Update arm and leg configs with bendy ids.
- (Robot) Change robot godnode name to god for consistency.
- (Templates) Updates templates with latest code.
- (Twists) Changed twistIds() method to return a list of lists to inline with new subsystem.
- (Twists) Removed TwistServerIK for upr segments, reducing the number of IKHandles.
- (Roboball_Buildscript.Py) Robo Ball build script now builds selection sets correctly.
- (Zoomannequin_Buildscript.Py) The mannequin buildscript now supports new style hierarchical selection sets for use with the selection set marking menu.

Removed
~~~~~~~

- (Twists) Removed now redundant SRT for individual twists.
- (Robot_Buildscript.Py And Zoomannequin_Buildscript.Py) Removed build scripts for robot and zoo mannequin as they are no longer needed.


1.0.0b7 (2023-01-25)
--------------------

Added
~~~~~

- (Rig) Added helper method to clear component cache.

Bug
~~~

- (Components) Fix case where a user has manually deleted a layer transform.
- (Components) Updating an existing guide Setting raises Type error.
- (Guidevisibility) Fix guide control visibility state when setting both the control and pivot visibility at the same time.
- (Guides) Fix buildGuides causing a transformation difference when certain components have a different alignment for connected guides.
- (Spineik) Fix AutoAlign failure when a guide autoAlign is Off.

Change
~~~~~~

- (Alignguides) AlignGuides optimized up to 2x.
- (Guidevisibility) Support maya undo modifier for better speed.
- (License) Update copyright for 2023.
- (Splineik) Remove beta state.

Removed
~~~~~~~

- (Metanodes) Removed the use of old metaRig classes as hives base.


1.0.0b6 (2022-12-03)
--------------------

Added
~~~~~

- (Templates) Assorted new Hive templates added as defaults.
- (Fkcomponent) Added helper function to compose a fk id string.
- (Iolayer) Added clearInputs and clearOutputs methods to IO scene layer nodes.
- (Skirt_Buildscript.Py) Skirt hive template, buildscript added.

Bug
~~~

- (Alignguides) Ik components polevector sets to world 0 if angle is 0.
- (Buildguides) Joints are not reset on build guides.
- (Buildrig) Building the rig doesn't reset the skeleton transforms.
- (Fkcomponent) Fix guide deletion skipping when the parent/child relationship doesn't match numerical values ids.
- (Guides) Fix Guides not being locked after building.
- (Guides) Temp removal of controller tags due to a maya bug which doesn't update transforms when a guide shape isn't visible.
- (Iolayer) Fix IO scene nodes not being deleted from the scene after deleting the rig resulting in modified transforms.
- (Namingpresets) Fix incorrect default naming preset path for case sensitivity.
- (Namingpresets) Fix naming of default name preset folder.
- (Natalie) Face rig scale attributes not reset when rig is deleted.
- (Recalculatepolevector) If angle is 0.0 the polevector will be set to world 0.
- (Recalculatepolevector) Undo Fails when executing recalculatePoleVector command.
- (Spineik) Fix idMapping method returning ids which don't exist for deformLayer.
- (Natalie_Buildscript.Py) Added fix when hair and toes don't exist in the scene for Nat Lightweight.
- (Natalie_Buildscript.Py) Prepopulate fix for the natalie build script due to Zoo changes.

Change
~~~~~~

- (Controlpanel) Port control getter logic to meta.
- (Fbxexporter) Added user message when attempting to export geometry with no geometry parented.
- (Recalculatepolevector) RecalculatePoleVector now selects the poleVectors after the commands has run.
- (Templates) SaveTemplate command now uses hive exporter plugin.
- (Twists) Change twist guide scale to 0.25. Templates updated to reflect this.
- (Api) Fix missing errors types in api module.
- (Guides) Update Movable guides to have a sphere_arrow shape for differing between guides.
- (Tortoise_Buildscript.Py) Upvector on neck visible by default.


1.0.0b5 (2022-11-17)
--------------------

Added
~~~~~

- (Tortoise_Buildscript.Py) Added new build script for the new tortoise template and rig.

Bug
~~~

- (Applysymmetry) Fix applySymmetry not updating control shape location due to 2023.2 viewport bug.
- (Fbxexport) Fix geo root not being unlocked before export when exporting animation and meshes at the same time.
- (Legcomponent) Fix footBreak not being animatable.
- (Selectionsets) RigLayer.selectionSet() returning None at all times.
- (Settings) Fix adding the same setting between builds not updating.
- (Spineik) Fix autoAlign behaviour ignoring AutoAlign state attribute.
- (Twists) Fix twist settings not updating between builds when the setting already exists.

Change
~~~~~~

- (Controls) RotateOrder to be displayed in the channelBox.
- (Controls) RotateOrder to be keyable due to studio library issues with non-keyable.
- (Markingmenu) Renamed mirror label to Create Mirror.
- (Buildscripting .Rst Docs) Updated build scripts docs website documentation to add further clarity.
- (Buildscripts) Changed documentation for all build scripts. template_buildscript.py documentation has been improved.
- (Buildscripts) Updated all build scripts to point to new website documentation.


1.0.0b4 (2022-10-26)
--------------------

Added
~~~~~

- (Buildscript) Added buildscripts from Silke.
- (Definition) RigLayer settings now forces update from the base instead of the scene overriding.
- (Spineik) Added Translation space switch to ctrl02.
- (Spineik) Added parent space to ctrl02 and remove rotSpace.
- (Hivemirrorcopypasteanim.Py) Tool added auto set start end from timeline on tool open. Small refactoring.
- (Mirroranim.Py) Added some documentation and small refactor pass.

Bug
~~~

- (Addfkguide) Fix adding a new fk guide via the marking menu when adding from a parent guide which has existing children.
- (Autoalign) Regression fix where control visibility would switch on, This was a workaround for a 2023 bug but we need didn't reset state after operation.
- (Core) Fix liveLinking a root joint off world 0 would result in a transform offset.
- (Legcomponent) Fix Legcomponent ballRoll using wrong axis.
- (Spaceswitching) Fix duplicate spaceSwitch driver labels.
- (Spine) Space switches not marking as not editable.
- (Spineik) Fix custom space switches not being maintained during rebuild.
- (Spineik) Fix duplicate spaceSwitch definitions.
- (Spineik) Fix missing marking menu space switch menus.
- (Vchaincomponent) Fix to a maya evaluation issue with expressions when anim cache is off where on scene load the mel expression isn't evaluated causing incorrect transformations, This change replaces the expression with nodes.

Change
~~~~~~

- (Command) Added setGuideLRA command to hive command module.
- (Fkcomponents) Temporary change to force autoAlign Off til we have WorldUpVector artist exposure.
- (Mainwindow) Removed show argument from init function due to visual artifacts it can cause due to events.
- (Naming) Removed redundant system field example for "object" rule.

Misc
~~~~

- (Templates) Various templates upgraded. Robots support stretch and new build scripts. Natalie has tweaks. Arms have auto-align off for fingers.
- (Hive_Artist_Ui_Shelf.Layout) Added tool Hive Mirror Paste Anim to the animation shelf.
- (Icons) Checkbox name fixed that was causing error.
- (Mirroranim.Py) Functions for copy/paste mirroring selected Hive controls for cycles and other.
- (Mirrorconstants.Py) Control flip curve related constants for mirroring tools (will be meta data later).
- (Mirroranim.Py) Selection now restricted to transforms only for Hive mirror animation.
- (Mirroranim.Py) Documentation. Added ( mirrorconstants.py ) Added all Hive rig components and ids to mirrorconstants.py.
- (Selection.Py) Misc selection set helper functions added Added ( natalie_buildscript.py ) Added custom animator selection sets to the natalie build script.


1.0.0b3 (2022-09-29)
--------------------

Added
~~~~~

- (Core) Added support for Named DependencyGraph storage as part of the definition.
- (Naming) Added UE5 Presets.
- (Spineik) Added SpineIK Component.
- (Templates) Added UE5 mannequin Templates.
- (Vchain) Added upper,lower stretch attributes.

Bug
~~~

- (Commands) Fix ShowLRA command including the root guide.
- (Components) Deleting rig doesn't reset scale.
- (Components) Deleting the rig layer of a component results in joint rotations being non-zero.
- (Components) Fix KeyError when live linking.
- (Components) Fix case where rebuilding the guides after polish raises AttributeError due to missing container.
- (Components) Fix incorrect UpVector calculation for AimComponent.
- (Components) Fix stretch attributes not being removed based on hasStretch setting.
- (Containers) Fix missing component nodes in containers.
- (Displaylayers) HideOnPlayback should be on by default.
- (Fbx) Fix failure when exporting geometry when the geo root is locked.
- (Fkcomponent) Fix parent constraint causing issues with scale compensation.
- (Guides) Fix guide change in guide parent during build stage.
- (Headcomponent) Fix global scale not being handled correctly.
- (Jawcomponent) Fix parent constraint causing issues with scale compensation.
- (Legcomponent) Ball and heel rotation fix.
- (Naming) Fix Output name type spec.
- (Naming) Fix side labeling case sensitivity.
- (Outliner) Container Asset Contents display now reflects "containerOutlinerDisplayUnderParent" Preference on build.
- (Rig) Fix hideOnPlayback being set to off for controls.
- (Serialization) Avoid serialization of internal attributes that aren't important.
- (Templates) Rename Template uses incorrect registry id format.
- (Togglelra) Fix ToggleLRA not skipping root guide when check current display state.
- (Togglelra) Fix guide Layer failing to update when a definition attribute doesn't have a value field.
- (Twists) Fix twist joints not removing redundancies.
- (Vchain) Fix stretch attributes not being removed based on hasStretch setting.
- (Vchaincomponent) Fix Scaling issues related to ikfk blending.
- (Vchaincomponent) Fix global scale not being handled correctly.

Change
~~~~~~

- (Biped) Renamed biped to biped_spineFK before creation of IK version.
- (Commands) ToggleGuide Pivots now include root components.
- (Components) Added anim attribute for upr IK visibility for vchain/arm/leg components.
- (Components) Arm/vchain/leg now uses locators for control guide pivots.
- (Components) Avoid parenting components when the driver guide doesn't link to a joint.
- (Components) BuildConstraint updated to latest base code.
- (Components) SegmentScale compensate to now default to true.
- (Components) Support for flagging a component as beta.
- (Core) Guides now track pivot shape nodes as metaData.
- (Core) Moved util modules into util package.
- (Definition) Force the Default pivotColor and shape to base definition.
- (Definition) GuideLayer now supports delete a single Setting at a time.
- (Godnodecomponent) Adding visibility attributes for guide pivots.
- (Markingmenu) Temporary Remove of the deformLayer marking menu until we have deformation tools.
- (Natalie) Update natalie build script to latest spine changes.
- (Natalietemplate) Replaced natalie template to use spineik.
- (Spinefk) Fix default location and scale of spineFk.
- (Spineik) Changed ikCtrlVis to midIkVis.
- (Spineik) Replaced Anim curve/frame cache nodes with remap and anim attributes.
- (Splineik) Guide curve now has a visibility attribute.
- (Templates) Replace biped with spineIk.
- (Templates) Replaced zoo_mannequin spine with spine ik.
- (Templates) Updated to latest rig changes.
- (Zapi) Update template unittest for biped.

Misc
~~~~

- (Misc) Testing.

Misc
~~~~

- (Misc) Testing.


1.0.0b2 (2022-07-25)
--------------------

Bug
~~~

- (Naming) Fix incorrect name expression for rig level layers.
- (Naming) Fix renaming of components not saving.
- (Naming) Fix rig renaming missing a few nodes.
- (Naming) Hive Rig meta node name doesn't match naming convention from configuration.

Change
~~~~~~

- (Natalie) Update Natalies Buildscript for latest naming changes.
- (Unittests) Added basic template tests.
- (Unittests) Update rig rename tests.


1.0.0b1 (2022-07-20)
--------------------

Added
~~~~~

- (Naming) Add support for naming configuration presets.
- (Preferences) Added support for naming configuration paths to preferences UI.

Bug
~~~

- (Alignguides) Pin/unPin being run multiple times depending on the component resulting in a 20%ish slow down.
- (Buildscripting) BuildScripts outside of zoo packages doesn't reload when zoo is reloaded.
- (Commands) Crash when repeating delete components command.
- (Commands) Force clear selection to avoid Maya attribute editor raising errors due to deletion and rename operations.
- (Commands) Undoing Delete commands multiple times cumulates all deleted components across multiple commands results in too many created components.
- (Component) Deleting a component results in a crash.
- (Components) Fix leg,arm,vchain pole vector not having locked transforms.
- (Definition) Node full names being serialized instead of shortnames.
- (Fbxexport) Fix geometry root and geometry names containing namespaces.
- (Fbxexport) Fix maya error raised when the current scene is untitled.
- (Fkchain) Adding a new guide results in incorrect scaling.
- (Liveguiding) Fix Live guiding where a jnt id may not have the same guide id which results in build failure.
- (Markingmenu) Fix Marking menus not being applied to a component due to the template having an empty value.
- (Markingmenu) Fixed missing marking menu when the template value is empty for the rigLayer.
- (Serialization) Serializing the definition resulted in an unnecessary deepcopy resulting in a further slow down during builds/saves.
- (Spaceswitching) Build a rig multiple times even though it's already built results in a space switch error.
- (Spaceswitching) Removing FK guides doesn't update the linked space switch, resulting in ValueError.
- (Templates) Template configuration not being applied when creating a rig from a template.

Change
~~~~~~

- (Api) Function addSettingsNode renamed to createSettingsNode.
- (Definition) Expanded definition serialization to scene into multiple attributes to reduce possibility of hit char length limits. This Break backwards compatibility.
- (Errors) Added MissingControlError exception for RigLayer.Control as replacement for ValueError.
- (Fingercomponent) Deform joint Ids prefix to "bind" instead of Fk for future Ik mode support.
- (Fkcomponent) Changed Input Node ID to "parent" for clarity.
- (Fkcomponent) Fk component to support different Deform Jnt ids.
- (Guides) Better support for local transforms being locked.
- (Layers) Replaced settings node attribute metadata with a compound array for faster lookup and better organization. This Break backwards compatibility.
- (Markingmenu) Marking menu to provide a user warning message when the rig may require an upgrade before proceeding.
- (Naming) Added base naming configuration for each component type.
- (Naming) Build time naming configuration cache to allow naming to change between builds.
- (Naming) Change all rule expression names to camelCase for consistency and for UI expression conversion.
- (Naming) Update templates with new arm component.
- (Naming) Updated all components with new naming scheme.
- (Naming) Updated preference interface with naming related pathing.
- (Preferences) Added hive interface frontend function to preferences.interfaces.hiveinterfaces.
- (Spine) Added Gimbal visibility switch.
- (Spine) Changed spine component type to spineFk for separation of spine types.
- (Spinecomponent) Restructured Skeleton ahead of adding Ik. Includes renaming.
- (Templates) Updated Natalie to replace fkchain fingers for finger type component.
- (Templates) Updated biped and zoo_mannequin to use the finger component instead of the fkchain.
- (Templates) Updated templates with latest spine changes.
- (Vchaincomponent) UpVector transform to be locked.

Misc
~~~~

- (Markingmenutils.Py) Marking menu rig upgrade message changed.

Remove
~~~~~~

- (Components) Removed getOrCreateLayer method as it's preferred to use the component metaclass.


1.0.0a19 (2022-06-05)
---------------------

Bug
~~~

- (Spaceswitching) Build failure when a SpaceSwitch Driver Component dependency has yet to be built.


1.0.0a18 (2022-05-31)
---------------------

Bug
~~~

- (Preferences) KeyError when upgrading preferences when the user has no existing preferences.


1.0.0a17 (2022-05-31)
---------------------

Added
~~~~~

- (Jawcomponent) Added rotate All control.
- (Spaceswitching) User defined SpaceSwitching support within the definition.

Bug
~~~

- (Aimcomponent) Eye aim constraint not constraining aim control.
- (Aimcomponent) Eye control has no shape.
- (Guides) Missing attributes from the definition don't get added to the scene guide.
- (Jawcomponent) Incorrect control hierarchy.
- (Jawcomponent) Incorrect control naming.

Change
~~~~~~

- (Deformation) Deform Layer now updates the deform Layer definition joint transforms before creating joints, allowing component subclasses to change behaviour.
- (Jawcomponent) Chin deform joint being added to the deform selectionSet.

Remove
~~~~~~

- (Headcomponent) Removed Redundant parent_space input node.


1.0.0a16 (2022-04-16)
---------------------

Added
~~~~~

- (Buildscripting) Support pre deletion methods.
- (Core) Added helper method to retrieve the control display layer.
- (Docs) Added Commandline mayapy script example for upgrading rigs.
- (Natalie_Buildscript.Py) Added natalie buildscript example to prefs.
- (Natalie_Buildscript.Py) New functionality added to natalie_buildscript.py including support for skeleton and guide mode also handles the hive rig without a face for building.
- (Template_Buildscript.Py) Added template buildscript example to prefs.

Bug
~~~

- (Components) Missing controlPanel node in selectionSet.
- (Components) ScaleCompensate attributes needs to be turned off.
- (Ikfkswitching) Ikfk attribute doesn't override the existing keyframes when baking.
- (Ikstretch) Stretch not working predictably when lengths are negative values.
- (Mirroring) Mirroring and applySymmetry to a component doesn't unlock local transform attributes before applying mirrored data.
- (Naming) Head control name duplicates "_anim" suffix.
- (Preferences) Missing QuatNodes plugin as a requirement.
- (Rig) Renaming control layer to the same name errors.
- (Spaceswitching) Space attribute doesn't override the existing keyframes when baking.
- (Vchaincomponent) Fix vchain anim attributes not being correctly keyable.
- (Vchaincomponent) Missing DG nodes in meta data connections.
- (Vchaincomponent) Missing deform joint in selection set when hasTwists is False.
- (Vchaincomponent) Stretch math expression needs negating when handling negative incoming lengths.

Change
~~~~~~

- (Componentgroups) Move logic into component layer meta node class.
- (Core) Moved default templates into preference assets.
- (Displaylayer) Control display layer hide on playback.
- (Docs) General fixes to documentation errors.
- (Documentation) Added table of contents to certain pages.
- (Layersapi) MetaData can now be updated on the layer meta nodes from the definition and not just the guideLayer.
- (Naming) Animation controls no longer use namespace to allow compatibility with studio library which doesn't support nested namespaces correctly.
- (Playback) Control Display layer to default playback to True.
- (Pluginmanager) Added name to plugin manager for logging.
- (Preferences) Added IncludeDefaultAssets to preferences.
- (Preferences) Added support for build script default path under user assets folder.
- (Preferences) Fix preferences not being merge with missing keys.
- (Preferences) Hive Assets will now merge the defaults structure.
- (Preferences) UI saving to upgrade assets if necessary.
- (Twists) Unlock twist translation attributes.

Updated
~~~~~~~

- (Natalie.Template) Upgraded template with toes and bob hair.
- (Robot.Template) Upgraded template with shorter arms.


1.0.0a15 (2022-03-14)
---------------------

Added
~~~~~

- (Zoo_Mannequin.Template) Added new zoo_mannequin template for Zoo 2.6.7.

Bug
~~~

- (Components) Setting the components parent to None causes AttributeError.
- (Components) Setting the components parent to None isn't supported.
- (Fbxexport) Ensure FBX Plugin is Loaded.
- (Inputs) Missing Input Error when creating an input when meta attribute already exists but not connected.
- (Unittest) Temp solution to handle unittest base code updates for creating new scene per test.

Change
~~~~~~

- (Natalie.Template) Template updated, finger ends no longer scaled, fingers better zeroed by default.
- (Robot.Template) Updated template to latest Zoo 2.6.7.
- (Templates) Update arm, biped templates, added arm hand template variants.


1.0.0a14 (2022-02-22)
---------------------

Added
~~~~~

- (Attributedefinitions) Added support to insert attributes.
- (Core) Added live linking to marking menu commands in prep for future user features.
- (Core) Added support to generate SRTs nodes when creating controls.
- (Legcomponent) ToeUpDown,ToeSide,ToeBank,heelSideToSide Attributes.
- (Markingmenu) Added support for Fixing IKFK mid joint rotations.
- (Spaceswitching) Added neck space switch.

Bug
~~~

- (Definition) Attributes incorrect channelBox setting resulting in a grey value in channelBox.
- (Definition) Node Attributes incorrectly merging existing attributes.
- (Definition) Node Deserialization resulting in recursion issues.
- (Definition) Node attributes not maintaining order.
- (Guide) Guide default attributes being applied after the user attributes.
- (Guides) Fix missing controller tags on guides.
- (Legcomponent) BallRoll having invert rotations on the toe.
- (Legcomponent) FootPivots don't account for custom orientations.
- (Legcomponent) Incorrect pivot alignment for ballroll.
- (Legcomponent) Incorrect pivot alignment for toe.
- (Logging) Error on building would create an unnecessary layer to the logs.
- (Markingmenu) Ik FK Spaces always showing up, now only show IK Space when in IK.
- (Markingmenu) Spine/FkChain now merges all spaces to Just "FK Space".
- (Proxyattributes) Crash when creating proxy attributes for numeric compounds.
- (Publishing) Attribute publish would crash adding a child plug.
- (Spaceswitching) Missing World space constraint to the godnode for all current spaces.
- (Spaceswitching) VChainComponent ik Space labels inconsistent ordering.
- (Templates) Duplicate entries of pivotShape and pivotColor.

Change
~~~~~~

- (Fixfkrotation) Only display marking menu if more than 2 rotation channels are non zero.
- (Legcomponent) Reorder animation attributes.
- (Spaceswitching) RigLayer createSpaceSwitch will now automatically add constraint nodes to metadata.
- (Templates) All templates updated with latest guide changes.

Removed
~~~~~~~

- (Legcomponent) Remove toeTap from definition as it's been merged with ball.
- (Vscode) Removed vscode project.


1.0.0a13 (2022-02-04)
---------------------

Added
~~~~~

- (Buildscripting) Support for Loading a maya reference file which was exported via hive tools.
- (Buildscripting) Support providing Properties which will be passed to each pre/post methods and to the UI, property changes will be baked into the rig metadata.
- (Exportpluginregistry) Added registry for exporters.
- (Fbxexport) Support for mesh and skin options.
- (Fbxexporter) Fbx export now supports bindPose and Animation.
- (Fkcomponent) Added Orient space switching to all fk controls.
- (Ikfkcomponents) Added support for set polevector over framerange.
- (Ikfkmatch) Support for baking on keys.
- (Mayareferenceexporter) Support for exporting a maya Reference for geometry and skeleton.

Bug
~~~

- (Buildscripting) Fix Registry not having a class interface as a filter.
- (Controls) Fix selectionChildHighlighting not being applied to controls.
- (Core) Jnt namespaces being removed on a referenced joint.
- (Docstring) Fix Several typos in docstrings.
- (Documentation) Fix invalid attributeDefinition link.
- (Fbxexport) Bindpose exporting DisplayLayers.
- (Legcomponent) Incorrect transform for toe tip.
- (Mirrorwidget) Fix UI failure when the current component side isn't a symmetrical name ie. M.
- (Typo) CamelCase Typo fix for DeformlayerDefinition.

Change
~~~~~~

- (Animmarkingmenu) Menu layout reordered.
- (Collapsableframelayout) Rename to CollapsableFrame.
- (Components) Ensure anim attributes are set to display in channelbox.
- (Controls) SelectionChildHighlighting off by default.
- (Documentation) Added documentation for export plugins and updated build scripting docs.
- (Ikfkcomponents) Spaces ikEndSpace and UpVecSpace renamed to ikSpace and PoleVectorSpace.
- (Legcomponent) Updated anim attribute layout.
- (Polevectors) Support for updating existing keys instead of just every frame.
- (Rotationordermm) Display current rotationOrder in bold.
- (Spinecomponent) RotationOrder of first guide to be ZXY.
- (Templates) Update bipedal templates to have ankle rotateOrder as ZXY.
- (Vchaincomponent) Updated anim attribute layout.


1.0.0a12 (2022-01-18)
---------------------

Added
~~~~~

- (Ikfk) Support for matching IKFK over the currently selected frame range.
- (Markingmenu) Change Rotation order options.
- (Spaceswitching) Added baking options.

Bug
~~~

- (Animmarkingmenu) Ignore DGNodes in current selection.
- (Animmarkingmenu) SelectChildControls marking menu to also include currently selected.
- (Symmetry) Fix component children not being included with symmetry.

Change
~~~~~~

- (Legcomponent) IkEnd rotation order is now ZXY.
- (Naming) Basic refactor of naming config on components in prep for new configuration method.
- (Naming) Component deformLayer joints no longer use name spaces.


1.0.0a11 (2021-12-20)
---------------------

Bug
~~~

- (Animation) Deleting all Keyframes deletes the underlying controlPanel.


1.0.0a10 (2021-12-17)
---------------------

Added
~~~~~

- (Symmetry) Added support for guide symmetry via markingmenu.

Bug
~~~

- (Commands) Save template always overrides the template if it exists.
- (Components) Building godnode off world zero results in incorrectly placed controls.
- (Components) Regression Fix for leg and vchain components not hiding twistOffset guides in the viewport.
- (Components) TwistCtrlsVis, baseIK local transform and foot pivots attributes keyable state should be Off.
- (Components) Vchain uprTwistOffset Guide visibility state not off.
- (Components) Visibility attribute baked into component definition.
- (Core) Duplicate attributes present in node definition.
- (Core) Ensure Rig Layer definition only comes from the base component definition not scene.
- (Core) Visibility Attribute being serialized from scene guide.
- (Duplicate) Duplicating a component doesn't duplicate children.
- (Mirror) Mismatch constraints when mirrored components already exists.
- (Templates) Template saving contains visibility configuration, now removed from templates on save.

Change
~~~~~~

- (Alignment) Speed improvements when disconnecting/connecting components before aligning.
- (Buildscripting) Build scripting plugins now get temporarily cached and reused between Pre/Post methods but removed from the cache afterwards.
- (Buildscripting) Default build script now turns off preserveChildren.
- (Component) LegComponent FootBreak to use 40.0 as the default value.
- (Pinning) Speed improvements to Pin/unPin.


1.0.0a9 (2021-12-8)
-------------------

Added
~~~~~

- (Api) CreateGuideControllerTags method to provide components custom ordering. Defaults to creation Order.
- (Api) CreateRigControllerTags method to provide components custom ordering. Defaults to creation Order.
- (Api) SetupSelectionSet method to components.
- (Buildscripting) Add pre guide build method.
- (Core) Support for attribute definition propagation.
- (Spaceswitching) FkSpace for vchain/leg components.
- (Templates) Biped template.

Bug
~~~

- (Anim Rig) Fix twist offset controls not being driven by the rig.
- (Annotations) Fix annotation visiblity lock state not being repected.
- (Buildsystem) Deleting Hive Layers wouldn't happen if you delete when in a early build stage but contains later stage layers.
- (Core) Failure to polish when certain components aren't built.
- (Core) Loading a rig from the scene doesn't use the base component definition for the base before merging the scene state.
- (Core) Setting shape colour with no value raises TypeError.
- (Core) Shape Colour being overridden when using the raw shapeData.
- (Core) Unicode issue for py2.
- (Guide) Annotation setGuideVisible doesn't toggle annotation visibility.
- (Guides) Fix guide pivot visibility toggle only toggling one component instead of all components.
- (Guides) Hive now deletes out of sync scene guides based on the definition cache.
- (Ikfkmatch) Select all IK/FK specified controls across components.
- (Ikfkmatch) TypeError when undoing.
- (Markingmenu) Head component space switching missing from marking menu.
- (Markingmenu) LinkFKtoFk doesn't sort guides by component leading to corrupt guides.
- (Markingmenu) Space switching menu actions to be combined between components.
- (Markingmenu) Space switching setting matrix on wrong node.
- (Markingmenu) Terrible lag when running "reset all below" marking menu action.
- (Rig) Guide visibility effect rig control visibility.
- (Spaceswitching) Head component spaces using parent instead of orient constraint.
- (Spaceswitching) Vchain/leg component space switch missing world when godnode doesn't exist.
- (Templates) LoadFromTemplate selects all root guides on all components instead of just the created.
- (Twists) Control shapes transforms and shapes aren't maintained when changing count.
- (Twists) HasTwists not removing guides.

Change
~~~~~~

- (Api) Definition transform attributes get and set maya types.
- (Api) Guide.shapeNode now returns a controlNode class for better access to shape methods.
- (Component) Update finger and spine base definition.
- (Components) Fix broken godnode definition.
- (Components) Head Component shapes and positioning defaults updated.
- (Components) Leg component defaults.
- (Components) Spine,vchain,godnode to remove the bind joints which don't need to be part of the selectionSet.
- (Components) Update default vchain and leg defaults.
- (Core) Added layersById helper method for faster layer lookup.
- (Core) Batch together node deletion during live link per component.
- (Core) Better batching of default guide alignment code.
- (Core) Cache the parent component instance during build.
- (Core) General Optimisation guide creation.
- (Core) General speed improvements to Guide building.
- (Core) In prep for attr type classes.
- (Core) Template registry save to raise an error if unable to save to disk.
- (Core Optimisation) Minor pass at improving rig deletion speed.
- (Marking Menu) Renamed "Set Parent Guide" to "Link FK to FK".
- (Templates) Natalie,robot,robo_ball,arm,godnode and spine updated controls.

Removed
~~~~~~~

- (Templates) Removed spine template.


1.0.0a8 (2021-11-16)
--------------------

Bug
~~~

- (Misc) Fix Natalie template foot pivots orientations.
- (Misc) Fix terrible lag when running "reset all below" marking menu action.


1.0.0a7 (2021-11-15)
--------------------

Added
~~~~~

- (Misc) API: Support for deleting joints, outputs and inputs from Hive layers.
- (Misc) Added 'HIVE_TEMPLATE_SAVE_PATH' environment variable to act as fallback path.
- (Misc) Added Foot/wrist space to pole vector.
- (Misc) LRA marking menu option now always visible.
- (Misc) New 'Add Guide' marking menu option for fk components.
- (Misc) New 'Set Parent Guide' marking menu option for fk components.

Bug
~~~

- (Misc) Changing FK joint from 1 to anything greater will result in all new guides overlapping.
- (Misc) Changing Fk joint count resets the guides to world zero.
- (Misc) Duplicate entries in definition for I/O nodes.
- (Misc) FK I/O nodes don't match the joint count.
- (Misc) Has Twists no longer working.
- (Misc) Parenting using hotkey "p" corrupts build, guide parenting will now cause standard maya parenting error.
- (Misc) Proxy attributes not maintaining min/max state of primary attribute.
- (Misc) Rebuilding after a Fk joint count change errors.
- (Misc) Twist guide offsets not compensating for scale during auto alignment.

Change
~~~~~~

- (Misc) Marking menu Rig option "Publish Rig" renamed to "Polish Rig" for consistency.
- (Misc) Updated Leg component control shapes to less chaoic.


1.0.0a6 (2021-11-3)
-------------------

Bug
~~~

- (Misc) Fix guide alignment reseting scale.
- (Misc) Fix regression to leg rotation alignment due to legacy code still running.


1.0.0a5 (2021-11-2)
-------------------

Bug
~~~

- (Misc) Fixed regression where changing twist settings for the first would use old guide scene state.


1.0.0a4 (2021-11-1)
-------------------

Bug
~~~

- (Misc) Fixed AttributeError when the guide and deform skeleton count don't match. We currently delete any joints which don't have a guide.
- (Misc) Fixed Container unbound attributes not being removed between builds.
- (Misc) Fixed Twist Guide Settings not sticking between build states.


1.0.0a3 (2021-10-18)
--------------------

Added
~~~~~

- (Misc) Add publish rig to rig marking menu.
- (Misc) Added Align Guides tools to Marking menu.
- (Misc) Added Biped template.
- (Misc) Added Natalie template.
- (Misc) Added arm template.
- (Misc) Added duplicateGuide method to guideLayer.
- (Misc) Added rootMotion and offset controls to godNode component.
- (Misc) Added skeleton visibility toggle to anim menu.
- (Misc) Added spine template.
- (Misc) Added support for serializing only specific Hive layers.
- (Misc) Added support in GuideLayer class to delete a subset of guides in the scene.
- (Misc) Changed "Select guide Shapes" to "Select Guide controls".
- (Misc) Changed Default head component control colors to match robot.
- (Misc) Changed Root Shape Node to be larger for better visibility and selection.
- (Misc) Changed Root Shape Node to cube_bounding.
- (Misc) Consolidated Default guide settings into the GuideDefinition class for consistency.
- (Misc) Replaced Robot spine with new templated version.
- (Misc) Template library to register as lower case for better discovery.

Bug
~~~

- (Ankle) Animation control not aligning with the ball on World Y.
- (Misc) Auto align vchain/leg will now handle the srts making undo more predictable and resetting rotations on the guide is now give more ideal result.
- (Misc) Fixed Crash when undoing auto alignment due to mays undo queue and cmds.
- (Misc) Fixed aim component auto alignment.
- (Misc) Fixed annotations not being deleted when a subset of guides are being deleted.
- (Misc) Fixed annotations setParent not setting extraNodes parent.
- (Misc) Fixed case loading a template onto an existing rig would reconnect formally removed component parents.
- (Misc) Fixed case where Twists alignment would ignore translation.
- (Misc) Fixed case where building the VChain component would error due to no twist definitions.
- (Misc) Fixed case where the user couldn't snap to the root in the viewport.
- (Misc) Fixed case where twist offsets visibility would be reset on build.
- (Misc) Fixed component library refresh not clearing definitions even though a definition was removed on disk.
- (Misc) Fixed component.componentParentJoint failure when deformLayer doesn't exist yet.
- (Misc) Fixed coplanar math for vchain autoalign ignoring Plane Normal.
- (Misc) Fixed create Component doesn't match rotations to currently first selected node.
- (Misc) Fixed default shape type being the circle, now builds with no shape better troubleshooting.
- (Misc) Fixed duplicate and mirror components selecting either all root guides across the rig or rig root.
- (Misc) Fixed edge case where head component error on build deform due to scene serialization missing important info.
- (Misc) Fixed foot pivots don't align relative to ankle in world Y.
- (Misc) Fixed god node controls have different naming convention to other parts of the rig.
- (Misc) Fixed guide Srts doubling up when rebuilding.
- (Misc) Fixed guide attributes not propagating from base definition.
- (Misc) Fixed guide axis shape not switching off when manual orient is toggled off.
- (Misc) Fixed guide visibility not being serialized.
- (Misc) Fixed iKFK matching double Transform on scale.
- (Misc) Fixed inconsistency between manual orient setting and auto align.
- (Misc) Fixed infinite loop when finding parent components joint.
- (Misc) Fixed multi duplication not remapping parents resulting in 2x the amount of duplicated components.
- (Misc) Fixed pole Vector not being auto aligned.
- (Misc) Fixed remove component parent not disconnecting metadata.
- (Misc) Fixed rename template not setting the rigName inside the template.
- (Misc) Fixed rig Hrc node being locked, as it was impossible to reparent.
- (Misc) Fixed rigLayer definition not merging differences between default def and scene state.
- (Misc) Fixed robot update to remove root shape nodes.
- (Misc) Fixed root Control node being created.
- (Misc) Fixed twist Offset guide visibility not being set during build.
- (Misc) Fixed twist Offset guides not being deleted.
- (Misc) Fixed twist joint position generation being inverted.
- (Misc) Fixed twist orients always being inverted by default.
- (Misc) Fixed user error displaying stacktrace when component parenting isn't supported.
- (Misc) Fixed vchain being rebuilt from scratch when twist settings have changed, also Fixes child components being disconnected.
- (Misc) Fixed vchain/leg outputs being in world space instead of local space.

Removed
~~~~~~~

- (Misc) Removed legacy code which dealt with definition versions.


1.0.0 (2023-09-19)
------------------

Added
~~~~~

- (Aimcomponent) Aim control now has parent/world spaceSwitch.
- (Templates) Added QuadSpine template with appropriate guide alignment.
- (Components) Added Quad Leg component integration, note: doesn't contain Bendy.

Bug
~~~

- (Aimcomponent) Aim control needs rotate and scale locked and hidden.
- (Aimcomponent) Alignment fixes.
- (Aimcomponent) Aim anim control doesn't scale with the component.
- (Core) Fix Rebuild error when InputLayer is deleted.
- (Definition) Attributes aren't serialized if the base definition has no attributes specified.
- (Jaw) Fix guide scale alignment for jaw.
- (Spinecomponent) Fix WorldUpVec control having non zero local transforms.
- (Twists) Fix Deform joints not being removed from definition when count changes.
- (Twists) Fix outputs not being deleted when twist count changes.
- (Zoomannequin_Buildscript.Py) Zoo mannequin build script no longer fails if no heel tweaker controls.
