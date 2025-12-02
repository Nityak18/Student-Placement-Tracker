from flask import Flask, render_template, request, redirect, url_for, flash, session, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import os
import requests
import json

# ---------------- App Config ----------------
load_dotenv()
app = Flask(__name__)

# ---------------- Secret Key ----------------
app.secret_key = os.getenv('SECRET_KEY', 'fallback_secret_key')

# ---------------- Mailjet settings (used via REST API) ----------------
MJ_APIKEY_PUBLIC = os.getenv('MJ_APIKEY_PUBLIC')
MJ_APIKEY_PRIVATE = os.getenv('MJ_APIKEY_PRIVATE')
MAIL_DEFAULT_SENDER = os.getenv('MAIL_DEFAULT_SENDER', MJ_APIKEY_PUBLIC)

# Debug print (optional)

print("DEBUG MAILJET KEY:", os.environ.get("MJ_API_KEY"))
print("DEBUG MAILJET SECRET:", os.environ.get("MJ_API_SECRET"))
print("DEBUG SENDER:", os.environ.get("MAIL_DEFAULT_SENDER"))

# ---------------- Database Config ----------------
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(BASE_DIR, 'database.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ---------------- Upload Config ----------------
app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'resumes')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
ALLOWED_EXT = {'pdf'}


# ---------------- Database Models ----------------
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    student = db.relationship('Student', backref='user', uselist=False)


class Student(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    roll_no = db.Column(db.String(50), nullable=False)
    department = db.Column(db.String(100), nullable=False)
    skills = db.Column(db.String(200))
    resume_path = db.Column(db.String(200))
    applications = db.relationship('Application', backref='student')


class Admin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=False)


class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    role = db.Column(db.String(100), nullable=False)
    salary = db.Column(db.String(50))
    eligibility = db.Column(db.String(200))
    location = db.Column(db.String(100))
    applications = db.relationship('Application', backref='job')


class Application(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('student.id'), nullable=False)
    job_id = db.Column(db.Integer, db.ForeignKey('job.id'), nullable=False)
    status = db.Column(db.String(50), default="Applied")


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)


# ---------------- Helpers ----------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXT


def send_status_email(student_email: str, student_name: str, job_title: str, company_name: str, status: str):
    """
    Send email using Mailjet's v3.1 send API via requests.
    Returns (True, message) on success, (False, error) on failure.
    """
    if not (MJ_APIKEY_PUBLIC and MJ_APIKEY_PRIVATE and MAIL_DEFAULT_SENDER):
        err = "Mailjet credentials or sender not configured."
        print(err)
        return False, err

    url = "https://api.mailjet.com/v3.1/send"

    # Compose a professional HTML email
    html_body = f"""
    <div style="font-family: Arial, sans-serif; line-height:1.5; color:#333;">
      <p>Dear {student_name},</p>

      <p>We are writing to inform you that the status of your application for the position of
      <strong>{job_title}</strong> at <strong>{company_name}</strong> has been updated to:</p>

      <p style="font-size:18px; font-weight:600; color:#0b6efd;">{status}</p>

      <p>Please log in to your placement dashboard to view additional details and next steps.</p>

      <hr>
      <p style="font-size:13px; color:#666;">
        This email was sent by the Placement Cell. If you believe you received this in error, please contact the placement cell administrator.
      </p>

      <p>Best regards,<br>Placement Cell Team</p>
    </div>
    """

    message_payload = {
        "Messages": [
            {
                "From": {
                    "Email": MAIL_DEFAULT_SENDER,
                    "Name": "Placement Cell"
                },
                "To": [
                    {
                        "Email": student_email,
                        "Name": student_name
                    }
                ],
                "Subject": f"Application Update — {job_title} at {company_name}",
                "TextPart": f"Your application status for {job_title} at {company_name} is now: {status}",
                "HTMLPart": html_body
            }
        ]
    }

    try:
        response = requests.post(url, auth=(MJ_APIKEY_PUBLIC, MJ_APIKEY_PRIVATE), json=message_payload, timeout=10)
        # Mailjet returns 200 for success; you may also check response.ok
        if response.status_code == 200:
            return True, "Email sent successfully"
        else:
            # return the response body for debugging
            err_text = f"Mailjet error ({response.status_code}): {response.text}"
            print(err_text)
            return False, err_text
    except Exception as e:
        err = f"Exception while calling Mailjet: {str(e)}"
        print(err)
        return False, err


