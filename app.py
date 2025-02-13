from flask import Flask, render_template, request, redirect, url_for, session, flash, send_file
from dotenv import load_dotenv
from captcha.image import ImageCaptcha
import smtplib
import os
import mysql.connector
from mysql.connector import Error
import random
import string
import io
import hashlib
from functools import wraps

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

# Environment variables
email = os.getenv('EMAIL')
app_password = os.getenv('APP_PASSWORD')
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')

# Database connection handling
def get_db_connection():
    try:
        connection = mysql.connector.connect(
            host=db_host,
            user=db_user,
            password=db_password,
            database=db_name
        )
        return connection
    except Error as err:
        print(f"Error: {err}")
        return None

# Login required decorator
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'email' not in session or not session.get('verified', False):
            flash('Please log in to access this page.', 'error')
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

def set_index():
    connection = get_db_connection()
    if not connection:
        return 1001
    
    cursor = connection.cursor()
    query = "SELECT MAX(ID) FROM USER_DETAILS"
    cursor.execute(query)
    max_id = cursor.fetchone()[0]
    cursor.close()
    connection.close()
    
    return (max_id or 1000) + 1

def hash_text(plain_text):
    return hashlib.sha256(plain_text.encode()).hexdigest()

def generate_captcha_image(captcha_text):
    image_captcha = ImageCaptcha(width=200, height=70)
    data = image_captcha.generate(captcha_text)
    return io.BytesIO(data.read())

def send_otp_email(receiver_email, otp):
    try:
        subject = "Account Login Verification"
        msg = f"Your verification code is {otp}"
        text = f"Subject: {subject}\n\n{msg}"
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email, app_password)
        server.sendmail(email, receiver_email, text)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

@app.route("/captcha")
def captcha():
    captcha_text = session.get("captcha_value", "")
    image = generate_captcha_image(captcha_text)
    return send_file(image, mimetype="image/png")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        user_email = request.form["email"]
        user_password = request.form["password"]
        
        connection = get_db_connection()
        if not connection:
            flash("Service temporarily unavailable. Please try again later.", "error")
            return render_template("signup.html")
        
        cursor = connection.cursor()
        
        # Check if email already exists
        query = "SELECT * FROM USER_DETAILS WHERE email=%s"
        cursor.execute(query, (user_email,))
        result = cursor.fetchall()
        
        if result:
            cursor.close()
            connection.close()
            flash("Email is already registered!", "error")
            return render_template("signup.html")
        
        try:
            count = set_index()
            hashed_password = hash_text(user_password)
            query = "INSERT INTO USER_DETAILS (ID, EMAIL, Password) VALUES (%s, %s, %s)"
            cursor.execute(query, (count, user_email, hashed_password))
            connection.commit()
            flash("Account created successfully! Please login.", "success")
            return redirect(url_for("login"))
        except Error as err:
            flash("An error occurred during registration. Please try again.", "error")
            return render_template("signup.html")
        finally:
            cursor.close()
            connection.close()
            
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_email = request.form["email"]
        user_password = request.form["password"]
        captcha = request.form["captcha"]
        
        # Validate captcha
        if captcha.strip().lower() != session.get("captcha_value", "").lower():
            flash("Invalid CAPTCHA!", "error")
            session["captcha_value"] = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
            return render_template("login.html")
        
        connection = get_db_connection()
        if not connection:
            flash("Service temporarily unavailable. Please try again later.", "error")
            return render_template("login.html")
        
        cursor = connection.cursor()
        hashed_password = hash_text(user_password)
        
        try:
            query = "SELECT * FROM USER_DETAILS WHERE email=%s AND password=%s"
            cursor.execute(query, (user_email, hashed_password))
            result = cursor.fetchall()
            
            if not result:
                flash("Incorrect email or password!", "error")
                session["captcha_value"] = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
                return render_template("login.html")
            
            # Generate and send OTP
            otp = random.randint(1001, 9999)
            session["otp"] = otp
            session["email"] = user_email
            session["verified"] = False
            
            if not send_otp_email(user_email, otp):
                flash("Error sending OTP. Please try again.", "error")
                return render_template("login.html")
                
            return redirect(url_for("verify"))
            
        except Error as err:
            flash("An error occurred. Please try again.", "error")
            return render_template("login.html")
        finally:
            cursor.close()
            connection.close()
    
    # GET request
    session["captcha_value"] = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
    return render_template("login.html")

@app.route("/verify", methods=["GET", "POST"])
def verify():
    if 'email' not in session:
        flash("Please log in first.", "error")
        return redirect(url_for("login"))
    
    if request.method == "POST":
        try:
            user_otp = int(request.form["otp"])
            if user_otp == session.get("otp"):
                session["verified"] = True
                return redirect(url_for("dashboard"))
            else:
                flash("Invalid OTP!", "error")
                return render_template("verify.html")
        except ValueError:
            flash("Invalid OTP format!", "error")
            return render_template("verify.html")
    
    # GET request
    otp = random.randint(1001, 9999)
    session["otp"] = otp
    
    if not send_otp_email(session["email"], otp):
        flash("Error sending OTP. Please try again.", "error")
        return redirect(url_for("login"))
    
    return render_template("verify.html")

@app.route("/dashboard")
@login_required
def dashboard():
    return render_template("dashboard.html")

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out successfully.", "success")
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=True)