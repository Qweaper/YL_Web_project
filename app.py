from flask import Flask, redirect, render_template, request
from userDB import UserModel
from booksDB import NewsModel  #######
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired
from flask_wtf import FlaskForm

app = Flask(__name__)
session = {}
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
curr_user = ''


class AddNewsForm(FlaskForm):
    title = StringField('Заголовок новости', validators=[DataRequired()])
    content = TextAreaField('Текст новости', validators=[DataRequired()])
    submit = SubmitField('Добавить')


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    remember_me = BooleanField('Запомнить меня')
    submit = SubmitField('Войти')


class SignInForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Зарегистрироваться')


@app.route('/')
def hello_world():
    return 'Hello World!'


@app.route('/success')
def success():
    return '''success'''


@app.route('/error')
def error():
    return '''error'''


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/login')


@app.route('/sign_in', methods=['GET', 'POST'])
def sign_in():
    try:
        form = SignInForm()
        if request.method == 'GET':
            return render_template('sign_in.html', form=form)
        if request.method == 'POST':
            user_name = form.username.data
            password = form.password.data
            users.insert(user_name, password)
            return redirect('/login')
    except ValueError:
        return redirect('/error')


@app.route('/users_log')
def users_log():
    user_list = [i[1] for i in users.get_users()]
    logs = {}
    for user in list(set(user_list)):
        us = users.get_id(user)[1]
        logs[user] = len(news.get_all(us))
    return render_template('user_logs.html', logs=logs, user_list=user_list)


if __name__ == '__main__':
    db = DB()

    users = UserModel(db.get_connection())
    users.init_table()

    news = NewsModel(db.get_connection())
    news.init_table()
    try:
        users.insert('admin', 'admin')
    except Exception:
        pass
    app.run(port=8080, host='127.0.0.1', debug=True)
