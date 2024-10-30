import mysql.connector
import streamlit as st
from mysql.connector import Error
import teacher_view
import student_view
import admin_page

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

def verify_login(email, password):
    try:
        with get_connection_to_mysql() as connection:
            with connection.cursor(dictionary=True) as cursor:
                cursor.execute("SELECT user_id, email_id, password_hash, name, role FROM users WHERE email_id=%s", (email,))
                user = cursor.fetchone()

        if user and user["password_hash"] == password:
            return user
        return None
    except Error as e:
        st.error(f"Database error: {e}")
        return None

def login_page():
    st.title("Welcome to School")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_id = None
        st.session_state.user_email = None
        st.session_state.user_role = None

    if st.session_state.logged_in:
        st.subheader(f"Welcome, {st.session_state.user_name}")
        st.write(f"Email: {st.session_state.user_email}")

        if st.button("Logout"):
            st.session_state.logged_in = False
            st.session_state.user_id = None
            st.session_state.user_email = None
            st.session_state.user_role = None
    else:
        st.subheader("Login")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user = verify_login(email, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.user_id = user["user_id"]
                st.session_state.user_name = user["name"]
                st.session_state.user_email = user["email_id"]
                st.session_state.user_role = user["role"]
                st.success(f"Welcome, {user['name']}")
            else:
                st.error("Invalid credentials")

def main():
    if "logged_in" in st.session_state and st.session_state.logged_in:
        if st.session_state.user_role == "student":
            student_view.main(st.session_state.user_name)
        elif st.session_state.user_role == "teacher":
            teacher_view.main(st.session_state.user_name)
        elif st.session_state.user_role == "admin":
            admin_page.main(st.session_state.user_name)
    else:
        login_page()

if __name__ == "__main__":
    main()
