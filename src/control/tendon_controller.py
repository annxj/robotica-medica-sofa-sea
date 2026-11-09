"""TODO: controller unico per SEA, tastiera e modalità automatiche.

Responsabile: Annapia. Convenzioni del glossario: u2=comando motore,
u1=spostamento tendine a valle della molla, ΔL_s=max(0, u2-u1).
"""

try:
    import Sofa.Core
except ImportError:  # Permette di importare il repository fuori da SOFA.
    Sofa = None


if Sofa is not None:
    class TendonController(Sofa.Core.Controller):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            raise NotImplementedError("Completare il controller SEA in ambiente SOFA")
else:
    class TendonController:
        def __init__(self, *args, **kwargs):
            raise RuntimeError("TendonController richiede SofaPython3 nell'ambiente SOFA")
