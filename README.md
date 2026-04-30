# Welcome to our Health Monitoring App for the Building Usable Software module at the University of Birmingham!
The application consists of three main programming languages, but is primarily rooted in HTML and Python.
A small amount of CSS code is also included. 
The BUS Health Monitoring App is a Flask-based web application that supports the communication of patients, doctors, carers and family members through a health monitoring system.

## The BUS Health Monitoring App is designed to complete challenge 2: Remote Health Monitoring- Supporting Independent Living for Older Adults.
Whilst much of the code within this project encapsulates all four challenge focuses, we have mainly picked points one and three.
Support for medication adherence (or daily routines) has been implemented through the notes system and the prescription system.
Built within the routes of this project, the app allows for medication to be prescribed from doctor to patient.
Family members have access to these notes, as do Carers.
As such, Carers also have the capabilities to add notes for doctors and family members to view.
In cases such as this, we can imagine an example where the patient has refused to take a certain medicine during morning rounds. 
The carer can leave a note for a family member, or the next round of carers to view this. 
In terms of basic health tracking, patients and family members can book appointments with the doctor.
The doctor can view their upcoming appointments, as well as schedule appointments with patients.
An example of this may be a check up. 
I believe that this also encompassses point four, where we can see that there is a chain of communication between carers, family members and doctors. 
Furthermore, patients' family members can leave notes too. For example, if a family member is out of town and a patient can't reach the door, a note can be left to describe where the spare key has been left.
The date, time and type of prescription ordered and assigned to a patient is kept record of. 
The patient and doctor are also privy to a record of completed, pending and cancelled appointments.
These features encompass the application's trackable nature of patient care.
As such, the application is designed for several different types of users. Where each user has access to a personalised dashboard, that contains features unique to the user's identity.

# User Roles and Capabilities
The roles for this specific project are outlined under the user stories section within the portfolio, but I will outline them here briefly.
## User roles include: 
### - Elderly Adults (detailed as Pateints)
### - Family members
### - Care Workers (Social Careworkers/Carers)
### - Doctors

For the purposes of this demonstration, you will find the logins for each user (in relation to user stories S1, S2, S3, S4 and S5) within 'seed.py'.
Upon viewing the username and password for each user, you must use the login page to sign into the account.
From here you will be taken to a personalised user dashboard, where you can explore the features for each user.
This is demonstrated by the walkthrough video.
Whilst a registration page does exist, and can be used to make users, for the purposes of the demonstration, the code has been gutted to allow for a smoother flow.
You can sign in as the doctor and make notes, create prescriptions and schedule appointments with the two patients in the system. 
When signed in as a carer, you can have access to this patient information, which would inform your roles for the day/time you have with the patient in person.
This removes communication barriers between patients and carers. 
As a family member, you have unfettered access to patient notes, due to the linked id between family member roles and patient roles.
You cannot access any other roles dashboard than your own. This is to guarantee security and privacy between doctors, patients, family members and carers. As well as a professional look from the app.
The UI of the app is intentionally in large print, as older patients may have issues reading smaller prints.
As such, the font style is also kept simple and non-intrusive. 
Furthermore, the button design is big and blocky, making it easier for older patients, who may not be technilogically adept, to navigate through the dashboard effortlessly.
The monitoring app is designed as a suplementary device, suporting the role of real life and in-person decision making. 
The principle purpose of the app is as an aid for carers who may struggle with communication issues, long waits from doctors or language barriers. 

## Specific User Role Features
### Doctor
- Creation and management of prescriptions for patients.
- View and ammend patient notes.
- View, schedule and manage patient appointments.

### Carer
- View patient notes.
- Add carer notes.
- View patient's medication and appointments.

### Patient
- Create and manage appointments.
- View prescriptions.
- View notes from doctors, carers and family members.
- Book appointments.
### Family Member
- View patient notes.
- Leave family member notes.
- Book appointments on behalf of their family member (the patient)

# Running the Application
If you the repository is going to be cloned, the following dependency must be installed:
''' pip install -r requirements.txt '''
As previously mentioned, this is a flask-based web service, so flask must be installed to run the app. 
The database has already been seeded with ''' python seed.py '''.
If necessary, please do seed the database again so that the demonstration can be viewed/ran correctly. 
**Logins** can be found in **seed.py**.
If there are any issues, the format for logins is: firstname.lastname@example.com
The password for every account in this demonstration is: **password123**.
This is for ease of access.
However, when creating/registerting an account, it can be noted that **password123** will not be sufficient, as there are password encryptions and protections in the code to ensure user safety.
For the purposes of the demonstration only, this does not hold.

# Logic used in this application
- Backend: Python (Flask)
- Fronted: HTML/CSS
- SQLite: Database
- Jinja2: Templating
- Backend Security: Werkzeug (Password Hashsing)

Thank you for reading! I hope that you enjoy the app as hours of hardwork and debugging has been poured into it. 
If you run into any issues, do not hesitate to refer to the walkthrough video to see the successful implementation of each role.
Happy testing!

Kind regards,

Keira-Mae Drysdale, on behalf of BUS 14

