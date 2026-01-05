import streamlit as st
import pandas as pd
import io

# Sayfa Ayarları
st.set_page_config(page_title="Program Birleştirici", layout="centered")

st.title("🏭 Drag Finish Program Birleştirici")
st.markdown("""
Bu araç, birbirinin aynısı olan makine programlarını tespit eder ve ortak programlar altında birleştirir.
**Kullanım:** Aşağıdan CSV dosyanızı yükleyin ve sonuçları indirin.
""")

# Dosya Yükleme Alanı
uploaded_file = st.file_uploader("RECIPE dosyasını buraya sürükleyin (CSV)", type=["csv"])

if uploaded_file is not None:
    try:
        # Dosyayı oku
        # Excel'den gelen CSV'lerde başlık genelde 2. satırdadır (header=1)
        df = pd.read_csv(uploaded_file, header=1)
        
        st.info(f"Dosya yüklendi. Toplam {len(df)} satır veri var. İşleniyor...")

        # --- Temizlik ve Analiz İşlemleri ---
        df.columns = df.columns.str.strip()
        
        # Karşılaştırılacak sütunlar (Program Kodu hariç)
        cols_to_compare = [col for col in df.columns if col != 'PROGRAM KODU' and not col.startswith('Unnamed')]
        df_filled = df.fillna(0)

        # Gruplama
        grouped = df_filled.groupby(cols_to_compare)['PROGRAM KODU'].agg(list).reset_index()

        # Yeni İsimlendirme
        grouped.insert(0, 'YENI_ORTAK_ISIM', [f'ORTAK_PRG_{i+1:03d}' for i in range(len(grouped))])
        grouped.insert(1, 'ESKI_KODLAR', grouped['PROGRAM KODU'].apply(lambda x: ', '.join(x)))
        grouped.insert(2, 'BIRLESEN_ADET', grouped['PROGRAM KODU'].apply(len))
        grouped = grouped.drop(columns=['PROGRAM KODU'])
        
        # Sıralama
        grouped = grouped.sort_values(by='BIRLESEN_ADET', ascending=False)
        
        # --- Sonuç Gösterimi ---
        st.success(f"İşlem Tamam! {len(grouped)} adet ortak program oluşturuldu.")
        
        # Ekranda önizleme göster
        st.dataframe(grouped.head())

        # İndirme Butonu Hazırla
        csv_buffer = io.BytesIO()
        grouped.to_csv(csv_buffer, index=False, encoding='utf-8-sig')
        csv_data = csv_buffer.getvalue()

        st.download_button(
            label="📥 Sonuç Dosyasını İndir (Excel Uyumlu)",
            data=csv_data,
            file_name="HAZIR_ORTAK_PROGRAM_LISTESI.csv",
            mime="text/csv"
        )

    except Exception as e:
        st.error(f"Bir hata oluştu: {e}")
        st.warning("Lütfen dosyanın 'RECIPE' formatında olduğundan emin olun.")