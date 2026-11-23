"""Generate Annalisa's Phase 1 hollow tube mesh with Gmsh.

The delivered meshes are already in ``meshes/``. This script preserves her
geometry and meshing parameters while making output paths explicit.
"""

from pathlib import Path


def generate_tube_mesh(
    output_dir: str = "meshes", *, fine: bool = False, overwrite: bool = False
) -> None:
    """Write a tetrahedral VTK, surface STL, and native Gmsh mesh.

    ``fine=False`` uses Annalisa's 0.2–0.8 mm element size range; ``fine=True``
    uses 0.1–0.4 mm. Existing files are protected unless overwrite is requested.
    """
    import gmsh

    destination = Path(output_dir).expanduser().resolve()
    suffix = "_fine" if fine else ""
    files = (
        destination / f"tube_volumetric{suffix}.vtk",
        destination / f"tube_surface{suffix}.stl",
        destination / f"tube_mesh{suffix}.msh",
    )
    existing = [path for path in files if path.exists()]
    if existing and not overwrite:
        raise FileExistsError(
            "Refusing to replace existing meshes: "
            + ", ".join(str(path) for path in existing)
        )
    destination.mkdir(parents=True, exist_ok=True)

    gmsh.initialize()
    try:
        gmsh.model.add("RobotTubo")
        length_mm = 100.0
        outer_radius_mm = 1.93 / 2.0
        inner_radius_mm = 1.49 / 2.0
        outer = gmsh.model.occ.addCylinder(
            0, 0, 0, 0, 0, length_mm, outer_radius_mm
        )
        inner = gmsh.model.occ.addCylinder(
            0, 0, 0, 0, 0, length_mm, inner_radius_mm
        )
        gmsh.model.occ.cut([(3, outer)], [(3, inner)])
        gmsh.model.occ.synchronize()

        minimum, maximum = (0.1, 0.4) if fine else (0.2, 0.8)
        gmsh.option.setNumber("Mesh.MeshSizeMin", minimum)
        gmsh.option.setNumber("Mesh.MeshSizeMax", maximum)
        gmsh.option.setNumber("Mesh.Algorithm", 6)
        gmsh.option.setNumber("Mesh.Algorithm3D", 10)
        gmsh.model.mesh.generate(3)

        element_types, element_tags, _ = gmsh.model.mesh.getElements(3)
        tetrahedra = sum(
            len(tags)
            for kind, tags in zip(element_types, element_tags)
            if gmsh.model.mesh.getElementProperties(kind)[0].startswith("Tetrahedron")
        )
        if tetrahedra == 0:
            raise RuntimeError("Gmsh produced no tetrahedra for the tube volume")

        for path in files:
            gmsh.write(str(path))
    finally:
        gmsh.finalize()

    print(f"Generated {tetrahedra} tetrahedra in {destination}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", default="meshes/regenerated",
        help="Destination directory (default: meshes/regenerated)",
    )
    parser.add_argument("--fine", action="store_true", help="Generate the fine mesh")
    parser.add_argument(
        "--overwrite", action="store_true", help="Replace existing outputs"
    )
    args = parser.parse_args()
    generate_tube_mesh(args.output_dir, fine=args.fine, overwrite=args.overwrite)
