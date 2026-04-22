from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SelectField, SubmitField, TextAreaField, DateTimeLocalField, DateField, BooleanField
from wtforms.validators import DataRequired, Email, Length, EqualTo


class RegistrationForm(FlaskForm):
    first_name = StringField("First Name", validators=[DataRequired()])
    last_name = StringField("Last Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired(), Email()])

    role = SelectField(
        "Register As",
        choices=[
            ("carer", "Carer"),
            ("family", "Family Member"),
            ("patient", "Patient"),
            ("doctor", "Doctor"),
        ],
        validators=[DataRequired()],
    )

    password = PasswordField(
        "Password",
        validators=[DataRequired(), Length(min=8)],
    )

    confirm_password = PasswordField(
        "Confirm Password",
        validators=[DataRequired(), EqualTo("password")],
    )

    submit = SubmitField("Register")

class LoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired(), Email()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")

class AppointmentForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])

    appointment_date = DateTimeLocalField(
        "Appointment Date",
        format="%Y-%m-%dT%H:%M",
        validators=[DataRequired()]
    )

    status = SelectField(
        "Status",
        choices=[
            ("scheduled", "Scheduled"),
            ("completed", "Completed"),
            ("cancelled", "Cancelled")
        ],
        validators=[DataRequired()]
    )

    description = TextAreaField("Description")

    # Only used by doctor/carer, but must exist
    patient_id = SelectField("Patient", coerce=int)

    submit = SubmitField("Create Appointment")


class PrescriptionForm(FlaskForm):

    medicine_name = StringField(
        "Medicine:", validators=[DataRequired()]
    )

    dosage = StringField(
        "Dosage", validators=[DataRequired()]
    )

    instructions = TextAreaField("Instructions")
    repeat_allowed = BooleanField("Allow Repeat Prescriptions")
    submit = SubmitField("Send Prescription")