"""CONSTANTS FOR UNIVERSAL MESHES

from zoo.libs.hive.universalmesh import umeshconstants
umeshconstants.ZOO_SKIN_PROXY_DICT

"""
from zoo.libs.maya.cmds.animation import batchconstraintconstants as bcc

# KEYS --------------------------------------------
K_SPLINE_SPINE_BASE = bcc.SPINE00
K_SPLINE_SPINE_TOP = bcc.SPINE05
K_NECK_BASE = bcc.NECK01
K_HEAD = bcc.HEAD
K_CLAVICLE_L = bcc.CLAVICLE_L
K_UPPERARM_L = bcc.SHOULDER_L
K_ELBOW_L = bcc.ELBOW_L
K_WRIST_L = bcc.WRIST_L
K_THUMB00_L = bcc.THUMB01_L
K_THUMB01_L = bcc.THUMB02_L
K_THUMB02_L = bcc.THUMB03_L
K_POINTERMETA_L = bcc.INDEXMETACARPAL_L
K_POINTER00_L = bcc.INDEX01_L
K_POINTER01_L = bcc.INDEX02_L
K_POINTER02_L = bcc.INDEX03_L
K_MIDDLEMETA_L = bcc.MIDDLEMETACARPAL_L
K_MIDDLE00_L = bcc.MIDDLE01_L
K_MIDDLE01_L = bcc.MIDDLE02_L
K_MIDDLE02_L = bcc.MIDDLE03_L
K_RINGMETA_L = bcc.RINGMETACARPAL_L
K_RING00_L = bcc.RING01_L
K_RING01_L = bcc.RING02_L
K_RING02_L = bcc.RING03_L
K_PINKYMETA_L = bcc.PINKYMETACARPAL_L
K_PINKY00_L = bcc.PINKY01_L
K_PINKY01_L = bcc.PINKY02_L
K_PINKY02_L = bcc.PINKY03_L
K_THIGH_L = bcc.THIGH_L
K_KNEE_L = bcc.KNEE_L
K_ANKLE_L = bcc.ANKLE_L
K_BALL_L = bcc.BALL_L
# FOOT PIVOTS --------------------------------------------
K_FOOT_TIP_L = bcc.TOE_L
K_FOOTBANK_OUTER_L = "footBankOuterL"
K_FOOTBANK_INNER_L = "footBankInnerL"
K_HEELPIVOT_L = "heelPivotL"

# ZOO SKIN PROXY --------------------------------------------
SPLINE_SPINE_BASE = [2135, 5590, 2180, 5631, 7019, 7042]
SPLINE_SPINE_TOP = [2184, 5635, 2117, 5572]
NECK_BASE = [2173, 2201]
HEAD = [1053, 4598, 1054, 4599]
CLAVICLE_L = [2122, 2625, 2626, 2632]
UPPERARM_L = [720, 727]
ELBOW_L = [893, 894, 900, 901]
WRIST_L = [7107, 7108, 7109, 7110, 7111, 7112, 7113, 7114, 7115, 7116, 7117, 7118, 7119, 7120, 7121, 7122, 7123, 7124,
           7125, 7126]
THUMB00_L = [190, 193, 194, 299, 302, 696]
THUMB01_L = [113, 140, 161, 241]
THUMB02_L = [118, 119, 121, 144, 145, 164, 165, 177]
POINTERMETA_L = [189, 194, 195, 697]
POINTER00_L = [80, 81, 217, 229, 254, 289]
POINTER01_L = [502, 503, 504, 505, 506, 507, 508, 509]
POINTER02_L = [526, 527, 528, 529, 530, 531, 532, 533]
MIDDLEMETA_L = [199, 207, 265, 698]
MIDDLE00_L = [86, 87, 94, 95, 250, 252, 285, 287]
MIDDLE01_L = [558, 559, 560, 561, 562, 563, 564, 565]
MIDDLE02_L = [574, 575, 576, 577, 578, 579, 580, 581]
RINGMETA_L = [304, 309, 310, 700]
RING00_L = [82, 83, 84, 85, 256, 258, 281, 282, 283, 284]
RING01_L = [630, 631, 632, 633, 634, 635, 636, 637]
RING02_L = [598, 599, 600, 601, 602, 603, 604, 605]
PINKYMETA_L = [102, 306, 307, 318]
PINKY00_L = [266, 291]
PINKY01_L = [654, 655, 656, 657, 658, 659, 660, 661]
PINKY02_L = [686, 687, 688, 689, 690, 691, 692, 693]
THIGH_L = [2154, 2229, 6979, 6991]
KNEE_L = [2903, 2905, 2919, 2920]
ANKLE_L = [3191, 3196, 3200, 3205, 3207, 3214]
BALL_L = [3319, 3320, 3330, 3331]
# FOOT PIVOTS --------------------------------------------
FOOT_TIP_L = [2314]
FOOTBANK_OUTER_L = [3320]
FOOTBANK_INNER_L = [3331]
HEELPIVOT_L = [3204]
# AIMS --------------------------------------------
AIM_THUMBLOWER_L = [144, 145]
AIM_THUMBUPPER_L = [121, 177]

