import os
import numpy as np
import pandas as pd
import joblib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import seaborn as sns

from sklearn.model_selection import train_test_split, GridSearchCV, learning_curve, cross_validate, RepeatedStratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    log_loss,
    roc_auc_score,
    confusion_matrix,
    roc_curve,
    precision_recall_curve,
    auc as _auc
)


def load_and_clean(path_full='data/titanic_full.csv', path_clean='data/titanic_clean.csv'):
    if os.path.exists(path_clean):
        df = pd.read_csv(path_clean)
        expected_cols = ['age', 'sex', 'class', 'survived']
        if all(col in df.columns for col in expected_cols):
            return df[expected_cols].copy()

    # Use the full Titanic dataset as the single source of truth
    source = path_full
    if not os.path.exists(source):
        raise FileNotFoundError(f"No data file found at {source}")

    df = pd.read_csv(source)
    df.columns = df.columns.str.strip()

    # Normalize and map common original column names to expected lowercase names
    # Age
    if 'age' not in df.columns and 'Age' in df.columns:
        df['age'] = pd.to_numeric(df['Age'], errors='coerce')
    else:
        df['age'] = pd.to_numeric(df.get('age', pd.Series(dtype=float)), errors='coerce')
    age_median = df['age'].median()
    if pd.isna(age_median):
        age_median = df['age'].dropna().median() if not df['age'].dropna().empty else 30
    df['age'] = df['age'].fillna(age_median)

    # Sex
    if 'sex' not in df.columns and 'Sex' in df.columns:
        df['sex'] = df['Sex'].astype(str).str.strip().replace({'': None, 'nan': None})
    else:
        df['sex'] = df.get('sex', pd.Series(dtype=str)).astype(str).str.strip().replace({'': None, 'nan': None})

    # Class / Pclass
    if 'class' not in df.columns and 'Pclass' in df.columns:
        df['class'] = df['Pclass'].astype(str)
    else:
        df['class'] = df.get('class', pd.Series(dtype=str)).astype(str).str.strip().replace({'': None, 'nan': None})

    # Survived
    df['survived'] = pd.to_numeric(df.get('survived', df.get('Survived', pd.Series(dtype=int))), errors='coerce').fillna(0).astype(int)

    # Keep only the final, minimal dataset used by the project
    df = df[['age', 'sex', 'class', 'survived']].copy()

    # Save cleaned copy
    os.makedirs(os.path.dirname(path_clean), exist_ok=True)
    df.to_csv(path_clean, index=False)
    print(f'Wczytano i zapisano oczyszczone dane do {path_clean}')
    return df


def build_preprocessor(numeric_features, categorical_features):
    numeric_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='median')),
        ('scaler', StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ('imputer', SimpleImputer(strategy='most_frequent')),
        ('onehot', OneHotEncoder(handle_unknown='ignore', sparse_output=False))
    ])

    preprocessor = ColumnTransformer(transformers=[
        ('num', numeric_transformer, numeric_features),
        ('cat', categorical_transformer, categorical_features)
    ])
    return preprocessor


