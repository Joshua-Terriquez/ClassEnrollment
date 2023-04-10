from flask import Flask, request, render_template, redirect
from flask.helpers import url_for
from flask_admin import Admin
from flask_login import login_required, logout_user, login_user, current_user, LoginManager, UserMixin
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
# text to commit
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///class-enrollment.sqlite"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['FLASK_ADMIN_SWATCH'] = 'cerulean'
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
app.secret_key = 'keep it secret, keep it safe'
db = SQLAlchemy(app)

@login_manager.user_loader 
def load_user(user_id): 
    return Users.query.filter_by(user_id = user_id).first()

# Many to many relationship table with Users and Classes
class Enrollment(db.Model):
    __tablename__ = "Enrollment"
    users_id = db.Column(db.ForeignKey("Users.user_id"), primary_key = True)
    classes_id = db.Column(db.ForeignKey("Courses.class_id"), primary_key = True)
    grade = db.Column(db.Integer, nullable = False)

    def __init__(self, user_id, classes_id, grade):
        self.users_id = user_id
        self.classes_id = classes_id
        self.grade = grade

# User table
class Users(UserMixin, db.Model):
    __tablename__ = "Users"
    user_id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String, nullable = False)
    name = db.Column(db.String, nullable = False)
    password = db.Column(db.String, nullable = False)
    acct_type = db.Column(db.Integer, nullable = False) # 0 - Student, 1 - Teacher, 2 - Admin

    def __init__(self, username, name, password, acct_type):
        self.username = username
        self.name = name
        self.password = password
        self.acct_type = acct_type

    def check_password(self, password):
        return self.password == password

    def get_id(self):
        return self.user_id

# Classes Table
class Courses(db.Model):
    __tablename__ = "Courses"
    class_id = db.Column(db.Integer, primary_key = True)
    class_name = db.Column(db.String, nullable = False)
    teacher = db.Column(db.String, nullable = False)
    time = db.Column(db.String, nullable = False)
    enrolled = db.Column(db.Integer, nullable = False)
    capacity = db.Column(db.Integer, nullable = False)

    def __init__(self, class_name, teacher, time, enrolled, capacity):
        self.class_name = class_name
        self.teacher = teacher
        self.time = time
        self.enrolled = enrolled
        self.capacity = capacity


# Login
@app.route("/", methods = ["GET", "POST"])
def login():
    if request.method == "POST":
        data = request.get_json()
        user = Users.query.filter_by(username=data['username']).first() 
        if user is None or not user.check_password(data['password']): 
            return (url_for('login'))[1:]
        login_user(user)
        if user.acct_type == 0:
            return url_for('student_view')[1:]
        elif user.acct_type == 1:
            return url_for('teacher_view')[1:]
        else:
            return url_for('admin')[1:]
    else:   
        return render_template('login.html')

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return url_for('login')[1:]

# Admin
@app.route('/admin', methods = ["GET", "POST", "PUT", "DELETE"])
@login_required
def admin():
    if request.method == "POST":
        data = request.get_json()
        if data["post"] == "user":
            user = Users.query.filter_by(username = data["username"]).first()
            if user is None:
                user = Users(data["username"], data["name"], data["password"], int(data["acct_type"]))
                db.session.add(user)
                db.session.commit()
                return "success"
        elif data["post"] == "class":
            course = Courses.query.filter_by(class_name = data["classname"]).first()
            if course is None:
                course = Courses(data["classname"], data["teacher"], data["time"], int(data["enrollment"]), int(data["capacity"]))
                db.session.add(course)
                db.session.commit()
                return "success"
        else:
            user = Users.query.filter_by(username = data["username"]).first()
            course = Courses.query.filter_by(class_name = data["classname"]).first()
            if user is not None and course is not None and user.acct_type == 0:
                enroll = Enrollment(user.user_id, course.class_id, int(data["grade"]))
                course.enrolled = course.enrolled + 1
                db.session.add(enroll)
                db.session.commit()
                return "success"
    elif request.method == "PUT":
        data = request.get_json()
        if data["put"] == "user":
            user = Users.query.filter_by(username = data["original_name"]).first()
            if user is not None:
                if data["new_username"] != "":
                    user.username = data["new_username"]
                if data["new_name"] != "":
                    user.name = data["new_name"]
                if data["new_password"] != "":
                    user.password = data["new_password"]
                if data["new_acct"] != "":
                    user.acct_type = int(data["new_acct"])
                db.session.commit()
                return "success"
        elif data["put"] == "class":
            course = Courses.query.filter_by(class_name = data["original_class"]).first()
            if course is not None:
                if data["new_class"] != "":
                    course.class_name = data["new_class"]
                if data["new_teacher"] != "":
                    course.teacher = data["new_teacher"]
                if data["new_time"] != "":
                    course.time = data["new_time"]
                if data["new_enrolled"] != "":
                    course.enrolled = int(data["new_enrolled"])
                if data["new_capacity"] != "":
                    course.capacity = int(data["new_capacity"])
                db.session.commit()
                return "success"
        else:
            user = Users.query.filter_by(username = data["name"]).first()
            course = Courses.query.filter_by(class_name = data["course"]).first()
            if user is not None and course is not None:
                enroll = Enrollment.query.filter_by(users_id = user.user_id, classes_id = course.class_id).first()
                enroll.grade = data["grade"]
                db.session.commit()
                return "success"

    elif request.method == "DELETE":
        data = request.get_json()
        if data["delete"] == "user":
            user = Users.query.filter_by(username = data["name"]).first()
            if user is not None:
                enroll = Enrollment.query.filter_by(users_id = user.user_id)
                for row in enroll:
                    courses = Courses.query.filter_by(class_id = row.classes_id)
                    for course in courses:
                        course.enrolled = course.enrolled - 1
                    db.session.delete(row)
                db.session.delete(user)
                db.session.commit()
                return "success"
        elif data["delete"] == "class":
            course = Courses.query.filter_by(class_name = data["class"]).first()
            if course is not None:
                enroll = Enrollment.query.filter_by(classes_id = course.class_id)
                for row in enroll:
                    db.session.delete(row)
                db.session.delete(course)
                db.session.commit()
                return "success"
        else:
            user = Users.query.filter_by(username = data["name"]).first()
            course = Courses.query.filter_by(class_name = data["class"]).first()
            if user is not None and course is not None:
                enroll = Enrollment.query.filter_by(classes_id = course.class_id, users_id = user.user_id).first()
                if enroll is not None:
                    course.enrolled = course.enrolled - 1
                    db.session.delete(enroll)
                    db.session.commit()
                    return "success"
    elif request.method == "GET":
        all_courses = []
        all_grades = []
        all_users = []
        allRows = Enrollment.query.all()
        for row in allRows:
            user = Users.query.filter_by(user_id = row.users_id).first()
            course = Courses.query.filter_by(class_id = row.classes_id).first()
            all_courses.append(course.class_name)
            all_users.append(user.name)
            all_grades.append(row.grade)
        return render_template('admin.html', courses = Courses.query.all(), users = Users.query.all(), enrollCourses = all_courses, enrollUsers = all_users, enrollGrades = all_grades, length = len(all_courses))