# ---------------- Routes ----------------
@app.route('/')
def home():
    return render_template('index.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        message = request.form.get('message', '').strip()

        if not (name and email and message):
            flash("All fields are required!", "danger")
            return redirect(url_for('contact'))

        contact_msg = ContactMessage(name=name, email=email, message=message)
        db.session.add(contact_msg)
        db.session.commit()

        flash("Your message has been sent successfully!", "success")
        return redirect(url_for('contact'))

    return render_template('contact.html')


@app.route('/terms')
def terms():
    return render_template('terms.html')


# ---------------- Student Routes ----------------
@app.route('/student_register', methods=['GET', 'POST'])
def student_register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        raw_password = request.form.get('password', '')
        roll_no = request.form.get('roll_no', '').strip()
        department = request.form.get('department', '').strip()
        skills = request.form.get('skills', '').strip()

        if not (username and email and raw_password and roll_no and department):
            flash("Please fill required fields.", "danger")
            return redirect(url_for('student_register'))

        # check duplicate email or username
        if User.query.filter((User.email == email) | (User.username == username)).first():
            flash("Username or email already registered.", "danger")
            return redirect(url_for('student_register'))

        # handle resume
        filename = None
        if 'resume' in request.files and request.files['resume'].filename != '':
            resume = request.files['resume']
            if not allowed_file(resume.filename):
                flash("Only PDF resumes are allowed.", "danger")
                return redirect(url_for('student_register'))
            filename = secure_filename(resume.filename)
            filename = f"{username}_{filename}"
            resume.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        password = generate_password_hash(raw_password)
        new_user = User(username=username, email=email, password=password, role='student')
        db.session.add(new_user)
        db.session.commit()

        new_student = Student(user_id=new_user.id, roll_no=roll_no,
                              department=department, skills=skills,
                              resume_path=filename)
        db.session.add(new_student)
        db.session.commit()

        # auto-login
        session['user_id'] = new_user.id
        session['username'] = new_user.username
        session['role'] = 'student'
        flash("Registration successful! Welcome.", "success")
        return redirect(url_for('student_dashboard'))

    return render_template('student_registration.html')


@app.route('/student_dashboard')
def student_dashboard():
    if session.get('role') != 'student' or 'user_id' not in session:
        flash("Access denied! Students only.", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        flash("Student record not found. Please register or login.", "danger")
        return redirect(url_for('login'))

    jobs = Job.query.all()
    applications = Application.query.filter_by(student_id=student.id).all()

    return render_template('student_dashboard.html', student=student, jobs=jobs, applications=applications)


@app.route('/delete_account', methods=['POST'])
def delete_account():
    if 'user_id' not in session:
        flash("Please log in first.", "warning")
        return redirect(url_for('login'))

    user_id = session['user_id']
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        flash("Student record not found.", "danger")
        return redirect(url_for('home'))

    try:
        # delete applications
        Application.query.filter_by(student_id=student.id).delete()

        # delete resume file
        if student.resume_path:
            resume_file = os.path.join(app.config['UPLOAD_FOLDER'], student.resume_path)
            if os.path.exists(resume_file):
                os.remove(resume_file)

        # delete student and user
        db.session.delete(student)
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)

        db.session.commit()
        session.clear()
        flash("Your account and data have been permanently deleted.", "success")
    except Exception as e:
        db.session.rollback()
        print("Error deleting account:", repr(e))
        flash("An error occurred while deleting your account. Contact support.", "danger")

    return redirect(url_for('home'))


@app.route('/apply_job/<int:job_id>')
def apply_job(job_id):
    if session.get('role') != 'student' or 'user_id' not in session:
        flash("Access denied! Students only.", "danger")
        return redirect(url_for('login'))

    user_id = session['user_id']
    student = Student.query.filter_by(user_id=user_id).first()
    if not student:
        flash("Student profile not found.", "danger")
        return redirect(url_for('student_dashboard'))

    existing = Application.query.filter_by(student_id=student.id, job_id=job_id).first()
    if existing:
        flash("You already applied for this job!", "warning")
    else:
        new_app = Application(student_id=student.id, job_id=job_id)
        db.session.add(new_app)
        db.session.commit()
        flash("Application submitted successfully!", "success")

    return redirect(url_for('student_dashboard'))


# ---------------- Admin Routes ----------------
@app.route('/admin_register', methods=['GET', 'POST'])
def admin_register():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        raw_password = request.form.get('password', '')
        department = request.form.get('department', '').strip()

        if not (username and email and raw_password and department):
            flash("Please fill required fields.", "danger")
            return redirect(url_for('admin_register'))

        if Admin.query.filter_by(email=email).first():
            flash("Email already registered!", "danger")
            return redirect(url_for('admin_register'))

        admin = Admin(username=username, email=email,
                      password=generate_password_hash(raw_password),
                      department=department)
        db.session.add(admin)
        db.session.commit()

        # auto-login admin
        session['user_id'] = admin.id
        session['username'] = admin.username
        session['role'] = 'admin'
        flash("Placement cell registered and logged in!", "success")
        return redirect(url_for('admin_dashboard'))

    return render_template('admin_registration.html')


@app.route('/admin_dashboard')
def admin_dashboard():
    if session.get('role') != 'admin' or 'user_id' not in session:
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('login'))

    return render_template('admin_dashboard.html')


