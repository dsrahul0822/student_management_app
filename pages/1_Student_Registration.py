import streamlit as st
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
st.set_page_config(page_title="Student Registration Wizard", layout="centered")

# -------------------- AUTH CHECK --------------------
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.warning("🔐 Please log in first from the Login page.")
    st.stop()

# -------------------- SIDEBAR LOGOUT --------------------
with st.sidebar:
    st.write(f"👤 Logged in as: `{st.session_state.username}`")
    if st.button("🚪 Logout"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# -------------------- GOOGLE SHEETS SETUP --------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds_dict = st.secrets["gcp_service_account"]
creds = ServiceAccountCredentials.from_json_keyfile_dict(dict(creds_dict), scope)
#creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
SHEET = client.open("LearnerDatabase")

def add_student(data):
    SHEET.worksheet("students").append_row(data)

def get_student_count(batch_name):
    students = SHEET.worksheet("students").get_all_records()
    return len([s for s in students if s['batch'] == batch_name])

def add_education_row(data):
    SHEET.worksheet("education").append_row(data)

def add_job_row(data):
    SHEET.worksheet("jobs").append_row(data)

# -------------------- STREAMLIT SETUP --------------------

st.title("🎓 Student Registration Wizard")

# -------------------- INIT SESSION --------------------
if "step" not in st.session_state:
    st.session_state.step = 1
if "student_id" not in st.session_state:
    st.session_state.student_id = None

# -------------------- STEP 1: STUDENT INFO --------------------
if st.session_state.step == 1:
    st.subheader("Step 1: Student Information")

    with st.form("student_form"):
        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone Number")
        linkedin_url = st.text_input("LinkedIn Profile URL")
        batch = st.selectbox("Batch", ["DAG14", "DAG15", "DAG16"])
        course = st.selectbox("Course", ["Python", "SQL", "Power BI"])
        submit = st.form_submit_button("Next")

    if submit:
        count = get_student_count(batch) + 1
        student_id = f"{batch}-{str(count).zfill(3)}"
        st.session_state.student_id = student_id
        add_student([
            student_id, name, email, phone, linkedin_url, batch, course, str(datetime.now().date())
        ])
        st.success(f"✅ Registered Successfully! Your Student ID: **{student_id}**")
        st.session_state.step = 2

# -------------------- STEP 2: EDUCATION --------------------
if st.session_state.step == 2:
    st.subheader("Step 2: Add Education Details")

    if "education_list" not in st.session_state:
        st.session_state.education_list = []

    with st.form("edu_form", clear_on_submit=True):
        degree = st.text_input("Degree")
        institute = st.text_input("Institute / University")
        year = st.text_input("Year of Completion")
        percentage = st.text_input("Percentage / CGPA")
        edu_submit = st.form_submit_button("Add Education")

    if edu_submit:
        row = [st.session_state.student_id, degree, institute, year, percentage]
        add_education_row(row)
        st.session_state.education_list.append(row)
        st.success("🎓 Education record added!")

    if st.session_state.education_list:
        st.markdown("### 📚 Education Records Added")
        for idx, edu in enumerate(st.session_state.education_list, 1):
            st.markdown(f"**{idx}.** {edu[1]} from {edu[2]} ({edu[3]}) — {edu[4]}")

    st.button("Next: Add Job History", on_click=lambda: st.session_state.update({"step": 3}))

# -------------------- STEP 3: JOB HISTORY --------------------
if st.session_state.step == 3:
    st.subheader("Step 3: Add Job History")

    if "job_list" not in st.session_state:
        st.session_state.job_list = []

    with st.form("job_form", clear_on_submit=True):
        company = st.text_input("Company Name")
        designation = st.text_input("Designation")
        start_date = st.date_input("Start Date")
        end_date = st.date_input("End Date")
        job_submit = st.form_submit_button("Add Job")

    if job_submit:
        row = [st.session_state.student_id, company, designation, str(start_date), str(end_date)]
        add_job_row(row)
        st.session_state.job_list.append(row)
        st.success("💼 Job record added!")

    if st.session_state.job_list:
        st.markdown("### 🧾 Job Records Added")
        for idx, job in enumerate(st.session_state.job_list, 1):
            st.markdown(f"**{idx}.** {job[1]} as {job[2]} ({job[3]} to {job[4]})")

    st.button("Finish Registration", on_click=lambda: st.session_state.update({"step": 4}))

# -------------------- STEP 4: COMPLETE --------------------
if st.session_state.step == 4:
    st.success("🎉 All data saved successfully!")
    st.markdown("### ✅ Registration Complete")
    st.markdown(f"**Student ID:** `{st.session_state.student_id}`")
    st.info("You can now go to the Search Page to view this full profile.")

    if st.button("➕ Register Another Student"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
