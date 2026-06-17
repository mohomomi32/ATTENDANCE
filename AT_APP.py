import streamlit as st
from streamlit_geolocation import streamlit_geolocation
from datetime import datetime
import pandas as pd

st.set_page_config(page_title="GEPL Attendance Portal", page_icon="📍", layout="centered")

try:
    SHEET_ID = st.secrets["connections"]["gsheets"]["spreadsheet"].split("/d/")[1].split("/")[0]
    EMP_URL = f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/gviz/tq?tqx=out:csv&sheet=Employees"
    
    # Data load karte hi column ke names ke aas paas se faltu space khatam karna
    emp_data = pd.read_csv(EMP_URL)
    emp_data.columns = emp_data.columns.str.strip().str.lower()
except Exception as e:
    st.error("Google Sheet load nahi ho saki. Kindly Sheet ki Share settings check karein.")
    st.stop()

OFFICE_START_TIME = "09:15:00"

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
    st.session_state.emp_id = ""
    st.session_state.emp_name = ""

if not st.session_state.logged_in:
    st.markdown("<h2 style='text-align: center;'>📍 GEPL Attendance System</h2>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: gray;'>Apni ID aur Password daal kar Login karein</p>", unsafe_allow_html=True)
    
    emp_id = st.text_input("Employee ID").strip()
    password = st.text_input("Password", type="password").strip()
    
    if st.button("Login", use_container_width=True, type="primary"):
        # Yahan humne column names ko lowercase (.str.lower()) handle kiya hai safely
        if 'emp_id' in emp_data.columns and 'password' in emp_data.columns:
            user_row = emp_data[(emp_data['emp_id'].astype(str).str.strip() == emp_id) & (emp_data['password'].astype(str).str.strip() == password)]
            
            if not user_row.empty:
                st.session_state.logged_in = True
                st.session_state.emp_id = emp_id
                st.session_state.emp_name = user_row['name'].values[0] if 'name' in user_row.columns else emp_id
                st.rerun()
            else:
                st.error("❌ Galat ID ya Password! Dobara check karein.")
        else:
            st.error("❌ Google Sheet ki pehli line me 'emp_id' aur 'password' ki headings missing hain!")

else:
    st.markdown(f"### 👋 KhushAamdeed, **{st.session_state.emp_name}**")
    st.caption(f"ID: {st.session_state.emp_id} | Date: {datetime.now().strftime('%d-%B-%Y')}")
    
    st.warning("⚠️ Attendance lagane se pehle mobile ki Location (GPS) lazmi ON karein.")
    
    location = streamlit_geolocation()
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🚀 Duty ON (In)", use_container_width=True, type="primary"):
            if location and location.get('latitude'):
                now = datetime.now()
                current_time = now.strftime("%H:%M:%S")
                status = "Late" if current_time > OFFICE_START_TIME else "Present"
                st.success(f"✅ Duty ON lag gayi!\nTime: {current_time} ({status})")
            else:
                st.error("❌ Location nahi mil saki. Kindly GPS ON karein.")
                
    with col2:
        if st.button("🛑 Duty OFF (Out)", use_container_width=True):
            if location and location.get('latitude'):
                current_time = datetime.now().strftime("%H:%M:%S")
                st.warning(f"🔒 Duty OFF lag gayi!\nTime: {current_time}")
            else:
                st.error("❌ Location error!")

    st.write("---")
    if st.button("Logout", type="secondary", use_container_width=True):
        st.session_state.logged_in = False
        st.session_state.emp_id = ""
        st.session_state.emp_name = ""
        st.rerun()
