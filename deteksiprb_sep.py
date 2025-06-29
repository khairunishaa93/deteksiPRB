import streamlit as st
import os
import tempfile
import pandas as pd
import pdfplumber

st.set_page_config(page_title="Deteksi Potensi PRB dari SEP", layout="wide")

st.title("📄 Deteksi Pasien Potensi PRB dari File SEP (PDF)")
st.write("Unggah beberapa file PDF SEP dan sistem akan mendeteksi pasien dengan label 'Pasien Potensi PRB'.")

# Upload file PDF
uploaded_files = st.file_uploader("Unggah file PDF SEP (bisa lebih dari satu)", type=["pdf"], accept_multiple_files=True)

# Fungsi ekstraksi teks dari PDF
def extract_text_from_pdf(file):
    try:
        with pdfplumber.open(file) as pdf:
            text = ""
            for page in pdf.pages:
                text += page.extract_text() + "\n"
            return text
    except Exception as e:
        return ""

# Simpan hasil deteksi
results = []

if uploaded_files:
    with st.spinner("🔍 Memproses file..."):
        for uploaded_file in uploaded_files:
            file_name = uploaded_file.name
            text = extract_text_from_pdf(uploaded_file)
            if "Pasien Potensi PRB" in text:
                # Coba ekstrak nama pasien
                nama_pasien = ""
                for line in text.split("\n"):
                    if "Nama Peserta" in line:
                        nama_pasien = line.split(":")[-1].strip()
                results.append({
                    "Nama File": file_name,
                    "Nama Pasien": nama_pasien if nama_pasien else "(tidak ditemukan)",
                    "Status PRB": "Potensi PRB"
                })

    if results:
        df_results = pd.DataFrame(results)
        st.success(f"✅ Ditemukan {len(df_results)} pasien potensi PRB.")
        st.dataframe(df_results)

        # Export hasil ke Excel
        output_excel = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        df_results.to_excel(output_excel.name, index=False)
        with open(output_excel.name, "rb") as f:
            st.download_button("⬇️ Unduh Hasil Deteksi (Excel)", f, file_name="Hasil_Deteksi_PRB.xlsx")
    else:
        st.warning("Tidak ditemukan pasien potensi PRB dalam file yang diunggah.")
