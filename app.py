import streamlit as st
import pandas as pd
import numpy as np
from scipy.optimize import minimize
import plotly.express as px
import wbgapi as wb

# Sayfa yapılandırması
st.set_page_config(page_title="Firma Finansman Stratejileri ve Maliyet Minimizasyonu", layout="wide")

# Başlık ve Açıklamalar
st.title("Firma Finansman Stratejileri ve Maliyet Minimizasyonu: Panel Veri Simülasyonu")
st.markdown("""
Bu interaktif simülasyon paneli, farklı finansman stratejileri izleyen iki firmanın (Tamamen Özkaynak vs. Borç Finansmanı) maliyet minimizasyonu davranışlarını karşılaştırmaktadır. 

Simülasyon, Cobb-Douglas üretim fonksiyonu kısıtı altında çalışmaktadır. Analiz, Modigliani-Miller teoreminin temel varsayımları çerçevesinde vergi kalkanı etkisini (Modigliani & Miller, 1963) incelememize olanak tanır.

### Teorik Çerçeve
* **Üretim Fonksiyonu:** $Q = A \\cdot L^\\alpha \\cdot K^\\beta$ (Cobb & Douglas, 1928)
* **Maliyet Fonksiyonu:** $C = w \\cdot L + r \\cdot K$
* **Sermaye Maliyeti ($r$):**
    * **Firma 1 (Özkaynak Finansmanı):** CAPM Modeli $r_e = R_f + \\beta \\cdot (R_m - R_f)$
    * **Firma 2 (Borç Finansmanı):** Vergi kalkanı sonrası maliyet $r_k = r_d \\cdot (1 - t)$
""")

# --- Yan Menü (Sidebar) Parametreleri ---
st.sidebar.header("Veri Kaynağı ve Parametreler")

data_source = st.sidebar.radio(
    "Veri Kaynağını Seçin:",
    ("Sentetik Veri", "Gerçek Veri (Dünya Bankası API)")
)

alpha = st.sidebar.slider("Emek Esnekliği (α)", min_value=0.1, max_value=0.9, value=0.6, step=0.05)
beta = round(1.0 - alpha, 2)
st.sidebar.markdown(f"**Sermaye Esnekliği (β):** {beta}")

if data_source == "Sentetik Veri":
    interest_multiplier = st.sidebar.slider("Küresel Faiz Çarpanı", min_value=0.5, max_value=2.0, value=1.0, step=0.1, 
                                            help="Faiz oranlarındaki makroekonomik şokları simüle etmek için kullanılır.")
else:
    interest_multiplier = 1.0 # Gerçek veride kullanılmayacak
    st.sidebar.info("Gerçek Veri modunda faiz oranları Dünya Bankası'ndan anlık çekilir.")

# Sabitler
Q_target = 1000
A = 10
beta_firm_synthetic = 1.2 # Sentetik verideki standart beta

# --- Veri Seti Fonksiyonları ---

@st.cache_data
def generate_synthetic_data(multiplier):
    countries = [
        {"name": "Ülke A (Düşük Vergi)", "tax_rate": 0.15, "base_w": 50, "base_rf": 0.03, "base_rp": 0.05, "base_rd": 0.06},
        {"name": "Ülke B (Orta Vergi)", "tax_rate": 0.25, "base_w": 70, "base_rf": 0.04, "base_rp": 0.06, "base_rd": 0.08},
        {"name": "Ülke C (Yüksek Vergi)", "tax_rate": 0.35, "base_w": 90, "base_rf": 0.05, "base_rp": 0.07, "base_rd": 0.10}
    ]
    years = [2022, 2023, 2024, 2025, 2026]
    
    data = []
    for country in countries:
        for i, year in enumerate(years):
            w_trend = country["base_w"] * (1 + 0.05 * i)
            rf_trend = country["base_rf"] * multiplier * (1 + 0.1 * i)
            rd_trend = country["base_rd"] * multiplier * (1 + 0.08 * i)
            
            r_e = rf_trend + (beta_firm_synthetic * country["base_rp"])
            r_k = rd_trend * (1 - country["tax_rate"])
            
            data.append({
                "Ülke": country["name"],
                "Yıl": year,
                "Vergi Oranı (t)": country["tax_rate"],
                "Ücret (w)": w_trend,
                "Firma 1 Sermaye Maliyeti (r_e)": r_e * 100, 
                "Firma 2 Sermaye Maliyeti (r_k)": r_k * 100,
                "Detay": "Sentetik"
            })
    return pd.DataFrame(data)