# Student
@app.route("/student")
@login_required
def student_view():
    listCourses = []
    enrolled_classes = Enrollment.query.filter_by(users_id = current_user.user_id)
    for course in enrolled_classes:
        listCourses.append(course.classes_id)
    classes = Courses.query.filter(Courses.class_id.in_(listCourses))
    return render_template('student-view-classes.html', courses = classes)

@app.route("/student/courses", methods=["GET", "POST"])
@login_required
def student_edit():
    if request.method=="POST":
        data = request.get_json()
        course = Courses.query.filter_by(class_name=data["class_name"]).first()
        if course is not None and course.enrolled < course.capacity:
            enrollment = Enrollment(current_user.user_id, course.class_id, 0)
            db.session.add(enrollment)
            course.enrolled = course.enrolled+1
            db.session.commit()
            return "success"
    if request.method == "GET":
        enrollment = Enrollment.query.filter_by(users_id = current_user.user_id)
        enrolledClasses = []
        for course in enrollment:
            enrolledClasses.append(course.classes_id)
        return render_template('student-edit-classes.html', courses = Courses.query.all(), enrollment = enrolledClasses)


# Teacher
@app.route("/teacher")
@login_required
def teacher_view():
    taught_classes = Courses.query.filter_by(teacher = current_user.name)
    return render_template('teacher-view-classes.html', courses = taught_classes)

@app.route("/teacher/<course_name>", methods=['GET', 'PUT'])
@login_required
def teacher_edit(course_name):

    if request.method == "PUT":
        data = request.get_json()
        user = Users.query.filter_by(name = data["name"]).first()
        if user != None:
            course = Courses.query.filter_by(class_name = course_name).first()
            cId = course.class_id
            enroll = Enrollment.query.filter_by(users_id = user.user_id, classes_id = cId).first()
            if enroll != None:
                enroll.grade = data["grade"]
                db.session.commit()

    listStudentIds = []
    listStudentNames = []

    grades = []
    # Acquire Course
    course_details = Courses.query.filter_by(class_name = course_name).first()
    # Acquire class id
    classId = course_details.class_id
    # Acquire all enrolled in class id
    listEnrolled = Enrollment.query.filter_by(classes_id = classId).order_by(Enrollment.users_id)
    # Acquire grades
    for user in listEnrolled:
        grades.append(user.grade)
    # Acquire Student Ids
    for enrolled in listEnrolled:
        listStudentIds.append(enrolled.users_id)
    # Acquire Student users
    enrolled_users =  Users.query.filter(Users.user_id.in_(listStudentIds))
    # Acquire Student name
    for names in enrolled_users:
        listStudentNames.append(names.name)
    length = len(listStudentIds)

    return render_template('teacher-view-class-details.html', name = course_name, students = listStudentNames, grades = grades, length = length)

# Run
if __name__ == "__main__":
    # db.create_all() # Only need this line if db not created
    app.run(debug=True)