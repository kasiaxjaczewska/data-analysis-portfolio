Projekt: Przewidywanie przeżycia pasażerów Titanica

## Opis
Projekt przewiduje przeżycie pasażera Titanica na podstawie cech `age`, `sex` i `class`. Pipeline obejmuje preprocessing, strojenie hiperparametrów, porównanie pięciu modeli oraz zapis pełnych artefaktów do plików.

## Workflow
1. Wczytanie i oczyszczenie danych z `data/titanic_full.csv`.
2. Ujednolicenie nazw kolumn do formatu `age`, `sex`, `class`, `survived`.
3. Preprocessing w `ColumnTransformer`:
	- imputacja braków,
	- skalowanie cech numerycznych,
	- kodowanie cech kategorycznych.
4. Trenowanie i strojenie pięciu modeli:
	- `LogisticRegression`,
	- `KNN`,
	- `SVM`,
	- `GaussianNB`,
	- `RandomForest`.
5. Ewaluacja modeli na zbiorze testowym i zapis metryk.
6. Repeated k-fold CV do sprawdzenia stabilności wyników.
7. Generowanie learning curves i wykresów ewaluacyjnych.
8. Zapis raportu, artefaktów i wyników do plików `.json`, `.csv` i `.png`.

## Wejścia
- `data/titanic_full.csv` — główny zbiór danych wejściowych.
- `data/titanic_clean.csv` — znormalizowana wersja danych tworzona przez `train.py`.
- `temat.txt` — treść wymagań zadania.

## Wyjścia
- Modele: `model_best_logistic_regression.joblib`, `model_best_knn.joblib`, `model_best_svm.joblib`, `model_best_gaussian_nb.joblib`, `model_best_rf.joblib`
- Raport metryk: `training_report.json`
- Porównanie stabilności: `repeated_cv_summary.csv`
- Learning curves: pliki `*_learning_curve.png`
- Wykresy metryk: confusion matrix, ROC, PR
- Interpretacja cech: `rf_feature_importances.csv`, `rf_feature_importances.png`, `rf_permutation_importance.csv`, `rf_permutation_importance.png`
- EDA: wykresy i crosstaby z `notebook.ipynb`

## Uruchomienie na Windows
```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python train.py
```

## Dodatkowe uruchomienia
- EDA można przeglądać w `notebook.ipynb`.
- Jeśli chcesz odtworzyć wszystkie wyniki, uruchom ponownie `python train.py`.

## Uwagi
- Wejściowy zbiór danych powinien mieć kolumny `age`, `sex`, `class`, `survived` lub ich odpowiedniki z oryginalnego pliku Titanic.
- `train.py` zapisuje modele, macierze pomyłek, ROC/PR, learning curves, repeated CV oraz feature importances.
- `report.md` zawiera pełne porównanie modeli, wybór najlepszego modelu i interpretację metryk.

## Źródła i wsparcie AI
- Głównym źródłem danych był klasyczny zbiór Titanic z Kaggle, zapisany lokalnie w `data/titanic_full.csv`.
- AI było użyte do dopracowania planu projektu, wygenerowania danych pomocniczych oraz dopracowania kodu i dokumentacji.
