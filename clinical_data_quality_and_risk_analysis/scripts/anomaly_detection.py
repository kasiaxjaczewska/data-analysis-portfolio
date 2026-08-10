import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


DATA_PATH = Path("data/synthetic_clinical_data.csv")
OUTPUT_DIR = Path("outputs")


def detect_anomalies(df):
    lab = df["lab_value"].dropna()
    median = float(lab.median())
    mad = float(np.median(np.abs(lab - median)))
    q1 = float(lab.quantile(0.25))
    q3 = float(lab.quantile(0.75))
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr

    z_scores = (lab - lab.mean()) / lab.std()
    anomaly_df = df.dropna(subset=["lab_value"]).copy()
    anomaly_df["z_score"] = z_scores
    anomaly_df["is_iqr_outlier"] = anomaly_df["lab_value"].lt(lower_bound) | anomaly_df["lab_value"].gt(upper_bound)
    anomaly_df["is_zscore_outlier"] = anomaly_df["z_score"].abs() > 3
    anomaly_df["mad_score"] = (anomaly_df["lab_value"] - median) / mad if mad != 0 else 0
    anomaly_df["is_mad_outlier"] = anomaly_df["mad_score"].abs() > 3.5
    anomaly_df["is_anomalous"] = anomaly_df[["is_iqr_outlier", "is_zscore_outlier", "is_mad_outlier"]].any(axis=1)
    anomaly_df["anomaly_methods"] = anomaly_df.apply(
        lambda row: [
            method
            for method, flag in {
                "IQR": row["is_iqr_outlier"],
                "Z-score": row["is_zscore_outlier"],
                "MAD": row["is_mad_outlier"],
            }.items()
            if flag
        ],
        axis=1,
    )

    site_summary = (
        anomaly_df.groupby("site_id")
        .agg(anomaly_count=("is_anomalous", "sum"), total_records=("patient_id", "count"), anomaly_rate=("is_anomalous", "mean"))
        .reset_index()
        .sort_values("anomaly_count", ascending=False)
    )

    visit_summary = (
        anomaly_df.groupby("visit")
        .agg(anomaly_count=("is_anomalous", "sum"), anomaly_rate=("is_anomalous", "mean"))
        .reset_index()
        .sort_values("anomaly_count", ascending=False)
    )

    return anomaly_df, site_summary, visit_summary


def save_outputs(anomaly_df, site_summary, visit_summary, output_dir=OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)

    anomaly_df.to_csv(output_dir / "reports" / "anomalies_detected.csv", index=False)
    site_summary.to_csv(output_dir / "reports" / "anomaly_by_site.csv", index=False)
    visit_summary.to_csv(output_dir / "reports" / "anomaly_by_visit.csv", index=False)

    report_lines = [
        "Anomaly Detection Report",
        "========================",
        "",
        f"Total suspicious observations: {int(anomaly_df['is_anomalous'].sum())}",
        "",
        "Top sites by anomaly count:",
    ]
    for _, row in site_summary.head(5).iterrows():
        report_lines.append(f"- {row['site_id']}: {int(row['anomaly_count'])} anomalies ({row['anomaly_rate'] * 100:.1f}%)")

    report_lines.extend(["", "Top visits by anomaly count:"])
    for _, row in visit_summary.head(5).iterrows():
        report_lines.append(f"- Visit {int(row['visit'])}: {int(row['anomaly_count'])} anomalies ({row['anomaly_rate'] * 100:.1f}%)")

    (output_dir / "reports" / "anomaly_detection_report.txt").write_text("\n".join(report_lines), encoding="utf-8")

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(8, 4))
    sns.barplot(data=site_summary, x="site_id", y="anomaly_count")
    plt.title("Anomalies by Site")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "plots" / "anomalies_by_site.png")
    plt.close()

    plt.figure(figsize=(8, 4))
    sns.barplot(data=visit_summary, x="visit", y="anomaly_count")
    plt.title("Anomalies by Visit")
    plt.tight_layout()
    plt.savefig(output_dir / "plots" / "anomalies_by_visit.png")
    plt.close()


if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    anomaly_df, site_summary, visit_summary = detect_anomalies(df)
    save_outputs(anomaly_df, site_summary, visit_summary)
    print(anomaly_df[["patient_id", "site_id", "visit", "lab_value", "is_anomalous", "anomaly_methods"]].head(20).to_string(index=False))
    print(f"\nDetected anomalies: {int(anomaly_df['is_anomalous'].sum())}")
