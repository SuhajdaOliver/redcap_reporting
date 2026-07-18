import streamlit as st
import pandas as pd
from redcap_api import kitoltottseg

st.title("Redcap reporting")

api_key = st.text_input("API kulcs", type="password")

if st.button("Kötelező mezők kitöltöttségének lekérdezése"):
    df = kitoltottseg(api_key)
    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")
    st.download_button(
        "CSV letöltése",
        csv,
        "eredmeny.csv",
        "text/csv"
    )
