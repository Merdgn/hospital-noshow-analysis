import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss

from .features import CATEGORICAL_LOW_CARD, CATEGORICAL_HIGH_CARD, NUMERIC_FEATURES


def make_preprocessor():
    """Sayısal ve kategorik özellikler için ön işleme pipeline'ı kurar."""
    numeric = Pipeline([
        ("imputer", SimpleImputer(strategy="median")),
        ("scaler", StandardScaler())
    ])

    low_card = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown='ignore', min_frequency=20))
    ])

    high_card = Pipeline([
        ("imputer", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown='ignore', max_categories=50))
    ])

    pre = ColumnTransformer([
        ("num", numeric, NUMERIC_FEATURES),
        ("low", low_card, CATEGORICAL_LOW_CARD),
        ("high", high_card, CATEGORICAL_HIGH_CARD)
    ])
    return pre


def time_based_split(df: pd.DataFrame, time_col='appointment_timestamp', test_start=None, val_start=None):
    """Zamana göre eğitim, doğrulama ve test kümelerini ayırır."""
    df = df.sort_values(time_col)
    if val_start is None or test_start is None:
        raise ValueError("val_start ve test_start verilmelidir")
    X_train = df[df[time_col] < val_start]
    X_val = df[(df[time_col] >= val_start) & (df[time_col] < test_start)]
    X_test = df[df[time_col] >= test_start]
    return X_train, X_val, X_test


def fit_calibrated(model, X, y, method="isotonic"):
    """Modeli kalibre eder (olasılıkları daha doğru hale getirir)."""
    return CalibratedClassifierCV(model, method=method, cv=3)


def train_and_eval(df: pd.DataFrame, label_col='target_noshow', model_type='lr', val_start=None, test_start=None):
    """Veriyi bölüp modeli eğitir ve temel metrikleri döndürür."""
    X_train, X_val, X_test = time_based_split(df, test_start=test_start, val_start=val_start)
    y_train = X_train[label_col]
    y_val = X_val[label_col]
    y_test = X_test[label_col]

    X_train = X_train.drop(columns=[label_col])
    X_val = X_val.drop(columns=[label_col])
    X_test = X_test.drop(columns=[label_col])

    pre = make_preprocessor()

    if model_type == 'lr':
        base = LogisticRegression(max_iter=1000, class_weight='balanced', C=1.0)
    elif model_type == 'rf':
        base = RandomForestClassifier(
            n_estimators=400, min_samples_leaf=5,
            class_weight='balanced_subsample', n_jobs=-1, random_state=42
        )
    else:
        raise ValueError("model_type 'lr' veya 'rf' olmalı")

    pipe = Pipeline([("pre", pre), ("clf", base)])
    clf = fit_calibrated(pipe, X_train, y_train, method="isotonic")
    clf.fit(X_train, y_train)

    def metrics(X, y, split_name):
        p = clf.predict_proba(X)[:, 1]
        return {
            "split": split_name,
            "n": int(len(y)),
            "pr_auc": float(average_precision_score(y, p)),
            "roc_auc": float(roc_auc_score(y, p)),
            "brier": float(brier_score_loss(y, p))
        }

    results = [
        metrics(X_train, y_train, "train"),
        metrics(X_val, y_val, "val"),
        metrics(X_test, y_test, "test")
    ]
    return clf, pd.DataFrame(results)


def best_threshold_by_cost(y_true, p, cost_tp=50, cost_fp=-15, cost_fn=-100, cost_tn=0):
    """Maliyet matrisine göre en kârlı karar eşiğini bulur."""
    thresholds = np.linspace(0, 1, 501)
    best_th, best_gain = 0.5, -np.inf
    for th in thresholds:
        yhat = (p >= th).astype(int)
        tp = ((yhat == 1) & (y_true == 1)).sum()
        fp = ((yhat == 1) & (y_true == 0)).sum()
        fn = ((yhat == 0) & (y_true == 1)).sum()
        tn = ((yhat == 0) & (y_true == 0)).sum()
        gain = tp * cost_tp + fp * cost_fp + fn * cost_fn + tn * cost_tn
        if gain > best_gain:
            best_gain, best_th = int(gain), float(th)
    return best_th, best_gain
