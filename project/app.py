from flask import Flask
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_migrate import Migrate

# instantiate app
app = Flask(__name__)

# creating an sqlite database 
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///Lab8.db'
# gets rid of annoying terminal warnings that are not needed
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#for session cookies
app.config['SECRET_KEY'] = 'secret'


db = SQLAlchemy(app)
#this is used for migration(Model changes)
migrate = Migrate(app,db)
admin = Admin(app)

# Model(table) creations
class Users(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    username = db.Column(db.String(30), unique=True)
    password = db.Column(db.String(30), unique=True)
    teachers = db.relationship("Teachers", backref="teacher_user_id")
    students = db.relationship("Students", backref="students_user_id")  
class Students(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(30))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    enrollment = db.relationship("Enrollments", backref="student_user_id")

class Teachers(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    name = db.Column(db.String(30))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    Prof_classes = db.relationship("Classes", backref="teachers_user_id")

class Classes(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    class_name = db.Column(db.String(30))
    teacher_id = db.Column(db.Integer, db.ForeignKey('teachers.id'))
    num_enrolled = db.Column(db.Integer)
    class_cap = db.Column(db.Integer)
    class_time = db.Column(db.String(30))
    enrollment = db.relationship("Enrollments", backref="class_enrollment_id")

class Enrollments(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    class_id = db.Column(db.Integer, db.ForeignKey("classes.id"))
    student_id = db.Column(db.Integer, db.ForeignKey("students.id"))
    student_grade = db.Column(db.String(5))
    
#adds the tables to the admin (so data can be modified through admin)
admin.add_view(ModelView(Users,db.session))
admin.add_view(ModelView(Students,db.session))
admin.add_view(ModelView(Teachers,db.session))
admin.add_view(ModelView(Classes,db.session))
admin.add_view(ModelView(Enrollments,db.session))


if __name__== '__main__':
    app.run(debug=True)

#creates all the models
with app.app_context():
    db.create_all()
