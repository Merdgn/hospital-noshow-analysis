import pandas as pd
import matplotlib.pyplot as plt
from src.data_prep import load_data, basic_clean
from src.features import build_patient_history
from src.modeling import make_preprocessor
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline

# Veriyi yükle
df = load_data("data/raw/no_show_sample.csv")
df = basic_clean(df)
df = build_patient_history(df)

# Ön işleme
pre = make_preprocessor()
X = df.drop(columns=["target_noshow"])
y = df["target_noshow"]

# Modeller
pipe_lr = Pipeline([("pre", pre), ("clf", LogisticRegression(max_iter=1000))])
pipe_rf = Pipeline([("pre", pre), ("clf", RandomForestClassifier(n_estimators=200, random_state=42))])

pipe_lr.fit(X, y)
pipe_rf.fit(X, y)

# Tahmin DataFrame
preds = pd.DataFrame({
    "patient_id": df["patient_id"],
    "LR_no_show_prob": pipe_lr.predict_proba(X)[:, 1],
    "RF_no_show_prob": pipe_rf.predict_proba(X)[:, 1]
})

# Grafik
plt.figure(figsize=(8, 5))
plt.plot(preds["patient_id"], preds["LR_no_show_prob"], marker="o", label="Lojistik Regresyon", color="royalblue")
plt.plot(preds["patient_id"], preds["RF_no_show_prob"], marker="s", label="Random Forest", color="orange")
plt.title("No-Show Olasılıkları Karşılaştırması")
plt.xlabel("Hasta ID")
plt.ylabel("Gelmememe Olasılığı")
plt.legend()
plt.grid(True)
plt.tight_layout()

# Grafik kaydet
plt.savefig("reports/figures/model_comparison.png", dpi=150)
plt.show()
