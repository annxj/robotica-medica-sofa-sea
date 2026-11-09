# Setup SOFA per chi parte da zero

## Prima del progetto

1. Installare SOFA e annotare versione, sistema operativo e percorso dell'eseguibile `runSofa`.
2. Verificare che siano disponibili SoftRobots e SofaPython3. I nomi dei plugin/componenti possono dipendere dalla versione: controllare la documentazione corrispondente alla propria installazione.
3. Avviare una scena vuota/minima con un `rootNode`, `dt` e gravità esplicitati.
4. Aggiungere un componente alla volta; dopo ogni aggiunta controllare la console e lo stato `Valid` dei componenti.
5. Non sviluppare subito l'intero robot: prima verificare un oggetto FEM semplice, poi la mesh del tubo, il vincolo, il tendine, la visualizzazione e infine le collisioni.

## Ambiente Python

Le librerie scientifiche sono elencate nel file `requirements.txt`. SOFA può usare un interprete Python incorporato o configurato separatamente: verificare quale interprete viene effettivamente usato da SofaPython3 e installare lì le dipendenze necessarie. Non dare per scontato che il Python del terminale sia quello di SOFA.

## Mesh

- Gmsh: generare la mesh volumetrica tetraedrica del tubo cavo e le superfici STL.
- Visualizzare i file in ParaView o in uno strumento equivalente.
- Controllare che il volume contenga tetraedri, non soltanto triangoli di superficie.
- Salvare dimensione caratteristica della mesh e risultato del test di convergenza.

## Verifica minima della scena

- Tubo lungo 100 mm con asse lungo Z.
- I primi 40 mm sono bloccati con `BoxROI` e `FixedConstraint`.
- I 60 mm distali sono liberi di flettersi.
- Il modello visuale segue il FEM mediante mapping.
- Il cavo è instradato all'interno e presenta offset `y_t = +0,60 mm`.
- Il movimento della punta è letto dal MechanicalObject del tubo, non dall'ultimo punto del cavo.

## Conversioni

Con mm, N e s: 1 MPa = 1 N/mm²; 5 kPa = 0,005 MPa; 10, 20 e 50 mN = 0,010, 0,020 e 0,050 N. Verificare sempre che massa/densità usino le unità compatibili con il sistema adottato.
