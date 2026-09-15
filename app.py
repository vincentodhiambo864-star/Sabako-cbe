import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
from fpdf import FPDF
import plotly.express as px

st.set_page_config(page_title="Sabako Comprehensive School", layout="wide", page_icon="🎓")
DB = "sabako.db"

# PP1 TO GRADE 12
LEVELS = ["PP1","PP2","Grade 1","Grade 2","Grade 3","Grade 4","Grade 5","Grade 6","Grade 7","Grade 8","Grade 9","Grade 10","Grade 11","Grade 12"]
STREAMS = ["","East","West","North","South","A","B","C"]
TERMS = ["Term 1","Term 2","Term 3"]
EXAMS = ["Opener","Mid Term","End Term"]

def get_conn():
    conn = sqlite3.connect(DB, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_conn()
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS students (
        upi TEXT PRIMARY KEY, name TEXT, level TEXT, stream TEXT,
        parent_phone TEXT, status TEXT DEFAULT 'Active', created_at TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS marks (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        upi TEXT, term TEXT, exam TEXT, subject TEXT, score REAL)''')
    conn.commit()
    conn.close()

init_db()

st.title("🎓 SABAKO COMPREHENSIVE SCHOOL - CBE Portal")
st.caption("PP1 to Grade 12 | CBC Management System | Eldoret - Rift Valley")

menu = st.sidebar.selectbox("MENU", ["Dashboard","Admit Learner","Bulk Import","Manage Learners","Enter Marks","Analysis & Ranking","Report Cards"])

if menu == "Dashboard":
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    if df.empty:
        st.info("No learners yet. Go to Admit Learner.")
    else:
        col1,col2,col3,col4 = st.columns(4)
        col1.metric("Total", len(df))
        col2.metric("Active", len(df[df['status']=='Active']))
        col3.metric("Inactive/Gone", len(df[df['status']!='Active']))
        col4.metric("Classes", df['level'].nunique())
        st.divider()
        c1,c2 = st.columns(2)
        active_counts = df[df['status']=='Active'].groupby('level').size().reindex(LEVELS, fill_value=0)
        c1.bar_chart(active_counts)
        c1.caption("Active per Level (PP1-Grade12)")
        fig = px.pie(df, names='status', title="Active vs Inactive - All levels remain in portal")
        c2.plotly_chart(fig, use_container_width=True)
        st.dataframe(df, use_container_width=True)

elif menu == "Admit Learner":
    st.subheader("Admit Learner - PP1 to Grade 12")
    with st.form("admit"):
        upi = st.text_input("UPI / Assessment No. *")
        name = st.text_input("Full Name *")
        col1,col2 = st.columns(2)
        level = col1.selectbox("Level", LEVELS)
        stream = col2.selectbox("Stream", STREAMS)
        phone = st.text_input("Parent Phone")
        status = st.selectbox("Status", ["Active","Inactive / Gone"])
        if st.form_submit_button("Save Learner"):
            if not upi or not name:
                st.error("UPI and Name required")
            else:
                try:
                    conn = get_conn()
                    conn.execute("INSERT INTO students VALUES (?,?,?,?,?,?,?)",
                        (upi.strip(), name.strip().title(), level, stream, phone, status, datetime.now().isoformat()))
                    conn.commit()
                    conn.close()
                    st.success(f"{name} admitted to {level}!")
                except sqlite3.IntegrityError:
                    st.error("UPI already exists!")

elif menu == "Bulk Import":
    st.subheader("Bulk Import Excel - PP1 to Grade 12")
    st.write("Columns needed: UPI, Name, Level, Stream, Parent_Phone, Status")
    file = st.file_uploader("Upload Excel/CSV", type=["xlsx","csv"])
    if file:
        try:
            df = pd.read_excel(file) if file.name.endswith("xlsx") else pd.read_csv(file)
            st.dataframe(df.head())
            if st.button("Import Now"):
                conn = get_conn()
                count=0
                for _, r in df.iterrows():
                    try:
                        conn.execute("INSERT OR REPLACE INTO students VALUES (?,?,?,?,?,?,?)",
                            (str(r.get('UPI','')).strip(), str(r.get('Name','')).strip(), str(r.get('Level','')).strip(), str(r.get('Stream','')).strip(), str(r.get('Parent_Phone','')).strip(), str(r.get('Status','Active')).strip() or 'Active', datetime.now().isoformat()))
                        count+=1
                    except: pass
                conn.commit()
                conn.close()
                st.success(f"Imported {count} learners!")
        except Exception as e:
            st.error(f"Error: {e}")

elif menu == "Manage Learners":
    st.subheader("Manage Learners - Inactive remain in system (not deleted)")
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM students", conn)
    conn.close()
    if df.empty:
        st.info("No data")
    else:
        f1,f2 = st.columns(2)
        lvl_filter = f1.multiselect("Filter Level", LEVELS)
        stat_filter = f2.selectbox("Status", ["All","Active","Inactive / Gone"])
        if lvl_filter:
            df = df[df['level'].isin(lvl_filter)]
        if stat_filter!="All":
            df = df[df['status']==stat_filter]
        st.dataframe(df, use_container_width=True)
        st.divider()
        upi_edit = st.selectbox("Select UPI to Edit", df['upi'].tolist())
        if upi_edit:
            conn = get_conn()
            row = conn.execute("SELECT * FROM students WHERE upi=?", (upi_edit,)).fetchone()
            conn.close()
            new_status = st.selectbox("New Status", ["Active","Inactive / Gone"], index=0 if row['status']=='Active' else 1)
            c1,c2 = st.columns(2)
            if c1.button("Update Status"):
                conn=get_conn()
                conn.execute("UPDATE students SET status=? WHERE upi=?", (new_status, upi_edit))
                conn.commit()
                conn.close()
                st.success("Updated! Learner kept as Inactive - not removed.")
                st.rerun()
            if c2.button("DELETE PERMANENTLY"):
                conn=get_conn()
                conn.execute("DELETE FROM students WHERE upi=?", (upi_edit,))
                conn.execute("DELETE FROM marks WHERE upi=?", (upi_edit,))
                conn.commit()
                conn.close()
                st.warning("Permanently deleted!")
                st.rerun()

elif menu == "Enter Marks":
    st.subheader("Enter Marks - PP1 to Grade 12")
    col1,col2,col3,col4 = st.columns(4)
    term = col1.selectbox("Term", TERMS)
    exam = col2.selectbox("Exam", EXAMS)
    level = col3.selectbox("Level", LEVELS)
    subject = col4.text_input("Subject")
    if subject:
        conn = get_conn()
        learners = pd.read_sql_query("SELECT * FROM students WHERE level=? AND status='Active'", conn, params=(level,))
        conn.close()
        if learners.empty:
            st.warning(f"No Active learners in {level}")
        else:
            st.write(f"Entering {subject} for {level} - {term} {exam}")
            scores = {}
            for _, lr in learners.iterrows():
                scores[lr['upi']] = st.number_input(f"{lr['name']} ({lr['upi']})", 0.0, 100.0, 0.0, key=lr['upi'])
            if st.button("Save Marks"):
                conn = get_conn()
                for upi, sc in scores.items():
                    conn.execute("DELETE FROM marks WHERE upi=? AND term=? AND exam=? AND subject=?", (upi, term, exam, subject))
                    if sc>0:
                        conn.execute("INSERT INTO marks (upi,term,exam,subject,score) VALUES (?,?,?,?,?)", (upi, term, exam, subject, sc))
                conn.commit()
                conn.close()
                st.success("Marks saved!")

elif menu == "Analysis & Ranking":
    st.subheader("Analysis PP1-Grade 12")
    conn = get_conn()
    marks = pd.read_sql_query("SELECT m.*, s.name, s.level FROM marks m JOIN students s ON m.upi=s.upi", conn)
    conn.close()
    if marks.empty:
        st.info("No marks yet")
    else:
        c1,c2,c3 = st.columns(3)
        term = c1.selectbox("Term", TERMS)
        exam = c2.selectbox("Exam", EXAMS)
        level = c3.selectbox("Level", ["All"]+LEVELS)
        f = marks[(marks['term']==term) & (marks['exam']==exam)]
        if level!="All":
            f = f[f['level']==level]
        if f.empty:
            st.warning("No data")
        else:
            pivot = f.pivot_table(index=['upi','name','level'], columns='subject', values='score', aggfunc='mean').reset_index()
            pivot['Total'] = pivot.select_dtypes(include='number').sum(axis=1)
            pivot['Mean'] = pivot.select_dtypes(include='number').mean(axis=1)
            pivot = pivot.sort_values('Total', ascending=False)
            pivot['Rank'] = range(1, len(pivot)+1)
            st.dataframe(pivot, use_container_width=True)
            fig = px.bar(pivot.head(10), x='name', y='Total', color='level', title="Top 10")
            st.plotly_chart(fig, use_container_width=True)

elif menu == "Report Cards":
    st.subheader("Report Cards")
    conn = get_conn()
    learners = pd.read_sql_query("SELECT * FROM students WHERE status='Active'", conn)
    conn.close()
    if learners.empty:
        st.info("No learners")
    else:
        upi = st.selectbox("Select Learner", learners['upi']+" - "+learners['name']+" - "+learners['level'])
        term = st.selectbox("Term", TERMS)
        exam = st.selectbox("Exam", EXAMS)
        if st.button("Generate PDF") and upi:
            real_upi = upi.split(" - ")[0]
            conn = get_conn()
            st_row = conn.execute("SELECT * FROM students WHERE upi=?", (real_upi,)).fetchone()
            mks = pd.read_sql_query("SELECT * FROM marks WHERE upi=? AND term=? AND exam=?", conn, params=(real_upi, term, exam))
            conn.close()
            if mks.empty:
                st.warning("No marks")
            else:
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial","B",16)
                pdf.cell(0,10,"S
