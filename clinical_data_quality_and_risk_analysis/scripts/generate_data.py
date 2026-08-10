import numpy as np
import pandas as pd


def generate_synthetic_clinical_data(n_rows=1200, n_sites=8):
    rng = np.random.default_rng(42)

    site_ids = [f"Site_{i:03d}" for i in range(101, 101 + n_sites)]
    treatment_groups = ["Control", "Treatment"]
    sexes = ["F", "M"]

    data = {
        "patient_id": [f"P{i:05d}" for i in range(1, n_rows + 1)],
        "site_id": rng.choice(site_ids, size=n_rows),
        "age": np.clip(rng.normal(58, 12, n_rows).round().astype(int), 18, 90),
        "sex": rng.choice(sexes, size=n_rows),
        "visit": rng.choice([1, 2, 3, 4], size=n_rows, p=[0.2, 0.3, 0.3, 0.2]),
        "treatment_group": rng.choice(treatment_groups, size=n_rows),
        "lab_value": np.zeros(n_rows, dtype=float),
        "visit_date": pd.date_range(start="2024-01-01", periods=n_rows, freq="D"),
        "data_entry_days": np.zeros(n_rows, dtype=int),
        "missing_lab": np.zeros(n_rows, dtype=int),
        "protocol_deviation": np.zeros(n_rows, dtype=int),
    }

    base_lab = 90 + (data["visit"] - 2) * 3 + rng.normal(0, 8, n_rows)
    data["lab_value"] = base_lab

    # Introduce outliers and anomalies
    outlier_idx = rng.choice(n_rows, size=max(10, int(n_rows * 0.02)), replace=False)
    data["lab_value"][outlier_idx] = data["lab_value"][outlier_idx] + rng.choice([-80, 80], size=len(outlier_idx))

    # Introduce site-specific issues
    for site in site_ids:
        site_mask = np.array(data["site_id"]) == site
        if site in ["Site_101", "Site_102", "Site_104"]:
            missing_rate = 0.15 if site == "Site_104" else 0.08
            missing_idx = rng.choice(np.where(site_mask)[0], size=max(1, int(n_rows * missing_rate / n_sites)), replace=False)
            data["missing_lab"][missing_idx] = 1
            data["lab_value"][missing_idx] = np.nan

            dev_idx = rng.choice(np.where(site_mask)[0], size=max(1, int(n_rows * 0.06 / n_sites)), replace=False)
            data["protocol_deviation"][dev_idx] = 1

            if site == "Site_104":
                delay_idx = rng.choice(np.where(site_mask)[0], size=max(1, int(n_rows * 0.12 / n_sites)), replace=False)
                data["data_entry_days"][delay_idx] = rng.integers(8, 21, size=len(delay_idx))
        else:
            data["data_entry_days"][np.where(site_mask)[0]] = rng.integers(0, 5, size=np.sum(site_mask))

    data["visit_date"] = pd.to_datetime(data["visit_date"]) + pd.to_timedelta(rng.integers(0, 6, size=n_rows), unit="D")
    data["data_entry_days"] = np.clip(data["data_entry_days"], 0, 30)

    df = pd.DataFrame(data)
    df["visit_date"] = pd.to_datetime(df["visit_date"])
    return df


if __name__ == "__main__":
    df = generate_synthetic_clinical_data()
    output_path = "data/synthetic_clinical_data.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved synthetic dataset to {output_path}")
