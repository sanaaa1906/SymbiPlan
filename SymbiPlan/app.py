import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import folium
from streamlit_folium import st_folium

# --- 1. AI PREDICTION LOGIC ---
def get_ai_recommendation(df, selected_location):
    # This finds the columns by searching for keywords instead of the full question
    try:
        location_col = [c for c in df.columns if '70%' in c][0]
        operator_col = [c for c in df.columns if 'Operator' in c][0]
        signal_col = [c for c in df.columns if 'Signal Strength' in c][0]
    except IndexError:
        return "Error: Could not find the right columns in the Google Sheet. Check your headers!"

    subset = df[df[location_col] == selected_location]
    
    if subset.empty:
        return f"No data reported for {selected_location} yet."
    
    # Calculate the best operator
    avg_signals = subset.groupby(operator_col)[signal_col].mean()
    best_op = avg_signals.idxmax()
    strength = round(avg_signals.max(), 1)
    
    return f"AI Analysis: **{best_op}** is currently the strongest at {selected_location} (Avg: {strength}/5)."
    
    # Filter data for the chosen spot
    subset = df[df[location_col] == selected_location]
    
    if subset.empty:
        return f"No data reported for {selected_location} yet. AI predicts standard outdoor coverage."
    
    # Calculate average signal per operator
    # Note: Ensure signal_col is numeric!
    avg_signals = subset.groupby(operator_col)[signal_col].mean()
    
    best_op = avg_signals.idxmax()
    strength = round(avg_signals.max(), 1)
    
    return f"AI Analysis: **{best_op}** is currently the strongest at {selected_location} with an average strength of {strength}/5."
def display_geospatial_map(df):
    st.write("### 📍 Live Campus Signal Hotspots")
    
    # Coordinates for Symbiosis Kiwale spots
    location_coords = {
        "Engineering Block": [18.661137, 73.717647],
        "Management Block": [18.661208, 73.718160],
        "Admin Block":[18.660660, 73.718208],
        "Library":[18.66181884364397, 73.71833802016623],
        "Open Cafeteria": [18.661544, 73.718335],
        "Nescafe":[18.660965, 73.718379],
        "Hostel":[18.661609483643133, 73.71628323295177],
        "Amphitheatre":[18.660895, 73.717906],
        "Canteen": [18.660520, 73.717550],
        "Skill Center": [18.660730, 73.719091]
    }

    # Center the map on the Kiwale campus
    m = folium.Map(location=[18.6445, 73.7135], zoom_start=18)

    # Automatically find column names from your Google Sheet
    try:
        location_col = [c for c in df.columns if '70%' in c][0]
        signal_col = [c for c in df.columns if 'Signal Strength' in c][0]
        
        avg_data = df.groupby(location_col)[signal_col].mean().reset_index()

        for _, row in avg_data.iterrows():
            loc_name = row[location_col]
            signal = row[signal_col]
            
            if loc_name in location_coords:
                color = "red" if signal < 2.5 else "orange" if signal < 3.8 else "green"
                folium.Circle(
                    location=location_coords[loc_name],
                    radius=25,
                    popup=f"{loc_name}: {round(signal, 1)}/5",
                    color=color,
                    fill=True,
                    fill_opacity=0.5
                ).add_to(m)
        
        st_folium(m, width=700, height=450)
    except:
        st.warning("Map is waiting for more survey data to pinpoint locations.")
        
# --- 2. WEBSITE SETTINGS ---
st.set_page_config(page_title="SymbiPlan SSPU", page_icon="📶", layout="wide")

st.title("📶 SymbiPlan: SSPU Kiwale")
st.markdown("Analyzing campus network signals using peer-to-peer data.")

# --- 3. CONNECT TO DATA ---
SHEET_URL = "https://docs.google.com/spreadsheets/d/1FVhzop8SMzmLylTPeqtm2PW2GxNbO1eTas4j7nYD__M/edit?usp=sharing"

try:
     conn = st.connection("gsheets", type=GSheetsConnection)
     df = conn.read()
except:
    # This 'except' block fixes your SyntaxError
     csv_url = SHEET_URL.split('/edit')[0] + '/export?format=csv'
     df = pd.read_csv(csv_url)
    
# --- 4. PAGE CONTROLLER (Navigation Logic) ---
# This initializes the app to stay on 'Home' until a button is clicked
if 'page' not in st.session_state:
    st.session_state.page = 'Home'

def set_page(page_name):
    st.session_state.page = page_name

# --- 5. THE HOME PAGE ---
if st.session_state.page == 'Home':
    # Add your College Logo
    # Replace 'logo.png' with your actual filename or a URL
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Use a placeholder if logo is missing: st.image("https://placehold.co/400x150?text=SSPU+LOGO")
        st.image("https://www.sspu.ac.in/images/sspu-logo.png", use_container_width=True) 
    
    st.markdown("<h1 style='text-align: center; color: #1E3A8A; font-family: sans-serif;'>SymbiPlan</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-style: italic;'>Your Campus, Your Signal, Your Solution.</p>", unsafe_allow_html=True)
    
    st.divider()

    # Create the 3 Boxes (Buttons) one below the other
    st.markdown("### Choose a Tool:")
    
    # Box 1: Signal Finder
    if st.button("🔍 SIGNAL FINDER - Find the best network for your spot", use_container_width=True):
        set_page('Signal Finder')

    # Box 2: Heatmap
    if st.button("📊 LIVE HEATMAP - View visual campus hotspots", use_container_width=True):
        set_page('Heatmap')

    # Box 3: Report
    if st.button("📢 REPORT SIGNAL - Help the community grow", use_container_width=True):
        set_page('Report')

# --- 6. INDIVIDUAL PAGES ---

elif st.session_state.page == 'Signal Finder':
    if st.button("⬅️ Back to Home"): set_page('Home')
    st.header("🔍 Signal Finder")
    campus_addas = ["Admin Block", "Management Block", "Engineering Block", "Skill Center", "Library", "Canteen", "Open Cafeteria", "Nescafe", "Hostel Wings", "Parking", "Amphitheater"]
    selected_adda = st.selectbox("Where are you located?", campus_addas)
    if st.button("Check Best Signal"):
        result = get_ai_recommendation(df, selected_adda)
        st.info(result)

elif st.session_state.page == 'Heatmap':
    if st.button("⬅️ Back to Home"): set_page('Home')
    st.header("📊 Visual Network Analysis")
    display_geospatial_map(df)

elif st.session_state.page == 'Report':
    if st.button("⬅️ Back to Home"): set_page('Home')
    st.header("📢 Help the Community")
    st.write("Submit a new signal report for your current location.")
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfmsDX0Oo2nWGt6xScoIV-X0_UPHV_qLCsYDnKQ4P07ZN5CYg/viewform"
    st.link_button("Open Signal Form", form_url)
