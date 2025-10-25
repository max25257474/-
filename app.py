import streamlit as st
import pandas as pd
import numpy as np
import re
from datetime import datetime
import io
import os

st.set_page_config(page_title="Автоматичне очищення даних", layout="wide")
st.title("🧹 Автоматичне очищення Excel-даних")

st.sidebar.header("📂 Завантаження Excel")
uploaded_file = st.sidebar.file_uploader("Завантаж свій Excel-файл", type=["xlsx", "xls"])

default_file = "raw_data.xlsx"  

if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    st.success("✅ Завантажено власний файл.")
elif os.path.exists(default_file):
    df = pd.read_excel(default_file)
    st.success("✅ Автоматично підвантажено raw_data.xlsx із локальної папки.")
else:
    st.error("❌ Файл raw_data.xlsx не знайдено. Завантаж файл вручну.")
    st.stop()

st.subheader("📋 Попередній перегляд сирих даних")
st.dataframe(df.head(10), use_container_width=True)


def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    for col in df.columns:

        df[col].replace(["", " ", "NA", "NaN", "None", None], np.nan, inplace=True)

        if df[col].dtype == object:
            df[col] = df[col].astype(str).apply(lambda x: x.strip().title())

            df[col] = df[col].apply(lambda x: re.sub(r"[^0-9.,-]", "", x) if re.search(r"\d", x) else x)
            df[col] = df[col].replace("", np.nan)

        try:
            df[col] = pd.to_datetime(df[col], errors='ignore', dayfirst=True)
        except Exception:
            pass

        try:
            df[col] = df[col].apply(lambda x: float(str(x).replace(",", ".")) if re.match(r"^\d+[.,]?\d*$", str(x)) else x)
        except Exception:
            pass

    df.dropna(how="all", inplace=True)
    df.reset_index(drop=True, inplace=True)
    return df

if st.button("🚀 Очистити дані"):
    cleaned_df = clean_data(df)
    st.success("✅ Дані успішно очищено!")

    st.subheader("📊 Очищені дані")
    st.dataframe(cleaned_df.head(10), use_container_width=True)

    buffer = io.BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        cleaned_df.to_excel(writer, sheet_name="clean_data", index=False)
    buffer.seek(0)

    st.download_button(
        label="⬇️ Завантажити очищений Excel",
        data=buffer,
        file_name="clean_data.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
