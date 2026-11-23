import Sofa
import numpy as np

# Cambia questo nome tra 'tube_mesh.msh' e 'tube_mesh_fine.msh'
MESH_FILE = "tube_mesh.msh"

class TipMonitor(Sofa.Core.Controller):
    def __init__(self, mo, tip_indices):
        super().__init__()
        self.mo = mo
        self.tip_indices = tip_indices
        self.initial_pos = np.copy(mo.position.value[tip_indices])

    def onAnimateEndEvent(self, event):
        current_pos = self.mo.position.value[self.tip_indices]
        disp = np.linalg.norm(current_pos - self.initial_pos, axis=1).mean()
        Sofa.msg_info("TipMonitor", f"[{MESH_FILE}] Spostamento medio punta: {disp:.4f} mm")

def createScene(rootNode):
    rootNode.addObject("RequiredPlugin", pluginName=[
        "Sofa.Component.IO.Mesh",
        "Sofa.Component.Topology.Container.Dynamic",
        "Sofa.Component.StateContainer",
        "Sofa.Component.Mass",
        "Sofa.Component.SolidMechanics.FEM.Elastic",
        "Sofa.Component.Engine.Select",
        "Sofa.Component.Constraint.Projective",
        "Sofa.Component.MechanicalLoad",
        "Sofa.Component.ODESolver.Backward",
        "Sofa.Component.LinearSolver.Direct",
        "Sofa.Component.Mapping.Linear",
        "Sofa.Component.Visual",
        "Sofa.GL.Component.Rendering3D"
    ])

    rootNode.addObject("DefaultAnimationLoop")
    rootNode.addObject("VisualStyle", displayFlags="showBehaviorModels showForceFields")
    rootNode.gravity = [0, 0, 0]
    rootNode.dt = 0.01

    tube = rootNode.addChild("Tube")
    tube.addObject("EulerImplicitSolver", rayleighStiffness=0.1, rayleighMass=0.1)
    tube.addObject("SparseLDLSolver", template="CompressedRowSparseMatrixd")

    # Usiamo MeshGmshLoader sul file nativo .msh
    loader = tube.addObject("MeshGmshLoader", name="loader", filename=MESH_FILE)
    loader.init()

    tube.addObject("TetrahedronSetTopologyContainer", name="topo", position="@loader.position", tetrahedra="@loader.tetrahedra")
    tube.addObject("TetrahedronSetGeometryAlgorithms", template="Vec3d")
    mo = tube.addObject("MechanicalObject", name="dofs", position="@loader.position")
    mo.init()

    tube.addObject("UniformMass", totalMass=0.005)
    tube.addObject("TetrahedronFEMForceField", youngModulus=77000.0, poissonRatio=0.33, method="large")

    # Visualizzazione 3D del tubo
    visu = tube.addChild("Visual")
    visu.addObject("OglModel", src="@../topo", color=[0.3, 0.8, 1.0, 1.0])
    visu.addObject("BarycentricMapping")

    # Incastro sui primi 40 mm (z tra -0.1 e 40.0)
    fixed_roi = tube.addObject("BoxROI", name="fixedROI", box=[-2, -2, -0.1, 2, 2, 40.0])
    fixed_roi.init()
    tube.addObject("FixedProjectiveConstraint", indices="@fixedROI.indices")

    # Forza applicata in punta (z tra 99.0 e 100.1)
    tip_roi = tube.addObject("BoxROI", name="tipROI", box=[-2, -2, 99.0, 2, 2, 100.1])
    tip_roi.init()
    tube.addObject("ConstantForceField", indices="@tipROI.indices", totalForce=[0.0, 0.5, 0.0])

    rootNode.addObject(TipMonitor(mo, tip_roi.indices.value))
    return rootNode