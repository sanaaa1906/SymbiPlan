import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd

# --- 1. AI PREDICTION LOGIC ---
def get_ai_recommendation(df, selected_adda):
    # Ensure this matches your Google Sheet header EXACTLY
    location_col = "Adda" 
    
    # This is the line that was crashing
    subset = df[df[location_col] == selected_location]
    # ... rest of your code
    if subset.empty:
        return "No data for this spot yet. AI predicts standard outdoor coverage."
    
    # Calculate which operator has the best average signal strength
    avg_signals = subset.groupby('Primary Network Operator')['Current Signal Strength'].mean()
    best_op = avg_signals.idxmax()
    strength = round(avg_signals.max(), 1)
    
    return f"AI Analysis: **{best_op}** is currently the strongest at {selected_adda} (Avg: {strength}/5)."
def get_ai_recommendation(df, selected_location):
    # This matches your actual Sheet column: "Where do you spend 70% of your time on campus?"
    location_col = 'Where do you spend 70% of your time on campus?'
    operator_col = 'Primary Telecom Operator'
    signal_col = 'Signal Strength at your primary campus location'

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
    
# --- 4. NAVIGATION TABS ---
tab1, tab2, tab3 = st.tabs(["🔍 Signal Finder", "📊 Live Heatmap", "📢 Report Issue"])

with tab1:
    st.header("Find the Best Network")
    # This list matches your form options
    campus_addas = [
        "Admin Block", "Management Block", "Engineering Block", "Skill Center", 
        "Library", "Canteen", "Open Cafeteria", "Nescafe", 
        "Hostel Wings", "Parking", "Amphitheater"
    ]
    
    selected_adda = st.selectbox("Where are you located?", campus_addas)
    
    if st.button("Check Best Signal"):
        result = get_ai_recommendation(df, selected_adda)
        st.info(result)

with tab2:
    st.header("Campus Network Heatmap")
    st.write("Visualizing real-time signal data across SSPU.")
    # PASTE YOUR POWER BI LINK BELOW
    pbi_url = "PASTE_YOUR_POWER_BI_EMBED_LINK_HERE"
    st.components.v1.iframe(pbi_url, height=600)

with tab3:
    st.header("Help the Community")
    st.write("Submit a new signal report for your current location.")
    # This is your actual form link
    form_url = "https://docs.google.com/forms/d/e/1FAIpQLSfmsDX0Oo2nWGt6xScoIV-X0_UPHV_qLCsYDnKQ4P07ZN5CYg/viewform"
    st.link_button("Open Signal Form", form_url)

with st.expander("📊 View Raw Campus Data"):
    st.dataframe(df)
