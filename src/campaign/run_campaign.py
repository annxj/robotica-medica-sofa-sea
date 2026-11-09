"""TODO: runner batch di simulazioni SOFA reali.

Responsabile: Josh. Ogni run deve avviare/inizializzare una scena SOFA,
passare i parametri al controller e verificare il risultato. Vietato generare
CSV sintetici per sostituire simulazioni non eseguite.
"""


def run_one_case(params: dict) -> dict:
    raise NotImplementedError("Collegare il runner all'eseguibile/API SOFA")


def run_campaign(cases: list[dict], output_dir: str = "data/raw") -> None:
    raise NotImplementedError("Implementare batch e campaign_manifest.csv")
