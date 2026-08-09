Podsumowanie

Wprowadza ostateczn─ş wersj─ş projektu „Projekt3” zawieraj─ş kompletny, powtarzalny pipeline klasyfikacyjny do przewidywania prze┼╝ycia pasa┼╝erów Titanica na podstawie cech `age`, `sex` i `class`.

Zawartość zmian

- Skrypty treningowe i ewaluacyjne: `train.py`, `compute_permutation_importance.py`.
- Notebook z EDA: `notebook.ipynb`.
- Zaktualizowane dokumenty: `README.md`, `report.md`, `training_report.json`.
- Dane źródłowe i przetworzone: `data/titanic_full.csv`, `data/titanic_clean.csv`.
- Kluczowe artefakty wynikowe: wykresy metryk, macierze pomy┼éek, `repeated_cv_summary.csv`, `rf_feature_importances.csv` oraz pliki modeli (`*.joblib`) (modele zosta┼é dołączone do repo jako pojedyncze pliki; rekomenduje si─Ö ew. przeniesienie do release jako assets w razie potrzeby).

Weryfikacja zmian

1. Przejrze─ç plik `report.md` i wygenerowane wykresy w katalogu repozytorium.
2. Uruchomi─ç `train.py` w wirtualnym ┼úrodowisku zgodnie z `README.md` by powtórzy─ç trening i zweryfikowa─ç artefakty.
3. Por├│wnanie wyników z `repeated_cv_summary.csv` oraz `training_report.json`.

Metadane

- Branch źr├│d┼╗owy: `finalize/Projekt3`
- Branch docelowy: `main`
- Commit zawieraj─Öcy zmiany: f6b83bf513b0f3231e51ebd0f5e121ce0c4c299b

Checklist (do review)

- [ ] Dokumentacja (`README.md`, `report.md`) jest kompletna i zrozumiała.
- [ ] Zawarte pliki są jedynie niezb─ůdne artefakty końcowe (brak tymczasowych plik├│w).
- [ ] Modele binarne (`*.joblib`) zosta┼é dodane zgodnie z ustaleniami lub przygotowane jako assets releasu.
- [ ] Testy/trening uruchamiaj─ů si─Ö lokalnie zgodnie z instrukcj─ş w `README.md`.
- [ ] Pliki danych w katalogu `data/` s─ů zgodne ze zgodami licencyjnymi i anonimowe.

Prosz─ç o review i ewentualne uwagi; po akceptacji zostanie wykonane scalanie do `main` oraz opcjonalne utworzenie releasu v1.0.0.
