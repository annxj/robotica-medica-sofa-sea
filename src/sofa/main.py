"""SOFA scene entry point for Phase 1 integration (Josh).

Anna's ``build_robot`` returns (tube, cable, tip). Annapia's controller is
expected to accept those references as keyword arguments. The full scene needs
their implementation and Annalisa's meshes before it can be validated.
"""

from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_module(name, filename):
    spec = spec_from_file_location(name, filename)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import {filename}")
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def createScene(rootNode):
    rootNode.addObject(
        "RequiredPlugin",
        pluginName=[
            "SofaPython3",
            "SoftRobots",
            "Sofa.Component.AnimationLoop",
            "Sofa.Component.Constraint.Lagrangian.Correction",
            "Sofa.Component.Constraint.Lagrangian.Solver",
            "Sofa.Component.Constraint.Projective",
            "Sofa.Component.Engine.Select",
            "Sofa.Component.IO.Mesh",
            "Sofa.Component.LinearSolver.Direct",
            "Sofa.Component.Mapping.Linear",
            "Sofa.Component.Mass",
            "Sofa.Component.ODESolver.Backward",
            "Sofa.Component.SolidMechanics.FEM.Elastic",
            "Sofa.Component.StateContainer",
            "Sofa.Component.Topology.Container.Constant",
            "Sofa.Component.Topology.Container.Dynamic",
            "Sofa.Component.Visual",
            "Sofa.GL.Component.Rendering3D",
        ],
    )

    config_path = REPO_ROOT / "config" / "project_config.json"
    with config_path.open(encoding="utf-8") as stream:
        config = json.load(stream)

    rootNode.dt = float(config["simulation"]["dt_s"])
    rootNode.gravity = [0.0, 0.0, 0.0]  # Initial free-motion test.
    rootNode.addObject("FreeMotionAnimationLoop")
    rootNode.addObject(
        "BlockGaussSeidelConstraintSolver", tolerance=1e-5, maxIterations=100
    )

    builder = _load_module("project_scene_builder", REPO_ROOT / "src" / "sofa" / "scene_builder.py")
    controller_module = _load_module(
        "project_tendon_controller", REPO_ROOT / "src" / "control" / "tendon_controller.py"
    )
    tube, cable, tip = builder.build_robot(rootNode, REPO_ROOT, config)
    rootNode.addObject(
        controller_module.TendonController(
            name="ManualTendonController", tube=tube, cable=cable, tip=tip
        )
    )
    return rootNode
