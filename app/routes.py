from flask import render_template, redirect, url_for, session, flash, request
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

from app import app, db
from app.models import User, Appointment, Prescription, PrescriptionRequest, Note
from app.forms import RegistrationForm, AppointmentForm, PrescriptionForm, LoginForm


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

    user = User.query.get(session["user_id"])

    # If family, show the linked patient's appointments
    if user.role == "family":
        appointments = Appointment.query.filter_by(patient_id=user.linked_patient_id).all()
    else:
        appointments = Appointment.query.filter_by(patient_id=user.id).all()

    return render_template("appointments.html", appointments=appointments)



@app.route("/create_appointment", methods=["GET", "POST"])
def create_appointment():
    if "user_id" not in session:
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    form = AppointmentForm()

    if user.role in ["doctor", "carer"]:
        patients = User.query.filter_by(role="patient").all()
        form.patient_id.choices = [(p.id, p.full_name) for p in patients]
    else:
        form.patient_id.choices = []

    if request.method == "POST":
        title = request.form.get("title")
        appointment_date = request.form.get("appointment_date")
        status = request.form.get("status")

        if not title or not appointment_date or not status:
            flash("Please fill in all required fields.", "danger")
            return render_template("create_appointment.html", form=form, user=user)

        if user.role == "family":
            patient_id = user.linked_patient_id
        elif user.role == "patient":
            patient_id = user.id
        else:
            patient_id = int(request.form.get("patient_id"))

        new_appointment = Appointment(
            patient_id=patient_id,
            created_by=user.id,
            title=title,
            description=request.form.get("description"),
            appointment_date=form.appointment_date.data,
            status=status,
        )

        db.session.add(new_appointment)
        db.session.commit()
        flash("Appointment created.", "success")

        if user.role == "family":
            return redirect(url_for("family_dashboard"))
        elif user.role == "patient":
            return redirect(url_for("patient_dashboard"))
        elif user.role == "carer":
            return redirect(url_for("carer_dashboard"))
        else:
            return redirect(url_for("doctor_dashboard"))

    return render_template("create_appointment.html", form=form, user=user)


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


@app.route("/family_dashboard")
def family_dashboard():
    if "user_id" not in session or session["role"] != "family":
        return redirect(url_for("login"))

    user = User.query.get(session["user_id"])
    patient = User.query.get(user.linked_patient_id)

    appointments = Appointment.query.filter_by(patient_id=patient.id).all()
    prescriptions = Prescription.query.filter_by(patient_id=patient.id).all()
    notes = Note.query.filter_by(patient_id=patient.id).all()

    return render_template(
        "family_dashboard.html",
        patient=patient,
        appointments=appointments,
        prescriptions=prescriptions,
        notes=notes
    )


@app.route("/dashboard/doctor")
def doctor_dashboard():
    if "user_id" not in session or session["role"] != "doctor":
        flash("Access denied.", "danger")
        return redirect(url_for("login"))
    
    patients = User.query.filter_by(role="patient").all()
    appointments = Appointment.query.all()
    return render_template("doctor_dashboard.html", patients=patients, appointments=appointments)


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
    
    prescriptions = Prescription.query.filter_by(patient_id=session["user_id"]).all()
    return render_template("prescriptions.html", prescriptions=prescriptions)


@app.route("/prescriptions/request/<int:prescription_id>")
def request_repeat(prescription_id):
    if "user_id" not in session:
        return redirect(url_for("login"))

    request_obj = PrescriptionRequest(
        prescription_id=prescription_id, 
        requested_by=session["user_id"],
    )

    db.session.add(request_obj)
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
    request_obj = PrescriptionRequest.query.get_or_404(id)
    request_obj.status = "approved"
    db.session.commit()

    flash("Prescription request approved", "success")
    return redirect(url_for("prescription_requests"))


@app.route("/prescriptions/reject/<int:id>")
def reject_prescriptions(id):
    request_obj = PrescriptionRequest.query.get_or_404(id)
    request_obj.status = "rejected"
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
        patient_id=patient_id,
        author_id=session["user_id"],
        content=request.form["content"],
        note_type="doctor_note"
    )

    db.session.add(note)
    db.session.commit()

    return redirect(url_for("doctor_dashboard"))


@app.route("/patient/<int:patient_id>/family_request", methods=["POST"])
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
def patient_notes():
    if session.get("role") != "patient":
        return redirect(url_for("login"))
    
    notes = Note.query.filter_by(patient_id=session["user_id"]).order_by(Note.created_at.desc()).all()
    return render_template("patient_notes.html", notes=notes)


@app.route("/doctor/patient/<int:patient_id>/notes")
def view_patient_notes(patient_id):
    if session.get("role") != "doctor":
        return redirect(url_for("login"))
    
    patient = User.query.get_or_404(patient_id)
    notes = Note.query.filter_by(patient_id=patient_id).order_by(Note.created_at.desc()).all()

    return render_template("doctor_patient_notes.html", patient=patient, notes=notes)


@app.route("/doctor/patients")
def view_patients():
    if "user_id" not in session or session["role"] != "doctor":
        return redirect(url_for("login"))
    
    patients = User.query.filter_by(role="patient").all()
    return render_template("doctor_patients.html", patients=patients)


@app.route("/carer/patient/<int:patient_id>/notes")
def carer_view_patient_notes(patient_id):
    if session.get("role") != "carer":
        return redirect(url_for("login"))
    
    patient = User.query.get_or_404(patient_id)
    notes = Note.query.filter_by(patient_id=patient_id).order_by(Note.created_at.desc()).all()

    return render_template("carer_patient_notes.html", patient=patient, notes=notes)


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

    return redirect(url_for("carer_view_patient_notes", patient_id=patient_id))


@app.route("/carer/patients")
def carer_patients():
    if session.get("role") != "carer":
        return redirect(url_for("login"))
    
    patients = User.query.filter_by(role="patient").all()
    return render_template("carer_patients.html", patients=patients)
