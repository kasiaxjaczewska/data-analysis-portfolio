import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


DATA_PATH = Path("data/synthetic_clinical_data.csv")
OUTPUT_DIR = Path("outputs")


def calculate_risk_score(df):
    site_summary = (
        df.groupby("site_id")
        .agg(
            missing_data_rate=("missing_lab", "mean"),
            protocol_deviation_rate=("protocol_deviation", "mean"),
            delayed_entry_rate=("data_entry_days", lambda s: (s > 7).mean()),
            records=("patient_id", "count"),
            avg_lab_value=("lab_value", "mean"),
            anomaly_count=("lab_value", lambda s: (s - s.mean()).abs().gt(3 * s.std()).sum())
        )
        .reset_index()
    )

    site_summary["risk_score"] = (
        0.4 * site_summary["missing_data_rate"]
        + 0.3 * site_summary["protocol_deviation_rate"]
        + 0.3 * site_summary["delayed_entry_rate"]
    )

    def risk_label(score):
        if score >= 0.12:
            return "High Risk"
        elif score >= 0.06:
            return "Medium Risk"
        return "Low Risk"

    site_summary["risk_label"] = site_summary["risk_score"].apply(risk_label)
    site_summary = site_summary.sort_values("risk_score", ascending=False).reset_index(drop=True)
    return site_summary


def save_risk_report(site_summary, output_dir=OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)
    report_path = output_dir / "reports" / "site_risk_summary.csv"
    site_summary.to_csv(report_path, index=False)

    summary_text = [
        "Clinical Site Risk Summary",
        "=========================",
        "",
        "Risk Score = 0.4 * missing_data_rate + 0.3 * protocol_deviation_rate + 0.3 * delayed_entry_rate",
        "",
    ]
    for _, row in site_summary.iterrows():
        summary_text.append(
            f"{row['site_id']}: missing={row['missing_data_rate']:.3f}, protocol={row['protocol_deviation_rate']:.3f}, delayed={row['delayed_entry_rate']:.3f}, risk_score={row['risk_score']:.3f}, label={row['risk_label']}"
        )

    highest_risk = site_summary.iloc[0]
    summary_text.extend(
        [
            "",
            f"Highest risk site: {highest_risk['site_id']} ({highest_risk['risk_label']}, score={highest_risk['risk_score']:.3f})",
        ]
    )
    (output_dir / "reports" / "site_risk_report.txt").write_text("\n".join(summary_text), encoding="utf-8")

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(8, 4))
    sns.barplot(data=site_summary, x="site_id", y="risk_score", hue="risk_label", dodge=False)
    plt.title("Risk Score by Site")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "plots" / "risk_score_by_site.png")
    plt.close()

    return report_path


if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    site_summary = calculate_risk_score(df)
    report_path = save_risk_report(site_summary)
    print(site_summary.to_string(index=False))
    print(f"\nSaved risk summary to {report_path}")