def evaluate_model(model, X_test, y_test, prefix='model'):
    preds = model.predict(X_test)
    probs = None
    try:
        probs = model.predict_proba(X_test)[:, 1]
    except Exception:
        pass

    acc = accuracy_score(y_test, preds)
    prec = precision_score(y_test, preds, zero_division=0)
    rec = recall_score(y_test, preds, zero_division=0)
    f1 = f1_score(y_test, preds, zero_division=0)
    auc = roc_auc_score(y_test, probs) if probs is not None else None
    loss = log_loss(y_test, probs, labels=[0, 1]) if probs is not None and len(set(y_test)) > 1 else None

    print(f"{prefix} - Accuracy: {acc:.4f}, Precision: {prec:.4f}, Recall: {rec:.4f}, F1: {f1:.4f}")
    if auc is not None:
        print(f"{prefix} - ROC AUC: {auc:.4f}")
    if loss is not None:
        print(f"{prefix} - Log loss: {loss:.4f}")

    # Confusion matrix plot (force 2x2 labels to keep consistent visualization)
    labels = [0, 1]
    cm = confusion_matrix(y_test, preds, labels=labels)
    plt.figure(figsize=(4, 3))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=labels, yticklabels=labels)
    plt.title(f'Confusion matrix - {prefix}')
    plt.xlabel('Predicted')
    plt.ylabel('Actual')
    out_png = f'{prefix}_confusion_matrix.png'
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()
    print(f'Saved confusion matrix to {out_png}')

    results = {'accuracy': acc, 'precision': prec, 'recall': rec, 'f1': f1, 'auc': auc, 'log_loss': loss}

    # ROC and PR plots if probabilities available and both classes present
    if probs is not None and len(set(y_test)) > 1:
        fpr, tpr, _ = roc_curve(y_test, probs)
        roc_auc = _auc(fpr, tpr)
        plt.figure()
        plt.plot(fpr, tpr, label=f'ROC (AUC = {roc_auc:.3f})')
        plt.plot([0, 1], [0, 1], linestyle='--', color='gray')
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title(f'ROC Curve - {prefix}')
        plt.legend(loc='lower right')
        roc_png = f'{prefix}_roc.png'
        plt.tight_layout()
        plt.savefig(roc_png)
        plt.close()
        print(f'Saved ROC plot to {roc_png}')

        prec, rec, _ = precision_recall_curve(y_test, probs)
        pr_auc = _auc(rec, prec)
        plt.figure()
        plt.plot(rec, prec, label=f'PR (AUC = {pr_auc:.3f})')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title(f'Precision-Recall Curve - {prefix}')
        plt.legend(loc='lower left')
        pr_png = f'{prefix}_pr.png'
        plt.tight_layout()
        plt.savefig(pr_png)
        plt.close()
        print(f'Saved PR plot to {pr_png}')

        results.update({'roc_curve': roc_png, 'pr_curve': pr_png})

    return results


def train_grid_model(name, pipeline, param_grid, X_train, y_train, X_test, y_test, scoring='f1'):
    cv_folds = 3 if y_train.value_counts().min() >= 3 else 2
    grid = GridSearchCV(pipeline, param_grid, cv=cv_folds, scoring=scoring, n_jobs=-1)
    grid.fit(X_train, y_train)
    print(f'\n{name} GridSearchCV - best params:')
    print(grid.best_params_)

    best_model = grid.best_estimator_
    metrics = evaluate_model(best_model, X_test, y_test, prefix=name)
    metrics['best_params'] = grid.best_params_
    return best_model, metrics


def plot_learning_curve(estimator, X, y, prefix='model', scoring='f1'):
    cv_folds = 3 if y.value_counts().min() >= 3 else 2
    train_sizes, train_scores, val_scores = learning_curve(
        estimator,
        X,
        y,
        cv=cv_folds,
        scoring=scoring,
        n_jobs=-1,
        train_sizes=np.linspace(0.1, 1.0, 5),
        shuffle=True,
        random_state=42,
    )

    train_mean = train_scores.mean(axis=1)
    train_std = train_scores.std(axis=1)
    val_mean = val_scores.mean(axis=1)
    val_std = val_scores.std(axis=1)

    plt.figure(figsize=(6, 4))
    plt.plot(train_sizes, train_mean, marker='o', label='Training score')
    plt.fill_between(train_sizes, train_mean - train_std, train_mean + train_std, alpha=0.15)
    plt.plot(train_sizes, val_mean, marker='o', label='Validation score')
    plt.fill_between(train_sizes, val_mean - val_std, val_mean + val_std, alpha=0.15)
    plt.xlabel('Training examples')
    plt.ylabel(scoring)
    plt.title(f'Learning curve - {prefix}')
    plt.legend(loc='best')
    plt.grid(alpha=0.2)
    out_png = f'{prefix}_learning_curve.png'
    plt.tight_layout()
    plt.savefig(out_png)
    plt.close()
    print(f'Saved learning curve to {out_png}')


