import streamlit as st
import pandas as pd
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
import send__mail
import login_page
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


def configure_grid_options(df, editable_status=True):
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_column("attendance_status", editable=editable_status,
                        cellEditor='agSelectCellEditor',
                        cellEditorParams={'values': ['absent', 'present', 'late']})
    gb.configure_column("date_", editable=False, sortable=False, resizable=False)
    gb.configure_column("student_id", editable=False, sortable=False, resizable=False)
    gb.configure_column("record_id", editable=False, sortable=False, resizable=False)
    gb.configure_default_column(filterable=False, sortable=False)
    return gb.build()


def calculate_attendance_percentage_and_fetch_ineligible_emails():
    db = get_connection_to_mysql()
    cursor = db.cursor(dictionary=True)

    cursor.execute("""
        SELECT student_id,
               SUM(CASE WHEN attendance_status = 'present' THEN 1 ELSE 0 END) AS present_count,
               COUNT(*) AS total_classes
        FROM attendance
        GROUP BY student_id
    """)
    attendance_data = cursor.fetchall()
    attendance_df = pd.DataFrame(attendance_data)

    attendance_df['attendance_percentage'] = (attendance_df['present_count'] / attendance_df['total_classes']) * 100
    attendance_df['exam_eligibility'] = attendance_df['attendance_percentage'] >= 75

    ineligible_students_emails = []

    for index, row in attendance_df.iterrows():
        cursor.execute("""
            UPDATE student
            SET attendance_percentage = %s, exam_eligibility = %s
            WHERE student_id = %s
        """, (row['attendance_percentage'], row['exam_eligibility'], row['student_id']))

        if not row['exam_eligibility']:
            cursor.execute("SELECT email_id FROM student WHERE student_id = %s", (row['student_id'],))
            ineligible_students_emails.append(cursor.fetchone()['email_id'])

    db.commit()
    cursor.close()
    db.close()
    return ineligible_students_emails


def send_email():
    db = get_connection_to_mysql()
    cursor = db.cursor(dictionary=True)
    email_ = login_page.mail_id()
    cursor.execute("SELECT teacher_name, department_name, subject_name FROM teacher WHERE email_id=%s", (email_,))
    teacher = cursor.fetchone()
    department_name, subject_name = teacher['department_name'], teacher['subject_name']

    cursor.execute("SELECT full_name FROM student WHERE department_name=%s", (department_name,))
    full_name_list = [name['full_name'] for name in cursor.fetchall()]

    selected_student = st.selectbox("Select student", options=full_name_list)
    cursor.execute("SELECT email_id FROM student WHERE full_name=%s", (selected_student,))
    mail = cursor.fetchone()['email_id']

    subject = st.text_input("Subject")
    body = st.text_area("Body")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Send Mail"):
            if selected_student:
                send__mail.send_email(subject, body, mail)
                st.success(f"Email sent to {selected_student}!")
            else:
                st.warning("No student selected.")

    with col2:
        if st.button("Send mail to non-eligible students"):
            mail_lst = calculate_attendance_percentage_and_fetch_ineligible_emails()
            for mail in mail_lst:
                send__mail.send_email("Not eligible", "Hello, you are not eligible for the exam.", mail)


def mark_attendance():
    db = get_connection_to_mysql()
    cursor = db.cursor(dictionary=True)

    email = login_page.mail_id()
    cursor.execute('SELECT teacher_name, department_name, subject_name FROM teacher WHERE email_id=%s', (email,))
    teacher = cursor.fetchone()
    department_name, subject_name = teacher['department_name'], teacher['subject_name']

    selected_date = st.date_input('Select date', pd.to_datetime('today').date())
    cursor.execute("""
        SELECT record_id, student_id, student_name, attendance_status, date_
        FROM attendance
        WHERE department_name=%s AND subject_name=%s AND date_=%s
    """, (department_name, subject_name, selected_date.strftime('%Y-%m-%d')))

    attendance_df = pd.DataFrame(cursor.fetchall())
    if selected_date:
        attendance_df['date_'] = selected_date.strftime('%Y-%m-%d')

    if attendance_df.empty:
        st.info(f"No records found for {selected_date}. New records will be created.")
        cursor.execute("SELECT student_id, full_name AS student_name FROM student WHERE department_name=%s",
                       (department_name,))
        students_df = pd.DataFrame(cursor.fetchall())
        students_df['attendance_status'] = 'absent'
        students_df['date_'] = selected_date.strftime('%Y-%m-%d')
        attendance_df = students_df

    grid_option = configure_grid_options(attendance_df)
    grid_response = AgGrid(attendance_df, gridOptions=grid_option, update_mode=GridUpdateMode.VALUE_CHANGED)

    if st.button("Save Attendance"):
        updated_data = grid_response['data']
        if isinstance(updated_data, pd.DataFrame):
            updated_data = updated_data.to_dict(orient="records")

        for row in updated_data:
            attendance_status = row['attendance_status']
            date_ = row['date_']
            student_id = row['student_id']
            student_name = row['student_name']

            cursor.execute("""
                SELECT record_id
                FROM attendance
                WHERE student_id=%s AND subject_name=%s AND date_=%s
            """, (student_id, subject_name, date_))

            record = cursor.fetchone()
            if record:
                cursor.execute("UPDATE attendance SET attendance_status=%s WHERE record_id=%s",
                               (attendance_status, record['record_id']))
            else:
                cursor.execute("""
                    INSERT INTO attendance (student_id, student_name, attendance_status, date_, department_name, subject_name)
                    VALUES (%s, %s, %s, %s, %s, %s)
                """, (student_id, student_name, attendance_status, date_, department_name, subject_name))

        db.commit()
        st.success(f"Attendance for {selected_date} saved successfully!")


def main(name):
    st.title(f"Welcome {name}")
    st.title("Students Attendance")
    selection = st.sidebar.radio("Edit Mode", options=['Attendance Mark', 'Send Mail'])
    if selection == 'Attendance Mark':
        mark_attendance()
    elif selection == 'Send Mail':
        send_email()


if __name__ == '__main__':
    main(login_page.get_name())
