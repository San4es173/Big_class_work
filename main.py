from flask import Flask, render_template, redirect, flash
from flask_login import LoginManager, login_user, login_required, logout_user
from data import db_session
from data.jobs import Jobs
from data.users import User
from forms.users import RegisterForm, LoginForm
from forms.jobs import AddJobForm

app = Flask(__name__)
login_manager = LoginManager(app)
app.config["SECRET_KEY"] = "SECRETTOKEN"


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.get(User, user_id)


@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = User(
            surname=form.surname.data,
            name=form.name.data,
            age=form.age.data,
            position=form.position.data,
            speciality=form.speciality.data,
            address=form.address.data,
            email=form.login.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect("/login")
    return render_template("register.html", title="Регистрация", form=form)


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        flash("Неправильный логин или пароль", "danger")
        return render_template("login.html", form=form)
    return render_template("login.html", title="Авторизация", form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route("/addjob", methods=["GET", "POST"])
@login_required
def add_job():
    form = AddJobForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        job = Jobs(
            job=form.job.data,
            team_leader_id=form.team_leader.data,
            work_size=form.work_size.data,
            collaborators=form.collaborators.data,
            is_finished=form.is_finished.data
        )
        db_sess.add(job)
        db_sess.commit()
        return redirect("/")
    return render_template("add_job.html", form=form, title="Adding a job")


@app.route("/")
def work_log():
    db_sess = db_session.create_session()
    jobs = db_sess.query(Jobs).all()
    return render_template("work_log.html", jobs=jobs)


def main():
    db_session.global_init("db/blogs.db")
    app.run("", port=8080)


if __name__ == '__main__':
    main()
