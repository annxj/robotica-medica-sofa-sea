"""TODO: dashboard real-time Matplotlib non bloccante.

Responsabile: Josh. Mostrare X, Y, ΔY e u, T, ΔL_s, F_contatto.
"""


class LivePlotter:
    def __init__(self, enabled: bool = True):
        raise NotImplementedError("Implementare LivePlotter")

    def update(self, sample: dict) -> None:
        raise NotImplementedError
