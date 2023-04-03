from flask import Flask,render_template, request, redirect, url_for, session
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin,LoginManager,login_user, logout_user, login_required, current_user
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
login_manager = LoginManager(app)

# Model(table) creations
class Users(db.Model,UserMixin):
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

@login_manager.user_loader
def load_user(user_id):
   #returns the user from the database
   return Users.query.get(int(user_id))

@app.route('/')
def index():
   return render_template('index.html')
@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
 return render_template("dashboard.html")

@app.route("/login", methods=["GET", "POST"])
def login():
   if request.method == "POST":
       username = request.form.get("username")
       password = request.form.get("password")
      
       user = Users.query.filter_by(username=username).first()
      
       if not user or not user.password == password:
           return "Incorrect username or password"
      
       login_user(user)
       return redirect(url_for("dashboard"))
      
   return render_template("index.html")

@app.route("/logout")
def logout():
   logout_user()
   return redirect(url_for("index"))


if __name__== '__main__':
    app.run(debug=True)

#creates all the models
with app.app_context():
    db.create_all()