@st.cache_data(ttl=3600)
def fetch_real_data():
    country_map = {
        'TUR': 'Türkiye',
        'USA': 'ABD',
        'DEU': 'Almanya'
    }
    
    # Hibrit model için statik ortalama değerler
    static_data = {
        'TUR': {'tax_rate': 0.25, 'base_w': 50, 'beta': 1.1, 'base_rp': 0.08, 'rf': 0.15},
        'USA': {'tax_rate': 0.21, 'base_w': 150, 'beta': 1.0, 'base_rp': 0.05, 'rf': 0.04},
        'DEU': {'tax_rate': 0.29, 'base_w': 120, 'beta': 0.9, 'base_rp': 0.05, 'rf': 0.02}
    }
    
    years = list(range(2018, 2023))
    
    try:
        # API İstekleri
        # FR.INR.LEND = Kredi Faiz Oranları (Lending Interest Rate %)
        # FP.CPI.TOTL.ZG = Enflasyon (TÜFE %)
        df_lend = wb.data.DataFrame('FR.INR.LEND', list(country_map.keys()), time=years)
        df_cpi = wb.data.DataFrame('FP.CPI.TOTL.ZG', list(country_map.keys()), time=years)
        
        df_lend.columns = [int(col[2:]) for col in df_lend.columns]
        df_cpi.columns = [int(col[2:]) for col in df_cpi.columns]
        
        data = []
        for c_code, c_name in country_map.items():
            s_data = static_data[c_code]
            current_w = s_data['base_w']
            
            for year in years:
                rd_percent = df_lend.loc[c_code, year] if pd.notna(df_lend.loc[c_code, year]) else 8.0
                cpi_percent = df_cpi.loc[c_code, year] if pd.notna(df_cpi.loc[c_code, year]) else 5.0
                
                rd = rd_percent / 100.0
                
                # Ücret, enflasyon oranında artırılır (Basitleştirilmiş model)
                current_w = current_w * (1 + (cpi_percent / 100.0))
                
                # CAPM ile Firma 1 (Özkaynak) Maliyeti
                r_e = s_data['rf'] + (s_data['beta'] * s_data['base_rp'])
                # Vergi Kalkanı ile Firma 2 (Borç) Maliyeti
                r_k = rd * (1 - s_data['tax_rate'])
                
                data.append({
                    "Ülke": c_name,
                    "Yıl": year,
                    "Vergi Oranı (t)": s_data['tax_rate'],
                    "Ücret (w)": current_w,
                    "Firma 1 Sermaye Maliyeti (r_e)": r_e * 100, 
                    "Firma 2 Sermaye Maliyeti (r_k)": r_k * 100,
                    "Detay": f"Kredi: %{rd_percent:.1f}, TÜFE: %{cpi_percent:.1f}"
                })
        return pd.DataFrame(data)
    except Exception as e:
        st.error(f"Dünya Bankası API Veri Çekme Hatası: {e}")
        return pd.DataFrame()

# Veri Setini Yükle
if data_source == "Sentetik Veri":
    df = generate_synthetic_data(interest_multiplier)
else:
    with st.spinner("Dünya Bankası API'sinden veriler çekiliyor..."):
        df = fetch_real_data()

if df.empty:
    st.warning("Veri yüklenemedi. Lütfen daha sonra tekrar deneyin veya Sentetik Veri moduna geçin.")
    st.stop()

# --- Optimizasyon Fonksiyonları ---
def objective_function(vars, w, r):
    L, K = vars
    return w * L + r * K

def constraint_function(vars):
    L, K = vars
    return A * (L**alpha) * (K**beta) - Q_target

