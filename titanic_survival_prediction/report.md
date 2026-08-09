# Raport końcowy

## Cel zadania
Celem było zbudowanie powtarzalnego pipeline'u klasyfikacyjnego do przewidywania przeżycia pasażera Titanica na podstawie cech `age`, `sex` oraz `class`.

## Wykonane kroki
1. Przygotowano i oczyszczono dane wejściowe, uzupełniając braki i normalizując format kolumn.
2. Zbudowano pipeline preprocessingu z `ColumnTransformer`, obejmujący imputację braków, kodowanie cech kategorycznych i skalowanie cech liczbowych.
3. Wytrenowano model bazowy `LogisticRegression`.
4. Rozszerzono eksperyment o dodatkowe modele: `KNN`, `SVM` i `GaussianNB`.
5. Wytrenowano model ulepszony `RandomForestClassifier` z `GridSearchCV`.
6. Zapisano modele, macierze pomyłek, ROC/PR oraz feature importances.

## Wyniki
Po uruchomieniu treningu na pełnym zbiorze Titanica (`data/titanic_full.csv`) otrzymano miarodajne wyniki na zbiorze testowym (20%):

- **LogisticRegression (baseline)**:
	- Accuracy: 0.7877
	- Precision: 0.7460
	- Recall: 0.6812
	- F1: 0.7121
	- ROC AUC: 0.8345

- **RandomForest (GridSearchCV)** — najlepsze parametry i metryki:
	- Best params: `{'classifier__max_depth': None, 'classifier__min_samples_split': 2, 'classifier__n_estimators': 50}`
	- Accuracy: 0.8156
	- Precision: 0.8000
	- Recall: 0.6957
	- F1: 0.7442
	- ROC AUC: 0.8178

- **KNN (GridSearchCV)**:
	- Best params: `{'classifier__n_neighbors': 7, 'classifier__p': 1, 'classifier__weights': 'distance'}`
	- Accuracy: 0.8212
	- Precision: 0.8136
	- Recall: 0.6957
	- F1: 0.7500
	- ROC AUC: 0.8109

- **SVM (GridSearchCV)**:
	- Best params: `{'classifier__C': 0.5, 'classifier__gamma': 'scale', 'classifier__kernel': 'rbf'}`
	- Accuracy: 0.7765
	- Precision: 0.7458
	- Recall: 0.6377
	- F1: 0.6875
	- ROC AUC: 0.8437

- **GaussianNB (GridSearchCV)**:
	- Best params: `{'classifier__var_smoothing': 1e-09}`
	- Accuracy: 0.7709
	- Precision: 0.7258
	- Recall: 0.6522
	- F1: 0.6870
	- ROC AUC: 0.8322

Krótka interpretacja hiperparametrów użytych w eksperymentach:

- `KNN`:
	- `n_neighbors` określa, ilu najbliższych sąsiadów bierze udział w głosowaniu. Mniejsze wartości są bardziej „czułe” na szum, większe wygładzają decyzję modelu.
	- `weights='distance'` powoduje, że bliżsi sąsiedzi mają większy wpływ niż dalsi, co zwykle poprawia jakość na danych mieszanych.
	- `p=1` oznacza odległość Manhattan, a `p=2` odległość euklidesową.

- `SVM`:
	- `C` kontroluje karę za błędną klasyfikację; mniejsze wartości dają szerszy margines i mocniejsze uogólnienie, większe bardziej dopasowują model do danych treningowych.
	- `gamma` określa zasięg wpływu pojedynczej obserwacji w kernelu RBF; większe wartości tworzą bardziej lokalne, złożone granice decyzyjne.
	- `kernel='rbf'` pozwala modelować nieliniowe zależności, co jest użyteczne przy kombinacji wieku, płci i klasy biletu.

- `RandomForest`:
	- `n_estimators` to liczba drzew w lesie; większa liczba zwykle stabilizuje wynik, ale zwiększa koszt obliczeń.
	- `max_depth` ogranicza głębokość pojedynczego drzewa; pomaga kontrolować przeuczenie.
	- `min_samples_split` określa minimalną liczbę próbek potrzebną do podziału węzła; większe wartości upraszczają drzewa i mogą poprawić generalizację.

- `GaussianNB`:
	- Model zakłada, że cechy w obrębie klasy mają rozkład normalny i są warunkowo niezależne.
	- `var_smoothing` dodaje małą wartość do wariancji, żeby ustabilizować obliczenia i uniknąć problemów numerycznych.

Te parametry były stworzone osobno dla każdego modelu, dzięki czemu porównanie dotyczyło faktycznie kilku różnych wersji algorytmów, a nie jednego ustawienia domyślnego.

Najważniejsze cechy w Random Forest wskazują, że najwięcej informacji wnosił wiek. W modelu z one‑hot encodingiem pojedyncze kolumny wyglądają tak (zapisano w `rf_feature_importances.csv`):

