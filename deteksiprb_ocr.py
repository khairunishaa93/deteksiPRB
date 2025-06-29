import streamlit as st
import os
import tempfile
import pandas as pd
import pdfplumber
from PIL import Image
import pytesseract

# SETUP JIKA DI WINDOWS:
# pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

st.set_page_config(page_title="Deteksi PRB (OCR)", layout="wide")
st.title("📄 Deteksi Pasien Potensi PRB dari File SEP (OCR Mode)")
st.write("Unggah file PDF SEP hasil scan untuk mendeteksi tulisan 'Pasien Potensi PRB'.")

uploaded_files = st.file_uploader("Unggah file PDF SEP (bisa banyak)", type=["pdf"], accept_multiple_files=True)

results = []

def ocr_from_pdf(pdf_file):
    with pdfplumber.open(pdf_file) as pdf:
        full_text = ""
        for page in pdf.pages:
            image = page.to_image(resolution=300).original
            ocr_text = pytesseract.image_to_string(image)
            full_text += ocr_text + "\n"
        return full_text

if uploaded_files:
    with st.spinner("🔍 Memproses file..."):
        for file in uploaded_files:
            text = ocr_from_pdf(file)
            if "Pasien Potensi PRB" in text:
                nama_pasien = ""
                for line in text.split("\n"):
                    if "Nama Peserta" in line:
                        nama_pasien = line.split(":")[-1].strip()
                results.append({
                    "Nama File": file.name,
                    "Nama Pasien": nama_pasien if nama_pasien else "(tidak ditemukan)",
                    "Status PRB": "Potensi PRB"
                })

    if results:
        df = pd.DataFrame(results)
        st.success(f"✅ Ditemukan {len(df)} pasien potensi PRB (OCR).")
        st.dataframe(df)

        # Download hasil
        output_excel = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
        df.to_excel(output_excel.name, index=False)
        with open(output_excel.name, "rb") as f:
            st.download_button("⬇️ Unduh Hasil (Excel)", f, file_name="Hasil_Deteksi_PRB_OCR.xlsx")
    else:
        st.warning("Tidak ditemukan tulisan 'Pasien Potensi PRB'. Pastikan file hasil scan memiliki teks terbaca.")
