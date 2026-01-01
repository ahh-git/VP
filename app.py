import streamlit as st
import pandas as pd
import re
import os

# --- CONFIGURATION ---
DATA_FILE = "section_registrations.csv"
SECTIONS = ["Section A", "Section B", "Section C", "Section D", "Section E"]
LIMIT = 50

# Initialize CSV storage
if not os.path.exists(DATA_FILE):
    df = pd.DataFrame(columns=["Student ID", "Section", "Status"])
    df.to_csv(DATA_FILE, index=False)

def load_data():
    return pd.read_csv(DATA_FILE)

# --- PAGE UI ---
st.set_page_config(page_title="Uni Section Tracker", layout="wide")

st.title("🏛️ University Section Registration")
st.info("Note: You can only register for ONE section. ID Format: xxx-xx-xxx")

# Load current data
df_current = load_data()

# --- SIDEBAR: LIVE CAPACITY ---
st.sidebar.header("📊 Section Capacity")
for sec in SECTIONS:
    count = len(df_current[df_current["Section"] == sec])
    col1, col2 = st.sidebar.columns([3, 1])
    col1.write(f"**{sec}**")
    col2.write(f"{count}/{LIMIT}")
    st.sidebar.progress(count / LIMIT)

# --- MAIN FORM ---
with st.container():
    st.subheader("Register Your Desired Section")
    
    with st.form("reg_form", clear_on_submit=True):
        input_id = st.text_input("Enter Student ID", placeholder="e.g. 221-15-123")
        input_section = st.selectbox("Select Section", SECTIONS)
        
        submit_btn = st.form_submit_button("Confirm Registration")

        if submit_btn:
            # 1. Check ID Format (Regex)
            if not re.match(r"^\d{3}-\d{2}-\d{3}$", input_id):
                st.error("❌ Invalid ID format! Use xxx-xx-xxx")
            
            # 2. STRICT CHECK: Same Roll multiple section check
            elif input_id in df_current["Student ID"].astype(str).values:
                # Find which section they are already in
                existing_sec = df_current[df_current["Student ID"] == input_id]["Section"].values[0]
                st.warning(f"⚠️ Access Denied: ID {input_id} is already registered in **{existing_sec}**.")
            
            # 3. Check if section is full
            elif len(df_current[df_current["Section"] == input_section]) >= LIMIT:
                st.error(f"🚫 {input_section} is full! Please select another.")
            
            else:
                # Save to CSV
                new_row = pd.DataFrame([[input_id, input_section, "Registered"]], 
                                     columns=["Student ID", "Section", "Status"])
                new_row.to_csv(DATA_FILE, mode='a', header=False, index=False)
                st.success(f"✅ Success! ID {input_id} has been added to {input_section}.")
                st.balloons()
                st.rerun()

# --- DATA VISUALIZATION ---
st.divider()
st.subheader("Current Enrollment Overview")
if not df_current.empty:
    # Creating a summary pivot table
    summary = df_current.groupby("Section").count().rename(columns={"Student ID": "Students Enrolled"})
    st.table(summary)
else:
    st.write("No registrations yet. Be the first!")

# Optional: Search feature
search_id = st.text_input("🔍 Search if your ID is registered")
if search_id:
    result = df_current[df_current["Student ID"] == search_id]
    if not result.empty:
        st.write(f"Record found: Registered in **{result['Section'].values[0]}**")
    else:
        st.write("No record found.")
