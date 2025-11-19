import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.calibration import CalibratedClassifierCV
from sklearn.metrics import average_precision_score, roc_auc_score, brier_score_loss


# ========================================================
#  PREPROCESSOR (Yeni dataset için uyarlanmış HATASIZ versiyon)
# ========================================================
def make_preprocessor():

    # --- Sayısal kolonlar ---
    numeric_cols = [
        "age",
        "lead_time_days",
        "previous_appointments",
        "previous_noshow",
        "past_appointments_patient",
        "past_noshow_count",
        "historical_noshow_rate_patient"
    ]

    # --- Kategorik kolonlar ---
    categorical_cols = [
        "appointment_id",
        "patient_id",
        "created_channel",
        "department",
        "doctor_id",
        "sex",
        "neighborhood",
        "insurance_type",
        "dow_hour"
    ]

    numeric_transformer = Pipeline(steps=[
        ("scaler", StandardScaler())
    ])

    categorical_transformer = Pipeline(steps=[
        ("onehot", OneHotEncoder(handle_unknown="ignore"))
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", numeric_transformer, numeric_cols),
            ("cat", categorical_transformer, categorical_cols),
        ]
    )

    return preprocessor


# ========================================================
#  ZAMANA DAYALI SPLIT
# ========================================================
def time_based_split(df: pd.DataFrame, time_col='appointment_timestamp', test_start=None, val_start=None):

    df = df.sort_values(time_col)

    if val_start is None or test_start is None:
        raise ValueError("val_start ve test_start zorunludur!")

    train_df = df[df[time_col] < val_start]
    val_df = df[(df[time_col] >= val_start) & (df[time_col] < test_start)]
    test_df = df[df[time_col] >= test_start]

    return train_df, val_df, test_df


# ========================================================
#  MODEL EĞİTİMİ + KALİBRASYON + METRİKLER
# ========================================================
def train_and_eval(df: pd.DataFrame, label_col='target_noshow',
                   model_type='lr', val_start=None, test_start=None):

    train_df, val_df, test_df = time_based_split(df, test_start=test_start, val_start=val_start)

    y_train = train_df[label_col]
    y_val = val_df[label_col]
    y_test = test_df[label_col]

    X_train = train_df.drop(columns=[label_col])
    X_val = val_df.drop(columns=[label_col])
    X_test = test_df.drop(columns=[label_col])

    pre = make_preprocessor()

    if model_type == "lr":
        base_model = LogisticRegression(max_iter=1000, class_weight="balanced")
    elif model_type == "rf":
        base_model = RandomForestClassifier(
            n_estimators=400,
            random_state=42,
            class_weight="balanced_subsample",
            n_jobs=-1
        )
    else:
        raise ValueError("model_type = 'lr' veya 'rf' olmalıdır!")

    pipe = Pipeline([("pre", pre), ("clf", base_model)])
    clf = CalibratedClassifierCV(pipe, cv=3, method="isotonic")
    clf.fit(X_train, y_train)

    def metrics_fn(X, y, name):
        p = clf.predict_proba(X)[:, 1]
        return {
            "split": name,
            "n": len(y),
            "roc_auc": roc_auc_score(y, p),
            "pr_auc": average_precision_score(y, p),
            "brier": brier_score_loss(y, p)
        }

    results = pd.DataFrame([
        metrics_fn(X_train, y_train, "train"),
        metrics_fn(X_val, y_val, "val"),
        metrics_fn(X_test, y_test, "test"),
    ])

    return clf, results


# ========================================================
#  MALİYET TAHMİNİNE GÖRE EN İYİ EŞİK
# ========================================================
def best_threshold_by_cost(y_true, p,
                           cost_tp=50, cost_fp=-10,
                           cost_fn=-100, cost_tn=0):

    thresholds = np.linspace(0, 1, 501)
    best_th, best_gain = 0.5, -1e18

    for th in thresholds:
        y_pred = (p >= th).astype(int)

        tp = ((y_pred == 1) & (y_true == 1)).sum()
        fp = ((y_pred == 1) & (y_true == 0)).sum()
        fn = ((y_pred == 0) & (y_true == 1)).sum()
        tn = ((y_pred == 0) & (y_true == 0)).sum()

        gain = tp * cost_tp + fp * cost_fp + fn * cost_fn + tn * cost_tn

        if gain > best_gain:
            best_gain = gain
            best_th = th

    return best_th, best_gain
