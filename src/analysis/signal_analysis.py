"""TODO: calcolo isteresi H e stabilità contatto dai CSV SOFA.

Responsabile: Annapia. Non extrapolare tra rami di carico/scarico; verificare
che la finestra di mantenimento contenga cinque secondi dopo l'assestamento.
"""


def compute_hysteresis(csv_path: str) -> float:
    raise NotImplementedError("Implementare H sui rami di carico/scarico")


def check_contact_stability(csv_path: str) -> dict:
    raise NotImplementedError("Implementare stabilità negli ultimi 5 s")
