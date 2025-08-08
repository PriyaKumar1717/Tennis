%%writefile tennis_dashboard.py


import streamlit as st
import pandas as pd
import sqlalchemy
from sqlalchemy import create_engine, text
import plotly.express as px

# Database configuration
DB_USER = 'root'
DB_PASSWORD = 'princepk3366&$'
DB_HOST = 'localhost'
DB_PORT = '3306'
DB_NAME = 'sys'

def get_engine():
    url = f"mysql+mysqlconnector://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    return create_engine(url)

# Load data functions
def load_doubles_rankings(engine, year_range, week_range, gender, rank_range):
    try:
        with engine.connect() as conn:
            query = text(f"""
                SELECT * FROM doubles_rankings
                WHERE `rank` BETWEEN :rank_start AND :rank_end
                ORDER BY `rank` ASC
            """)
            result = conn.execute(query, {
                'rank_start': rank_range[0],
                'rank_end': rank_range[1]
            })
            return pd.DataFrame(result.fetchall(), columns=result.keys())
    except Exception as e:
        st.error(f"Error loading rankings: {e}")
        return pd.DataFrame()

def load_competitions(engine):
    try:
        with engine.connect() as conn:
            df = pd.read_sql("SELECT * FROM competitions", conn)
            return df
    except Exception as e:
        st.error(f"Error loading competitions: {e}")
        return pd.DataFrame()

def load_complexes(engine):
    try:
        with engine.connect() as conn:
            df = pd.read_sql("SELECT * FROM complexes", conn)
            return df
    except Exception as e:
        st.error(f"Error loading complexes: {e}")
        return pd.DataFrame()

# App layout
st.set_page_config(page_title="Tennis Analytics Dashboard", layout="wide")
st.title("🎾 Tennis Analytics Dashboard")

# Sidebar filters
st.sidebar.header("Filters")
rank_range = st.sidebar.slider("Select Rank Range", 1, 100, (1, 20))
gender = st.sidebar.selectbox("Select Gender", ["All", "male", "female"])
year_range = st.sidebar.slider("Year Range (N/A in sample)", 2000, 2030, (2020, 2025))
week_range = st.sidebar.slider("Week Range (N/A in sample)", 1, 52, (1, 10))

# Connect to DB
db_engine = get_engine()

tabs = st.tabs(["🏆 Doubles Rankings", "📊 Competitions", "🏟 Complexes & Venues"])

# Tab 1: Doubles Rankings
with tabs[0]:
    st.subheader("Top Doubles Rankings")
    rankings_df = load_doubles_rankings(db_engine, year_range, week_range, gender, rank_range)
    if not rankings_df.empty:
        st.dataframe(rankings_df, use_container_width=True)

        fig = px.bar(rankings_df, x='team_name', y='points', color='country',
                     title='Points by Team (Top Rankings)', text='rank')
        fig.update_layout(xaxis_title="Team Name", yaxis_title="Points", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No ranking data found for the selected filters.")

# Tab 2: Competitions
with tabs[1]:
    st.subheader("Competition Details")
    competitions_df = load_competitions(db_engine)
    if not competitions_df.empty:
        st.dataframe(competitions_df, use_container_width=True)

        comp_counts = competitions_df['gender'].value_counts().reset_index()
        comp_counts.columns = ['Gender', 'Count']
        fig = px.pie(comp_counts, values='Count', names='Gender', title='Competitions by Gender', hole=0.4)
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No competition data available.")

# Tab 3: Complexes and Venues
with tabs[2]:
    st.subheader("Tennis Complexes and Venues")
    complexes_df = load_complexes(db_engine)
    if not complexes_df.empty:
        st.dataframe(complexes_df, use_container_width=True)

        complexes_df['venue_count'] = complexes_df['venues'].apply(lambda v: len(v.split(',')) if isinstance(v, str) else 0)
        fig = px.bar(complexes_df, x='name', y='venue_count', title='Number of Venues per Complex', text='venue_count')
        fig.update_layout(xaxis_title="Complex Name", yaxis_title="Venue Count", template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("No complexes or venues data found.")


