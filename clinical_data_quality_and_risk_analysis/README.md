# Clinical Data Quality & Risk Analysis

A simulated clinical trial data analysis project focused on identifying data quality issues, anomalies, and potential risk signals across clinical trial sites.

## Project Objective
This project demonstrates a practical data quality and risk assessment workflow using synthetic clinical-trial-like data. The analysis focuses on identifying incomplete records, unusual laboratory values, site-level risk patterns, and the clinical sites that may require further investigation.

## Key Aspects
- Data quality assessment
- Missing data analysis
- Duplicate and invalid value checks
- Outlier and anomaly detection
- Site-level risk scoring
- Statistical summaries
- Data visualization
- Final reporting

## Tools Used
- Python
- pandas
- numpy
- scipy
- matplotlib
- seaborn

## Project Structure
- data/ - synthetic input dataset
- notebooks/ - analysis notebook workspace
- scripts/ - reusable Python scripts for data generation, analysis, risk scoring, anomaly detection, and visualization
- outputs/plots/ - generated charts and figures
- outputs/reports/ - summary reports and CSV outputs

## Workflow
1. Generate a synthetic clinical dataset
2. Perform data quality checks
3. Calculate site-level risk metrics
4. Run statistical analysis on laboratory values
5. Detect anomalous laboratory results
6. Create visualizations
7. Produce a final report summarizing findings

## Main Results
- 1,200 records were analyzed
- 0 duplicates were detected
- 46 missing values were identified overall
- The most problematic variable was lab_value
- Site 104 was identified as the highest-risk site
- A total of 39 suspicious laboratory observations were detected

## Key Finding
Site 104 showed the strongest combination of missing data, delayed data entry, protocol deviations, and laboratory anomalies, making it the primary site for further investigation.

## Outputs
- Final report: outputs/reports/final_report.txt
- Data quality report: outputs/reports/data_quality_report.txt
- Site risk summary: outputs/reports/site_risk_summary.csv
- Anomaly detection report: outputs/reports/anomaly_detection_report.txt
- Visualizations: outputs/plots/

## How to Run
```bash
python scripts/generate_data.py
python scripts/analyze_data.py
python scripts/risk_scoring.py
python scripts/statistical_analysis.py
python scripts/anomaly_detection.py
python scripts/visualizations.py
```
