# SABAKO COMPREHENSIVE SCHOOL - CBE MASTER PP1-GRADE 10
import streamlit as st
import pandas as pd
import plotly.express as px
from fpdf import FPDF
import sqlite3

st.set_page_config(page_title="Sabako Comprehensive - CBE", layout="wide")
st.title("SABAKO COMPREHENSIVE SCHOOL")
st.subheader("CBE MASTER - PP1 to Grade 12")
st.caption("Gone learners remain unless deleted | Hosted Version")

conn = sqlite3.connect('cbe.db', check_same_thread=False)
conn.execute('''CREATE TABLE IF NOT EXISTS students
(id INTEGER PRIMARY KEY, upi TEXT, name TEXT, level TEXT, stream TEXT, status TEXT DEFAULT 'Active', parent_phone TEXT)''')
conn.execute('''CREATE TABLE IF NOT EXISTS marks
(id INTEGER PRIMARY KEY, student_id INTEGER, exam TEXT, term TEXT, year INTEGER, learning_area TEXT, score INTEGER, level TEXT)''')

def get_level(score):
    if score >= 80: return "EE"
    if score >= 60: return "ME"
    if score >= 40: return "AE"
    return "BE"

ALL_LEVELS = ["PP1","PP2","Grade 1","Grade 2","Grade 3","Grade 4","Grade 5","Grade 6","Grade 7","Grade 8","Grade 9","Grade 10"]
# ... full code from previous version included ...
