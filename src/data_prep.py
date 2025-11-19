import pandas as pd

def load_data(path: str) -> pd.DataFrame:
    """CSV dosyasını okur ve tarih alanlarını datetime tipine çevirir."""
    df = pd.read_csv(path, parse_dates=['scheduled_timestamp', 'appointment_timestamp'])
    return df


def basic_clean(df: pd.DataFrame) -> pd.DataFrame:
    """Temel veri temizleme işlemleri."""
    # Yaş aralığı mantıksız olanları çıkar
    df = df[df['age'].between(0, 110)]

    # Randevu tarihi, planlama tarihinden önce olamaz
    df = df[df['appointment_timestamp'] >= df['scheduled_timestamp']]

    # Randevu arası süreyi hesapla (gün cinsinden)
    df['lead_time_days'] = (
        df['appointment_timestamp'] - df['scheduled_timestamp']
    ).dt.total_seconds() / 86400

    # Haftanın günü ve saati özellikleri
    df['dow'] = df['appointment_timestamp'].dt.dayofweek  # 0=Mon
    df['hour'] = df['appointment_timestamp'].dt.hour
    df['dow_hour'] = df['dow'].astype(str) + '_' + df['hour'].astype(str)

    return df