- `num__age` = 0.4387
- `cat__sex_male` = 0.2054, `cat__sex_female` = 0.1953 (suma dla `sex` ≈ 0.4007)
- `cat__class_1/2/3` sumują się ≈ 0.1606

Uwagi interpretacyjne:
- One‑hot encoding rozdziela wpływ jednej cechy na wiele kolumn — dlatego warto agregować importances po oryginalnej cesze (`sex`, `class`) przy interpretacji.
- Wartość `num__age` była najwyższa w analizie Gini (z `rf_feature_importances.csv`), jednak `feature_importances_` w Random Forest pokazuje tylko spadek nieczystości w drzewach i może faworyzować cechy ciągłe.
- Dlatego główną interpretację wpływu cech na jakość modelu oparto na permutation importance, obliczonym na zbiorze testowym (scoring = F1). Wyniki (zapisane w `rf_permutation_importance.csv`):

- `sex`: mean importance = 0.3038 (std = 0.0492)
- `class`: mean importance = 0.1390 (std = 0.0278)
- `age`: mean importance = 0.1025 (std = 0.0238)

Interpretacja permutation importance:
- Po zastosowaniu permutation importance (które permutuje kolumny wejściowe przed preprocesorem) `sex` okazało się najbardziej krytyczną cechą dla metryki F1 na zbiorze testowym, następnie `class`, a na końcu `age`.
- Różnica między `feature_importances_` a permutation importance wynika z różnych mechanizmów obliczania: Gini mierzy zmniejszenie nieczystości w drzewach, natomiast permutation importance mierzy bezpośredni wpływ danej kolumny na wynik modelu na danym zbiorze.
- W praktyce oznacza to, że `sex` i `class` mają silny wpływ na jakość modelu, a `age` nadal wnosi informację, ale jest mniej istotny niż sugerowałby sam wykres Gini.

## Wygenerowane pliki
- `model_best_logistic_regression.joblib`
- `model_best_knn.joblib`
- `model_best_svm.joblib`
- `model_best_gaussian_nb.joblib`
- `model_best_rf.joblib`
- `best_logistic_regression_confusion_matrix.png`
- `best_logistic_regression_roc.png`
- `best_logistic_regression_pr.png`
- `best_random_forest_confusion_matrix.png`
- `best_random_forest_roc.png`
- `best_random_forest_pr.png`
- `rf_feature_importances.csv`
- `rf_feature_importances.png`
- `training_report.json`
- EDA: `eda_age_distribution.png`, `eda_count_sex.png`, `eda_count_class.png`, `eda_missing_heatmap.png`, `eda_crosstab_sex_survived.csv`, `eda_crosstab_class_survived.csv`

## Wnioski
Pipeline został przygotowany zgodnie z wymaganiami zadania i zapisuje wszystkie kluczowe artefakty. Na podstawie pełnego porównania modeli, a nie jednego metrycznego „zwycięzcy”, najlepszym wyborem jest `LogisticRegression`.

Uzasadnienie wyboru:
- W repeated k-fold CV `LogisticRegression` miała najwyższe średnie `ROC AUC` (około 0.850) i najniższy `log_loss` (około 0.453), czyli najlepiej porządkowała próbki i dawała najbardziej sensowne prawdopodobieństwa.
- Wyniki były stabilne: odchylenia standardowe dla `accuracy`, `F1` i `ROC AUC` były małe, co wskazuje na odporność modelu na zmianę podziału danych.
- `SVM` i `RandomForest` dawały bardzo podobne `accuracy`/`F1`, ale miały słabszą kalibrację prawdopodobieństw, a `RandomForest` miał wyraźnie gorszy `log_loss`.
- `KNN` wyglądał dobrze na pojedynczym podziale testowym, ale w repeated CV był mniej stabilny i miał bardzo wysoki `log_loss`, więc nie jest najlepszym wyborem końcowym.

Jak czytać metryki:
- `Accuracy` pokazuje, jaki odsetek przykładów został sklasyfikowany poprawnie, ale nie mówi nic o rozkładzie błędów między klasami.
- `F1` łączy `precision` i `recall`, więc jest lepszy, gdy chcemy zbalansować fałszywe alarmy i pominięcia.
- `ROC AUC` mierzy zdolność modelu do porządkowania przykładów według ryzyka klasy pozytywnej niezależnie od progu decyzyjnego.
- `log_loss` karze za błędne, ale pewne predykcje probabilistyczne, więc jest dobrym wskaźnikiem jakości samych prawdopodobieństw.

W praktyce oznacza to, że `LogisticRegression` jest tutaj najlepszym kompromisem między jakością predykcji, stabilnością i interpretowalnością. `SVM` jest bardzo blisko i może być alternatywą, ale jeśli trzeba wskazać jeden model końcowy do projektu, to `LogisticRegression` jest najbardziej obroniona merytorycznie.

