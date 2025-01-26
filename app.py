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


load_dotenv()


app = Flask(__name__)
app.secret_key = os.urandom(24)

email = os.getenv('EMAIL')
app_password = os.getenv('APP_PASSWORD')
db_host = os.getenv('DB_HOST')
db_user = os.getenv('DB_USER')
db_password = os.getenv('DB_PASSWORD')
db_name = os.getenv('DB_NAME')


try:
    connection = mysql.connector.connect(
        host=db_host,
        user=db_user,
        password=db_password,
        database=db_name
    )
    cursor = connection.cursor()
except Error as err:
    print(f"Error: {err}")
    exit()

def generate_captcha_image(captcha_text):
    image_captcha = ImageCaptcha(width=200, height=70)
    data = image_captcha.generate(captcha_text)
    return io.BytesIO(data.read())

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
        
        query = "SELECT * FROM USER_DETAILS WHERE email=%s"
        cursor.execute(query, (user_email,))
        result = cursor.fetchall()
        
        if result:
            flash("Email is already registered!", "error")
            return redirect(url_for("signup"))
        else:
            query = "INSERT INTO USER_DETAILS (email, password) VALUES (%s, %s)"
            cursor.execute(query, (user_email, user_password))
            connection.commit()
            flash("Account created successfully! Please login.", "success")
            return redirect(url_for("login"))
    return render_template("signup.html")

@app.route("/login", methods=["GET", "POST"])
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user_email = request.form["email"]
        user_password = request.form["password"]
        captcha = request.form["captcha"]
        if captcha.strip().lower() != session.get("captcha_value", "").lower():
            flash("Invalid CAPTCHA!", "error")
            return redirect(url_for("login"))
        query = "SELECT * FROM USER_DETAILS WHERE email=%s AND password=%s"
        cursor.execute(query, (user_email, user_password))
        result = cursor.fetchall()
        
        if not result:
            flash("Incorrect email or password!", "error")
            return redirect(url_for("login"))
        else:
            session["email"] = user_email
            return redirect(url_for("verify"))
    else:
        session["captcha_value"] = ''.join(random.choices(string.ascii_letters + string.digits, k=6))
        return render_template("login.html")

@app.route("/verify", methods=["GET", "POST"])
def verify():
    if request.method == "POST":
        user_otp = int(request.form["otp"])
        if user_otp == session.get("otp"):
            flash("Login Successful!", "success")
            return redirect(url_for("dashboard"))
        else:
            flash("Invalid OTP!", "error")
            return redirect(url_for("verify"))
    else:
        otp = random.randint(1001, 9999)
        session["otp"] = otp
        
        receiver_email = session["email"]
        subject = "Account Login Verification"
        msg = f"Your verification code is {otp}"
        text = f"Subject: {subject}\n\n{msg}"
        
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(email, app_password)
        server.sendmail(email, receiver_email, text)
        server.quit()
        
        return render_template("verify.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)
