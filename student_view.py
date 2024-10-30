import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import mysql.connector
from mysql.connector import Error

def get_connection_to_mysql():
    try:
        return mysql.connector.connect(
            host="localhost",
            user="root",
            password="1234",
            database="student_"
        )
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None

def get_students_list(name):
    with get_connection_to_mysql() as connection:
        with connection.cursor() as cursor:
            cursor.execute("SELECT attendance_percentage, exam_eligibility, department_name FROM student WHERE full_name=%s", (name,))
            attendance = cursor.fetchone()
    attendance_percentage, exam_eligibility, department_name = attendance
    st.write(f"Attendance Percentage = {attendance_percentage}")
    if exam_eligibility:
        st.success("Eligible for exam")
    else:
        st.error("Not eligible for exam")

    subject_options = {
        "cs": ["Data Structures", "Algorithm"],
        "maths": ["Statistics", "Probability"]
    }
    selection = st.selectbox("Select subject", options=subject_options.get(department_name, []))

    with get_connection_to_mysql() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT student_id, student_name, department_name, date_, attendance_status
                FROM attendance
                WHERE student_name=%s AND subject_name=%s;
            """, (name, selection))
            student = cursor.fetchall()
    attendance_df = pd.DataFrame(student, columns=['Student ID', 'Full Name', 'Department Name', 'Date', 'Attendance Status'])
    st.dataframe(attendance_df)

def pie_graph(name):
    with get_connection_to_mysql() as connection:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    SUM(CASE WHEN attendance_status = 'present' THEN 1 ELSE 0 END) AS present_count,
                    SUM(CASE WHEN attendance_status = 'absent' THEN 1 ELSE 0 END) AS absent_count,
                    SUM(CASE WHEN attendance_status = 'late' THEN 1 ELSE 0 END) AS late_count,
                    COUNT(*) AS total_classes
                FROM attendance
                WHERE student_name=%s
            """, (name,))
            present_count, absent_count, late_count, total_classes = cursor.fetchone()

    labels = ['Absent', 'Late', 'Present']
    values = [absent_count, late_count, present_count]
    colors = ['#ff9999', '#66b3ff', '#99ff99']
    explode = (0.1, 0.1, 0.1)

    fig, ax = plt.subplots(figsize=(4, 4), facecolor=None)
    wedges, texts, autotexts = ax.pie(
        values,
        explode=explode,
        labels=labels,
        colors=colors,
        autopct='%1.1f%%',
        startangle=90,
        shadow=True,
        textprops={'color': 'white'}
    )
    ax.set_facecolor(None)
    ax.set_title('Attendance Breakdown', color='white')
    ax.axis('equal')
    fig.patch.set_alpha(0.0)
    st.pyplot(fig)

def main(name):
    st.title(f"Welcome {name}")
    get_students_list(name)
    pie_graph(name)

if __name__ == "__main__":
    main("name")
