# Annalisa's Phase 1 mesh handoff

Copied from `~/Desktop/FASE1_ANNALISA_Creazione della mesh del tubo/` on
23 November 2026. The original Desktop folder was left unchanged.

## Files in the repository

- `meshes/tube_volumetric.vtk`, `tube_surface.stl`, and `tube_mesh.msh` are
  the standard mesh. `src/sofa/scene_builder.py` expects the VTK and STL at
  these exact paths.
- `meshes/fine/` contains the finer VTK, STL, and Gmsh mesh for comparison.
- This folder keeps Annalisa's original generator scripts, mesh images,
  convergence test scripts, and report.
- `src/geometry/generate_tube_mesh.py` implements the same standard and fine
  mesh settings as a reusable function and command-line script. Its default
  command-line destination is `meshes/regenerated` to protect the delivered
  files. Regenerated meshes may have different element counts across Gmsh
  versions.

## Checks performed during import

The standard VTK has 2,027 points and 6,069 tetrahedra; the fine VTK has
8,000 points and 24,018 tetrahedra. Both span Z = 0–100 mm and X/Y =
−0.965–0.965 mm. SOFA v26.06 loaded each VTK with an explicitly tetrahedral
topology and completed 1,000 batch steps without mesh errors.

The report states a tip displacement of 0.9009 mm for the standard mesh and
1.0205 mm for the fine mesh (13.28% difference). Those convergence simulations
were reported by Annalisa and were not rerun during this import.

The combined project scene is not yet validated: its current scene builder
uses all cell types from the mixed VTK as topology and reports inconsistent
edges/triangles. Its cable mapping also reports an unsupported edge topology.
Anna needs to resolve these scene issues, and Annapia's controller is still a
placeholder. The original VTK files themselves loaded successfully in the
isolated tetrahedral check.
