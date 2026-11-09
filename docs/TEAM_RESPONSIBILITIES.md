# Responsabilità del gruppo

## Annalisa — geometria, materiale e modello H(k)

- `src/geometry/generate_tube_mesh.py`: tubo cavo, mesh volumetrica tetraedrica e superficie STL; verifica dimensioni e convergenza.
- `src/geometry/generate_obstacles.py`: mesh superficie rigida e volume soffice da 20 mm.
- Fornire e documentare E_load, E_unload, ν, isteresi del materiale e ipotesi di massa/densità.
- `src/analysis/reduced_model.py`: modello H(k), fitting ai minimi quadrati sui soli k di identificazione, residui e parametri stimati.
- `src/plots/plot_sensitivity.py`: sensibilità di H rispetto a Fh_molla e di stabilità rispetto a c, usando risultati effettivi.

## Annapia — controller SEA e post-processing

- `src/control/tendon_controller.py`: unico proprietario del controller completo: tastiera, carico/scarico, reset, manuale/automatico, ciclo libero, mantenimento, direzione e logging dei valori fisici di controllo.
- Implementare la relazione SEA con `u2` (comando motore), `u1` (spostamento del tendine a valle della molla), `ΔL_s = max(0, u2-u1)`, contributo viscoso con segno coerente e isteresi con stato/direzione espliciti.
- `src/analysis/signal_analysis.py`: H dai rami di carico/scarico sul dominio comune; stabilità sugli ultimi cinque secondi di mantenimento dopo assestamento, controllando F_min, oscillazione e stato di contatto.
- Validare il modello ridotto sui soli k=0,9 e 3,4 N/mm, senza rifare il fitting includendo quei punti.

## Anna — scena fisica SOFA e grafici principali

- `src/sofa/scene_builder.py`: tubo FEM, topologia, massa motivata, BoxROI/FixedConstraint, tendine, mapping visivo e di collisione.
- Implementare pipeline di collisione e oggetto rigido/soffice; costruire la superficie triangolare del volume soffice con mapping topologico appropriato alla versione SOFA.
- Misurare la forza normale di contatto dai dati dei vincoli risolti dal solver; non stimarla con una formula basata sulla sola penetrazione.
- `src/plots/plot_main_results.py`: H(k), oscillazione del contatto e intervalli validi separati per rigido, soffice e comune.

## Josh — integrazione, dati e grafici di ciclo

- `src/sofa/main.py`: configurazione plugin, caricamento moduli e creazione della scena.
- `src/monitoring/live_plotter.py`: grafici real-time X, Y, ΔY e u, T, ΔL_s, F_contatto.
- `src/monitoring/csv_logger.py`: registrazione, intestazioni, unità, flush e chiusura robusta.
- `src/campaign/run_campaign.py`: runner che lancia vere simulazioni SOFA, passa i parametri per ogni caso, controlla exit code e durata e genera `campaign_manifest.csv`.
- `src/plots/plot_cycles.py`: cicli ΔY(u) per SEA e attuazione diretta; serie temporali della forza negli ultimi cinque secondi per rigido e soffice.
- Controllo qualità CSV: campioni, NaN, colonne, unità, scenario e parametri effettivamente usati.

## Interfacce e regole di integrazione

- Anna definisce i riferimenti SOFA restituiti da `build_robot` e li documenta; Annapia riceve i riferimenti senza ricostruire la scena.
- Josh non modifica la logica del controller: usa l'interfaccia concordata e collega logger/plotter.
- Annalisa non scrive dati di simulazione: consegna mesh e parametri; Josh orchestra l'esecuzione; i CSV sono prodotti dal logger collegato alla scena.
- Modifiche condivise tramite branch e pull request; evitare che più persone modifichino contemporaneamente lo stesso file.
