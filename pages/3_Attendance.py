import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
from datetime import date
st.set_page_config(page_title="Attendance Tracker", layout="centered")

# -------------------- AUTH CHECK --------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔐 Please log in first from the Login page.")
    st.stop()

# -------------------- SIDEBAR LOGOUT --------------------
with st.sidebar:
    st.write(f"👤 Logged in as: `{st.session_state.username}`")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# -------------------- GOOGLE SHEETS --------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_dict), scope)
#creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("LearnerDatabase")

students_df = pd.DataFrame(sheet.worksheet("students").get_all_records())
attendance_ws = sheet.worksheet("attendance")

# -------------------- UI --------------------
st.title("📋 Attendance Tracker")

batch_list = sorted(students_df["batch"].unique())
selected_batch = st.selectbox("Select Batch", batch_list)
class_name = st.text_input("Enter Class Name (e.g., Python Class 1)")
selected_date = st.date_input("Select Date", value=date.today())

filtered_students = students_df[students_df["batch"] == selected_batch]

if not filtered_students.empty:
    st.markdown("### ✅ Mark Attendance (check = Present)")
    present_ids = st.multiselect(
        "Select Present Students",
        options=filtered_students["name"].tolist(),
        default=filtered_students["name"].tolist()  # Preselect all as present
    )

    if st.button("✅ Submit Attendance"):
        for _, row in filtered_students.iterrows():
            status = "Present" if row["name"] in present_ids else "Absent"
            attendance_ws.append_row([
                row["student_id"],
                row["name"],
                row["batch"],
                str(selected_date),
                class_name,
                status
            ])
        st.success("🎉 Attendance recorded successfully!")
else:
    st.info("No students found in this batch.")
