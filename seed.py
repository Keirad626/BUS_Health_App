from app import app, db
from app.models import User
from werkzeug.security import generate_password_hash

with app.app_context():

    db.drop_all()
    db.create_all()

    doctor = User(
        first_name="Adam",
        last_name="Smith",
        email="adam.smith@example.com",
        role="doctor",
        password=generate_password_hash("password123")
    )

    carer = User(
        first_name="Tanisha",
        last_name="Brown",
        email="tanisha.brown@example.com",
        role="carer",
        password=generate_password_hash("password123")
    )

    patient1 = User(
        first_name="Hamish",
        last_name="O'Riley",
        email="hamish.oriley@example.com",
        role="patient",
        password=generate_password_hash("password123")
    )

    patient2 = User(
        first_name="Margaret",
        last_name="Carter",
        email="margaret.carter@example.com",
        role="patient",
        password=generate_password_hash("password123")
    )

    db.session.add_all([doctor, carer, patient1, patient2])
    db.session.commit()

    family = User(
        first_name="Alex",
        last_name="Carter",
        email="alex.carter@example.com",
        role="family",
        password=generate_password_hash("password123"),
        linked_patient_id=patient2.id
    )

    db.session.add_all([doctor, carer, patient1, patient2, family])
    db.session.commit()

    print("seed data created successfully!!")
