# 📈 Firma Finansman Stratejileri ve Maliyet Minimizasyonu: Panel Veri Simülasyonu

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?style=for-the-badge&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.30%2B-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)
![SciPy](https://img.shields.io/badge/SciPy-Optimization-8CAAE6?style=for-the-badge&logo=scipy&logoColor=white)
![World Bank API](https://img.shields.io/badge/Data-World%2B_Bank_API-0071BC?style=for-the-badge&logo=worldbank&logoColor=white)

Bu proje, akademik araştırma ve eğitim amacıyla geliştirilmiş interaktif bir **Ekonometrik Simülasyon Paneli**'dir. Farklı finansman stratejileri izleyen iki firmanın (**Tamamen Özkaynak** ile finansman sağlayan Firma 1 ve **Borç Finansmanı** kullanan Firma 2) **Cobb-Douglas Üretim Fonksiyonu** kısıtı altındaki maliyet minimizasyon davranışlarını karşılaştırmalı olarak analiz eder.

---

## 🎯 Projenin Amacı ve Odak Noktası

Kurumsal finansmanda temel bir tartışma olan sermaye yapısı ve sermaye maliyeti arasındaki ilişki, bu uygulamanın temelini oluşturmaktadır. Uygulama, **Modigliani-Miller Teoremi (1963)** çerçevesinde vergi kalkanının (tax shield) maliyet minimizasyonu ve faktör talebi (Emek ve Sermaye) üzerindeki doğrudan etkilerini görsel ve veriye dayalı olarak inceleme fırsatı sunar.

## 🧮 Teorik Çerçeve

Simülasyon aşağıdaki yapısal eşitlikler üzerinden çözümlenmektedir:

### 1. Üretim Fonksiyonu (Kısıt)
Klasik bir Cobb-Douglas üretim teknolojisi varsayılmıştır:
$$Q = A \cdot L^\alpha \cdot K^\beta$$
*Burada:*
*   $Q$: Hedef Üretim Miktarı (1000 Birim)
*   $A$: Toplam Faktör Verimliliği
*   $L, K$: Emek ve Sermaye miktarları
*   $\alpha, \beta$: Emek ve Sermaye esneklikleri

### 2. Maliyet Fonksiyonu (Minimize Edilecek Hedef)
$$TC = w \cdot L + r \cdot K$$

### 3. Sermaye Maliyetleri ($r$)
İki firma, fonlama türlerine göre farklı sermaye maliyetlerine katlanırlar:

*   **Firma 1 (Özkaynak / Equity):** Maliyetler **CAPM (Sermaye Varlıklarını Fiyatlama Modeli)** kullanılarak hesaplanır.
    $$r_e = R_f + \beta \cdot (R_m - R_f)$$

*   **Firma 2 (Borç / Debt):** Kurumlar vergisinin yarattığı **Vergi Kalkanı** hesaba katılır.
    $$r_k = r_d \cdot (1 - t)$$

---

## 🌍 Veri Kaynakları: Hibrit Mimari

Kullanıcılar yan menü (sidebar) üzerinden analizi gerçekleştirmek için iki farklı veri opsiyonu arasından seçim yapabilir:

1.  **⚙️ Sentetik Veri Modu:** Kullanıcının belirlediği manuel faiz şokları (Küresel Faiz Çarpanı) altında 5 yıllık varsayımsal bir makroekonomik trend simüle edilir.
2.  **🌐 Gerçek Veri (Dünya Bankası API):** Model, canlı olarak **Dünya Bankası (`wbgapi`)** üzerinden Türkiye (TUR), ABD (USA) ve Almanya (DEU) için şu verileri çeker:
    *   **Kredi Faiz Oranları (Lending Interest Rate - `FR.INR.LEND`)**
    *   **Enflasyon/TÜFE (Consumer Price Index - `FP.CPI.TOTL.ZG`)**
    *   *Not:* Analitik tutarlılığı korumak adına Kurumlar Vergisi ve Firma Betası parametreleri modele gömülü ortalamalardan (statik) alınır.

---

## 🚀 Teknik Altyapı ve Optimizasyon

*   **Matematiksel Optimizasyon:** Projedeki "Maliyet Minimizasyonu" problemi, bir Non-Linear Programming (Doğrusal Olmayan Programlama) problemidir. Bunun çözümü için `scipy.optimize.minimize` modülündeki **SLSQP (Sequential Least Squares Programming)** algoritması kullanılmıştır.
*   **Arayüz:** `Streamlit`
*   **Veri Manipülasyonu:** `Pandas`, `Numpy`
*   **Görselleştirme:** Dinamik ve interaktif grafikler için `Plotly Express`

---

## 💻 Kurulum ve Çalıştırma (Local Environment)

Projeyi kendi bilgisayarınızda çalıştırmak için aşağıdaki adımları izleyebilirsiniz. Sisteminizde Python (3.8+) kurulu olduğundan emin olun.

**1. Depoyu Klonlayın**
```bash
git clone https://github.com/ibrahimguney/nuriaksoy.git
cd nuriaksoy
```

**2. Gerekli Kütüphaneleri Yükleyin**
```bash
pip install -r requirements.txt
```

**3. Uygulamayı Başlatın**
```bash
streamlit run app.py
```
*Uygulama başarıyla başlatıldığında tarayıcınızda otomatik olarak `http://localhost:8501` adresinde açılacaktır.*

---

## 📸 Ekran Görüntüsü / Arayüz Bileşenleri

1.  **Simülasyon Parametreleri (Sidebar):** Emek/Sermaye esnekliklerini ayarlayın ve Veri Kaynağını (Sentetik/API) seçin.
2.  **İnteraktif Grafik:** Plotly tabanlı grafik üzerinde ülke filtrelenerek Firma 1 ve Firma 2'nin Birim Maliyet (ATC) trendleri karşılaştırılabilir.
3.  **Panel Veri Tablosu:** Optimizasyon döngüsünden çıkan kesin $L$ ve $K$ girdi talepleri, maliyetler ve makroekonomik parametrelerin tam matrisini inceleyin.

---

## 📚 Referanslar ve Akademik Altyapı

*   **Cobb, C. W., & Douglas, P. H. (1928).** A Theory of Production. *American Economic Review*, 18(1), 139-165.
*   **Modigliani, F., & Miller, M. H. (1958).** The Cost of Capital, Corporation Finance and the Theory of Investment. *The American Economic Review*, 48(3), 261-297.
*   **Modigliani, F., & Miller, M. H. (1963).** Corporate Income Taxes and the Cost of Capital: A Correction. *The American Economic Review*, 53(3), 433-443.
*   **Sharpe, W. F. (1964).** Capital Asset Prices: A Theory of Market Equilibrium under Conditions of Risk. *The Journal of Finance*, 19(3), 425-442.

---
*Bu proje akademik kullanım ve finansal ekonometri eğitimleri amacıyla hazırlanmıştır.*
