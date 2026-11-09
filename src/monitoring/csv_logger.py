"""TODO: logger CSV per ogni simulazione.

Responsabile: Josh. Registrare tempo, scenario, parametri, u2, u1, ΔL_s,
T, X/Y/Z punta, ΔY, F_contatto e contact_active. Chiudere il file a fine run.
"""


class CsvLogger:
    def __init__(self, output_path: str):
        raise NotImplementedError("Implementare logger CSV")
