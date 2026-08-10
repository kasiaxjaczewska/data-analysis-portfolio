import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path


DATA_PATH = Path("data/synthetic_clinical_data.csv")
OUTPUT_DIR = Path("outputs")


def create_visualizations(df):
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    sns.set_theme(style="whitegrid")

    # 1. Missing data by site
    missing_by_site = (
        df.groupby("site_id")["missing_lab"]
        .mean()
        .sort_values(ascending=False)
    )
    plt.figure(figsize=(8, 4))
    plt.bar(missing_by_site.index, missing_by_site.values, color="tomato")
    plt.title("Missing Data Rate by Site", fontsize=12)
    plt.xlabel("Site ID")
    plt.ylabel("Missing Data Rate")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "plots" / "missing_data_by_site.png")
    plt.close()

    # 2. Protocol deviations by site
    protocol_by_site = (
        df.groupby("site_id")["protocol_deviation"]
        .mean()
        .sort_values(ascending=False)
    )
    plt.figure(figsize=(8, 4))
    plt.bar(protocol_by_site.index, protocol_by_site.values, color="steelblue")
    plt.title("Protocol Deviation Rate by Site", fontsize=12)
    plt.xlabel("Site ID")
    plt.ylabel("Protocol Deviation Rate")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "plots" / "protocol_deviations_by_site.png")
    plt.close()

    # 3. Distribution of lab values
    plt.figure(figsize=(8, 4))
    sns.histplot(df["lab_value"].dropna(), bins=25, kde=True, color="steelblue")
    plt.title("Distribution of Lab Values", fontsize=12)
    plt.xlabel("Lab Value")
    plt.ylabel("Frequency")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "plots" / "lab_value_distribution.png")
    plt.close()

    # 4. Data-entry delays
    delay_summary = df.groupby("site_id")["data_entry_days"].mean().sort_values(ascending=False)
    plt.figure(figsize=(8, 4))
    plt.bar(delay_summary.index, delay_summary.values, color="mediumseagreen")
    plt.title("Average Data Entry Delay by Site", fontsize=12)
    plt.xlabel("Site ID")
    plt.ylabel("Average Data Entry Days")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "plots" / "data_entry_delays.png")
    plt.close()

    # 5. Risk score by site
    risk_df = pd.read_csv(OUTPUT_DIR / "reports" / "site_risk_summary.csv")
    plt.figure(figsize=(8, 4))
    sns.barplot(data=risk_df, x="site_id", y="risk_score", hue="risk_label", dodge=False, palette="magma")
    plt.title("Risk Score by Site", fontsize=12)
    plt.xlabel("Site ID")
    plt.ylabel("Risk Score")
    plt.xticks(rotation=45)
    plt.legend(title="Risk Level")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "plots" / "risk_score_by_site.png")
    plt.close()

    # 6. Boxplots for treatment groups and sites
    plt.figure(figsize=(8, 4))
    sns.boxplot(data=df, x="treatment_group", y="lab_value", color="lightsteelblue")
    plt.title("Lab Values by Treatment Group", fontsize=12)
    plt.xlabel("Treatment Group")
    plt.ylabel("Lab Value")
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "plots" / "lab_values_by_treatment_group.png")
    plt.close()

    plt.figure(figsize=(8, 4))
    sns.boxplot(data=df, x="site_id", y="lab_value", color="lightgreen")
    plt.title("Lab Values by Site", fontsize=12)
    plt.xlabel("Site ID")
    plt.ylabel("Lab Value")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(OUTPUT_DIR / "plots" / "lab_values_by_site.png")
    plt.close()

    print("All visualization files were created successfully.")


if __name__ == "__main__":
    df = pd.read_csv(DATA_PATH)
    create_visualizations(df)
