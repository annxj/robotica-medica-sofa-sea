# Robotica Medica — Robot continuo azionato da tendine con molla in serie (SEA)

Repository di lavoro per il Progetto 1 — Sezione A: compromesso della molla in serie passiva tra moto libero e contatto, con tubo continuo in Nitinol e simulazione in SOFA.

> **Stato:** struttura iniziale del repository. I moduli Python contengono scheletri e TODO: non rappresentano una simulazione SOFA già verificata. I risultati devono provenire da esecuzioni reali della scena SOFA; non inserire CSV sintetici al posto delle simulazioni.

## Obiettivi

1. Costruire e verificare la geometria e la mesh del tubo continuo (100 mm: 40 mm rigidi + 60 mm flessibili).
2. Realizzare la scena FEM SOFA, il tendine CableConstraint e il controller da tastiera.
3. Integrare SEA passiva, materiale Nitinol, collisione con ostacolo rigido e soffice e misura della forza di contatto.
4. Eseguire la campagna batch, salvare i CSV e analizzare isteresi e stabilità.
5. Identificare e validare il modello ridotto, determinare gli intervalli ottimali e produrre i grafici finali.

## Struttura

```text
robotica-medica-sofa-sea/
├── config/                 # Parametri e configurazioni delle prove
├── docs/
│   ├── reference/          # Guida operativa e glossario PDF
│   ├── SETUP_SOFA.md       # Setup ambiente e primo avvio
│   ├── WORKFLOW.md         # Fasi, dipendenze e riunioni
│   └── TEAM_RESPONSIBILITIES.md
├── src/
│   ├── geometry/           # Mesh Gmsh di tubo e ostacoli
│   ├── sofa/               # Scene graph, FEM, collisioni e main
│   ├── control/            # Controller SEA e stati automatici
│   ├── monitoring/         # Logger CSV e grafici real-time
│   ├── campaign/           # Runner batch SOFA reale
│   ├── analysis/            # H, stabilità, modello ridotto
│   └── plots/               # Grafici finali e sensibilità
├── data/
│   ├── raw/                # CSV grezzi prodotti dalle simulazioni (non versionare)
│   └── processed/          # Tabelle riassuntive (non versionare)
├── results/                # Figure e report (non versionare)
├── tests/                  # Test automatici e controlli di coerenza
├── requirements.txt
└── README.md
```

## Parametri di progetto

I valori specifici della traccia sono centralizzati in [`config/project_config.json`](config/project_config.json). Le unità adottate per la simulazione sono mm, N e s; quindi i moduli elastici sono espressi in MPa (= N/mm²) e le forze di contatto in N.

- Geometria: OD 1,93 mm; ID 1,49 mm; parete 0,22 mm; lunghezza 100 mm (40 + 60 mm).
- Nitinol: E_load 77000 MPa; E_unload 65000 MPa; ν 0,33.
- Tendine: offset y_t = +0,60 mm.
- SEA: L0 = 20 mm; k baseline = 1,20 N/mm; c = 1,50 N·s/mm; isteresi molla = ±0,45 N; isteresi materiale = ±0,40 N.
- Ambiente: ostacolo caratteristico 20 mm; E_s = 0,005 MPa (5 kPa); ν_s = 0,45; μ = 0,20.
- Contatto: intervallo 0,010–0,050 N; mantenimento obiettivo 0,020 N.

Il glossario contiene anche benchmark per configurazioni diverse. Quando un valore differisce, per questo elaborato prevale il parametro esplicito della traccia, salvo diversa indicazione della docente. La densità Nitinol del glossario è registrata come riferimento da verificare rispetto alla formulazione di massa scelta in SOFA.

## Installazione e avvio

1. Installare una distribuzione SOFA compatibile con SoftRobots e SofaPython3.
2. Verificare la presenza dei plugin richiesti nella versione installata.
3. Installare le dipendenze Python elencate in `requirements.txt` nell'ambiente Python usato da SOFA. Gmsh può essere usato offline per generare le mesh.
4. Copiare o generare i file mesh nella cartella indicata dalla configurazione.
5. Avviare prima la scena minima e poi la scena del progetto dall'ambiente SOFA. Non lanciare la campagna completa finché non è stata verificata una prova singola per ciascuno scenario.

Le istruzioni passo-passo sono in [`docs/SETUP_SOFA.md`](docs/SETUP_SOFA.md) e [`docs/WORKFLOW.md`](docs/WORKFLOW.md).

## Regole sui dati

- Ogni CSV deve essere tracciabile a una scena SOFA realmente eseguita.
- Registrare parametri, scenario, versione SOFA, durata, passo temporale ed esito in un manifest della campagna.
- Una prova fallita va marcata come fallita: non sostituire i dati mancanti con curve inventate o valori di comodo.
- I valori k=0,9 e 3,4 N/mm sono riservati alla validazione e non devono entrare nel fitting.
- Non versionare dataset grezzi molto grandi senza accordo del gruppo; conservare manifest, script e risultati finali selezionati.

## Responsabilità

- **Annalisa:** geometrie Gmsh, parametri costitutivi del Nitinol, modello ridotto H(k), grafici di sensibilità.
- **Annapia:** controller completo, legge SEA, analisi segnali H/stabilità e validazione indipendente.
- **Anna:** architettura FEM SOFA, mapping, collisioni, forza di contatto e grafici principali/intervalli ottimali.
- **Josh:** main e integrazione, LivePlotter, logger, runner batch SOFA reale, qualità dei CSV e grafici dei cicli/serie temporali.

La matrice dettagliata è in [`docs/TEAM_RESPONSIBILITIES.md`](docs/TEAM_RESPONSIBILITIES.md).

## Convenzioni Git

- Un ramo per attività: `feature/geometry`, `feature/sofa-scene`, `feature/controller`, `feature/batch`, `feature/analysis`.
- Aprire una pull request verso `main`; almeno un altro componente verifica la modifica.
- Non committare file temporanei, cache, ambienti virtuali o dataset grezzi.
- Usare commit brevi e descrittivi, ad esempio `feat: add tube mesh generator`.
