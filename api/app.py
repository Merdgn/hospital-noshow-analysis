from flask import Flask, request, jsonify
from flasgger import Swagger
import joblib
import pandas as pd
import os

app = Flask(__name__)
swagger = Swagger(app)

# ===========================
# 🔥 MODELI YÜKLE
# ===========================

MODEL_PATH = os.path.join(os.path.dirname(__file__), "..", "models", "rf_model.pkl")
MODEL_PATH = os.path.abspath(MODEL_PATH)

print("📌 Model Yolu:", MODEL_PATH)

model = joblib.load(MODEL_PATH)


# ===========================
# 🏠 HOME ENDPOINT
# ===========================
@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "No-Show Prediction API çalışıyor!"})


# ===========================
# 🔮 PREDICT ENDPOINT
# ===========================
@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json()
    df = pd.DataFrame([data])

    prob = model.predict_proba(df)[0][1]
    pred = int(model.predict(df)[0])

    return jsonify({
        "prediction": pred,
        "probability_no_show": prob
    })


if __name__ == "__main__":
    app.run(debug=True)
