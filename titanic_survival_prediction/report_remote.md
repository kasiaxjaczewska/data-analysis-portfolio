# Raport ko┼äcowy

## Cel zadania
Celem by┼éo zbudowanie powtarzalnego pipeline'u klasyfikacyjnego do przewidywania prze┼╝ycia pasa┼╝era Titanica na podstawie cech `age`, `sex` oraz `class`.

## Wykonane kroki
1. Przygotowano i oczyszczono dane wej┼Ťciowe, uzupe┼éniaj─ůc braki i normalizuj─ůc format kolumn.
2. Zbudowano pipeline preprocessingu z `ColumnTransformer`, obejmuj─ůcy imputacj─Ö brak├│w, kodowanie cech kategorycznych i skalowanie cech liczbowych.
3. Wytrenowano model bazowy `LogisticRegression`.
4. Rozszerzono eksperyment o dodatkowe modele: `KNN`, `SVM` i `GaussianNB`.
5. Wytrenowano model ulepszony `RandomForestClassifier` z `GridSearchCV`.
6. Zapisano modele, macierze pomy┼éek, ROC/PR oraz feature importances.

## Wyniki
Po uruchomieniu treningu na pe┼énym zbiorze Titanica (`data/titanic_full.csv`) otrzymano miarodajne wyniki na zbiorze testowym (20%):

- **LogisticRegression (baseline)**:
	- Accuracy: 0.7877
	- Precision: 0.7460
	- Recall: 0.6812
	- F1: 0.7121
	- ROC AUC: 0.8345

- **RandomForest (GridSearchCV)** ÔÇö najlepsze parametry i metryki:
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

Kr├│tka interpretacja hiperparametr├│w u┼╝ytych w eksperymentach:

- `KNN`:
	- `n_neighbors` okre┼Ťla, ilu najbli┼╝szych s─ůsiad├│w bierze udzia┼é w g┼éosowaniu. Mniejsze warto┼Ťci s─ů bardziej ÔÇ×czu┼éeÔÇŁ na szum, wi─Öksze wyg┼éadzaj─ů decyzj─Ö modelu.
	- `weights='distance'` powoduje, ┼╝e bli┼╝si s─ůsiedzi maj─ů wi─Ökszy wp┼éyw ni┼╝ dalsi, co zwykle poprawia jako┼Ť─ç na danych mieszanych.
	- `p=1` oznacza odleg┼éo┼Ť─ç Manhattan, a `p=2` odleg┼éo┼Ť─ç euklidesow─ů.

- `SVM`:
	- `C` kontroluje kar─Ö za b┼é─Ödn─ů klasyfikacj─Ö; mniejsze warto┼Ťci daj─ů szerszy margines i mocniejsze uog├│lnienie, wi─Öksze bardziej dopasowuj─ů model do danych treningowych.
	- `gamma` okre┼Ťla zasi─Ög wp┼éywu pojedynczej obserwacji w kernelu RBF; wi─Öksze warto┼Ťci tworz─ů bardziej lokalne, z┼éo┼╝one granice decyzyjne.
	- `kernel='rbf'` pozwala modelowa─ç nieliniowe zale┼╝no┼Ťci, co jest u┼╝yteczne przy kombinacji wieku, p┼éci i klasy biletu.

- `RandomForest`:
	- `n_estimators` to liczba drzew w lesie; wi─Öksza liczba zwykle stabilizuje wynik, ale zwi─Öksza koszt oblicze┼ä.
	- `max_depth` ogranicza g┼é─Öboko┼Ť─ç pojedynczego drzewa; pomaga kontrolowa─ç przeuczenie.
	- `min_samples_split` okre┼Ťla minimaln─ů liczb─Ö pr├│bek potrzebn─ů do podzia┼éu w─Öz┼éa; wi─Öksze warto┼Ťci upraszczaj─ů drzewa i mog─ů poprawi─ç generalizacj─Ö.

- `GaussianNB`:
	- Model zak┼éada, ┼╝e cechy w obr─Öbie klasy maj─ů rozk┼éad normalny i s─ů warunkowo niezale┼╝ne.
	- `var_smoothing` dodaje ma┼é─ů warto┼Ť─ç do wariancji, ┼╝eby ustabilizowa─ç obliczenia i unikn─ů─ç problem├│w numerycznych.

Te parametry by┼éy strojeone osobno dla ka┼╝dego modelu, dzi─Öki czemu por├│wnanie dotyczy┼éo faktycznie kilku r├│┼╝nych wersji algorytm├│w, a nie jednego ustawienia domy┼Ťlnego.

Najwa┼╝niejsze cechy w Random Forest wskazuj─ů, ┼╝e najwi─Öcej informacji wnosi┼é wiek. W modelu z oneÔÇĹhot encodingiem pojedyncze kolumny wygl─ůdaj─ů tak (zapisano w `rf_feature_importances.csv`):

- `num__age` = 0.4387
- `cat__sex_male` = 0.2054, `cat__sex_female` = 0.1953 (suma dla `sex` Ôëł 0.4007)
- `cat__class_1/2/3` sumuj─ů si─Ö Ôëł 0.1606

