import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import os

st.set_page_config(page_title="AI Monitor", layout="wide")
st.title("🚀 Pokémon Emerald AI Control Center")

# --- DATEI-ÜBERSICHT ---
st.sidebar.header("📂 System-Pfade")
st.sidebar.code(f"Modelle: {os.path.abspath('checkpoints/')}")
st.sidebar.code(f"Spielstand: {os.path.abspath('Pokemon - Emerald Version (USA, Europe).sav')}")

# --- REWARD PLOT ---
st.header("📈 Lern-Statistiken (Rewards & Epochen)")
conn = sqlite3.connect('pokemon_research.db')
df = pd.read_sql_query("SELECT * FROM training_stats ORDER BY timesteps ASC", conn)

if not df.empty:
    # Plot der Rewards pro Epoche
    fig_reward = px.line(df, x="timesteps", y="reward", title="Reward-Entwicklung (Wie gut lernt er?)")
    st.plotly_chart(fig_reward, use_container_width=True)
    
    # Tabelle der Versionen
    st.header("💾 Gespeicherte Checkpoints")
    versions = [f for f in os.listdir('checkpoints') if f.endswith('.zip')]
    st.table(pd.DataFrame({"Version": versions, "Pfad": [os.path.abspath(os.path.join('checkpoints', v)) for v in versions]}))
else:
    st.info("Warte auf Daten vom Training...")