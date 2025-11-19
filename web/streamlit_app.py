import streamlit as st
import requests
import datetime

st.title("📅 No-Show Appointment Prediction")
st.write("Hastanın özelliklerini girerek randevuya gelmeme olasılığını tahmin edin.")

# Kullanıcıdan girdi al
age = st.number_input("Age", min_value=0, max_value=120, value=32)
sex = st.selectbox("Sex", ["F", "M"])
previous_appointments = st.number_input("Previous Appointments", min_value=0, value=5)
previous_noshow = st.number_input("Previous No-Shows", min_value=0, value=1)
past_appointments_patient = st.number_input("Past Appointments (Patient)", min_value=0, value=10)
past_noshow_count = st.number_input("Past No-Show Count", min_value=0, value=2)

neighborhood = st.text_input("Neighborhood", "Central")
department = st.text_input("Department", "Cardiology")
insurance_type = st.text_input("Insurance Type", "Private")
created_channel = st.text_input("Created Channel", "Online")
lead_time_days = st.number_input("Lead Time (days)", min_value=0, value=3)

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

    # MODELİN İSTEDİĞİ DUMMY KOLONLAR
    "appointment_id": "A0000",
    "patient_id": "P0000",
    "doctor_id": "D00",
    "dow_hour": "Mon_08",
    "historical_noshow_rate_patient": 0.0
}


if st.button("Tahmin Et"):
    response = requests.post("http://127.0.0.1:5000/predict", json=data)

    if response.status_code == 200:
        result = response.json()
        st.success(f"📌 Prediction: {result['prediction']}")
        st.info(f"🎯 Probability: {result['probability_no_show']:.3f}")
    else:
        st.error("API Hatası: " + response.text)
