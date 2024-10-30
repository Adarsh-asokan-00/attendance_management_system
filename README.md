# Attendance Management System

## Overview
The Attendance Management System is a web application designed to streamline the management of student, teacher, and admin records within a MySQL database. It allows for bulk data uploads, dynamic updates, and provides a user-friendly interface for managing user records. The application is built using Python, Streamlit, and integrates with MySQL for data storage.

## Technologies Used
- **Frontend**: Streamlit (for creating the web interface)
- **Backend**: Python (handling business logic and database interaction)
- **Database**: MySQL (storing student and attendance data)
- **Libraries**:
  - Pandas (data manipulation)
  - AgGrid (for interactive grid editing)
  - MySQL Connector (database connection)
  - Streamlit (for web application)

## Installation

### Clone the Repository
```bash
git clone https://github.com/yourusername/attendance-management-system.git
cd attendance-management-system
```

## Database Setup

### Create the Database
Connect to your MySQL server and run the following SQL queries to create the required tables:

```sql
CREATE TABLE student (
    student_id INT PRIMARY KEY AUTO_INCREMENT,
    full_name VARCHAR(100),
    email_id VARCHAR(100),
    department_name VARCHAR(100)
);

CREATE TABLE attendance (
    record_id INT PRIMARY KEY AUTO_INCREMENT,
    student_id INT,
    student_name VARCHAR(100),
    attendance_status ENUM('present', 'absent', 'late'),
    date_ DATE,
    department_name VARCHAR(100),
    subject_name VARCHAR(100),
    FOREIGN KEY (student_id) REFERENCES student(student_id)
);

CREATE TABLE admin (
    admin_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100) NOT NULL,
    email_id VARCHAR(100) NOT NULL,
    password_hash TEXT NOT NULL
);

CREATE TABLE users (
    user_id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(100),
    email_id VARCHAR(100),
    password_hash VARCHAR(255),
    role ENUM('student', 'teacher', 'admin')
);
```
## Running the Application

### Run the Admin Page
Launch the Streamlit application for the admin page by executing:

```bash
streamlit run admin_page.py
```
### Upload CSV Data
In the admin interface, upload CSV files containing data for students, teachers, or admins. Ensure the data is formatted correctly according to the created tables. After selecting the appropriate database table, click on the "Upload Database" button to import the data into the MySQL database.

### Update User Table
Once the data is uploaded, click on the "Update User Table" button to create secure passwords for users based on their email IDs and names.

### User Login

#### Run the Login Page
Launch the login page using the following command:

```bash
streamlit run login_page.py
```
### Authentication
Users can log in based on their roles (student, teacher, admin) using their email and the passwords updated in the user table.

### Flow of Application
1. **Login**: Teacher logs in using a secure username and password.
2. **Select Class**: Teacher selects the subject and date to mark attendance.
3. **Mark Attendance**: Teachers use an editable grid to mark attendance (present, absent, or late).
4. **Save Attendance**: Data is saved to the MySQL database.
5. **Send Emails**: Automated emails are sent to students with low attendance.

### Login Page Features
- **User Authentication**: Secure login for students, teachers, and admins using email and password.
- **Session Management**: Retains user data during the session for personalized experiences.
- **Dynamic Navigation**: Redirects users to views based on their roles.
- **Error Handling**: Provides user-friendly messages for invalid login attempts.

### Teacher Features
- **Grid Configuration**: Configures AgGrid options for efficient attendance management.
- **Attendance Marking**: Enables teachers to mark or update attendance records for students using an interactive grid.
- **Real-time Updates**: Automatically updates attendance records in real-time.
- **Email Notifications**: Sends email notifications to students who are not eligible for exams, along with a customizable option to send emails to selected students.

### Student Features
- **Fetching Student Data**: Retrieves attendance details based on student name and department.
- **Attendance Records Retrieval**: Displays attendance records in a user-friendly format.
- **Pie Chart Visualization**: Generates and customizes pie charts for attendance breakdown.

### Admin Features
Admins can log in to change user data, manage records, and perform other administrative functions as previously outlined.