# ZOO SKIN PROXY DICT --------------------------------------------
ZOO_SKIN_PROXY_DICT = {K_SPLINE_SPINE_BASE: SPLINE_SPINE_BASE,
                       K_SPLINE_SPINE_TOP: SPLINE_SPINE_TOP,
                       K_NECK_BASE: NECK_BASE,
                       K_HEAD: HEAD,
                       K_CLAVICLE_L: CLAVICLE_L,
                       K_UPPERARM_L: UPPERARM_L,
                       K_ELBOW_L: ELBOW_L,
                       K_WRIST_L: WRIST_L,
                       K_THUMB00_L: THUMB00_L,
                       K_THUMB01_L: THUMB01_L,
                       K_THUMB02_L: THUMB02_L,
                       K_POINTERMETA_L: POINTERMETA_L,
                       K_POINTER00_L: POINTER00_L,
                       K_POINTER01_L: POINTER01_L,
                       K_POINTER02_L: POINTER02_L,
                       K_MIDDLEMETA_L: MIDDLEMETA_L,
                       K_MIDDLE00_L: MIDDLE00_L,
                       K_MIDDLE01_L: MIDDLE01_L,
                       K_MIDDLE02_L: MIDDLE02_L,
                       K_RINGMETA_L: RINGMETA_L,
                       K_RING00_L: RING00_L,
                       K_RING01_L: RING01_L,
                       K_RING02_L: RING02_L,
                       K_PINKYMETA_L: PINKYMETA_L,
                       K_PINKY00_L: PINKY00_L,
                       K_PINKY01_L: PINKY01_L,
                       K_PINKY02_L: PINKY02_L,
                       K_THIGH_L: THIGH_L,
                       K_KNEE_L: KNEE_L,
                       K_ANKLE_L: ANKLE_L,
                       K_BALL_L: BALL_L,
                       K_FOOT_TIP_L: FOOT_TIP_L,
                       K_FOOTBANK_OUTER_L: FOOTBANK_OUTER_L,
                       K_FOOTBANK_INNER_L: FOOTBANK_INNER_L,
                       K_HEELPIVOT_L: HEELPIVOT_L
                       }

