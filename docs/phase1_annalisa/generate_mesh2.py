import gmsh

gmsh.initialize()
gmsh.model.add("RobotTubo")

L = 100.0
R_out = 1.93 / 2.0
R_in = 1.49 / 2.0

outer = gmsh.model.occ.addCylinder(0, 0, 0, 0, 0, L, R_out) # crea un cilindro grande per l'esterno
inner = gmsh.model.occ.addCylinder(0, 0, 0, 0, 0, L, R_in) # crea un cilindro piccolo per l'interno

gmsh.model.occ.cut([(3, outer)], [(3, inner)]) # esegue l'operazione booleana richiesta , prende il cilindro grande e gli sottrae il piccolo
gmsh.model.occ.synchronize()

# Riduciamo la dimensione della mesh per rispettare lo spessore di 0.22 mm
gmsh.option.setNumber("Mesh.MeshSizeMin", 0.2)
gmsh.option.setNumber("Mesh.MeshSizeMax", 0.8)

# Algoritmi robusti per spessori sottili
gmsh.option.setNumber("Mesh.Algorithm", 6)    # Frontal-Delaunay (2D)
gmsh.option.setNumber("Mesh.Algorithm3D", 10) # HXT (3D)

# prende il tubo cavo e lo riempe di tetraedi 3D
gmsh.model.mesh.generate(3)

# salva il lavoro nei tre formati richiesti 
gmsh.write("tube_volumetric.vtk") # .vtk (il volume completo per la meccanica)
gmsh.write("tube_surface.stl") #  .stl (solo la "pelle" esterna per la visualizzazione)
gmsh.write("tube_mesh.msh") # .msh (il formato nativo di sicurezza richiesto).
gmsh.finalize()

print("Mesh generate con successo!")