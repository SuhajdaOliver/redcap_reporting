import streamlit as st
import pandas as pd
from redcap_api import kitoltottseg, kitoltottseg_havi, kitoltottseg_havi_felvetel

st.title("Redcap reporting")

api_key = st.text_input("API kulcs", type="password")

if st.button("Lekérdezés"):
    df = kitoltottseg(api_key)
    df2 = kitoltottseg_havi(api_key)
    df3 = kitoltottseg_havi_felvetel(api_key)

    st.dataframe(df)

    csv = df.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Összesített kitöltöttség letöltése",
        csv,
        "osszesitett_kitoltottseg.csv",
        "text/csv"
    )

    st.dataframe(df2)

    csv2 = df2.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Havi kitöltöttség (completed státusz alapján) letöltése",
        csv2,
        "havi_kitoltottseg.csv",
        "text/csv"
    )

    st.dataframe(df3)

    csv3 = df3.to_csv(index=False).encode("utf-8")

    st.download_button(
        "Havi kitöltöttség (felvételi dátum alapján) letöltése",
        csv3,
        "havi_kitoltottseg.csv",
        "text/csv"
    )
