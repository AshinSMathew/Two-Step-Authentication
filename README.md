# Two-Step Authentication System with CAPTCHA

This project is a Flask-based web application implementing a **Two-Step Authentication System** with CAPTCHA protection. Users can register, log in, verify their login using an OTP sent via email, and access a secure dashboard.

---

## Features

- User Registration and Login
- CAPTCHA Protection to prevent bots
- Two-Step Authentication using OTP (One-Time Password)
- MySQL database integration for storing user credentials
- Email notifications for OTP verification
- Responsive and user-friendly interface

---

## Prerequisites

1. Python 3.8 or higher installed
2. MySQL server set up and running
3. Necessary environment variables configured in a `.env` file (explained below)

---

## Installation

### Clone the Repository

```bash
git clone https://github.com/your-username/your-repo-name.git
cd your-repo-name
```

### Install Dependencies
Install the required Python packages using the *requirements.txt* file:
```bash
pip install -r requirements.txt
```
---

## Set Up the Database
1. Create a MySQL database (e.g., two_step_auth).
2. Run the following query to create the necessary table:
```bash
CREATE TABLE USER_DETAILS (
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL
);
```
3. Update your .env file with your MySQL credentials and email configurations.

---
## Configure .env File
Create a .env file in the project directory with the following content:
```bash
EMAIL=your-email@gmail.com
APP_PASSWORD=your-email-app-password
DB_HOST=localhost
DB_USER=your-database-username
DB_PASSWORD=your-database-password
DB_NAME=two_step_auth
```

---
## Run the Application
Start the Flask development server:
```bash
python app.py
```
Access the application at http://127.0.0.1:5000

---
## Screenshots
*Login page*
![login](https://github.com/user-attachments/assets/5c4a6f06-89b3-48d0-9f58-4aa59df50358)

*Signup Page*
![Signup](https://github.com/user-attachments/assets/38a48c55-736b-4a18-a49c-d2ca834cb4bc)

*Verification Page*
![verify](https://github.com/user-attachments/assets/55be0b27-ce2c-4798-8b1a-6b9345fb7dad)

---

## Technologies Used
- Backend: Flask, Python
- Database: MySQL
- Frontend: HTML, CSS (rendered through Flask templates)
- Email Service: SMTP (Gmail)
- CAPTCHA: captcha library for dynamic image generation