@app.route('/post_job', methods=['GET', 'POST'])
def post_job():
    if session.get('role') != 'admin' or 'user_id' not in session:
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        company_name = request.form.get('company_name', '').strip()
        role_name = request.form.get('role', '').strip()
        salary = request.form.get('salary', '').strip()
        eligibility = request.form.get('eligibility', '').strip()
        location = request.form.get('location', '').strip()

        if not (company_name and role_name):
            flash("Company name and role are required.", "danger")
            return redirect(url_for('post_job'))

        new_job = Job(company_name=company_name, role=role_name, salary=salary,
                      eligibility=eligibility, location=location)
        db.session.add(new_job)
        db.session.commit()
        flash("Job posted successfully!", "success")
        return redirect(url_for('post_job'))

    jobs = Job.query.all()
    return render_template('post_job.html', jobs=jobs)


@app.route('/view_students')
def view_students():
    if session.get('role') != 'admin' or 'user_id' not in session:
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('login'))

    students = Student.query.all()
    return render_template('view_students.html', students=students)


@app.route('/track_applications', methods=['GET', 'POST'])
def track_applications():
    if session.get('role') != 'admin' or 'user_id' not in session:
        flash("Access denied! Admins only.", "danger")
        return redirect(url_for('login'))

    if request.method == 'POST':
        app_id = request.form.get('application_id')
        new_status = request.form.get('status')

        if app_id and new_status:
            application = Application.query.get(app_id)
            if application:
                application.status = new_status
                db.session.commit()

                # send email
                try:
                    student = application.student
                    student_user = student.user
                    job = application.job

                    success, msg = send_status_email(
                        student_email=student_user.email,
                        student_name=student_user.username,
                        job_title=job.role,
                        company_name=job.company_name,
                        status=new_status
                    )

                    if success:
                        flash(f"Application status updated to '{new_status}' and email sent to student!", "success")
                    else:
                        flash(f"Status updated to '{new_status}' but email notification failed: {msg}", "warning")
                except Exception as e:
                    print("Error during email send:", repr(e))
                    flash("Status updated but email notification failed.", "warning")
            else:
                flash("Application not found!", "danger")
        else:
            flash("Please provide application ID and status!", "danger")

        return redirect(url_for('track_applications'))

    applications = Application.query.all()
    return render_template('track_applications.html', applications=applications)


@app.route('/view_resume/<filename>')
def view_resume(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


# ---------------- Login / Logout ----------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        role = request.form.get('role', '').strip()

        if role == 'student':
            user = User.query.filter_by(email=email, role='student').first()
            if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                session['username'] = user.username
                session['role'] = 'student'
                flash('Login successful!', 'success')
                return redirect(url_for('student_dashboard'))
            else:
                flash('Invalid student credentials', 'danger')

        elif role == 'admin':
            admin = Admin.query.filter_by(email=email).first()
            if admin and check_password_hash(admin.password, password):
                session['user_id'] = admin.id
                session['username'] = admin.username
                session['role'] = 'admin'
                flash('Login successful!', 'success')
                return redirect(url_for('admin_dashboard'))
            else:
                flash('Invalid placement cell credentials', 'danger')

        else:
            flash('Please select a role to login.', 'danger')

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.clear()
    flash("Logged out successfully!", "info")
    return redirect(url_for('home'))


# ---------------- Run App ----------------
if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)