import pymel.core as pm


pm.connectAttr('ikRPsolver.message', 'IK_Chain_ikHandle.ikSolver', f=True)
pm.setAttr("IK_Chain_ikHandle.poleVectorX", 0)
pm.setAttr("IK_Chain_ikHandle.poleVectorY", 0)
pm.setAttr("IK_Chain_ikHandle.poleVectorZ", -1)

