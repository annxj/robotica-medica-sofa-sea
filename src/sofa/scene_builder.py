"""
Costruzione della scena fisica del robot continuo 
Funzione pubblica:
    tube, cable, tip = build_robot(rootNode, path, config)

La funzione costruisce:
- Tube: mesh volumetrica tetraedrica e modello FEM;
- BoxROI + FixedProjectiveConstraint per bloccare Z = 0 ... 40 mm;
- Visu: STL visuale collegato al FEM da BarycentricMapping;
- TendonGuides + Cable: guide nella parete anulare + MechanicalObject e
  CableConstraint alla quota nominale y_t = +0.60 mm nel lume;
- tip: riferimento che legge il centro della sezione distale dal MechanicalObject
  del TUBO, non dal cavo.

"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping, Sequence
import math
import warnings


# ---------------------------------------------------------------------------
# Lettura e controllo configurazione
# ---------------------------------------------------------------------------

def _section(config: Mapping[str, Any], key: str) -> Mapping[str, Any]:
    value = config.get(key, {})
    if not isinstance(value, Mapping):
        raise TypeError(f"La sezione config['{key}'] deve essere un oggetto/dizionario.")
    return value


def _number(section: Mapping[str, Any], key: str, default: float) -> float:
    value = section.get(key, default)
    try:
        result = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"Parametro '{key}' non numerico: {value!r}") from exc
    if not math.isfinite(result):
        raise ValueError(f"Parametro '{key}' non finito: {result!r}")
    return result


def _read_project_config(config_path: Path) -> dict[str, Any]:
    import json

    if not config_path.is_file():
        raise FileNotFoundError(f"File di configurazione non trovato: {config_path}")
    with config_path.open("r", encoding="utf-8") as stream:
        data = json.load(stream)
    if not isinstance(data, dict):
        raise TypeError("project_config.json deve contenere un oggetto JSON.")
    return data


def _resolve_mesh_dir(path: str | Path) -> Path:
    """
    Accetta sia:
    - il percorso diretto della cartella meshes;
    - la root del repository, se contiene una sottocartella meshes.
    """
    root = Path(path).expanduser().resolve()
    candidates = [root, root / "meshes"]
    for candidate in candidates:
        if ((candidate / "tube_volumetric.vtk").is_file()
                and (candidate / "tube_surface.stl").is_file()):
            return candidate
    expected = "\n".join(f"  - {p}" for p in candidates)
    raise FileNotFoundError(
        "Non trovo entrambe le mesh richieste da Anna.\n"
        "Annalisa deve consegnare tube_volumetric.vtk e tube_surface.stl.\n"
        f"Cartelle controllate:\n{expected}"
    )


def _geometry_and_material(config: Mapping[str, Any]) -> dict[str, float]:
    geometry = _section(config, "geometry")
    material = _section(config, "material")

    values = {
        "outer_diameter_mm": _number(geometry, "outer_diameter_mm", 1.93),
        "inner_diameter_mm": _number(geometry, "inner_diameter_mm", 1.49),
        "total_length_mm": _number(geometry, "total_length_mm", 100.0),
        "rigid_length_mm": _number(geometry, "rigid_length_mm", 40.0),
        "flexible_length_mm": _number(geometry, "flexible_length_mm", 60.0),
        "tendon_offset_y_mm": _number(geometry, "tendon_offset_y_mm", 0.60),
        "young_load_mpa": _number(material, "young_load_mpa", 77000.0),
        "poisson_ratio": _number(material, "poisson_ratio", 0.33),
    }

    ro = values["outer_diameter_mm"] / 2.0
    ri = values["inner_diameter_mm"] / 2.0
    if not (ro > ri > 0.0):
        raise ValueError("Geometria non valida: serve OD > ID > 0.")
    if values["total_length_mm"] <= 0.0:
        raise ValueError("Lunghezza totale deve essere positiva.")
    if not (0.0 < values["rigid_length_mm"] < values["total_length_mm"]):
        raise ValueError("L_rigid deve essere compresa tra 0 e L_tot.")
    if values["young_load_mpa"] <= 0.0:
        raise ValueError("Il modulo di Young deve essere positivo.")
    if not (0.0 < values["poisson_ratio"] < 0.5):
        raise ValueError("Il coefficiente di Poisson deve essere tra 0 e 0.5.")

    computed_flex = values["total_length_mm"] - values["rigid_length_mm"]
    if abs(computed_flex - values["flexible_length_mm"]) > 1e-6:
        warnings.warn(
            "L_flex in config non coincide con L_tot - L_rigid. "
            "Verrà usata la geometria L_tot/L_rigid.",
            RuntimeWarning,
        )

    computed_wall = ro - ri
    declared_wall = _number(geometry, "wall_thickness_mm", computed_wall)
    if abs(computed_wall - declared_wall) > 1e-6:
        warnings.warn(
            f"Spessore calcolato {computed_wall:.4f} mm diverso da "
            f"wall_thickness_mm={declared_wall:.4f} mm.",
            RuntimeWarning,
        )
    return values


# ---------------------------------------------------------------------------
# Massa: conversione coerente con la convenzione mm-N-s del progetto
# ---------------------------------------------------------------------------

def estimate_tube_mass(config: Mapping[str, Any]) -> dict[str, float]:
    """
    Stima la massa del tubo da densità e volume cilindrico anulare.

    Se si usano mm, N, s, l'unità di massa derivata è N*s^2/mm = 1000 kg.
    UniformMass.totalMass riceve quindi m[kg] / 1000.

    La densità 6.45e-6 kg/mm^3 è riportata dal glossario come riferimento:
    il gruppo deve confermarla prima dei risultati dinamici definitivi.
    """
    values = _geometry_and_material(config)
    material = _section(config, "material")

    density = material.get(
        "density_kg_per_mm3_reference",
        material.get("density_kg_per_mm3"),
    )
    if density is None:
        raise ValueError(
            "Manca material.density_kg_per_mm3_reference (o density_kg_per_mm3). "
            "Concordare la densità con il gruppo/docente e aggiungerla a "
            "config/project_config.json."
        )
    density = float(density)
    if not math.isfinite(density) or density <= 0.0:
        raise ValueError("La densità di riferimento deve essere positiva e finita.")

    ro = values["outer_diameter_mm"] / 2.0
    ri = values["inner_diameter_mm"] / 2.0
    length = values["total_length_mm"]

    volume_mm3 = math.pi * (ro**2 - ri**2) * length
    mass_kg = density * volume_mm3
    total_mass_sofa_units = mass_kg / 1000.0

    return {
        "volume_mm3": volume_mm3,
        "density_kg_per_mm3": density,
        "mass_kg": mass_kg,
        "total_mass_sofa_units": total_mass_sofa_units,
    }


# ---------------------------------------------------------------------------
# Riferimento alla punta FEM
# ---------------------------------------------------------------------------

@dataclass
class FEMTipReference:
    """
    Riferimento alla sezione distale del tubo FEM.

    Va interrogato dopo l'inizializzazione SOFA. La posizione è il centroide
    dei nodi FEM la cui coordinata Z di riposo è entro z_tolerance_mm da Zmax.
    """
    mechanical_object: Any
    z_tolerance_mm: float = 0.25

    def _positions(self, data_name: str) -> Sequence[Sequence[float]]:
        data = getattr(self.mechanical_object, data_name, None)
        if data is None:
            raise RuntimeError(
                f"Il MechanicalObject non espone il dato '{data_name}'."
            )
        value = getattr(data, "value", data)
        try:
            return list(value)
        except TypeError as exc:
            raise RuntimeError(
                f"Il dato '{data_name}' non è leggibile come lista di punti."
            ) from exc

    def node_indices(self) -> list[int]:
        rest = self._positions("rest_position")
        if not rest:
            raise RuntimeError(
                "Coordinate di riposo non inizializzate. "
                "Chiamare get_position() dopo l'inizializzazione SOFA."
            )
        z_max = max(float(point[2]) for point in rest)
        ids = [
            i for i, point in enumerate(rest)
            if float(point[2]) >= z_max - self.z_tolerance_mm
        ]
        if not ids:
            raise RuntimeError("Non trovo nodi FEM sulla sezione distale.")
        return ids

    def get_position(self) -> tuple[float, float, float]:
        current = self._positions("position")
        ids = self.node_indices()
        if not current:
            raise RuntimeError("Coordinate correnti FEM non inizializzate.")
        n = float(len(ids))
        return tuple(
            sum(float(current[i][axis]) for i in ids) / n
            for axis in range(3)
        )

    @property
    def position(self) -> tuple[float, float, float]:
        """Alias leggibile per chi preferisce tip.position."""
        return self.get_position()


def get_tip_position(tube_or_tip: Any) -> tuple[float, float, float]:
    """
    Restituisce X,Y,Z della punta reale del tubo FEM.
    Accetta direttamente FEMTipReference oppure il nodo Tube.
    """
    if isinstance(tube_or_tip, FEMTipReference):
        return tube_or_tip.get_position()

    dofs = getattr(tube_or_tip, "dofs", None)
    if dofs is None:
        raise TypeError("Passare il nodo Tube oppure un FEMTipReference.")
    return FEMTipReference(dofs).get_position()


# ---------------------------------------------------------------------------
# Costruzione del tubo e del cavo
# ---------------------------------------------------------------------------

def build_robot(rootNode: Any,
                path: str | Path,
                config: Mapping[str, Any],
                with_collision: bool = False):
    """
    Costruisce la parte fisica del robot per la Fase 1.

    Args:
        rootNode: nodo root creato da Josh in main.py.
        path: root del repository oppure cartella meshes.
        config: dizionario caricato da config/project_config.json.
        with_collision: non usare in Fase 1; la collision pipeline è Fase 3.

    Returns:
        tube: nodo SOFA del tubo FEM;
        cable: nodo SOFA del percorso tendine + CableConstraint;
        tip: FEMTipReference per leggere la punta dal tubo FEM.
    """
    if with_collision:
        raise NotImplementedError(
            "La collision pipeline e gli ostacoli appartengono alla Fase 3. "
            "In Fase 1 chiamare build_robot(..., with_collision=False)."
        )
    if not isinstance(config, Mapping):
        raise TypeError("config deve essere un dizionario caricato dal JSON.")

    values = _geometry_and_material(config)
    mass_info = estimate_tube_mass(config)
    mesh_dir = _resolve_mesh_dir(path)

    ro = values["outer_diameter_mm"] / 2.0
    ri = values["inner_diameter_mm"] / 2.0
    length = values["total_length_mm"]
    rigid_length = values["rigid_length_mm"]
    tendon_y = values["tendon_offset_y_mm"]

    # 1. Nodo Tube e integrazione meccanica.
    tube = rootNode.addChild("Tube")
    tube.addObject(
        "EulerImplicitSolver",
        name="odesolver",
        rayleighMass=0.1,
        rayleighStiffness=0.1,
    )
    tube.addObject(
        "SparseLDLSolver",
        name="linearSolver",
        template="CompressedRowSparseMatrixMat3x3d",
    )

    # 2. Mesh volumetrica, topologia tetraedrica e gradi di libertà.
    tube.addObject(
        "MeshVTKLoader",
        name="loader",
        filename=str(mesh_dir / "tube_volumetric.vtk"),
        scale3d=[1.0, 1.0, 1.0],
        printLog=True,
    )
    tube.addObject(
        "TetrahedronSetTopologyContainer",
        name="tetraTopology",
        src="@loader",
        checkTopology=True,
    )
    tube.addObject(
        "TetrahedronSetGeometryAlgorithms",
        name="tetraGeometry",
        template="Vec3",
    )
    dofs = tube.addObject(
        "MechanicalObject",
        name="dofs",
        template="Vec3",
        src="@loader",
    )

    # 3. Massa coerente (riferimento densità glossario) e FEM Nitinol in carico.
    tube.addObject(
        "UniformMass",
        name="mass",
        totalMass=mass_info["total_mass_sofa_units"],
    )
    tube.addObject(
        "TetrahedronFEMForceField",
        name="FEM",
        template="Vec3",
        method="large",
        youngModulus=values["young_load_mpa"],
        poissonRatio=values["poisson_ratio"],
    )

    # 4. BoxROI sull'albero prossimale Z=0..40 mm.
    roi_box = [
        -ro - 1.0, -ro - 1.0, -1.0,
        ro + 1.0, ro + 1.0, rigid_length + 0.1,
    ]
    tube.addObject(
        "BoxROI",
        name="rigidShaftROI",
        template="Vec3",
        box=roi_box,
        position="@dofs.rest_position",
        drawBoxes=True,
        drawSize=2.0,
        computeTetrahedra=False,
        computeTriangles=False,
        computeEdges=False,
    )
    tube.addObject(
        "FixedProjectiveConstraint",
        name="fixedShaft",
        template="Vec3",
        indices="@rigidShaftROI.indices",
        showObject=True,
    )

    # Correzione per vincoli lagrangiani (CableConstraint).
    tube.addObject(
        "GenericConstraintCorrection",
        name="constraintCorrection",
    )

    # 5. Modello visuale STL mappato esplicitamente sul FEM.
    visu = tube.addChild("Visu")
    visu.addObject(
        "MeshSTLLoader",
        name="surfaceLoader",
        filename=str(mesh_dir / "tube_surface.stl"),
        printLog=True,
    )
    visual_model = visu.addObject(
        "OglModel",
        name="visualModel",
        src="@surfaceLoader",
        color=[0.72, 0.80, 0.90, 1.0],
    )
    visu.addObject(
        "BarycentricMapping",
        name="visualMapping",
        input="@../dofs",
        output="@visualModel",
    )

    # 6. Nodo Cable e CableConstraint in displacement.
    # Modalità supportate per tendon.mapping_mode:
    # - "lumen_guides" (default): mantiene y_t = +0.60 mm nel lume e trasferisce
    #   trazione e reazioni tramite guide trasversali ancorate a r_m = (ri+ro)/2.
    # - "barycentric_wall": diagnostica con cavo spostato nella parete [ri, ro].
    # - "deferred" / "none": cavo non accoppiato meccanicamente al tubo.
    cable_cfg = _section(config, "tendon")
    mapping_mode = str(cable_cfg.get("mapping_mode", "lumen_guides")).lower()
    routing_step = _number(cable_cfg, "routing_step_mm", 10.0)
    if routing_step <= 0.0:
        raise ValueError("tendon.routing_step_mm deve essere positivo.")

    if mapping_mode == "barycentric_wall":
        if "mapping_y_mm" not in cable_cfg:
            raise ValueError(
                "Per mapping_mode='barycentric_wall' specificare "
                "tendon.mapping_y_mm."
            )
        routing_y = float(cable_cfg["mapping_y_mm"])
        radial_position = abs(routing_y)
        if not (ri < radial_position < ro):
            raise ValueError(
                f"mapping_y_mm={routing_y:.3f} mm non è nella parete del tubo "
                f"(raggio interno {ri:.3f} mm, esterno {ro:.3f} mm)."
            )
        warnings.warn(
            "È attivo il mapping del cavo nella PARETE. Questa scelta non "
            "rispetta l'offset nominale y_t=0.60 mm nel lume.",
            RuntimeWarning,
        )
    elif mapping_mode in ("lumen_guides", "deferred", "none"):
        routing_y = tendon_y
        if abs(routing_y) >= ro:
            raise ValueError(
                f"tendon_offset_y_mm={routing_y:.3f} mm eccede il raggio "
                f"esterno del tubo ({ro:.3f} mm)."
            )
    else:
        raise ValueError(
            "tendon.mapping_mode ammesso: 'lumen_guides', 'barycentric_wall' "
            "oppure 'deferred'."
        )

    # Indici ordinati dalla punta distale (Z=100 mm) verso la base (Z=10 mm);
    # pullPoint è il riferimento prossimale fisso a Z=0 mm.
    route_z = []
    z = length
    while z > 0.0 + 1e-9:
        route_z.append(round(z, 8))
        z -= routing_step
    if not route_z:
        raise ValueError("Percorso del tendine vuoto.")

    routing_points = [[0.0, routing_y, z_value] for z_value in route_z]

    cable_mapping = None
    if mapping_mode == "lumen_guides":
        # Raggio medio della parete anulare (strettamente dentro i tetraedri).
        mid_wall_r = 0.5 * (ri + ro)
        if abs(routing_y) >= mid_wall_r:
            raise ValueError(
                f"|tendon_offset_y_mm|={abs(routing_y):.3f} mm deve essere "
                f"inferiore al raggio medio della parete ({mid_wall_r:.3f} mm)."
            )

        guide_points = []
        guide_edges = []
        for idx, z_value in enumerate(route_z):
            # Piccolo margine interno rispetto ai piani estremi Z=0 e Z=L per
            # garantire appartenenza stretta ai tetraedri in BarycentricMapping.
            z_safe = min(max(z_value, 1e-4), length - 1e-4)
            guide_points.append([0.0, -mid_wall_r, z_safe])
            guide_points.append([0.0, +mid_wall_r, z_safe])
            guide_edges.append([2 * idx, 2 * idx + 1])

        guides = tube.addChild("TendonGuides")
        guides.addObject(
            "EdgeSetTopologyContainer",
            name="guideTopology",
            edges=guide_edges,
        )
        guides.addObject(
            "MechanicalObject",
            name="guideDofs",
            template="Vec3",
            position=guide_points,
        )
        guides.addObject(
            "BarycentricMapping",
            name="guideMapping",
            input="@../dofs",
            output="@guideDofs",
            mapForces=True,
            mapMasses=False,
        )

    cable = tube.addChild("Cable")
    cable.addObject(
        "MechanicalObject",
        name="dofs",
        template="Vec3",
        position=routing_points,
        showObject=True,
        showObjectScale=0.20,
        showColor=[0.95, 0.25, 0.15, 1.0],
    )
    cable.addObject(
        "CableConstraint",
        name="aCableActuator",
        template="Vec3",
        indices=list(range(len(routing_points))),
        pullPoint=[0.0, routing_y, 0.0],
        hasPullPoint=True,
        valueType="displacement",
        value=[0.0],
        minForce=0.0,
        drawPullPoint=True,
        drawPoints=True,
    )

    if mapping_mode == "lumen_guides":
        cable_mapping = cable.addObject(
            "BarycentricMapping",
            name="cableMapping",
            input="@../TendonGuides/guideDofs",
            output="@dofs",
            mapForces=True,
            mapMasses=False,
        )
    elif mapping_mode == "barycentric_wall":
        cable_mapping = cable.addObject(
            "BarycentricMapping",
            name="cableMapping",
            input="@../dofs",
            output="@dofs",
            mapForces=True,
            mapMasses=False,
        )
    else:
        warnings.warn(
            "Cavo creato in modalità 'deferred': mapping FEM non attivato.",
            RuntimeWarning,
        )

    tip = FEMTipReference(dofs)

    # Log iniziale: conteggio ROI e stato componenti saranno letti dopo init.
    print("[Anna/scene_builder] Struttura Tube creata.")
    print(f"[Anna/scene_builder] Volume mesh: {mesh_dir / 'tube_volumetric.vtk'}")
    print(f"[Anna/scene_builder] Surface mesh: {mesh_dir / 'tube_surface.stl'}")
    print(
        f"[Anna/scene_builder] D={values['outer_diameter_mm']:.3f} mm, "
        f"ID={values['inner_diameter_mm']:.3f} mm, "
        f"L={length:.1f} mm, L_rigid={rigid_length:.1f} mm."
    )
    print(
        f"[Anna/scene_builder] Mass estimate: V={mass_info['volume_mm3']:.4f} mm^3, "
        f"m={mass_info['mass_kg']:.6e} kg, "
        f"UniformMass.totalMass={mass_info['total_mass_sofa_units']:.6e} "
        "(unità derivate mm-N-s)."
    )
    print(
        f"[Anna/scene_builder] FEM impostato: E_load={values['young_load_mpa']:.1f} MPa, "
        f"nu={values['poisson_ratio']:.3f}, method='large'."
    )
    print(
        f"[Anna/scene_builder] CableConstraint: valueType='displacement', "
        f"y_t={routing_y:.3f} mm, {len(routing_points)} punti (distale -> prossimale)."
    )
    print(
        f"[Anna/scene_builder] Cable mapping ({mapping_mode}): "
        + ("ATTIVO" if cable_mapping is not None else "NON ATTIVO")
    )

    return tube, cable, tip


# ---------------------------------------------------------------------------
# Controlli da eseguire DOPO Sofa.Simulation.init(rootNode)
# ---------------------------------------------------------------------------

def _data_value(component: Any, data_name: str):
    data = getattr(component, data_name, None)
    if data is None:
        return None
    return getattr(data, "value", data)


def _component_state(component: Any) -> str:
    state = _data_value(component, "componentState")
    return str(state) if state is not None else "non leggibile"


def validate_robot_after_init(tube: Any, tip: FEMTipReference) -> dict[str, Any]:
    """
    Da chiamare dopo l'inizializzazione della scena SOFA.
    Stampa stato FEM/topologia, numero nodi ROI e coordinate punta.

    Esempio nel main di Josh, dopo init (se eseguito fuori da runSofa):
        report = validate_robot_after_init(tube, tip)
    """
    fem = getattr(tube, "FEM", None)
    loader = getattr(tube, "loader", None)
    topology = getattr(tube, "tetraTopology", None)
    roi = getattr(tube, "rigidShaftROI", None)
    guides = getattr(tube, "TendonGuides", None)
    cable = getattr(tube, "Cable", None)

    fem_state = _component_state(fem) if fem is not None else "mancante"
    loader_state = _component_state(loader) if loader is not None else "mancante"
    guide_map_state = (
        _component_state(getattr(guides, "guideMapping", None))
        if guides is not None else "non presente"
    )
    cable_map_state = (
        _component_state(getattr(cable, "cableMapping", None))
        if cable is not None else "non presente"
    )

    tetrahedra = _data_value(topology, "tetrahedra") if topology is not None else None
    roi_indices = _data_value(roi, "indices") if roi is not None else None

    n_tetra = len(tetrahedra) if tetrahedra is not None else 0
    n_fixed = len(roi_indices) if roi_indices is not None else 0
    tip_xyz = tip.get_position()

    report = {
        "loader_state": loader_state,
        "fem_state": fem_state,
        "guide_mapping_state": guide_map_state,
        "cable_mapping_state": cable_map_state,
        "n_tetrahedra": n_tetra,
        "n_fixed_nodes": n_fixed,
        "tip_xyz_mm": tip_xyz,
    }

    print("[Anna/scene_builder] ===== VERIFICA DOPO INIT =====")
    print(f"MeshVTKLoader componentState: {loader_state}")
    print(f"TetrahedronFEMForceField componentState: {fem_state}")
    print(f"Guide BarycentricMapping state: {guide_map_state}")
    print(f"Cable BarycentricMapping state: {cable_map_state}")
    print(f"Numero tetraedri: {n_tetra}")
    print(f"Nodi selezionati dalla BoxROI: {n_fixed}")
    print(
        f"Punta FEM: X={tip_xyz[0]:.4f} mm, "
        f"Y={tip_xyz[1]:.4f} mm, Z={tip_xyz[2]:.4f} mm"
    )

    if n_tetra <= 0:
        raise RuntimeError(
            "La mesh caricata non contiene tetraedri: controllare "
            "tube_volumetric.vtk e l'export di Annalisa."
        )
    if n_fixed <= 0:
        raise RuntimeError(
            "BoxROI non ha selezionato nodi: controllare asse Z, coordinate "
            "mesh e limiti del box."
        )
    if "Invalid" in fem_state or "Invalid" in loader_state:
        raise RuntimeError(
            "Loader o FEM sono Invalid. Controllare plugin, loader, topologia "
            "e messaggi della console SOFA."
        )
    if "Invalid" in guide_map_state or "Invalid" in cable_map_state:
        raise RuntimeError(
            "Uno dei mapping del tendine è Invalid. Verificare la "
            "coerenza delle coordinate della mesh con project_config.json."
        )
    return report


# ---------------------------------------------------------------------------
# Fase 3: funzioni non implementate qui intenzionalmente
# ---------------------------------------------------------------------------

def setup_collision_pipeline(rootNode: Any, friction_coefficient: float):
    """Da implementare nella Fase 3, non chiamare durante la Fase 1."""
    raise NotImplementedError(
        "La collision pipeline è assegnata ad Anna nella Fase 3."
    )


def add_obstacle(rootNode: Any, mesh_dir: str | Path,
                 obstacle_type: str, config: Mapping[str, Any]):
    """Da implementare nella Fase 3, non chiamare durante la Fase 1."""
    raise NotImplementedError(
        "Gli ostacoli rigido e soffice sono assegnati ad Anna nella Fase 3."
    )
