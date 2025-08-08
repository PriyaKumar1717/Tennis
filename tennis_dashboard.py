
import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error

st.set_page_config(page_title="🎾 Tennis Dashboard", layout="wide")

# ---- DB Query Function ----
def run_query(query):
    try:
        conn = mysql.connector.connect(
            host="localhost",
            user="root",
            password="your_password",       # <-- Replace with your MySQL password
            database="your_database_name"   # <-- Replace with your MySQL DB name
        )
        df = pd.read_sql(query, conn)
        return df
    except Error as e:
        st.error(f"Error retrieving data from database.\n{e}")
        return pd.DataFrame()
    finally:
        if 'conn' in locals() and conn.is_connected():
            conn.close()

# ---- Sidebar Filters ----
st.sidebar.header("🎯 Filters")
year = st.sidebar.number_input("Year", min_value=2000, max_value=2030, value=2024, step=1)
week = st.sidebar.number_input("Week", min_value=1, max_value=52, value=48, step=1)
gender = st.sidebar.selectbox("Gender", ["men", "women"])
rank_range = st.sidebar.slider("Rank Range", 1, 100, (1, 50))

# ---- Main Title ----
st.title("🎾 Tennis Data Explorer")

# ---- Tabs ----
tab1, tab2, tab3 = st.tabs(["🏆 Rankings", "📍 Venues", "📊 Future Insights"])

# ---- Tab 1: Rankings ----
with tab1:
    st.subheader("Filtered Doubles Rankings")

    query = f"""
        SELECT tour, year, week, gender, rank, points, player_name, country
        FROM doubles_rankings
        WHERE year = {year}
          AND week = {week}
          AND gender = '{gender}'
          AND rank BETWEEN {rank_range[0]} AND {rank_range[1]}
        ORDER BY rank ASC
        LIMIT 100;
    """

    df_rankings = run_query(query)
    if not df_rankings.empty:
        st.dataframe(df_rankings)
    else:
        st.warning("No data found for selected filters.")

# ---- Tab 2: Venues ----
with tab2:
    st.subheader("Venue and Complex Insights")
    st.info("Add venue-wise visuals, maps, or tournament distributions here.")

# ---- Tab 3: Future Insights ----
with tab3:
    st.subheader("Upcoming: Performance & Player Insights")
    st.info("This section is under development for advanced analytics like player progress, country-level summaries, etc.")




