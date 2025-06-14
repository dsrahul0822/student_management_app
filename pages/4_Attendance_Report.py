import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

# -------------------- PAGE SETUP --------------------
st.set_page_config(page_title="Attendance Report", layout="centered")
st.title("📊 Attendance Percentage Report")

# -------------------- AUTH GUARD --------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔐 Please log in first from the Login page.")
    st.stop()

# -------------------- LOGOUT --------------------
with st.sidebar:
    st.write(f"👤 Logged in as: `{st.session_state.username}`")
    if st.button("🚪 Logout"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.rerun()

# -------------------- GOOGLE SHEET SETUP --------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_dict), scope)
#creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open("LearnerDatabase")

attendance_df = pd.DataFrame(sheet.worksheet("attendance").get_all_records())
students_df = pd.DataFrame(sheet.worksheet("students").get_all_records())

# -------------------- SELECT BATCH --------------------
batches = sorted(students_df["batch"].unique())
selected_batch = st.selectbox("Select a Batch", batches)

# -------------------- FILTER & CALCULATE --------------------
filtered_attendance = attendance_df[attendance_df["batch"] == selected_batch]
filtered_students = students_df[students_df["batch"] == selected_batch]

if filtered_attendance.empty:
    st.info("No attendance records found for this batch.")
else:
    report = []
    for _, student in filtered_students.iterrows():
        sid = student["student_id"]
        name = student["name"]
        total = filtered_attendance[filtered_attendance["student_id"] == sid].shape[0]
        present = filtered_attendance[
            (filtered_attendance["student_id"] == sid) &
            (filtered_attendance["status"].str.lower() == "present")
        ].shape[0]
        percentage = round((present / total) * 100, 2) if total > 0 else 0
        report.append({
            "Student ID": sid,
            "Name": name,
            "Present": present,
            "Total Classes": total,
            "Attendance %": f"{percentage}%"
        })

    df_report = pd.DataFrame(report)
    st.dataframe(df_report)

    csv = df_report.to_csv(index=False).encode('utf-8')
    st.download_button("⬇️ Download Report as CSV", data=csv, file_name=f"{selected_batch}_attendance_report.csv")