Uwagi interpretacyjne:
- OneÔÇĹhot encoding rozdziela wp┼éyw jednej cechy na wiele kolumn ÔÇö dlatego warto agregowa─ç importances po oryginalnej cesze (`sex`, `class`) przy interpretacji.
- Warto┼Ť─ç `num__age` by┼éa najwy┼╝sza w analizie Gini (z `rf_feature_importances.csv`), jednak `feature_importances_` w Random Forest pokazuje tylko spadek nieczysto┼Ťci w drzewach i mo┼╝e faworyzowa─ç cechy ci─ůg┼ée.
- Dlatego g┼é├│wn─ů interpretacj─Ö wp┼éywu cech na jako┼Ť─ç modelu oparto na permutation importance, obliczonym na zbiorze testowym (scoring = F1). Wyniki (zapisane w `rf_permutation_importance.csv`):

- `sex`: mean importance = 0.3038 (std = 0.0492)
- `class`: mean importance = 0.1390 (std = 0.0278)
- `age`: mean importance = 0.1025 (std = 0.0238)

Interpretacja permutation importance:
- Po zastosowaniu permutation importance (kt├│re permutuje kolumny wej┼Ťciowe przed preprocesorem) `sex` okaza┼éo si─Ö najbardziej krytyczn─ů cech─ů dla metryki F1 na zbiorze testowym, nast─Öpnie `class`, a na ko┼äcu `age`.
- R├│┼╝nica mi─Ödzy `feature_importances_` a permutation importance wynika z r├│┼╝nych mechanizm├│w obliczania: Gini mierzy zmniejszenie nieczysto┼Ťci w drzewach, natomiast permutation importance mierzy bezpo┼Ťredni wp┼éyw danej kolumny na wynik modelu na danym zbiorze.
- W praktyce oznacza to, ┼╝e `sex` i `class` maj─ů silny wp┼éyw na jako┼Ť─ç modelu, a `age` nadal wnosi informacj─Ö, ale jest mniej istotny ni┼╝ sugerowa┼éby sam wykres Gini.

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
Pipeline zosta┼é przygotowany zgodnie z wymaganiami zadania i zapisuje wszystkie kluczowe artefakty. Na podstawie pe┼énego por├│wnania modeli, a nie jednego metrycznego ÔÇ×zwyci─ÖzcyÔÇŁ, najlepszym wyborem jest `LogisticRegression`.

Uzasadnienie wyboru:
- W repeated k-fold CV `LogisticRegression` mia┼éa najwy┼╝sze ┼Ťrednie `ROC AUC` (oko┼éo 0.850) i najni┼╝szy `log_loss` (oko┼éo 0.453), czyli najlepiej porz─ůdkowa┼éa pr├│bki i dawa┼éa najbardziej sensowne prawdopodobie┼ästwa.
- Wyniki by┼éy stabilne: odchylenia standardowe dla `accuracy`, `F1` i `ROC AUC` by┼éy ma┼ée, co wskazuje na odporno┼Ť─ç modelu na zmian─Ö podzia┼éu danych.
- `SVM` i `RandomForest` dawa┼éy bardzo podobne `accuracy`/`F1`, ale mia┼éy s┼éabsz─ů kalibracj─Ö prawdopodobie┼ästw, a `RandomForest` mia┼é wyra┼║nie gorszy `log_loss`.
- `KNN` wygl─ůda┼é dobrze na pojedynczym podziale testowym, ale w repeated CV by┼é mniej stabilny i mia┼é bardzo wysoki `log_loss`, wi─Öc nie jest najlepszym wyborem ko┼äcowym.

Jak czyta─ç metryki:
- `Accuracy` pokazuje, jaki odsetek przyk┼éad├│w zosta┼é sklasyfikowany poprawnie, ale nie m├│wi nic o rozk┼éadzie b┼é─Öd├│w mi─Ödzy klasami.
- `F1` ┼é─ůczy `precision` i `recall`, wi─Öc jest lepszy, gdy chcemy zbalansowa─ç fa┼észywe alarmy i pomini─Öcia.
- `ROC AUC` mierzy zdolno┼Ť─ç modelu do porz─ůdkowania przyk┼éad├│w wed┼éug ryzyka klasy pozytywnej niezale┼╝nie od progu decyzyjnego.
- `log_loss` karze za b┼é─Ödne, ale pewne predykcje probabilistyczne, wi─Öc jest dobrym wska┼║nikiem jako┼Ťci samych prawdopodobie┼ästw.

W praktyce oznacza to, ┼╝e `LogisticRegression` jest tutaj najlepszym kompromisem mi─Ödzy jako┼Ťci─ů predykcji, stabilno┼Ťci─ů i interpretowalno┼Ťci─ů. `SVM` jest bardzo blisko i mo┼╝e by─ç alternatyw─ů, ale je┼Ťli trzeba wskaza─ç jeden model ko┼äcowy do projektu, to `LogisticRegression` jest najbardziej obroniona merytorycznie.

