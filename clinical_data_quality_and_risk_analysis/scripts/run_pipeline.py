import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def main():
    scripts = [
        "scripts/generate_data.py",
        "scripts/analyze_data.py",
        "scripts/risk_scoring.py",
        "scripts/statistical_analysis.py",
        "scripts/anomaly_detection.py",
        "scripts/visualizations.py",
    ]

    for script in scripts:
        print(f"Running {script}...")
        result = subprocess.run([sys.executable, str(ROOT / script)], cwd=ROOT, capture_output=False)
        if result.returncode != 0:
            raise SystemExit(f"Pipeline failed at {script}")

    print("\nFull analysis pipeline completed successfully.")


if __name__ == "__main__":
    main()
