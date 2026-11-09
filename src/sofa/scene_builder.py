"""TODO: costruzione della scena fisica SOFA.

Responsabile: Anna. Implementare a piccoli passi e verificare ogni componente
nella versione SOFA effettivamente installata.
"""


def build_robot(root_node, mesh_dir: str, config: dict, with_collision: bool = False):
    """Costruisce Tube/FEM, vincolo prossimale, tendine e mapping.

    Restituire riferimenti espliciti a tubo, attuatore del cavo e punta FEM.
    La punta deve essere letta dal MechanicalObject del tubo, non dal cavo.
    """
    raise NotImplementedError("Implementare scena FEM SOFA")


def setup_collision_pipeline(root_node, friction_coefficient: float):
    """TODO: configurare broad/narrow phase e risposta d'attrito."""
    raise NotImplementedError("Implementare pipeline collisioni SOFA")


def add_obstacle(root_node, mesh_dir: str, obstacle_type: str, config: dict):
    """TODO: aggiungere ostacolo rigido o soffice con superficie di collisione."""
    raise NotImplementedError("Implementare ostacolo e mapping topologico")
