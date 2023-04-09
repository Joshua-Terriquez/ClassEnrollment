from flask import Flask, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_login import UserMixin, LoginManager, current_user, login_user, logout_user, login_required
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SECRET_KEY'] = 'secret key'

db = SQLAlchemy(app)
login = LoginManager(app)
bcrypt = Bcrypt(app)


login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return Student.query.get(int(user_id))

class Student(db.Model, UserMixin):
    s_id = db.Column(db.Integer, primary_key=True)
    studentName = db.Column(db.String(20), nullable=False, unique=True)
    studentPassword = db.Column(db.String(100), nullable=False)

    def get_id(self):
        return self.s_id

class Professor(db.Model, UserMixin):
    p_id = db.Column(db.Integer, primary_key=True)
    professorName = db.Column(db.String(20), nullable=False, unique=True)
    professorPassword = db.Column(db.String(100), nullable=False)

    def get_id(self):
        return self.p_id

class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=2,max=20)], render_kw={"placeholder": "Username"})
    password = PasswordField(validators=[InputRequired(), Length(min=2, max=20)], render_kw={"placeholder": "Password"})
    submit = SubmitField("Register")

    # def validate_username(self, username):
    #     existing_user_username = Student.query.filter_by(username = username.data).first()
    #     if existing_user_username:
    #         raise ValidationError("Username already exists!")

# Helps restrict access depending on login status
class MyModelView(ModelView):
    def is_accessible(self):
        return self.is_accessible() # return current_user.is_authenticated

# User will able to chooes between student login or Professor login
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/studentLogin', methods=["GET","POST"])
def studentLogin():
    form = LoginForm()
    if form.validate_on_submit():
        user = Student.query.filter_by(studentName=form.username.data).first()
        if user:
            if (user.studentPassword == form.password.data):
                login_user(user)
                return redirect(url_for('dashboard'))

    return render_template('student_login.html', form=form)

@app.route('/adminLogin', methods=["GET","POST"])
def adminLogin():
    form = LoginForm()
    if form.validate_on_submit():
        admin = Professor.query.filter_by(professorName=form.username.data).first()
        if admin:
            if (admin.professorPassword == form.password.data):
                login_user(admin)
                return redirect(url_for('dashboard'))
            
    return render_template('admin_login.html', form=form)

@app.route('/dashboard', methods=["GET", "POST"])
@login_required
def dashboard():
    return render_template('dashboard.html')

@app.route('/logout', methods=["GET","POST"])
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)