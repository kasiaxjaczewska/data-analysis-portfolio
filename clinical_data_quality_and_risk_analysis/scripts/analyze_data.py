import pandas as pd
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt

from pathlib import Path


DATA_PATH = Path("data/synthetic_clinical_data.csv")
OUTPUT_DIR = Path("outputs")


def load_data(path=DATA_PATH):
    return pd.read_csv(path, parse_dates=["visit_date"])


def basic_quality_checks(df, output_dir=OUTPUT_DIR):
    print("\nBasic data quality checks")
    print("-" * 40)
    print("Rows:", df.shape[0])
    print("Columns:", df.shape[1])
    print("Duplicates:", int(df.duplicated().sum()))

    missing_counts = df.isna().sum()
    missing_percentages = (missing_counts / len(df) * 100).round(2)

    invalid_checks = {
        "age": int((df["age"] <= 0).sum()),
        "visit": int((~df["visit"].isin([1, 2, 3, 4])).sum()),
        "missing_lab": int((~df["missing_lab"].isin([0, 1])).sum()),
        "protocol_deviation": int((~df["protocol_deviation"].isin([0, 1])).sum()),
        "visit_date": int(df["visit_date"].isna().sum()),
    }
    invalid_total = sum(invalid_checks.values())

    site_missing_summary = (
        df.groupby("site_id")
        .agg(missing_count=("missing_lab", "sum"), missing_rate=("missing_lab", "mean"))
        .reset_index()
        .sort_values(["missing_count", "missing_rate"], ascending=False)
    )

    visit_missing_summary = (
        df.groupby("visit")
        .agg(missing_count=("missing_lab", "sum"), missing_rate=("missing_lab", "mean"))
        .reset_index()
        .sort_values(["missing_count", "missing_rate"], ascending=False)
    )

    field_risk = pd.DataFrame(
        {
            "field": missing_counts.index,
            "missing_count": missing_counts.values,
            "missing_percentage": missing_percentages.values,
            "invalid_count": [invalid_checks.get(col, 0) for col in missing_counts.index],
        }
    )
    field_risk["invalid_percentage"] = (field_risk["invalid_count"] / len(df) * 100).round(2)
    field_risk["problem_score"] = (field_risk["missing_percentage"] + field_risk["invalid_percentage"]).round(2)
    field_risk = field_risk.sort_values("problem_score", ascending=False)

    overall_missing = int(missing_counts.sum())
    top_site = site_missing_summary.iloc[0]
    top_visit = visit_missing_summary.iloc[0]
    top_fields = field_risk.head(5)

    print("\nOverall missing values:", overall_missing)
    print("\nMissing values per column:")
    print(missing_counts.to_string())
    print("\nMissing percentage per column:")
    print(missing_percentages.to_string())
    print("\nMissing values per site:")
    print(site_missing_summary.to_string(index=False))
    print("\nMissing values per visit:")
    print(visit_missing_summary.to_string(index=False))
    print("\nInvalid or inconsistent values:")
    for key, value in invalid_checks.items():
        print(f"- {key}: {value}")
    print("\nTop problematic fields:")
    print(top_fields[["field", "missing_percentage", "invalid_percentage", "problem_score"]].to_string(index=False))
    print("\nSite with highest missing count:", top_site["site_id"], "(", int(top_site["missing_count"]), "missing values)")
    print("Visit with highest missing count:", int(top_visit["visit"]), "(", int(top_visit["missing_count"]), "missing values)")

    site_missing_summary.to_csv(output_dir / "reports" / "site_missing_summary.csv", index=False)
    visit_missing_summary.to_csv(output_dir / "reports" / "visit_missing_summary.csv", index=False)
    field_risk.to_csv(output_dir / "reports" / "field_risk_summary.csv", index=False)

    report_lines = [
        "Clinical Data Quality Summary",
        "============================",
        f"Rows: {df.shape[0]}",
        f"Columns: {df.shape[1]}",
        f"Duplicates: {int(df.duplicated().sum())}",
        f"Overall missing values: {overall_missing}",
        f"Invalid or inconsistent values: {invalid_total}",
        "",
        "Missing percentage by column:",
    ]
    for column, value in missing_percentages.items():
        report_lines.append(f"- {column}: {value:.2f}%")

    report_lines.extend(
        [
            "",
            "Site-level missing summary:",
        ]
    )
    for _, row in site_missing_summary.head(5).iterrows():
        report_lines.append(f"- {row['site_id']}: {int(row['missing_count'])} missing values ({row['missing_rate'] * 100:.1f}%)")

    report_lines.extend(
        [
            "",
            "Visit-level missing summary:",
        ]
    )
    for _, row in visit_missing_summary.head(5).iterrows():
        report_lines.append(f"- Visit {int(row['visit'])}: {int(row['missing_count'])} missing values ({row['missing_rate'] * 100:.1f}%)")

    report_lines.extend(
        [
            "",
            "Most problematic fields:",
        ]
    )
    for _, row in top_fields.iterrows():
        report_lines.append(
            f"- {row['field']}: missing {row['missing_percentage']:.2f}%, invalid {row['invalid_percentage']:.2f}%, problem score {row['problem_score']:.2f}"
        )

    report_lines.extend(
        [
            "",
            f"Highest-missing site: {top_site['site_id']} ({int(top_site['missing_count'])} missing values)",
            f"Highest-missing visit: Visit {int(top_visit['visit'])} ({int(top_visit['missing_count'])} missing values)",
        ]
    )

    report_path = output_dir / "reports" / "data_quality_report.txt"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    print("\nSaved report to", report_path)

    return {
        "rows": df.shape[0],
        "columns": df.shape[1],
        "duplicates": int(df.duplicated().sum()),
        "overall_missing": overall_missing,
        "invalid_total": invalid_total,
        "site_missing_summary": site_missing_summary,
        "visit_missing_summary": visit_missing_summary,
        "field_risk": field_risk,
    }


def create_summary_plots(df, output_dir=OUTPUT_DIR):
    sns.set_theme(style="whitegrid")

    missing_by_site = df.groupby("site_id")["missing_lab"].mean().sort_values(ascending=False)
    plt.figure(figsize=(8, 4))
    missing_by_site.plot(kind="bar", color="tomato")
    plt.title("Missing Data Rate by Site")
    plt.ylabel("Missing rate")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "plots" / "missing_by_site.png")
    plt.close()

    protocol_by_site = df.groupby("site_id")["protocol_deviation"].mean().sort_values(ascending=False)
    plt.figure(figsize=(8, 4))
    protocol_by_site.plot(kind="bar", color="steelblue")
    plt.title("Protocol Deviations by Site")
    plt.ylabel("Deviation rate")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(output_dir / "plots" / "protocol_by_site.png")
    plt.close()

    plt.figure(figsize=(8, 4))
    sns.histplot(df["lab_value"].dropna(), bins=25, kde=True)
    plt.title("Distribution of Lab Values")
    plt.xlabel("Lab value")
    plt.tight_layout()
    plt.savefig(output_dir / "plots" / "lab_distribution.png")
    plt.close()


if __name__ == "__main__":
    df = load_data()
    basic_quality_checks(df)
    create_summary_plots(df)
    print("\nPlots saved to outputs/plots")
