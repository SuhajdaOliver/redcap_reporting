import streamlit as st
import pandas as pd
from redcap_api import kitoltottseg, kitoltottseg_havi

st.title("Redcap reporting")

api_key = st.text_input("API kulcs", type="password")

if st.button("Lekérdezés"):
    df = kitoltottseg(api_key)
    df2 = kitoltottseg_havi(api_key)
    
    st.dataframe(df)
    st.dataframe(df2)

    csv = df.to_csv(index=False).encode("utf-8")
    csv2 = df2.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Összesített kitöltöttség letöltése",
        csv,
        "osszesitett_kitoltottseg.csv",
        "text/csv"
    )

    st.download_button(
        "Havi kitöltöttség letöltése",
        csv2,
        "havi_kitoltottseg.csv",
        "text/csv"
    )
