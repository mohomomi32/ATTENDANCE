import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime
import pandas as pd

# Page Configuration
st.set_page_config(page_title="GEPL Attendance Portal", page_icon="📍", layout="centered")

# --- Google Sheet Ka ID Direct Link Se Nikalna ---
# Aapko Streamlit Secrets ki ab zaroorat nahi paregi, hum direct connect kar rahe hain
try:
    # Yahan hum direct Sheet ka ID lagayenge jo niche settings se aayega
    SHEET_ID = st.secrets["connections"]["gsheets"]["spreadsheet"].split("/d/")[1].split("/")[0]
    
    # Direct URLs to read Google Sheet as CSV
    EMP_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Employees"
    LOGS_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Logs"
    
    emp_data = pd.read_csv(EMP_URL)
except Exception as e:
    st.error("Google Sheet ke sath connection nahi ho pa raha. Meharbani kar k Share Settings aur Secrets ka Link check karein.")
    st.stop()

# Office ka time (9:15 AM ke baad employee late consider hoga)
OFFICE_START_TIME = "09:15:00"

# --- Session State (Login status yaad rakhne ke liye) ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.emp_id = ""
    st.session_state.emp_name = ""

# --- 1. EMPLOYEE LOGIN SCREEN ---
if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>📍 GEPL Attendance System</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Apni ID aur Password daal kar Login karein</p>", unsafe_allow_html=True)
    
    emp_id = st.text_input("Employee ID (E.g., GEPL-01)").strip()
    password = st.text_input("Password", type="password")
    
    if st.button("Login", use_container_width=True, type="primary"):
        # Google Sheet me se check karega ke ID aur Password sahi hain ya nahi
        user_row = emp_data[(emp_data['emp_id'].astype(str) == emp_id) & (emp_data['password'].astype(str) == password)]
        
        if not user_row.empty:
            st.session_state.logged_in = True
            st.session_state.emp_id = emp_id
            st.session_state.emp_name = user_row['name'].values[0]
            st.rerun()
        else:
            st.error("❌ Galat ID ya Password! Dobara check karein.")

# --- 2. EMPLOYEE ATTENDANCE SCREEN (MOBILE INTERFACE) ---
else:
    st.markdown(f"### 👋 KhushAamdeed, **{st.session_state.emp_name}**")
    st.caption(f"ID: {st.session_state.emp_id} | Aaj ki Tareekh: {datetime.now().strftime('%d-%B-%Y')}")
    
    st.warning("⚠️ Attendance lagane se pehle mobile ki Location (GPS) lazmi ON karein.")
    
    location = streamlit_geolocation()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Duty ON (In)", use_container_width=True, type="primary"):
            if location and location.get('latitude'):
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                current_date = now.strftime("%Y-%m-%d")
                loc_str = f"{location['latitude']},{location['longitude']}"
                
                status = "Late" if current_time > OFFICE_START_TIME else "Present"
                st.success(f"✅ Duty ON lag gayi hai!\nTime: {current_time} ({status})")
                st.info("Form submitted! Google sheet checking logic enabled.")
            else:
                st.error("❌ Location nahi mil saki. Kindly mobile setting me browser ko location permission allow karein.")
                
    with col2:
        if st.button("🛑 Duty OFF (Out)", use_container_width=True):
            if location and location.get('latitude'):
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                st.warning(f"🔒 Duty OFF lag gayi hai!\nTime: {current_time}")
            else:
                st.error("❌ Location error! Mobile ka GPS check karein.")

    st.write("---")
    if st.button("Logout", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.emp_id = ""
        st.session_state.emp_name = ""
        st.rerun()
