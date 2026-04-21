from flask import render_template, redirect, url_for, session, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from app import app, db
from app.models import User, Appointment, Prescription, PrescriptionRequest, Note
from app.forms import RegistrationForm, LoginForm, AppointmentForm, PrescriptionForm


@app.route("/")
def index():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    role = session.get("role")
    role_redirects = {
        "doctor": "doctor_dashboard",
        "patient": "patient_dashboard",
        "carer": "carer_dashboard",
        "family": "family_dashboard"
    }
    return redirect(url_for(role_redirects.get(role, "login")))


@app.route("/register", methods=["GET", "POST"])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash("Email already registered", "warning")
            return redirect(url_for("register"))

        hashed_password = generate_password_hash(form.password.data)
        new_user = User(
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            email=form.email.data,
            role=form.role.data,
            password=hashed_password
        )
        db.session.add(new_user)
        db.session.commit()

        flash("Registration successful!", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and check_password_hash(user.password, form.password.data):
            session["user_id"] = user.id
            session["role"] = user.role

            flash("Login successful", "success")

            role_redirects = {
                "doctor": "doctor_dashboard",
                "patient": "patient_dashboard",
                "carer": "carer_dashboard",
                "family": "family_dashboard"
            }

            return redirect(url_for(role_redirects.get(user.role, "index")))

        else:
            flash("Invalid login details", "danger")

    return render_template("login.html", form=form)


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out", "info")
    return redirect(url_for("login"))


@app.route("/appointments")
def view_appointments():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    appointments = Appointment.query.filter_by(patient_id=session["user_id"]).all()
    return render_template("appointments.html", appointments=appointments)


@app.route("/appointments/create", methods=["GET", "POST"])
def create_appointment():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    form = AppointmentForm()

    if form.validate_on_submit():
        appointment = Appointment(
            patient_id=session["user_id"],
            created_by=session["user_id"],
            title=form.title.data,
            description=form.description.data,
            appointment_date=form.appointment_date.data
        )

        db.session.add(appointment)
        db.session.commit()

        flash("Appointment created successfully", "success")
        return redirect(url_for("view_appointments"))
    
    return render_template("create_appointment.html", form=form)


@app.route("/appointments/cancel/<int:id>")
def cancel_appointment(id):
    appointment = Appointment.query.get_or_404(id)
    appointment.status = "cancelled"
    db.session.commit()

    flash("Appointment cancelled", "info")
    return redirect(url_for("view_appointments"))


@app.route('/patient_dashboard')
def patient_dashboard():
    if "user_id" not in session or session["role"] != "patient":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    return render_template('patient_dashboard.html')


@app.route('/family_dashboard')
def family_dashboard():
    if "user_id" not in session or session["role"] != "family":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    return render_template('family_dashboard.html')


@app.route("/dashboard/doctor")
@app.route("/dashboard/doctor")
def doctor_dashboard():
    if "user_id" not in session or session["role"] != "doctor":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    
    patients = User.query.filter_by(role="patient").all()

    appointments = Appointment.query.filter_by(
        created_by=session["user_id"]
    ).all()

    return render_template(
        "doctor_dashboard.html",
        patients=patients,
        appointments=appointments
    )


@app.route('/carer_dashboard')
def carer_dashboard():
    if "user_id" not in session or session["role"] != "carer":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    return render_template('carer_dashboard.html')


@app.route("/create_prescription/<int:patient_id>", methods=["GET","POST"])
def create_prescription(patient_id):
    if "user_id" not in session or session["role"] != "doctor":
        flash("Access denied", "danger")
        return redirect(url_for("index"))

    form = PrescriptionForm()

    if form.validate_on_submit():
        prescription = Prescription(
            patient_id=patient_id,
            doctor_id=session["user_id"],
            medicine_name=form.medicine_name.data,
            dosage=form.dosage.data,
            instructions=form.instructions.data,
            repeat_allowed=form.repeat_allowed.data
        )

        db.session.add(prescription)
        db.session.commit()

        flash("Prescription created", "success")
        return redirect(url_for("prescriptions"))

    return render_template("create_prescription.html", form=form)


@app.route("/prescriptions")
def prescriptions():
    if "user_id" not in session:
        return redirect(url_for("login"))
    
    prescriptions = Prescription.query.filter_by(
        patient_id=session["user_id"]
    ).all()

    return render_template("prescriptions.html", prescriptions=prescriptions)


@app.route("/prescriptions/request/<int:prescription_id>")
def request_repeat(prescription_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    request = PrescriptionRequest(
        prescription_id=prescription_id, 
        requested_by=session["user_id"],
    )

    db.session.add(request)
    db.session.commit()

    flash("Repeat prescription requested")
    return redirect(url_for("prescriptions"))


@app.route("/prescription_requests")
def prescription_requests():
    if "user_id" not in session or session["role"] != "doctor":
        flash("Access Denied", "danger")
        return redirect(url_for("index"))
    
    requests = PrescriptionRequest.query.all()

    return render_template("prescription_requests.html", requests=requests)


@app.route("/prescriptions/approve/<int:id>")
def approve_prescription(id):
    request = PrescriptionRequest.query.get_or_404(id)
    request.status = "approved"

    db.session.commit()

    flash("Prescription request approved", "success")
    return redirect(url_for("prescription_requests"))


@app.route("/prescriptions/reject/<int:id>")
def reject_prescriptions(id):
    request = PrescriptionRequest.query.get_or_404(id)
    request.status = "rejected"

    db.session.commit()

    flash("Prescription request rejected", "info")
    return redirect(url_for("prescription_requests"))


@app.route("/patients")
def patients():
    if "user_id" not in session or session["role"] != "doctor":
        flash("Access Denied", "danger")
        return redirect(url_for("index"))
    
    patients = User.query.filter_by(role="patient").all()

    return render_template("patients.html", patients=patients)

@app.route("/patient/<int:patient_id>/notes/add", methods=["POST"])
def add_doctor_note(patient_id):
    if session.get("role") != "doctor":
        return redirect(url_for("login"))
    
    note = Note(
        patient_id = patient_id,
        author_id = session["user_id"],
        content = request.form["content"],
        note_type = "doctor_note"
    )

    db.session.add(note)
    db.session.commit()

    return redirect(url_for("doctor_dashboard"))

@app.route("/patient/<int:patient_id>/care-note", methods=["POST"])
def add_caregiver_note(patient_id):
    if session.get("role") != "carer":
        return redirect(url_for("login"))
    
    note = Note(
        patient_id=patient_id,
        author_id=session["user_id"],
        content=request.form["content"],
        note_type="caregiver_note"
    )

    db.session.add(note)
    db.session.commit()

    return redirect(url_for ("caregiver_dashboard"))

@app.route("/patient/<int:patient_id>/family-request", methods=["POST"])
def add_family_request(patient_id):
    if session.get("role") != "family":
        return redirect(url_for("login"))

    note = Note(
        patient_id=patient_id,
        author_id=session["user_id"],
        content=request.form["content"],
        note_type="family_request"
    )

    db.session.add(note)
    db.session.commit()

    return redirect(url_for("family_dashboard"))

@app.route("/patient/notes")
@app.route("/patient/notes")
def patient_notes():
    if session.get("role") != "patient":
        return redirect(url_for("login"))
    
    notes = Note.query.filter_by(
        patient_id=session["user_id"]
    ).order_by(Note.created_at.desc()).all()
    
    return render_template("patient/notes.html", notes=notes)


@app.route("/doctor/prescribe/<int:patient_id>", methods=["GET", "POST"])
def prescribe(patient_id):
    if session.get("role") != "doctor":
        return redirect(url_for("login"))
    
    patient = User.query.get_or_404(patient_id)

    if request.method == "POST":
        prescription = Prescription(
            patient_id=patient_id,
            doctor_id=session["user_id"],
            medicine_name=request.form["medicine_name"],
            dosage=request.form["dosage"],
            instructions=request.form["instructions"],
            repeat_allowed="repeat_allowed" in request.form
        )
        
        db.session.add(prescription)
        db.session.commit()

        flash("Prescription created successfully", "success")
        return redirect(url_for("doctor_dashboard"))

    return render_template("doctor/prescribe.html", patient=patient)


@app.route("/doctor/patient/<int:patient_id>/notes")
def view_patient_notes(patient_id):
    if session.get("role") != "doctor":
        return redirect(url_for("login"))
    
    patient = User.query.get_or_404(patient_id)

    notes = Note.query.filter_by(
        patient_id=patient_id
    ).order_by(Note.created_at.desc()).all()

    return render_template(
        "doctor/patient_notes.html",
        patient=patient,
        notes=notes
    )

@app.route("/doctor/patients")
def view_patients():
    if "user_id" not in session or session["role"] != "doctor":
        return redirect(url_for("login"))
    
    patients = User.query.filter_by(role="patient").all()
    return render_template("doctor_patients.html", patients=patients)