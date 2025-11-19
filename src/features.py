import pandas as pd

def build_patient_history(df: pd.DataFrame, cutoff_col='appointment_timestamp') -> pd.DataFrame:
    """Her hastanın geçmiş no-show istatistiklerini hesaplar (sızıntısız)."""
    # Randevuları hastaya göre sırala
    df = df.sort_values(["patient_id", cutoff_col])

    # Hasta bazında geçmiş randevu sayısı
    grp = df.groupby('patient_id', sort=False)
    df['past_appointments_patient'] = grp.cumcount()

    # Geçmiş no-show sayısı (her hasta için birikimli)
    df['past_noshow_count'] = (
        grp['target_noshow'].shift(1).fillna(0).groupby(df['patient_id']).cumsum()
    )

    # Geçmiş no-show oranı = geçmiş no-show / geçmiş randevular
    df['historical_noshow_rate_patient'] = (
        df['past_noshow_count'] / df['past_appointments_patient'].replace(0, pd.NA)
    ).fillna(0.0)

    return df


# Modelde kullanılacak sütun grupları
CATEGORICAL_LOW_CARD = ['sex', 'created_channel', 'department']
CATEGORICAL_HIGH_CARD = ['doctor_id', 'neighborhood', 'dow_hour']
NUMERIC_FEATURES = [
    'age', 'lead_time_days', 'past_appointments_patient',
    'historical_noshow_rate_patient', 'sms_received_before',
    'call_attempts_before'
]
