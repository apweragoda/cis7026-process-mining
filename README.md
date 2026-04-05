# CIS 7026 – Business Process and Data Analysis
## Hospital Billing and Claims Management – Process Mining Analysis

**Module**: CIS 7026 – Business Process and Data Analysis  
**Assignment**: Written Assessment 1 (WRIT 01)  
**Process**: Hospital Billing and Claims Management  
**Dataset**: BPI Challenge – Hospital Billing Event Log (4TU Research Data Repository)

---

## Dataset

**Source**: Mannhardt, F. (2017) *Hospital Billing – Event Log*. 4TU.ResearchData.  
**DOI**: https://doi.org/10.4121/uuid:76c46b83-c930-4798-a1c9-4be94dfeb741  
**License**: Creative Commons Attribution 4.0 (CC BY 4.0)

| Attribute | Value |
|---|---|
| Cases | 99,999 |
| Events | 451,359 |
| Activities | 18 |
| Time Period | December 2012 – January 2016 |
| Organisation | Anonymised regional hospital (Europe) |

This is a **real event log** from a hospital's ERP billing system, capturing the complete lifecycle of medical billing cases from creation to final settlement.

**Activity Reference:**

| Activity | Description |
|---|---|
| NEW | New billing case created in ERP system |
| CHANGE DIAGN | Diagnosis code updated by clinician |
| FIN | Case flagged as complete by clinical staff |
| RELEASE | Case released for billing processing |
| CODE OK | Billing code validated successfully |
| CODE NOK | Billing code validation failed (exception) |
| BILLED | Invoice sent to insurance/patient |
| STORNO | Billing reversed/cancelled |
| REJECT | Claim rejected by insurance |
| REOPEN | Closed case reopened for correction |
| DELETE | Case deleted from system |

---

## Repository Structure

```
├── dataset/
│   └── hospital_billing_event_log.csv    # Real event log (451,359 events)
│
├── code/
│   └── process_mining_analysis.py        # Full PM4Py analysis pipeline
│
├── output/
│   ├── bottleneck_analysis.png           # Case duration distribution + activity waits
│   ├── bottleneck_segmentation.png       # Duration by case type and speciality
│   ├── monthly_duration_trend.png        # Monthly average duration (2012–2016)
│   ├── process_variants.png              # Top 15 process variants by frequency
│   ├── conformance_results.png           # Inductive Miner: fitness, precision, simplicity
│   ├── ocpm_interaction_heatmap.png      # Object type co-occurrence matrix (OCPM)
│   ├── federated_process_mining.png      # Per-node performance + DP privacy-utility
│   └── process_enhancement.png          # Exception rates and enhancement opportunities
│
└── README.md
```

---

## Running the Analysis

### Requirements

```bash
pip install pm4py pandas numpy matplotlib seaborn scipy scikit-learn
```

> **Note**: Petri net and DFG visualisations require [Graphviz](https://graphviz.org/download/) installed and on your system PATH. All statistical charts work without Graphviz.

### Run

```bash
cd code
python process_mining_analysis.py
```

Charts are saved to the `output/` folder.

---

## Analysis Sections

| Section | Description |
|---|---|
| 1 – Data Loading | Load and validate the real event log |
| 2 – Process Discovery | Alpha Miner, Heuristics Miner, Inductive Miner, DFG |
| 3 – Conformance Checking | Alignment-based fitness (0.9625) and precision (0.5700) |
| 4 – Bottleneck Analysis | IQR + Z-score outlier detection across 99,999 cases |
| 5 – Process Variant Analysis | 1,022 unique variants discovered |
| 6 – Object-Centric Process Mining | OCEL 2.0: BillingCase, Resource, Speciality objects |
| 7 – Federated Process Mining | 3 case-type nodes with differential privacy (ε = 0.1) |
| 8 – Process Enhancement | Exception rates and improvement opportunities |

---

## Key Results

| Metric | Value |
|---|---|
| Inductive Miner fitness | 0.9625 |
| Inductive Miner precision | 0.5700 |
| Fitting traces | 86.48% |
| Unique process variants | 1,022 |
| Bottleneck cases (IQR) | 1,409 (1.4%) |
| Median case duration | 2,456.7 hours (~102 days) |
| CODE NOK exception rate | 3.1% |
| REJECT exception rate | 1.8% |
| REOPEN exception rate | 4.1% |

---

## Citation

Mannhardt, F. (2017) *Hospital Billing – Event Log*. 4TU.ResearchData.  
Available at: https://doi.org/10.4121/uuid:76c46b83-c930-4798-a1c9-4be94dfeb741
