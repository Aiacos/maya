from pxr import Usd, UsdGeom

def create_usd_skeleton_from_maya(maya_skeleton_data, usd_file_path):
    # Creare un nuovo stage USD
    stage = Usd.Stage.CreateNew(usd_file_path)

    # Creare un nuovo prim per lo scheletro
    skeleton = stage.DefinePrim("/skeleton")

    # Creare un nuovo prim per le joint dello scheletro
    joints = []
    for joint_name, joint_transform in maya_skeleton_data.items():
        joint = UsdGeom.Xform.Define(stage, f"{skeleton.GetPath()}/{joint_name}")
        joint.GetPrim().GetAttribute("xformOp:transform").Set(joint_transform)
        joints.append(joint.GetPath())

    # Aggiungere relazioni parent-child tra le joint
    for i in range(1, len(joints)):
        stage.DefineRelationship(joints[i - 1]).AddTarget(joints[i])

    # Salvare il file USD
    stage.GetRootLayer().Save()

    print(f"Scheletro definito in USD nel file: {usd_file_path}")

# Esempio di dati dello scheletro di Maya (nome della joint e trasformazione)
maya_skeleton_data = {
    "joint1": (1.0, 2.0, 3.0),
    "joint2": (4.0, 5.0, 6.0),
    "joint3": (7.0, 8.0, 9.0)
}




# Percorso del file USD in cui salvare lo scheletro
usd_file_path = "C:/Users/unilo/Desktop/Test_USD/skeleton_output.usda"

# Chiamata alla funzione per creare lo scheletro in USD
create_usd_skeleton_from_maya(maya_skeleton_data, usd_file_path)
