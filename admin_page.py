import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode

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

def password_hash(user_id, name):
    return str(user_id) + "@" + name

def update_database_with_aggrid_data(df, database):
    connection = get_connection_to_mysql()
    if connection is None:
        return
    cursor = connection.cursor()
    try:
        for _, row in df.iterrows():
            if database == "student":
                cursor.execute("SELECT * FROM student WHERE email_id = %s", (row['email_id'],))
                if cursor.fetchone():
                    cursor.execute(
                        """UPDATE student SET full_name = %s, phone_number = %s, address = %s, department_name = %s, password_hash = %s 
                           WHERE email_id = %s""",
                        (row['full_name'], row['phone_number'], row['address'], row['department_name'], row['password_hash'], row['email_id'])
                    )
                else:
                    cursor.execute(
                        """INSERT INTO student (full_name, email_id, phone_number, address, department_name, password_hash) 
                           VALUES (%s, %s, %s, %s, %s, %s)""",
                        (row['full_name'], row['email_id'], row['phone_number'], row['address'], row['department_name'], row['password_hash'])
                    )
            elif database == "teacher":
                cursor.execute("SELECT * FROM teacher WHERE email_id = %s", (row['email_id'],))
                if cursor.fetchone():
                    cursor.execute(
                        """UPDATE teacher SET teacher_name = %s, subject_name = %s, department_name = %s, password_hash = %s 
                           WHERE email_id = %s""",
                        (row['teacher_name'], row['subject_name'], row['department_name'], row['password_hash'], row['email_id'])
                    )
                else:
                    cursor.execute(
                        """INSERT INTO teacher (teacher_name, email_id, subject_name, department_name, password_hash) 
                           VALUES (%s, %s, %s, %s, %s)""",
                        (row['teacher_name'], row['email_id'], row['subject_name'], row['department_name'], row['password_hash'])
                    )
            elif database == "admin":
                cursor.execute("SELECT * FROM admin WHERE email_id = %s", (row['email_id'],))
                if cursor.fetchone():
                    cursor.execute(
                        """UPDATE admin SET name = %s, password_hash = %s 
                           WHERE email_id = %s""",
                        (row['name'], row['password_hash'], row['email_id'])
                    )
                else:
                    cursor.execute(
                        """INSERT INTO admin (name, email_id, password_hash) 
                           VALUES (%s, %s, %s)""",
                        (row['name'], row['email_id'], row['password_hash'])
                    )
        connection.commit()
        st.success(f"{database.capitalize()} data successfully updated in the database.")
    except Error as e:
        st.error(f"Error updating {database} data in MySQL: {e}")
    finally:
        cursor.close()
        connection.close()

def update_users_table():
    db = get_connection_to_mysql()
    if db is None:
        return
    cursor = db.cursor()
    try:
        cursor.execute("SELECT student_id, full_name, email_id FROM student")
        for student in cursor.fetchall():
            cursor.execute(
                """INSERT INTO users (email_id, password_hash, name, role)
                   VALUES (%s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash), name = VALUES(name), role = 'student'""",
                (student[2], password_hash(student[0], student[1]), student[1], 'student')
            )
        cursor.execute("SELECT teacher_id, teacher_name, email_id FROM teacher")
        for teacher in cursor.fetchall():
            cursor.execute(
                """INSERT INTO users (email_id, password_hash, name, role)
                   VALUES (%s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash), name = VALUES(name), role = 'teacher'""",
                (teacher[2], password_hash(teacher[0], teacher[1]), teacher[1], 'teacher')
            )
        cursor.execute("SELECT admin_id, name, email_id FROM admin")
        for admin in cursor.fetchall():
            cursor.execute(
                """INSERT INTO users (email_id, password_hash, name, role)
                   VALUES (%s, %s, %s, %s)
                   ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash), name = VALUES(name), role = 'admin'""",
                (admin[2], password_hash(admin[0], admin[1]), admin[1], 'admin')
            )
        db.commit()
        st.success("Users table updated successfully.")
    except Error as e:
        st.error(f"Error updating users table: {e}")
    finally:
        cursor.close()
        db.close()

def main(name=None):
    st.title(f"Welcome {name}")
    st.title("Upload CSV to Manage Database Tables")
    uploaded_file = st.file_uploader("Upload CSV", type=["csv"])

    if st.button("Update Users Table"):
        update_users_table()

    if uploaded_file:
        try:
            df = pd.read_csv(uploaded_file)
            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_side_bar()
            gb.configure_default_column(editable=True, groupable=True)
            grid_response = AgGrid(
                df,
                gridOptions=gb.build(),
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                update_mode=GridUpdateMode.FILTERING_CHANGED,
                fit_columns_on_grid_load=True,
                enable_enterprise_modules=True
            )
            database_selection = st.selectbox("Select Database", ["student", "teacher", "admin"])
            if st.button("Update Database"):
                update_database_with_aggrid_data(grid_response['data'], database_selection)
        except Exception as e:
            st.error(f"Error reading the uploaded file: {e}")

if __name__ == "__main__":
    main("Admin")
  