# --- Optimizasyon Döngüsü ---
results = []
bounds = ((1e-5, None), (1e-5, None)) # Pozitiflik kısıtı
initial_guess = [10, 10]
cons = {'type': 'eq', 'fun': constraint_function}

for index, row in df.iterrows():
    w = row["Ücret (w)"]
    r_e = row["Firma 1 Sermaye Maliyeti (r_e)"]
    r_k = row["Firma 2 Sermaye Maliyeti (r_k)"]
    
    # Firma 1 Optimizasyonu (Özkaynak)
    res_f1 = minimize(objective_function, initial_guess, args=(w, r_e), method='SLSQP', bounds=bounds, constraints=cons)
    L_f1, K_f1 = res_f1.x
    ATC_f1 = res_f1.fun / Q_target
    
    # Firma 2 Optimizasyonu (Borç)
    res_f2 = minimize(objective_function, initial_guess, args=(w, r_k), method='SLSQP', bounds=bounds, constraints=cons)
    L_f2, K_f2 = res_f2.x
    ATC_f2 = res_f2.fun / Q_target
    
    results.append({
        "Ülke": row["Ülke"],
        "Yıl": row["Yıl"],
        "F1 Ortalama Maliyet (ATC)": ATC_f1,
        "F2 Ortalama Maliyet (ATC)": ATC_f2,
        "F1 Emek (L)": L_f1,
        "F1 Sermaye (K)": K_f1,
        "F2 Emek (L)": L_f2,
        "F2 Sermaye (K)": K_f2,
        "w": w,
        "r_e": r_e,
        "r_k": r_k,
        "Ek Bilgi": row["Detay"]
    })

results_df = pd.DataFrame(results)

# --- Görselleştirme ---
st.subheader("Birim Maliyet (ATC) Karşılaştırması")

selected_country = st.selectbox("Analiz Edilecek Ülkeyi Seçiniz:", df["Ülke"].unique())
filtered_df = results_df[results_df["Ülke"] == selected_country]

fig = px.line(filtered_df, x="Yıl", y=["F1 Ortalama Maliyet (ATC)", "F2 Ortalama Maliyet (ATC)"],
              labels={"value": "Birim Maliyet (ATC)", "variable": "Firma Türü"},
              title=f"{selected_country} - Yıllara Göre Birim Maliyet Trendi",
              markers=True)
fig.update_layout(legend_title_text='Firma Finansmanı')
newnames = {'F1 Ortalama Maliyet (ATC)': 'Firma 1 (Özkaynak)', 'F2 Ortalama Maliyet (ATC)': 'Firma 2 (Borç)'}
fig.for_each_trace(lambda t: t.update(name = newnames[t.name], legendgroup = newnames[t.name], hovertemplate = t.hovertemplate.replace(t.name, newnames[t.name])))

st.plotly_chart(fig, use_container_width=True)

# --- Veri Tablosu ---
st.subheader("Panel Veri Optimizasyon Sonuçları")
st.dataframe(results_df.style.format({
    "F1 Ortalama Maliyet (ATC)": "{:.2f}",
    "F2 Ortalama Maliyet (ATC)": "{:.2f}",
    "F1 Emek (L)": "{:.2f}",
    "F1 Sermaye (K)": "{:.2f}",
    "F2 Emek (L)": "{:.2f}",
    "F2 Sermaye (K)": "{:.2f}",
    "w": "{:.2f}",
    "r_e": "{:.2f}",
    "r_k": "{:.2f}"
}))

# --- Referanslar ---
st.markdown("---")
st.markdown("### Referanslar")
st.markdown("""
* Cobb, C. W., & Douglas, P. H. (1928). A Theory of Production. *American Economic Review*, 18(1), 139-165.
* Modigliani, F., & Miller, M. H. (1958). The Cost of Capital, Corporation Finance and the Theory of Investment. *The American Economic Review*, 48(3), 261-297.
* Modigliani, F., & Miller, M. H. (1963). Corporate Income Taxes and the Cost of Capital: A Correction. *The American Economic Review*, 53(3), 433-443.
* Sharpe, W. F. (1964). Capital Asset Prices: A Theory of Market Equilibrium under Conditions of Risk. *The Journal of Finance*, 19(3), 425-442.
""")
