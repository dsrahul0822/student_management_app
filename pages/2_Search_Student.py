import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd

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

# -------------------- GOOGLE SHEETS SETUP --------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_dict), scope)
#creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
SHEET = client.open("LearnerDatabase")

# -------------------- LOAD DATA --------------------
students_df = pd.DataFrame(SHEET.worksheet("students").get_all_records())
education_df = pd.DataFrame(SHEET.worksheet("education").get_all_records())
jobs_df = pd.DataFrame(SHEET.worksheet("jobs").get_all_records())

# -------------------- SEARCH UI --------------------
st.title("🔍 Search Student Profile")

search_input = st.text_input("Enter student name or ID (partial allowed)")

if search_input:
    # Partial match search
    filtered_students = students_df[
        students_df['name'].str.lower().str.contains(search_input.lower()) |
        students_df['student_id'].str.lower().str.contains(search_input.lower())
    ]

    if not filtered_students.empty:
        st.markdown(f"### Found {len(filtered_students)} match(es)")
        
        # Format options like: DAG14-001 - Rahul Tiwari (Python)
        student_options = filtered_students.apply(
            lambda row: f"{row['student_id']} - {row['name']} ({row['course']})", axis=1
        )

        selected_entry = st.selectbox("Select a student to view details", student_options)
        selected_id = selected_entry.split(" - ")[0]

        student = students_df[students_df['student_id'] == selected_id].iloc[0]

        st.success(f"✅ Profile found for: {student['name']} ({student['student_id']})")

        # -------------------- STUDENT INFO --------------------
        st.subheader("👤 Student Information")
        st.write(student)

        # -------------------- EDUCATION INFO --------------------
        st.subheader("🎓 Education History")
        edu = education_df[education_df['student_id'] == selected_id]
        if not edu.empty:
            st.dataframe(edu.drop(columns=["student_id"]))
        else:
            st.info("No education records found.")

        # -------------------- JOB HISTORY --------------------
        st.subheader("💼 Job History")
        jobs = jobs_df[jobs_df['student_id'] == selected_id]
        if not jobs.empty:
            st.dataframe(jobs.drop(columns=["student_id"]))
        else:
            st.info("No job history found.")
    else:
        st.error("❌ No matching student found.")