def run_repeated_cv(estimator, X, y, prefix='model'):
    cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=42)
    scoring = {
        'accuracy': 'accuracy',
        'f1': 'f1',
        'roc_auc': 'roc_auc',
        'neg_log_loss': 'neg_log_loss'
    }
    scores = cross_validate(estimator, X, y, cv=cv, scoring=scoring, n_jobs=-1, return_train_score=False)

    summary = {
        'model': prefix,
        'accuracy_mean': float(scores['test_accuracy'].mean()),
        'accuracy_std': float(scores['test_accuracy'].std()),
        'f1_mean': float(scores['test_f1'].mean()),
        'f1_std': float(scores['test_f1'].std()),
        'roc_auc_mean': float(scores['test_roc_auc'].mean()),
        'roc_auc_std': float(scores['test_roc_auc'].std()),
        'log_loss_mean': float((-scores['test_neg_log_loss']).mean()),
        'log_loss_std': float((-scores['test_neg_log_loss']).std()),
    }
    print(f"Repeated CV summary for {prefix}: {summary}")
    return summary


def main():
    # Load and clean
    df = load_and_clean()

    # Features and target
    X_raw = df[['age', 'sex', 'class']].copy()
    y = df['survived']

    # Train/test split
    X_train, X_test, y_train, y_test = train_test_split(
        X_raw,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y if y.nunique() > 1 else None,
    )

    numeric_features = ['age']
    categorical_features = ['sex', 'class']
    preprocessor = build_preprocessor(numeric_features, categorical_features)

    # Baseline: Logistic Regression
    pipe_lr = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', LogisticRegression(max_iter=500, random_state=42))])
    lr_grid = {
        'classifier__C': [0.5, 1.0, 2.0],
        'classifier__solver': ['lbfgs']
    }
    best_lr, baseline_metrics = train_grid_model('best_logistic_regression', pipe_lr, lr_grid, X_train, y_train, X_test, y_test)
    joblib.dump(best_lr, 'model_best_logistic_regression.joblib')
    print('Saved best LogisticRegression model to model_best_logistic_regression.joblib')
    plot_learning_curve(best_lr, X_train, y_train, prefix='best_logistic_regression')

    # KNN
    pipe_knn = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', KNeighborsClassifier())])
    knn_grid = {
        'classifier__n_neighbors': [3, 5, 7],
        'classifier__weights': ['uniform', 'distance'],
        'classifier__p': [1, 2]
    }
    best_knn, knn_metrics = train_grid_model('best_knn', pipe_knn, knn_grid, X_train, y_train, X_test, y_test)
    joblib.dump(best_knn, 'model_best_knn.joblib')
    print('Saved best KNN model to model_best_knn.joblib')
    plot_learning_curve(best_knn, X_train, y_train, prefix='best_knn')

    # SVM
    pipe_svm = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', SVC(probability=True, random_state=42))])
    svm_grid = {
        'classifier__C': [0.5, 1, 2],
        'classifier__gamma': ['scale', 0.1],
        'classifier__kernel': ['rbf']
    }
    best_svm, svm_metrics = train_grid_model('best_svm', pipe_svm, svm_grid, X_train, y_train, X_test, y_test)
    joblib.dump(best_svm, 'model_best_svm.joblib')
    print('Saved best SVM model to model_best_svm.joblib')
    plot_learning_curve(best_svm, X_train, y_train, prefix='best_svm')

    # GaussianNB
    pipe_gnb = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', GaussianNB())])
    gnb_grid = {
        'classifier__var_smoothing': [1e-09, 1e-08, 1e-07]
    }
    best_gnb, gnb_metrics = train_grid_model('best_gaussian_nb', pipe_gnb, gnb_grid, X_train, y_train, X_test, y_test)
    joblib.dump(best_gnb, 'model_best_gaussian_nb.joblib')
    print('Saved best GaussianNB model to model_best_gaussian_nb.joblib')
    plot_learning_curve(best_gnb, X_train, y_train, prefix='best_gaussian_nb')

    # RandomForest with GridSearchCV
    pipe_rf = Pipeline(steps=[('preprocessor', preprocessor), ('classifier', RandomForestClassifier(random_state=42))])

    param_grid = {
        'classifier__n_estimators': [50, 100],
        'classifier__max_depth': [None, 5, 10],
        'classifier__min_samples_split': [2, 5]
    }

    cv_folds = 3 if y_train.value_counts().min() >= 3 else 2
    grid = GridSearchCV(pipe_rf, param_grid, cv=cv_folds, scoring='f1', n_jobs=-1)
    grid.fit(X_train, y_train)
    print('\nRandomForest GridSearchCV - best params:')
    print(grid.best_params_)

    best_rf = grid.best_estimator_
    rf_metrics = evaluate_model(best_rf, X_test, y_test, prefix='best_random_forest')
    joblib.dump(best_rf, 'model_best_rf.joblib')
    print('Saved best RandomForest model to model_best_rf.joblib')
    plot_learning_curve(best_rf, X_train, y_train, prefix='best_random_forest')

    # Feature importances (if RandomForest provided feature_importances_)
    try:
        clf = best_rf.named_steps['classifier']
        pre = best_rf.named_steps['preprocessor']
        # Attempt to get feature names
        try:
            feat_names = pre.get_feature_names_out()
        except Exception:
            # Fallback: build names from components
            num_feats = numeric_features
            cat_feats = []
            try:
                onehot = pre.named_transformers_['cat'].named_steps['onehot']
                for f, cats in zip(categorical_features, onehot.categories_):
                    cat_feats.extend([f + '_' + str(c) for c in cats])
            except Exception:
                cat_feats = categorical_features
            feat_names = list(num_feats) + list(cat_feats)

        importances = clf.feature_importances_
        fi = pd.DataFrame({'feature': feat_names, 'importance': importances})
        fi = fi.sort_values('importance', ascending=False)
        fi.to_csv('rf_feature_importances.csv', index=False)
        plt.figure(figsize=(6, 4))
        sns.barplot(data=fi.head(20), x='importance', y='feature')
        plt.title('Random Forest Feature Importances')
        plt.tight_layout()
        fi_png = 'rf_feature_importances.png'
        plt.savefig(fi_png)
        plt.close()
        print(f'Saved feature importances to {fi_png} and rf_feature_importances.csv')
        rf_metrics.update({'feature_importances_csv': 'rf_feature_importances.csv', 'feature_importances_png': fi_png})
    except Exception:
        pass

    # Save summary report
    cv_rows = [
        run_repeated_cv(best_lr, X_train, y_train, prefix='best_logistic_regression'),
        run_repeated_cv(best_knn, X_train, y_train, prefix='best_knn'),
        run_repeated_cv(best_svm, X_train, y_train, prefix='best_svm'),
        run_repeated_cv(best_gnb, X_train, y_train, prefix='best_gaussian_nb'),
        run_repeated_cv(best_rf, X_train, y_train, prefix='best_random_forest'),
    ]
    cv_summary = pd.DataFrame(cv_rows)
    cv_summary.to_csv('repeated_cv_summary.csv', index=False)
    print('Saved repeated CV summary to repeated_cv_summary.csv')

    report = {
        'baseline': baseline_metrics,
        'knn': knn_metrics,
        'svm': svm_metrics,
        'gaussian_nb': gnb_metrics,
        'random_forest': rf_metrics,
        'logistic_regression_best_params': baseline_metrics.get('best_params'),
        'repeated_cv_summary_csv': 'repeated_cv_summary.csv',
        'rf_best_params': grid.best_params_
    }
    pd.Series(report).to_json('training_report.json')
    print('Saved training summary to training_report.json')


if __name__ == '__main__':
    main()