# Default locator positions for the biped rig if no mesh is given
LOCATOR_BIPED_DEFAULT = {
    'spine00_M_zooPivot': ((0.0, 97.05272520844778, -0.5300275087356567),
                           (90.0, 0.0036065120198387848, 90.0)),
    'spine05_M_zooPivot': ((-4.609728805655094e-15, 142.47041687772156, -0.5300275087356572),
                           (90.0, -0.015542213049314784, 90.0)),
    'neck01_M_zooPivot': ((7.170370510222544e-06, 156.42101663847475, -5.874689237086597),
                          (-89.99996626318217, -11.781980586466924, 89.99999311134023)),
    'head_M_zooPivot': ((8.263861916115224e-06, 165.51602847375318, -3.9776272763648874),
                        (-89.99996626318217, -11.781980586466924, 89.99999311134023)),
    'clavicle_L_zooPivot': ((2.223051026888935, 152.2012169353098, -2.7603930312368017),
                            (0.0, 0.0, 0.0)),
    'shoulder_L_zooPivot': ((17.70022054189202, 149.5302476636506, -9.711001661259562),
                            (-21.543801414065143, 4.157579300748639, -49.71868083505998)),
    'elbow_L_zooPivot': ((37.26461053180798, 126.44545694817961, -11.910640019382264),
                         (-23.920954128284794, -25.411412436216363, -37.30211541213141)),
    'wrist_L_zooPivot': ((56.64601055026715, 111.67965587054096, -0.33519985192716284),
                         (-23.920954128282144, -25.411412436216214, -37.30211541213221)),
    'thumb01_L_zooPivot': ((57.13609179174256, 107.98687852891696, 4.247827563763514),
                           (116.20806672298606, -47.544273585538804, -79.19929966975906)),
    'thumb02_L_zooPivot': ((57.6255832019247, 105.42104508568903, 7.102868177802431),
                           (112.36456370323718, -38.4202368483786, -73.58203461884472)),
    'thumb03_L_zooPivot': ((58.52512203674119, 102.36820877032257, 9.627201214498704),
                           (109.94636512314861, -29.089041664305856, -69.24576763139981)),
    'indexMetacarpal_L_zooPivot': ((57.89660718118753, 109.9589218066049, 2.787712850700264),
                                   (6.845530448105837, -21.18897023044788, -47.39973720225126)),
    'index01_L_zooPivot': ((63.04231809825891, 103.81496762379986, 6.76639623222604),
                           (18.613434045097446, -17.980232038966726, -66.41747993844396)),
    'index02_L_zooPivot': ((64.67384522618646, 100.07744188889812, 8.08989904238503),
                           (21.362825316462736, -14.553309175242479, -76.20649087456515)),
    'index03_L_zooPivot': ((65.45704190005846, 96.88727610542554, 8.942692963234318),
                           (23.44212556776835, -10.733288588014275, -85.6803082759111)),
    'middleMetacarpal_L_zooPivot': ((58.40029139003466, 109.67941591687732, 1.3774946246901567),
                                    (6.845347375956717, -21.188970230447897, -47.39973720225145)),
    'middle01_L_zooPivot': ((64.49004584622269, 103.48136008270791, 4.479486979281666),
                            (14.03455308893872, -15.568724013864385, -62.83586180005135)),
    'middle02_L_zooPivot': ((66.5308373752244, 99.50428828542405, 5.724935660976091),
                            (16.490912602454095, -12.929425381733061, -72.7892535779894)),
    'middle03_L_zooPivot': ((67.58311062786537, 96.10719834527328, 6.541366934060608),
                            (18.42385729746787, -9.922085783190589, -82.52087462513643)),
    'ringMetacarpal_L_zooPivot': ((58.893662471049815, 109.40562828756462, -0.003855445013426806),
                                  (6.845347375956702, -21.18897023044792, -47.399737202251565)),
    'ring01_L_zooPivot': ((64.57561403161199, 103.03925412885248, 2.0826432789243237),
                          (9.114913418250355, -11.626726427800227, -62.30636498340183)),
    'ring02_L_zooPivot': ((66.59226512236384, 99.19706281385969, 2.9754783167546797),
                          (10.989480417514807, -9.876731251966735, -72.3288600110997)),
    'ring03_L_zooPivot': ((67.63197270277966, 95.93355389260422, 3.5718250832638683),
                          (12.518758195691056, -7.834457241348952, -82.2370519335734)),
    'pinkyMetacarpal_L_zooPivot': ((59.4042827886153, 109.12226784426319, -1.4334938583376347),
                                   (6.845347375956711, -21.188970230447925, -47.399737202251195)),
    'pinky01_L_zooPivot': ((64.02501714794985, 103.01749972290341, -0.1589174599652945),
                           (-8.141662942281773, -4.585939424351231, -57.508268466702525)),
    'pinky02_L_zooPivot': ((65.9371278501222, 100.01513108158649, 0.12659784151445624),
                           (-7.227625577962218, -5.926531640530045, -67.4601866531441)),
    'pinky03_L_zooPivot': ((67.0754786585604, 97.2723014326283, 0.43487358332687565),
                           (-6.091671045106676, -7.089214251313629, -77.4571219726718)),
    'thigh_L_zooPivot': ((9.00580960969279, 95.29984073270498, -0.5300275251856637),
                         (-184.36881443094111, 1.6583792624394154, -84.09299961593521)),
    'knee_L_zooPivot': ((13.37398983204935, 53.080284743625995, -1.7589042794896512),
                        (-184.42175015571328, 9.018479545553753, -84.66078811580697)),
    'ankle_L_zooPivot': ((17.07625502095665, 13.465861257241372, -8.073708919254647),
                         (84.17796614650022, -51.569830774569546, -85.43314859532005)),
    'ball_L_zooPivot': ((17.908687863364243, 3.044273721959513, 5.102682363656156),
                        (81.74667411865916, -71.82282328926767, -82.15328229435607)),
    'toe_L_zooPivot': ((18.328230584437332, 1.6964207816272392e-12, 14.461971761173844),
                       (81.74667411865924, -71.82282328926759, -82.15328229435606)),
    'footBankOuterL_zooPivot': ((23.998446862815264, 0.0, 0.8589934064913596),
                                (-3.8720056315866516e-13, 3.6149189510354676, 3.2331202327306844e-14)),
    'footBankInnerL_zooPivot': ((12.320348405775583, -4.014566457044566e-13, 1.3454617068578436),
                                (-3.8720056315866516e-13, 3.6149189510354676, 3.2331202327306844e-14)),
    'heelPivotL_zooPivot': ((17.22235540387797, -5.364597654988756e-13, -14.351869515995025),
                            (-3.8720056315866516e-13, 3.6149189510354676, 3.2331202327306844e-14))}

