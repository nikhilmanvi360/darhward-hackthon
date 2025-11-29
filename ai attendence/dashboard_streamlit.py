"""
Streamlit Dashboard for AI Attendance System
Run with: streamlit run dashboard_streamlit.py
"""

import streamlit as st
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import time
from datetime import datetime, timedelta
from fpdf import FPDF
import io
import os

# Page Config
st.set_page_config(
    page_title="AI Attendance Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
DB_PATH = os.path.join('models', 'students.db')

# Custom CSS
st.markdown("""
    <style>
    .stMetric {
        background-color: #f0f2f6;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
    .stDataFrame {
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Data Functions ---

def get_data(date_str):
    """Fetch attendance and student data from SQLite"""
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Get all students
        students_df = pd.read_sql_query("SELECT id, name, roll_number FROM students", conn)
        
        # Get attendance for specific date
        query = f"""
            SELECT a.name, s.roll_number, a.timestamp, a.status 
            FROM attendance a
            JOIN students s ON a.student_id = s.id
            WHERE DATE(a.timestamp) = '{date_str}'
        """
        attendance_df = pd.read_sql_query(query, conn)
        
        conn.close()
        return students_df, attendance_df
    except Exception as e:
        st.error(f"Database Error: {e}")
        return pd.DataFrame(), pd.DataFrame()

def process_data(students_df, attendance_df, late_threshold_time):
    """Process data to categorize students"""
    if students_df.empty:
        return [], [], []

    all_students = students_df['name'].tolist()
    present_records = attendance_df.to_dict('records')
    
    present_names = [r['name'] for r in present_records]
    absent_names = [name for name in all_students if name not in present_names]
    
    # Categorize Present vs Late
    on_time = []
    late = []
    
    threshold = datetime.strptime(late_threshold_time, "%H:%M").time()
    
    for record in present_records:
        # Parse timestamp
        try:
            ts = datetime.strptime(record['timestamp'], '%Y-%m-%d %H:%M:%S')
            record['time'] = ts.strftime("%H:%M:%S")
            
            if ts.time() > threshold:
                late.append(record)
                record['status'] = 'Late'
            else:
                on_time.append(record)
                record['status'] = 'Present'
        except:
            on_time.append(record)

    # Create DataFrames for display
    present_df = pd.DataFrame(present_records)
    absent_df = students_df[students_df['name'].isin(absent_names)].copy()
    absent_df['status'] = 'Absent'
    
    return present_df, absent_df, late

# --- Export Functions ---

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()

def to_pdf(df, date_str):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    
    pdf.cell(200, 10, txt=f"Attendance Report - {date_str}", ln=1, align='C')
    pdf.ln(10)
    
    # Table Header
    cols = df.columns.tolist()
    for col in cols:
        pdf.cell(40, 10, str(col), 1)
    pdf.ln()
    
    # Table Rows
    for _, row in df.iterrows():
        for col in cols:
            pdf.cell(40, 10, str(row[col]), 1)
        pdf.ln()
        
    return pdf.output(dest='S').encode('latin-1')

# --- Main Dashboard ---

def main():
    st.title("🎓 AI Attendance Analytics")
    
    # Sidebar
    st.sidebar.header("⚙️ Settings")
    selected_date = st.sidebar.date_input("Select Date", datetime.now())
    late_time = st.sidebar.time_input("Late Threshold", datetime.strptime("09:30", "%H:%M").time())
    auto_refresh = st.sidebar.checkbox("Auto Refresh (5s)", value=True)
    
    date_str = selected_date.strftime("%Y-%m-%d")
    late_str = late_time.strftime("%H:%M")
    
    # Fetch Data
    students_df, attendance_df = get_data(date_str)
    
    if students_df.empty:
        st.warning("No students registered in database.")
        return

    present_df, absent_df, late_list = process_data(students_df, attendance_df, late_str)
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_students = len(students_df)
    total_present = len(present_df)
    total_absent = len(absent_df)
    total_late = len(late_list)
    
    with col1:
        st.metric("Total Students", total_students)
    with col2:
        st.metric("Present", total_present, delta=f"{total_present/total_students*100:.1f}%" if total_students else "0%")
    with col3:
        st.metric("Absent", total_absent, delta_color="inverse", delta=f"-{total_absent}")
    with col4:
        st.metric("Late", total_late, delta_color="inverse", delta=f"{total_late}")

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Detailed View", "❌ Absent List", "📈 Analytics", "📥 Export"])
    
    with tab1:
        st.subheader("Present & Late Students")
        
        # Search
        search = st.text_input("🔍 Search Student", "")
        
        if not present_df.empty:
            display_df = present_df.copy()
            if search:
                display_df = display_df[display_df['name'].str.contains(search, case=False)]
            
            # Color highlighting
            def highlight_late(row):
                return ['background-color: #ffcccc' if row['status'] == 'Late' else '' for _ in row]
            
            st.dataframe(display_df.style.apply(highlight_late, axis=1), use_container_width=True)
        else:
            st.info("No attendance marked for this date.")

    with tab2:
        st.subheader("Absent Students")
        if not absent_df.empty:
            st.dataframe(absent_df[['name', 'roll_number', 'status']], use_container_width=True)
        else:
            st.success("Everyone is present! 🎉")

    with tab3:
        st.subheader("Daily Timeline")
        if not present_df.empty:
            # Timeline Chart
            present_df['hour'] = pd.to_datetime(present_df['timestamp']).dt.hour
            hourly_counts = present_df['hour'].value_counts().sort_index()
            
            fig, ax = plt.subplots(figsize=(10, 4))
            ax.bar(hourly_counts.index, hourly_counts.values, color='#4e73df')
            ax.set_xlabel("Hour of Day")
            ax.set_ylabel("Number of Students")
            ax.set_title("Arrival Time Distribution")
            ax.set_xticks(range(7, 18)) # Assuming school hours 7am-6pm
            ax.grid(axis='y', linestyle='--', alpha=0.7)
            
            st.pyplot(fig)
            
            # Pie Chart
            st.subheader("Attendance Distribution")
            labels = ['On Time', 'Late', 'Absent']
            sizes = [total_present - total_late, total_late, total_absent]
            colors = ['#1cc88a', '#f6c23e', '#e74a3b']
            
            fig2, ax2 = plt.subplots()
            ax2.pie(sizes, labels=labels, colors=colors, autopct='%1.1f%%', startangle=90)
            ax2.axis('equal')
            st.pyplot(fig2)
        else:
            st.info("Not enough data for analytics.")

    with tab4:
        st.subheader("Export Report")
        
        if not present_df.empty:
            # Prepare full report
            full_report = pd.concat([present_df, absent_df])
            
            # CSV
            csv = full_report.to_csv(index=False).encode('utf-8')
            st.download_button(
                "📄 Download CSV",
                csv,
                f"attendance_{date_str}.csv",
                "text/csv",
                key='download-csv'
            )
            
            # Excel
            excel_data = to_excel(full_report)
            st.download_button(
                "📊 Download Excel",
                excel_data,
                f"attendance_{date_str}.xlsx",
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key='download-excel'
            )
            
            # PDF
            # Simplified PDF for demo
            try:
                pdf_data = to_pdf(full_report[['name', 'roll_number', 'status']], date_str)
                st.download_button(
                    "📑 Download PDF",
                    pdf_data,
                    f"attendance_{date_str}.pdf",
                    "application/pdf",
                    key='download-pdf'
                )
            except Exception as e:
                st.error(f"PDF Generation Error: {e}")

    # Auto Refresh
    if auto_refresh:
        time.sleep(5)
        st.rerun()

if __name__ == "__main__":
    main()
