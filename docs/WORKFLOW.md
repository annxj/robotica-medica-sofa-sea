# Workflow, dipendenze e riunioni

## Fase 0 — Setup comune

**Obiettivo:** tutti riescono ad aprire una scena SOFA minima e a usare il repository.

**Insieme:** concordare versione SOFA, plugin, interprete Python, struttura delle cartelle, unità mm-N-s, convenzioni Git e modalità di scambio dei file. Ogni componente clona il repository e lancia la scena minima.

**Gate:** nessuno passa alla scena del progetto finché l'ambiente di ciascuno non è verificato.

## Fase 1 — Geometria, FEM, tendine e moto libero

**Obiettivo:** generare e visualizzare il tubo da 100 mm, bloccare i primi 40 mm e flettere i restanti 60 mm con il tendine in controllo di spostamento.

**Dipendenze:** Annalisa produce `tube_volumetric.vtk` e `tube_surface.stl` → Anna li usa in `scene_builder.py` → Josh integra la scena in `main.py` → Annapia collega il controller iniziale. Il gruppo verifica la scena completa.

**Riunione 1:** controllare geometria e mesh, validità del FEM, selezione della ROI, mapping visivo, instradamento del cavo e verso di flessione. Verificare che la punta sia letta dal tubo FEM.

**Gate:** scena apribile senza errori; 40 mm bloccati; tratto distale deformabile; comando e coordinate della punta coerenti.

## Fase 2 — SEA, isteresi del Nitinol, automazione e logging

**Obiettivo:** introdurre molla in serie, smorzamento, isteresi, controllo in forza, cicli manuali/automatici, grafici real-time e CSV.

**Dipendenze:** Annalisa fornisce i parametri costitutivi → Annapia integra la legge SEA e il controller completo → Josh collega logger e LivePlotter → Anna verifica l'interazione tra controller e scena FEM.

**Riunione 2:** provare carico e scarico, controllare `u`, `T`, `ΔL_s`, coordinate punta, cambio E_load/E_unload, reset, ciclo automatico e file CSV. Verificare segni, unità e assenza di tensione iniziale ingiustificata.

**Gate:** variabili registrate correttamente; ciclo completo ripetibile; dati fisicamente plausibili; logger chiuso correttamente a fine simulazione.

## Fase 3 — Ostacoli, collisioni e campagna batch

**Obiettivo:** aggiungere gli oggetti rigido e soffice, misurare la forza di contatto dal solver SOFA e automatizzare le prove.

**Dipendenze:** Annalisa genera le mesh degli ostacoli → Anna implementa topologia di collisione, mapping e scena per entrambi gli oggetti → Josh collega runner e parametri di prova → Annapia verifica i dati di output e il mantenimento.

**Runner:** ogni caso deve avviare una vera scena SOFA tramite la modalità batch disponibile nella versione installata oppure tramite `Sofa.Simulation.init/animate` nell'ambiente SOFA. Registrare parametri e stato della prova nel manifest. Non generare CSV sostitutivi con formule preimpostate.

**Campagna:** identificazione su k = 0,3; 0,6; 1,2; 2,4; 4,8; 9,6; 50 N/mm. Validazione separata su 0,9 e 3,4 N/mm. Sensibilità su k = 1,2; 2,4; 4,8 N/mm, Fh_molla = 0; 0,45; 0,9 N e c = 0,5; 1,5; 5 N·s/mm. Per ogni prova richiesta, distinguere moto libero, oggetto rigido e oggetto soffice.

**Riunione 3:** mostrare una scena rigida e una soffice; verificare deformazione del soffice; controllare che la forza provenga dai vincoli di contatto; mantenere circa 20 mN per cinque secondi; lanciare una sola prova batch per ogni scenario e ispezionare i CSV. Solo dopo il superamento dei controlli avviare la campagna completa.

**Gate:** runner esegue SOFA reale; forza misurata e tracciabile; mantenimento documentato; CSV completi e manifest coerente.

## Fase 4 — Analisi, modello ridotto, validazione e grafici

**Obiettivo:** calcolare H e stabilità dai CSV reali, identificare il modello ridotto, validarlo sui due k riservati e determinare gli intervalli ottimali.

**Dipendenze:** Annapia analizza i CSV → Annalisa esegue il fitting sui soli sette k di identificazione → Annapia valida su 0,9 e 3,4 → Anna determina gli intervalli e prepara i grafici principali → Josh controlla qualità dati e genera grafici dei cicli e delle serie temporali.

**Riunione 4:** verificare H(50), fitting, esclusione dei due k di validazione, errore <15%, stabilità negli ultimi cinque secondi dopo assestamento, assenza di perdita di contatto e intervalli validi senza unire segmenti disgiunti. Controllare anche la previsione della stabilità: H(k) da solo non descrive la dinamica di contatto; la parte aggiuntiva deve essere esplicitata e validata o concordata con la docente.

**Gate:** grafici, tabelle, CSV, parametri e script riproducibili; eventuali target non raggiunti dichiarati senza alterare i dati.

## Fase finale — Presentazione e video

Tutti contribuiscono alle 15 slide e al video dimostrativo. Ciascuno presenta la parte tecnica di cui è responsabile. Un componente esegue una prova completa del flusso dalla scena al grafico partendo dai file del repository.
