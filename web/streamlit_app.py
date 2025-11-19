import streamlit as st
import requests
import pandas as pd

# =========================================================
# 🔹 Dataset’ten departman, mahalle, sigorta, kanal bilgilerini çek
# =========================================================
DATA_PATH = "data/raw/no_show_dataset.csv"

df = pd.read_csv(DATA_PATH)

raw_departments = sorted(df["department"].dropna().unique().tolist())
raw_neighborhoods = sorted(df["neighborhood"].dropna().unique().tolist())
raw_insurance_types = sorted(df["insurance_type"].dropna().unique().tolist())
raw_channels = sorted(df["created_channel"].dropna().unique().tolist())

# =========================================================
#  🔹 Türkçe – İngilizce eşleştirmeler
# =========================================================

SEX_MAP = {
    "Kadın": "F",
    "Erkek": "M"
}

NEIGHBORHOOD_MAP = {
    "Central": "Merkez",
    "North": "Kuzey",
    "South": "Güney",
    "East": "Doğu",
    "West": "Batı"
}
NEIGHBORHOOD_REVERSE = {v: k for k, v in NEIGHBORHOOD_MAP.items()}

DEPARTMENT_MAP = {
    "Cardiology": "Kardiyoloji",
    "Dermatology": "Dermatoloji",
    "Neurology": "Nöroloji",
    "Orthopedics": "Ortopedi",
    "Pediatrics": "Pediatri",
    "Oncology": "Onkoloji",
    "General Medicine": "Dahiliye"
}
DEPARTMENT_REVERSE = {v: k for k, v in DEPARTMENT_MAP.items()}

INSURANCE_MAP = {
    "General": "Genel",
    "Private": "Özel"
}
INSURANCE_REVERSE = {v: k for k, v in INSURANCE_MAP.items()}

CHANNEL_MAP = {
    "CallCenter": "Çağrı Merkezi",
    "Online": "Online",
    "Onsite": "Yerinde"
}
CHANNEL_REVERSE = {v: k for k, v in CHANNEL_MAP.items()}

# =========================================================
# 🔹 Streamlit Arayüz
# =========================================================

st.title("🗓️ Randevuya Gelmeme (No-Show) Tahmini")
st.write("Lütfen hastanın bilgilerini doldurunuz.")

col1, col2 = st.columns(2)

with col1:
    age = st.number_input("Yaş", min_value=0, max_value=120, value=30)
with col2:
    sex_tr = st.selectbox("Cinsiyet", ["Kadın", "Erkek"])
    sex = SEX_MAP[sex_tr]

with col1:
    previous_appointments = st.number_input("Önceki Randevu Sayısı", min_value=0, value=5)
with col2:
    previous_noshow = st.number_input("Önceki No-Show Sayısı", min_value=0, value=1)

with col1:
    past_appointments_patient = st.number_input("Geçmiş Toplam Randevular", min_value=0, value=10)
with col2:
    past_noshow_count = st.number_input("Geçmiş No-Show Sayısı", min_value=0, value=2)

with col1:
    lead_time_days = st.number_input("Randevuya Kalan Gün (Lead Time)", min_value=0, value=3)

# Bölge dropdown'u (Türkçe gösteriliyor)
neighborhood_tr_list = [NEIGHBORHOOD_MAP.get(n, n) for n in raw_neighborhoods]
with col1:
    neighborhood_tr = st.selectbox("Bölge", neighborhood_tr_list)
    neighborhood = NEIGHBORHOOD_REVERSE.get(neighborhood_tr, neighborhood_tr)

# Departman dropdown'u (Türkçe)
department_tr_list = [DEPARTMENT_MAP.get(d, d) for d in raw_departments]
with col2:
    department_tr = st.selectbox("Departman", department_tr_list)
    department = DEPARTMENT_REVERSE.get(department_tr, department_tr)

# Sigorta dropdown'u
insurance_tr_list = [INSURANCE_MAP.get(i, i) for i in raw_insurance_types]
with col1:
    insurance_type_tr = st.selectbox("Sigorta Türü", insurance_tr_list)
    insurance_type = INSURANCE_REVERSE.get(insurance_type_tr, insurance_type_tr)

# Kanal dropdown'u
channel_tr_list = [CHANNEL_MAP.get(c, c) for c in raw_channels]
with col2:
    created_channel_tr = st.selectbox("Randevu Oluşturma Kanalı", channel_tr_list)
    created_channel = CHANNEL_REVERSE.get(created_channel_tr, created_channel_tr)

# =========================================================
#  API'ye gönderilecek veri
# =========================================================

data = {
    "age": age,
    "sex": sex,
    "previous_appointments": previous_appointments,
    "previous_noshow": previous_noshow,
    "past_appointments_patient": past_appointments_patient,
    "past_noshow_count": past_noshow_count,
    "neighborhood": neighborhood,
    "department": department,
    "insurance_type": insurance_type,
    "created_channel": created_channel,
    "lead_time_days": lead_time_days,
    "appointment_id": "A0000",
    "patient_id": "P0000",
    "doctor_id": "D00",
    "dow_hour": "Mon_08",
    "historical_noshow_rate_patient": 0.0
}

# =========================================================
# 🔮 Tahmin Butonu
# =========================================================

if st.button("Tahmin Et"):
    response = requests.post("http://127.0.0.1:5000/predict", json=data)

    if response.status_code == 200:
        result = response.json()

        pred_text = "Hasta Gelir" if result['prediction'] == 0 else "Hasta Gelmez"
        color = "#007F5F" if result["prediction"] == 0 else "#D00000"

        st.markdown(
            f"""
            <div style="
                background-color:{color};
                padding:12px;
                border-radius:8px;
                color:white;
                font-size:18px;
                text-align:center;">
                ✓ Tahmin: {pred_text}
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown(
            f"""
            <div style="
                background-color:#003566;
                padding:10px;
                border-radius:8px;
                color:white;
                font-size:16px;
                text-align:center;
                margin-top:10px;">
                📊 No-Show Olasılığı: {result['probability_no_show']:.3f}
            </div>
            """,
            unsafe_allow_html=True
        )
    else:
        st.error("❌ API Hatası: " + response.text)
