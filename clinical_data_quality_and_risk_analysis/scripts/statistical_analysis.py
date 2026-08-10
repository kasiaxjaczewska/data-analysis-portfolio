import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from pathlib import Path
from scipy import stats


DATA_PATH = Path("data/synthetic_clinical_data.csv")
OUTPUT_DIR = Path("outputs")


def compute_stats(df):
    lab = df["lab_value"].dropna()
    stats_summary = {
        "mean": float(lab.mean()),
        "median": float(lab.median()),
        "std": float(lab.std()),
        "min": float(lab.min()),
        "max": float(lab.max()),
        "q1": float(lab.quantile(0.25)),
        "q3": float(lab.quantile(0.75)),
        "iqr": float(lab.quantile(0.75) - lab.quantile(0.25)),
    }

    lower_bound = stats_summary["q1"] - 1.5 * stats_summary["iqr"]
    upper_bound = stats_summary["q3"] + 1.5 * stats_summary["iqr"]
    outliers = lab[(lab < lower_bound) | (lab > upper_bound)]
    z_scores = (lab - lab.mean()) / lab.std()
    z_outliers = lab[np.abs(z_scores) > 3]

    group_summary = (
        df.groupby("treatment_group")["lab_value"]
        .agg(["mean", "median", "std", "count"])
        .reset_index()
    )

    sex_summary = (
        df.groupby("sex")["lab_value"]
        .agg(["mean", "median", "std", "count"])
        .reset_index()
    )

    site_summary = (
        df.groupby("site_id")["lab_value"]
        .agg(["mean", "median", "std", "count"])
        .reset_index()
    )

    ttest_treatment = stats.ttest_ind(
        df.loc[df["treatment_group"] == "Control", "lab_value"].dropna(),
        df.loc[df["treatment_group"] == "Treatment", "lab_value"].dropna(),
        equal_var=False,
    )

    anova_site = stats.f_oneway(
        *[df.loc[df["site_id"] == site, "lab_value"].dropna() for site in df["site_id"].unique()]
    )

    summary = {
        "stats_summary": stats_summary,
        "outlier_count_iqr": int(outliers.count()),
        "outlier_count_zscore": int(z_outliers.count()),
        "group_summary": group_summary,
        "sex_summary": sex_summary,
        "site_summary": site_summary,
        "ttest_treatment": {
            "statistic": float(ttest_treatment.statistic),
            "p_value": float(ttest_treatment.pvalue),
        },
        "anova_site": {
            "statistic": float(anova_site.statistic),
            "p_value": float(anova_site.pvalue),
        },
    }
    return summary


def save_outputs(df, summary, output_dir=OUTPUT_DIR):
    output_dir.mkdir(parents=True, exist_ok=True)

    pd.DataFrame([summary["stats_summary"]]).to_csv(output_dir / "reports" / "lab_stats_summary.csv", index=False)
    summary["group_summary"].to_csv(output_dir / "reports" / "lab_group_summary.csv", index=False)
    summary["sex_summary"].to_csv(output_dir / "reports" / "lab_sex_summary.csv", index=False)
    summary["site_summary"].to_csv(output_dir / "reports" / "lab_site_summary.csv", index=False)

    report_lines = [
        "Laboratory Statistical Summary",
        "=============================",
        "",
        "Descriptive statistics for lab_value:",
    ]
    for key, value in summary["stats_summary"].items():
        report_lines.append(f"- {key}: {value:.3f}")

    report_lines.extend(
        [
            "",
            f"Outliers (IQR rule): {summary['outlier_count_iqr']}",
            f"Outliers (z-score > 3): {summary['outlier_count_zscore']}",
            "",
            "Treatment group comparison:",
            f"- t-test statistic: {summary['ttest_treatment']['statistic']:.3f}",
            f"- p-value: {summary['ttest_treatment']['p_value']:.3f}",
            "",
            "Site comparison:",
            f"- ANOVA statistic: {summary['anova_site']['statistic']:.3f}",
            f"- p-value: {summary['anova_site']['p_value']:.3f}",
        ]
    )
    (output_dir / "reports" / "lab_statistical_report.txt").write_text("\n".join(report_lines), encoding="utf-8")

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(8, 4))
    sns.histplot(df["lab_value"].dropna(), bins=25, kde=True)
    plt.title("Distribution of Lab Values")
    plt.xlabel("Lab value")
    plt.tight_layout()
    plt.savefig(output_dir / "plots" / "lab_distribution.png")
    plt.close()

    plt.figure(figsize=(8, 4))
    sns.boxplot(data=df, x="treatment_group", y="lab_value")
    plt.title("Lab Values by Treatment Group")
    plt.tight_layout()
    plt.savefig(output_dir / "plots" / "lab_by_treatment.png")
    plt.close()

    plt.figure(figsize=(8, 4))
    sns.boxplot(data=df, x="site_id", y="lab_value")
    plt.title("Lab Values by Site")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "plots" / "lab_by_site.png")
    plt.close()


if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    summary = compute_stats(df)
    save_outputs(df, summary)
    print("Statistical analysis completed successfully.")
    print(summary["stats_summary"])