JOINT_NAMES = ['hive:spine_M_00_jnt', 'hive:spine_M_05_jnt', 'hive:head_M_neck_jnt', 'hive:head_M_head_jnt',
               'hive:clavicle_L_00_jnt', 'hive:arm_L_shldr_jnt', 'hive:arm_L_elbow_jnt', 'hive:arm_L_wrist_jnt',
               'hive:finger_thumb_L_00_jnt', 'hive:finger_thumb_L_01_jnt', 'hive:finger_thumb_L_02_jnt',
               'hive:finger_pointer_L_00_jnt', 'hive:finger_pointer_L_01_jnt', 'hive:finger_pointer_L_02_jnt',
               'hive:finger_pointer_L_03_jnt', 'hive:finger_middle_L_00_jnt', 'hive:finger_middle_L_01_jnt',
               'hive:finger_middle_L_02_jnt', 'hive:finger_middle_L_03_jnt', 'hive:finger_ring_L_00_jnt',
               'hive:finger_ring_L_01_jnt', 'hive:finger_ring_L_02_jnt', 'hive:finger_ring_L_03_jnt',
               'hive:finger_pinky_L_00_jnt', 'hive:finger_pinky_L_01_jnt', 'hive:finger_pinky_L_02_jnt',
               'hive:finger_pinky_L_03_jnt', 'hive:leg_L_upr_jnt', 'hive:leg_L_knee_jnt', 'hive:leg_L_foot_jnt',
               'hive:leg_L_ball_jnt']

LRA_JOINTS = ['hive:finger_thumb_L_00_jnt', 'hive:finger_pointer_L_00_jnt', 'hive:finger_middle_L_00_jnt',
              'hive:finger_ring_L_00_jnt', 'hive:finger_pinky_L_00_jnt', 'hive:head_M_neck_jnt']

LOCATOR_TEMPLATE_GRP = "locatorCurveTemplates_grp"
LOCATOR_PIVOTS_GRP = "locatorPivots_grp"

MESH_VERT_COUNT = 7387  # The number of vertices in the default skin proxy mesh

BIPED_ORDER_SPINE = [K_SPLINE_SPINE_BASE, K_SPLINE_SPINE_TOP, K_NECK_BASE, K_HEAD]
BIPED_ORDER_LEG = [K_THIGH_L, K_KNEE_L, K_ANKLE_L, K_BALL_L, K_FOOT_TIP_L, K_FOOTBANK_OUTER_L, K_FOOTBANK_INNER_L]
BIPED_ORDER_ARM = [K_CLAVICLE_L, K_UPPERARM_L, K_ELBOW_L, K_WRIST_L]
BIPED_ORDER_THUMB = [K_THUMB00_L, K_THUMB01_L, K_THUMB02_L]
BIPED_ORDER_POINTER = [K_POINTERMETA_L, K_POINTER00_L, K_POINTER01_L, K_POINTER02_L]
BIPED_ORDER_MIDDLE = [K_MIDDLEMETA_L, K_MIDDLE00_L, K_MIDDLE01_L, K_MIDDLE02_L]
BIPED_ORDER_RING = [K_RINGMETA_L, K_RING00_L, K_RING01_L, K_RING02_L]
BIPED_ORDER_PINKY = [K_PINKYMETA_L, K_PINKY00_L, K_PINKY01_L, K_PINKY02_L]

BIPED_PIV_ORDER_UI = [BIPED_ORDER_SPINE, BIPED_ORDER_LEG, BIPED_ORDER_ARM, BIPED_ORDER_THUMB, BIPED_ORDER_POINTER,
                      BIPED_ORDER_MIDDLE, BIPED_ORDER_RING, BIPED_ORDER_PINKY]
SECTIONS_UI = ["Head/Spine", "Leg Pivots", "Arm", "Finger Thumb", "Finger Pointer", "Finger Middle", "Finger Ring",
               "Finger Pinky"]
