"""TODO: modello ridotto H(k) e identificazione least-squares.

Responsabile: Annalisa. Fit solo sui sette k di identificazione; mantenere
k=0.9 e 3.4 N/mm esclusivamente per validazione indipendente.
"""


def hysteresis_model(k, kt: float, f_h_spring: float, f_h_material: float, u_max: float):
    raise NotImplementedError("Implementare modello ridotto della traccia")


def identify_parameters(summary_csv: str):
    raise NotImplementedError("Implementare curve_fit e report dei residui")
