import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import Error
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode


def get_connection_to_mysql():
    try:
        return mysql.connector.connect(
            host="",
            user="",
            password="",
            database=""
        )
    except Error as e:
        st.error(f"Error connecting to database: {e}")
        return None


def password_hash(user_id, name):
    return f"{user_id}@{name}"


def update_database_with_aggrid_data(df, database):
    connection = get_connection_to_mysql()
    if connection is None:
        return

    cursor = connection.cursor()

    try:
        for index, row in df.iterrows():
            if database == "student":
                cursor.execute("SELECT * FROM student WHERE email_id = %s", (row.get('email_id'),))
                result = cursor.fetchone()

                if result:
                    cursor.execute("""
                        UPDATE student 
                        SET full_name = %s, phone_number = %s, address = %s, department_name = %s, password_hash = %s 
                        WHERE email_id = %s
                    """, (row.get('full_name'), row.get('phone_number'), row.get('address'), row.get('department_name'), row.get('password_hash'), row.get('email_id')))
                else:
                    cursor.execute("""
                        INSERT INTO student (full_name, email_id, phone_number, address, department_name, password_hash) 
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (row.get('full_name'), row.get('email_id'), row.get('phone_number'), row.get('address'), row.get('department_name'), row.get('password_hash')))

            elif database == "teacher":
                cursor.execute("SELECT * FROM teacher WHERE email_id = %s", (row.get('email_id'),))
                result = cursor.fetchone()

                if result:
                    cursor.execute("""
                        UPDATE teacher 
                        SET teacher_name = %s, subject_name = %s, department_name = %s, password_hash = %s 
                        WHERE email_id = %s
                    """, (row.get('teacher_name'), row.get('subject_name'), row.get('department_name'), row.get('password_hash'), row.get('email_id')))
                else:
                    cursor.execute("""
                        INSERT INTO teacher (teacher_name, email_id, subject_name, department_name, password_hash) 
                        VALUES (%s, %s, %s, %s, %s)
                    """, (row.get('teacher_name'), row.get('email_id'), row.get('subject_name'), row.get('department_name'), row.get('password_hash')))

            elif database == "admin":
                cursor.execute("SELECT * FROM admin WHERE email_id = %s", (row.get('email_id'),))
                result = cursor.fetchone()

                if result:
                    cursor.execute("""
                        UPDATE admin 
                        SET name = %s, password_hash = %s 
                        WHERE email_id = %s
                    """, (row.get('name'), row.get('password_hash'), row.get('email_id')))
                else:
                    cursor.execute("""
                        INSERT INTO admin (name, email_id, password_hash) 
                        VALUES (%s, %s, %s)
                    """, (row.get('name'), row.get('email_id'), row.get('password_hash')))

        connection.commit()
        st.success(f"{database.capitalize()} data successfully updated in the database.")

    except Error as e:
        st.error(f"Error updating {database} data in MySQL: {e}")

    finally:
        cursor.close()
        connection.close()


def update_users_table():
    try:
        db = get_connection_to_mysql()
        if db is None:
            return

        cursor = db.cursor()

        for student in cursor.execute("SELECT student_id, full_name, email_id FROM student"):
            student_id, name, email = student
            new_hash = password_hash(student_id, name)

            cursor.execute("""
                INSERT INTO users (email_id, password_hash, name, role)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash), name = VALUES(name), role = 'student'
            """, (email, new_hash, name, 'student'))

        for teacher in cursor.execute("SELECT teacher_id, teacher_name, email_id FROM teacher"):
            teacher_id, name, email = teacher
            new_hash = password_hash(teacher_id, name)

            cursor.execute("""
                INSERT INTO users (email_id, password_hash, name, role)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash), name = VALUES(name), role = 'teacher'
            """, (email, new_hash, name, 'teacher'))

        for admin in cursor.execute("SELECT admin_id, name, email_id FROM admin"):
            admin_id, name, email = admin
            new_hash = password_hash(admin_id, name)

            cursor.execute("""
                INSERT INTO users (email_id, password_hash, name, role)
                VALUES (%s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE password_hash = VALUES(password_hash), name = VALUES(name), role = 'admin'
            """, (email, new_hash, name, 'admin'))

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

    if uploaded_file is not None:
        try:
            df = pd.read_csv(uploaded_file)

            gb = GridOptionsBuilder.from_dataframe(df)
            gb.configure_pagination(paginationAutoPageSize=True)
            gb.configure_side_bar()
            gb.configure_default_column(editable=True, groupable=True)

            grid_options = gb.build()

            grid_response = AgGrid(
                df,
                gridOptions=grid_options,
                data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
                update_mode=GridUpdateMode.VALUE_CHANGED,
                fit_columns_on_grid_load=True,
                enable_enterprise_modules=True
            )

            updated_df = grid_response['data']
            database_selection = st.selectbox("Select Database", ["student", "teacher", "admin"])

            if st.button("Update Database"):
                update_database_with_aggrid_data(updated_df, database_selection)

        except Exception as e:
            st.error(f"Error reading the uploaded file: {e}")


if __name__ == "__main__":
    main("Admin")
