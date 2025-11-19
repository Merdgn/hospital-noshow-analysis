# src/generate_dataset.py

import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from pathlib import Path


def main(n_rows: int = 500):

    rng = np.random.default_rng(42)

    # Proje kökünü bul (src'nin bir üstü)
    project_root = Path(__file__).resolve().parents[1]
    out_path = project_root / "data" / "raw" / "no_show_dataset.csv"

    # Randevu tarih aralığı: 2025-12-01 ile 2027-12-31 arası
    start_apt = datetime(2025, 12, 1)
    end_apt = datetime(2027, 12, 31)
    total_days = (end_apt - start_apt).days

    patient_ids = [f"P{i:04d}" for i in range(1, 501)]   # 500 hasta
    doctor_ids = [f"D{i:02d}" for i in range(1, 51)]     # 50 doktor
    departments = [
        "Cardiology", "Orthopedics", "Neurology",
        "Dermatology", "Pediatrics", "Internal",
        "ENT", "Gynecology"
    ]
    neighborhoods = [
        "Central", "North", "South", "East",
        "West", "SuburbA", "SuburbB", "Rural"
    ]
    channels = ["Online", "CallCenter", "Onsite"]
    insurance_types = ["General", "Private", "None"]

    rows = []

    for i in range(n_rows):
        # Randevu tarihi
        day_offset = int(rng.integers(0, total_days + 1))
        hour = int(rng.choice([8, 9, 10, 11, 13, 14, 15, 16, 17]))
        appt_dt = start_apt + timedelta(days=day_offset, hours=hour)

        # Planlama ile randevu arası: 0–60 gün
        lead_days = int(rng.integers(0, 61))
        sched_dt = appt_dt - timedelta(days=lead_days)

        patient = rng.choice(patient_ids)
        age = int(rng.integers(0, 91))
        sex = rng.choice(["F", "M"])
        dept = rng.choice(departments)
        doctor = rng.choice(doctor_ids)
        channel = rng.choice(channels)
        neighborhood = rng.choice(neighborhoods)
        insurance = rng.choice(insurance_types)
        sms = int(rng.choice([0, 1], p=[0.3, 0.7]))  # %70 SMS gönderilmiş

        # Geçmiş randevu / no-show bilgisi
        prev_apps = int(rng.integers(0, 11))  # 0–10 geçmiş randevu
        if prev_apps > 0:
            prev_noshow = int(rng.integers(0, prev_apps + 1))
            history_rate = prev_noshow / prev_apps
        else:
            prev_noshow = 0
            history_rate = 0.0

        # No-show olasılığını gerçekçi faktörlere göre hesapla
        p = 0.15  # temel risk

        # Geçmişte sık no-show yapanlarda risk yüksek
        p += 0.12 * history_rate

        # Randevu çok önceden alınmışsa
        if lead_days > 30:
            p += 0.08

        # Akşamüstü randevuları
        if appt_dt.hour >= 15:
            p += 0.05

        # Sigortası olmayanlarda risk daha yüksek olsun
        if insurance == "None":
            p += 0.05

        # Online alanlarda biraz daha risk
        if channel == "Online":
            p += 0.03

        # SMS hatırlatması alanlarda risk azalsın
        if sms == 1:
            p -= 0.06

        # Çocuk ve yaşlılarda hafif değişiklikler
        if age < 18:
            p += 0.03
        if age > 65:
            p += 0.02

        # Olasılığı sınırla
        p = float(np.clip(p, 0.01, 0.8))

        target = int(rng.random() < p)  # 1 = gelmedi, 0 = geldi

        rows.append(
            {
                "appointment_id": f"A{i + 1:05d}",
                "patient_id": patient,
                "scheduled_timestamp": sched_dt,
                "appointment_timestamp": appt_dt,
                "created_channel": channel,
                "department": dept,
                "doctor_id": doctor,
                "age": age,
                "sex": sex,
                "neighborhood": neighborhood,
                "insurance_type": insurance,
                "sms_received": sms,
                "previous_appointments": prev_apps,
                "previous_noshow": prev_noshow,
                "target_noshow": target,
            }
        )

    df = pd.DataFrame(rows)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_path, index=False)
    print(f"✅ Veri seti kaydedildi: {out_path}")
    print(f"Toplam satır sayısı: {len(df)}")


if __name__ == "__main__":
    main()
