import streamlit as st
import pandas as pd
import json
import os

st.set_page_config(page_title="Internationale Presseschau", layout="wide")
st.title("Internationale Presseschau – DLF")


DATA_FILE = "presseschau.json" 


@st.cache_data(ttl=3600)  
def load_data() -> pd.DataFrame:
    """
    Liest die normale JSON-Datei direkt aus dem Repository ein
    und wandelt sie in ein Pandas DataFrame um.
    """
    if not os.path.exists(DATA_FILE):
        st.error(f"Die Datei `{DATA_FILE}` wurde im Repository nicht gefunden!")
        st.stop()
        
    try:
        with open(DATA_FILE, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
            return pd.DataFrame(json_data)
    except Exception as e:
        st.error(f"Fehler beim Laden der JSON-Datei: {e}")
        st.stop()


with st.spinner("Lade Daten"):
    df = load_data()

st.sidebar.header("Filter")

datum_options = sorted(df["datum"].unique(), reverse=True)
selected_datum = st.sidebar.multiselect("Datum", datum_options, default=datum_options[:5])

label_options = sorted(df["label"].unique())
selected_labels = st.sidebar.multiselect("Thema / Label", label_options, default=label_options)

zeitung_options = sorted(df["name"].unique())
selected_zeitungen = st.sidebar.multiselect("Zeitung", zeitung_options, default=zeitung_options)

filtered = df[
    df["datum"].isin(selected_datum) &
    df["label"].isin(selected_labels) &
    df["name"].isin(selected_zeitungen)
]

col1, col2, col3 = st.columns(3)
col1.metric("Einträge", len(filtered))
col2.metric("Zeitungen", filtered["name"].nunique())
col3.metric("Tage", filtered["datum"].nunique())

st.divider()

st.subheader("Themenverteilung")
if not filtered.empty:
    label_counts = filtered["label"].value_counts().reset_index()
    label_counts.columns = ["Label", "Anzahl"]
    st.bar_chart(label_counts.set_index("Label"))
else:
    st.info("Keine Daten für die gewählten Filter verfügbar.")

st.divider()

st.subheader("Einträge")
st.dataframe(
    filtered[["datum", "name", "label", "score", "text"]].sort_values("datum", ascending=False),
    use_container_width=True,
    hide_index=True,
    column_config={
        "datum": "Datum",
        "name": "Zeitung",
        "label": "Thema",
        "score": st.column_config.NumberColumn("Score", format="%.1f%%"),
        "text": st.column_config.TextColumn("Text", width="large"),
    }
)