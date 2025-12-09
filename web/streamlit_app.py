import streamlit as st
import requests

# =========================================================
# 🌈 Özel CSS – Modern kart tasarımı
# =========================================================
st.markdown(
    """
    <style>
    /* Genel sayfa genişliği */
    .main > div {
        padding-top: 2rem;
    }

    .app-container {
        max-width: 900px;
        margin: 0 auto;
    }

    /* Başlık */
    .app-title {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 2.4rem;
        font-weight: 700;
        color: #123047;
        margin-bottom: 0.25rem;
    }

    .app-icon {
        font-size: 2.8rem;
    }

    .app-subtitle {
        color: #4a5568;
        font-size: 0.95rem;
        margin-bottom: 1.5rem;
    }

    /* Adım göstergesi */
    .step-indicator {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.85rem;
        border-radius: 999px;
        background: #e3f2fd;
        color: #0f4c75;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 0.75rem;
    }

    .step-indicator span.step-number {
        background: #0f4c75;
        color: white;
        border-radius: 999px;
        padding: 0.15rem 0.55rem;
        font-size: 0.8rem;
    }

    /* Kartlar */
    .step-card {
        background-color: #ffffff;
        padding: 1.5rem 1.75rem;
        border-radius: 1rem;
        box-shadow: 0 8px 24px rgba(15, 76, 117, 0.04);
        border: 1px solid #edf2f7;
        margin-bottom: 1.25rem;
    }

    .step-card h3 {
        margin-top: 0;
        margin-bottom: 0.85rem;
        font-size: 1.1rem;
        color: #123047;
    }

    /* Butonlar */
    .stButton > button {
        width: 100%;
        border-radius: 999px;
        font-weight: 600;
        padding: 0.55rem 1rem;
        border: none;
        background: #0f4c75;
        color: #ffffff;
        transition: all 0.15s ease-in-out;
    }

    .stButton > button:hover {
        background: #13689e;
        transform: translateY(-1px);
    }

    .stButton.back-btn > button {
        background: #e2e8f0;
        color: #2d3748;
    }

    .stButton.back-btn > button:hover {
        background: #cbd5e0;
    }

    /* Sonuç kartları */
    .result-card-success {
        background: #0f9d58;
        color: white;
        padding: 0.9rem 1.2rem;
        border-radius: 0.9rem 0.9rem 0 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-weight: 600;
        font-size: 0.95rem;
    }

    .result-card-success span.icon {
        font-size: 1.2rem;
    }

    .result-card-danger {
        background: #d93025;
        color: white;
        padding: 0.9rem 1.2rem;
        border-radius: 0.9rem 0.9rem 0 0;
        display: flex;
        align-items: center;
        gap: 0.6rem;
        font-weight: 600;
        font-size: 0.95rem;
    }

    .result-card-danger span.icon {
        font-size: 1.2rem;
    }

    .result-prob {
        background: #123047;
        color: white;
        padding: 0.85rem 1.2rem;
        border-radius: 0 0 0.9rem 0.9rem;
        font-size: 0.9rem;
        display: flex;
        align-items: center;
        gap: 0.6rem;
    }

    .result-prob span.icon {
        font-size: 1.1rem;
    }

    /* Alt bilgi */
    .footer-note {
        margin-top: 1rem;
        font-size: 0.8rem;
        color: #718096;
        text-align: center;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


st.markdown("""
<style>

/* 🔹 Uygulamanın genel arka planı */
[data-testid="stAppViewContainer"] {
    background: radial-gradient(circle at top left,
                                #f7fafc 0%,
                                #eef2f7 35%,
                                #e3f2ff 100%);
}

/* 🔹 Üst barı şeffaf yapalım (Streamlit default header) */
[data-testid="stHeader"] {
    background: rgba(0,0,0,0);
}

/* 🔹 Orta bloğu biraz daraltıp ortaya alalım */
.block-container {
    max-width: 1050px;          /* sayfa genişliği */
    padding-top: 2.5rem;
    padding-bottom: 3rem;
}

/* 🔹 Formun olduğu kısım kart gibi dursun diye hafif gölge + köşe yuvarlama */
section.main > div {
    background-color: #ffffff;
    border-radius: 18px;
    padding: 2.5rem 2.5rem 2rem;
    box-shadow: 0 18px 40px rgba(15, 23, 42, 0.08);
    border: 1px solid rgba(15, 23, 42, 0.04);
}

/* 🔹 “Tahmin Et” ve “Geri / İleri” butonları biraz daha modern dursun */
button[kind="primary"] {
    border-radius: 999px !important;
    font-weight: 600 !important;
}

/* 🔹 Adım göstergeleri / badge’ler varsa biraz daha belirgin dursun */
.step-badge {
    background: #0f766e;
    color: white;
    border-radius: 999px;
    padding: 0.3rem 0.9rem;
    font-size: 0.9rem;
    font-weight: 600;
}

/* 🔹 Tahmin ve olasılık kutularını kart gibi gösteriyorsa; daha yumuşak köşe */
.prediction-box {
    border-radius: 14px;
}

/* Tooltip ikonların (❔) yan yana çok sıkışmaması için küçük boşluk */
.help-icon {
    margin-left: 0.25rem;
    cursor: default;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# 🔢 Sabit seçenekler ve mapping’ler
# =========================================================

# Cinsiyet
SEX_OPTIONS_TR_TO_EN = {
    "Kadın": "F",
    "Erkek": "M",
}

SEX_OPTIONS_TR = list(SEX_OPTIONS_TR_TO_EN.keys())

# Departmanlar
DEPARTMENT_TR_TO_EN = {
    "Kardiyoloji": "Cardiology",
    "Dahiliye": "Internal",
    "Nöroloji": "Neurology",
    "Ortopedi": "Orthopedics",
    "Dermatoloji": "Dermatology",
    "Psikiyatri": "Psychiatry",
    "KBB": "ENT",
    "Genel Cerrahi": "GeneralSurgery",
}

DEPARTMENT_TR = list(DEPARTMENT_TR_TO_EN.keys())

# Sigorta
INSURANCE_TR_TO_EN = {
    "Genel": "General",
    "Özel": "Private",
}
INSURANCE_TR = list(INSURANCE_TR_TO_EN.keys())

# Randevu kanalı
CHANNEL_TR_TO_EN = {
    "Çağrı Merkezi": "CallCenter",
    "Online": "Online",
    "Hastane": "Onsite",
}
CHANNEL_TR = list(CHANNEL_TR_TO_EN.keys())

# 81 il – model için şimdilik hepsini "Central" olarak işliyoruz
CITIES = [
    "Adana", "Adıyaman", "Afyonkarahisar", "Ağrı", "Aksaray", "Amasya", "Ankara",
    "Antalya", "Ardahan", "Artvin", "Aydın", "Balıkesir", "Bartın", "Batman",
    "Bayburt", "Bilecik", "Bingöl", "Bitlis", "Bolu", "Burdur", "Bursa",
    "Çanakkale", "Çankırı", "Çorum", "Denizli", "Diyarbakır", "Düzce", "Edirne",
    "Elazığ", "Erzincan", "Erzurum", "Eskişehir", "Gaziantep", "Giresun",
    "Gümüşhane", "Hakkari", "Hatay", "Iğdır", "Isparta", "İstanbul", "İzmir",
    "Kahramanmaraş", "Karabük", "Karaman", "Kars", "Kastamonu", "Kayseri",
    "Kırıkkale", "Kırklareli", "Kırşehir", "Kilis", "Kocaeli", "Konya",
    "Kütahya", "Malatya", "Manisa", "Mardin", "Mersin", "Muğla", "Muş",
    "Nevşehir", "Niğde", "Ordu", "Osmaniye", "Rize", "Sakarya", "Samsun",
    "Siirt", "Sinop", "Sivas", "Şanlıurfa", "Şırnak", "Tekirdağ", "Tokat",
    "Trabzon", "Tunceli", "Uşak", "Van", "Yalova", "Yozgat", "Zonguldak",
]

CITY_TO_NEIGHBORHOOD = {city: "Central" for city in CITIES}

# =========================================================
# 🧠 Session state – adım kontrolü
# =========================================================
if "step" not in st.session_state:
    st.session_state.step = 1

# Form alanları için başlangıç değerleri
defaults = {
    "age": 0,
    "previous_appointments": 0,
    "previous_noshow": 0,
    "past_appointments_patient": 0,
    "past_noshow_count": 0,
    "lead_time_days": 0,
    "sex_tr": SEX_OPTIONS_TR[0],
    "city_tr": CITIES[0],
    "department_tr": DEPARTMENT_TR[0],
    "insurance_tr": INSURANCE_TR[0],
    "channel_tr": CHANNEL_TR[0],
}

for key, val in defaults.items():
    st.session_state.setdefault(key, val)


def go_next():
    st.session_state.step += 1


def go_back():
    st.session_state.step -= 1 if st.session_state.step > 1 else 0


def reset_form():
    st.session_state.step = 1
    for key, val in defaults.items():
        st.session_state[key] = val


# =========================================================
# 🖼️ Başlık
# =========================================================
with st.container():
    st.markdown('<div class="app-container">', unsafe_allow_html=True)

    st.markdown(
        """
        <div class="app-title">
            <span class="app-icon">📅</span>
            <span>Randevuya Gelmeme Tahmini</span>
        </div>
        <div class="app-subtitle">
            Lütfen hastanın bilgilerini adım adım doldurun. Model, randevuya gelmeme (no-show) olasılığını hesaplayacaktır.
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Adım bilgisi
    st.markdown(
        f"""
        <div class="step-indicator">
            <span class="step-number">{st.session_state.step}</span> 
            <span>Adım / 3</span>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # =====================================================
    # 🔹 ADIM 1 – Temel Bilgiler
    # =====================================================
    if st.session_state.step == 1:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("<h3>1. Adım – Temel Bilgiler</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)
        with col1:
            st.session_state.age = st.number_input(
                "Yaş",
                min_value=0,
                max_value=120,
                value=st.session_state.age,
                help="Hastanın yaşı.",
            )

        with col2:
            st.session_state.sex_tr = st.selectbox(
                "Cinsiyet",
                SEX_OPTIONS_TR,
                index=SEX_OPTIONS_TR.index(st.session_state.sex_tr),
                help="Kadın / Erkek.",
            )

        st.session_state.city_tr = st.selectbox(
            "Şehir",
            CITIES,
            index=CITIES.index(st.session_state.city_tr),
            help="Hastanın yaşadığı / randevu aldığı şehir.",
        )

        st.markdown("</div>", unsafe_allow_html=True)

        # Butonlar
        col_next = st.columns(3)[2]
        with col_next:
            st.button("İleri →", on_click=go_next)

    # =====================================================
    # 🔹 ADIM 2 – Randevu Geçmişi
    # =====================================================
    elif st.session_state.step == 2:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("<h3>2. Adım – Randevu Geçmişi</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.session_state.previous_appointments = st.number_input(
                "Önceki Randevu Sayısı",
                min_value=0,
                value=st.session_state.previous_appointments,
                help="Bu klinikte/hastanede daha önce alınan randevu sayısı.",
            )

            st.session_state.past_appointments_patient = st.number_input(
                "Geçmiş Toplam Randevular",
                min_value=0,
                value=st.session_state.past_appointments_patient,
                help="Sistemde kayıtlı tüm randevu sayısı (eski randevular dahil).",
            )

        with col2:
            st.session_state.previous_noshow = st.number_input(
                "Önceki No-Show Sayısı",
                min_value=0,
                value=st.session_state.previous_noshow,
                help="Son dönemdeki randevular içinde gelinmeyen randevu sayısı.",
            )

            st.session_state.past_noshow_count = st.number_input(
                "Geçmiş No-Show Sayısı",
                min_value=0,
                value=st.session_state.past_noshow_count,
                help="Tüm geçmiş randevular içinde gelinmeyen randevu sayısı.",
            )

        st.session_state.lead_time_days = st.number_input(
            "Randevuya Kalan Gün (Lead Time)",
            min_value=0,
            value=st.session_state.lead_time_days,
            help="Randevunun oluşturulduğu gün ile randevu tarihi arasındaki gün sayısı.",
        )

        st.markdown("</div>", unsafe_allow_html=True)

        col_back, col_space, col_next = st.columns([1, 1, 1])
        with col_back:
            st.button("← Geri", on_click=go_back, key="back_step2", kwargs=None)
        with col_next:
            st.button("İleri →", on_click=go_next, key="next_step2", kwargs=None)

    # =====================================================
    # 🔹 ADIM 3 – Randevu Detayları + Tahmin
    # =====================================================
    elif st.session_state.step == 3:
        st.markdown('<div class="step-card">', unsafe_allow_html=True)
        st.markdown("<h3>3. Adım – Randevu Detayları</h3>", unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            st.session_state.department_tr = st.selectbox(
                "Departman",
                DEPARTMENT_TR,
                index=DEPARTMENT_TR.index(st.session_state.department_tr),
                help="Hastanın randevu aldığı bölüm.",
            )

            st.session_state.insurance_tr = st.selectbox(
                "Sigorta Türü",
                INSURANCE_TR,
                index=INSURANCE_TR.index(st.session_state.insurance_tr),
                help="Hastanın sigorta durumu.",
            )

        with col2:
            st.session_state.channel_tr = st.selectbox(
                "Randevu Oluşturma Kanalı",
                CHANNEL_TR,
                index=CHANNEL_TR.index(st.session_state.channel_tr),
                help="Randevunun alındığı kanal (Çağrı merkezi / Online / Hastane).",
            )

        st.markdown("</div>", unsafe_allow_html=True)

        # Tahmin butonu ve geri
        col_back, col_next = st.columns(2)

        with col_back:
            st.button("← Geri", on_click=go_back, key="back_step3")

        with col_next:
            if st.button("Tahmin Et"):
                # -----------------------------
                # API'ye gönderilecek veriyi hazırla
                # -----------------------------
                sex_en = SEX_OPTIONS_TR_TO_EN[st.session_state.sex_tr]
                department_en = DEPARTMENT_TR_TO_EN[st.session_state.department_tr]
                insurance_en = INSURANCE_TR_TO_EN[st.session_state.insurance_tr]
                channel_en = CHANNEL_TR_TO_EN[st.session_state.channel_tr]
                neighborhood_en = CITY_TO_NEIGHBORHOOD[st.session_state.city_tr]

                payload = {
                    "age": st.session_state.age,
                    "sex": sex_en,
                    "previous_appointments": st.session_state.previous_appointments,
                    "previous_noshow": st.session_state.previous_noshow,
                    "past_appointments_patient": st.session_state.past_appointments_patient,
                    "past_noshow_count": st.session_state.past_noshow_count,
                    "neighborhood": neighborhood_en,
                    "department": department_en,
                    "insurance_type": insurance_en,
                    "created_channel": channel_en,
                    "lead_time_days": st.session_state.lead_time_days,
                    # Modelin istediği sabit alanlar
                    "appointment_id": "A0000",
                    "patient_id": "P0000",
                    "doctor_id": "D00",
                    "dow_hour": "Mon_08",
                    "historical_noshow_rate_patient": 0.0,
                }

                try:
                    response = requests.post(
                        "http://127.0.0.1:5000/predict", json=payload, timeout=5
                    )

                    if response.status_code == 200:
                        result = response.json()
                        pred = int(result.get("prediction", 0))
                        prob = float(result.get("probability_no_show", 0.0))

                        # Sonuç kartları
                        if pred == 0:
                            st.markdown(
                                f"""
                                <div class="result-card-success">
                                    <span class="icon">✅</span>
                                    <span>Tahmin: Hasta randevuya <strong>GELİR</strong>.</span>
                                </div>
                                <div class="result-prob">
                                    <span class="icon">📊</span>
                                    <span>No-Show Olasılığı: <strong>{prob:.3f}</strong></span>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(
                                f"""
                                <div class="result-card-danger">
                                    <span class="icon">⚠️</span>
                                    <span>Tahmin: Hasta randevuya <strong>GELMEZ</strong>.</span>
                                </div>
                                <div class="result-prob">
                                    <span class="icon">📊</span>
                                    <span>No-Show Olasılığı: <strong>{prob:.3f}</strong></span>
                                </div>
                                """,
                                unsafe_allow_html=True,
                            )

                    else:
                        st.error("API hatası: " + response.text)

                except Exception as e:
                    st.error(f"Sunucuya erişilirken bir hata oluştu: {e}")

        # Yeniden başlatma için küçük buton
        st.markdown(
            '<div class="footer-note">Formu baştan doldurmak isterseniz sayfayı yenileyebilir veya aşağıdaki butonu kullanabilirsiniz.</div>',
            unsafe_allow_html=True,
        )
        if st.button("Formu Sıfırla"):
            reset_form()

    st.markdown("</div>", unsafe_allow_html=True)
