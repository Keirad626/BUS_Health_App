from app import db
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    role = db.Column(db.String(50), nullable=False)
    password = db.Column(db.String(200), nullable=False)
    appointments = db.relationship("Appointment", foreign_keys="Appointment.patient_id", backref="patient", lazy=True)
    created_appointments = db.relationship("Appointment", foreign_keys="Appointment.created_by", backref="creator", lazy=True)

    def __repr__(self):
        return f"<User {self.email}>"
    
class Appointment(db.Model):
    id = db.Column(db.Integer, primary_key = True)

    patient_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    created_by = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    appointment_date = db.Column(db.DateTime, nullable=False)
    status = db.Column(db.String(50), default="scheduled")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<Appointment {self.title}>"
    
class Prescription(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    patient_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    doctor_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    medicine_name = db.Column(db.String(200), nullable=False)
    dosage = db.Column(db.String(100), nullable=False)
    instructions = db.Column(db.Text)

    repeat_allowed = db.Column(db.Boolean, default=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    patient = db.relationship(
        "User",
        foreign_keys=[patient_id],
        backref=db.backref("prescriptions", lazy=True)
    )

    doctor = db.relationship(
        "User",
        foreign_keys=[doctor_id]
    )

    def __repr__(self):
        return f"<Prescription {self.medicine_name}>"

class PrescriptionRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    prescription_id = db.Column(
        db.Integer, db.ForeignKey("prescription.id"), nullable=False
    )

    request_by = db.Column(
        db.Integer, db.ForeignKey("user.id"), nullable=False   
    )

    status = db.Column(db.String(50), default="pending")

    createed_at = db.Column(db.DateTime, default=datetime.utcnow)

    prescription = db.relationship("Prescription", backref="requests")
    requestee = db.relationship("User")


    def __repr__(self):
        return f"<PresciptionRequest {self.id}"
    
class MedicationLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    prescription_id = db.Column(db.Integer, db.ForeignKey("prescription.id"))
    taken_by = db.Column(db.Integer, db.ForeignKey("user.id"))
    taken_at = db.Column(db.DateTime, default=datetime.utcnow)

    