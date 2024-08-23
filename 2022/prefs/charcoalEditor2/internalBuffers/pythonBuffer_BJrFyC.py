import pymel.core as pm



def setDrivenKey(driver, driverValueList, driven, drivenValueList, cvType='linear'):
    """
    Set Driven Key utility
    :param driver: str, driver + driving attribute (ctrl.attr)
    :param driverValueList: list, value list
    :param driven: str, driven + driven attribute (ctrl.attr)
    :param drivenValueList: list, value list
    :param cvType: str, auto, clamped, fast, flat, linear, plateau, slow, spline, step, and stepnext
    :return:
    """
    for driverV, drivenV in zip(driverValueList, drivenValueList):
        pm.setDrivenKeyframe(driven, currentDriver=driver, driverValue=driverV, value=drivenV, inTangentType=cvType,
                             outTangentType=cvType)


pm.setAttr("L_Wing_cntrl.translateZ", -90)
L_wing_master_ctrl = pm.ls('L_Wing_cntrl')[-1]
R_wing_master_ctrl = pm.ls('R_Wing_cntrl')[-1]

all_connection = pm.listConnections(L_wing_master_ctrl.Wing, c=True)

for cnn in all_connection:
    source, anim_destination = cnn
    print(source, '  ---  ', anim_destination)
    R_anim_dest = str(anim_destination.name()).replace('_L', '_R').replace('L_', 'R_').replace('Y1', 'Y')
    try:
        pm.connectAttr(R_wing_master_ctrl.Wing, R_anim_dest + '.input')
    except:
        print('SKIP: ', R_anim_dest)
    
    
#setDrivenKey('R_Wing_cntrl.translateZ', [0, -90], 'R_Wing_cntrl.Wing', [0, 50])
pm.connectAttr('R_Wing_cntrl.translateZ', 'R_Wing_cntrl_Wing.input', f=True)
pm.setAttr("R_Wing_cntrl.translateZ", -90)