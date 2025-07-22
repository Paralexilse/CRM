from flask import Flask, render_template, url_for, session, redirect, g, flash, request, abort, make_response
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash
import psycopg2
from psycopg2 import sql
from forms import LoginForm, RegisterForm
from use_db import UseDB, connect_db
from user_login import UserLogin
from user.user import user
from messenger.messenger import messenger
from department.department import department
from flask_socketio import SocketIO,  emit, join_room
from use_db import datetime



DEBUG = True
SECRET_KEY = 'dasidj8dj1892839hdf8732g4f683g87fg7836gf786g3478fg3476'

app = Flask(__name__)
app.config.from_object(__name__)
socketio = SocketIO(app)

app.register_blueprint(user, url_prefix='/user')
app.register_blueprint(messenger, url_prefix='/messenger')
app.register_blueprint(department, url_prefix='/department')

login_manager = LoginManager(app)

#WEB SOCKETS CHAT

@socketio.on('join')
def handle_join(data):
    user_id = data['user_id']
    join_room(f'user_{user_id}')

@socketio.on('send_message')
def handle_message(data):
    try:
        global dbase
        db = connect_db()
        dbase = UseDB(db)

        sender_id = str(data['sender_id'])
        receiver_id = str(data['receiver_id'])
        message = str(data['message'])
        dbase.send_message_to_user(sender_id, receiver_id, message)

        emit('receive_message', {'sender_id': current_user.get_id(), 'first_name': current_user.get_self()['first_name'], 'last_name': current_user.get_self()['last_name'], 'message': message, 'datetime': datetime()}, room=f'user_{receiver_id}')
        emit('receive_message', {'sender_id': current_user.get_id(), 'first_name': current_user.get_self()['first_name'], 'last_name': current_user.get_self()['last_name'], 'message': message, 'datetime': datetime()}, room=f'user_{sender_id}')

    except Exception as e:
        print(f'Ошибка отправки сообщение '+ str(e))


#WEB SOCKETS DEPARTMENT

@socketio.on('join_department')
def handle_join(data):
    department_id = data['department_id']
    join_room(f'department_{department_id}')

@socketio.on('send_message_department')
def handle_message(data):
    try:
        global dbase
        db = connect_db()
        dbase = UseDB(db)

        sender_id = str(data['sender_id'])
        department_id = str(data['department_id'])
        message = str(data['message'])
        dbase.send_message_to_department_chat(sender_id, department_id, message)

        sender = dbase.get_user_by_id(sender_id)

        emit('receive_message_department', {'sender_id': sender['id'], 'first_name': sender['first_name'], 'last_name': sender['last_name'], 'message': message, 'datetime': datetime()}, room=f'department_{department_id}')

    except Exception as e:
        print('Ошибка отправления сообщения в отдел' + str(e))



@app.before_request
def before_request():
    global dbase
    db = connect_db()
    dbase = UseDB(db)

@login_manager.user_loader
def load_user(user_id):
    print('Загрузка пользователя')
    return UserLogin().from_db(user_id, dbase)


@app.route('/')
@app.route('/index')
def index():
    if current_user.is_authenticated:
        return redirect('/user/profile')
    return render_template('index.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if current_user.is_authenticated:
        return redirect('/user/profile')

    form = LoginForm()
    try:
        if form.validate_on_submit():
            user = dbase.get_user_by_email(form.email.data)
            if check_password_hash(user['password_hash'], str(form.password.data)):
                login_user(UserLogin().create(user), remember = form.remember.data)
                print('Успешная авторизация ')
                return redirect('/user/profile')
            else:
                flash('Пароль неверный', category='error')
    except Exception as e:
        print("Ошибка авторизации " + str(e))
    return render_template('login.html', form = form)


@app.route('/register', methods = ['POST', 'GET'])
def register():
    form = RegisterForm()   
    try:
        if form.validate_on_submit():
            if dbase.create_user(form.first_name.data, form.last_name.data, form.position.data, form.email.data, form.date_of_birth.data, form.gender.data, generate_password_hash(form.password.data)):
                print('Успешная регистрация ')
                flash('Успешная регистрация')
            else:
                print('Ошибка регистрации возможно email уже используется или поля указаны неверно')
                flash('Ошибка регистрации возможно email уже используется или поля указаны неверно')

    except Exception as e:
        print('Ошибка регистрации ' + str(e))
    return render_template('register.html', form = form)


@app.route('/logout')
def logout():
    logout_user()
    print('Деавторизация')
    return redirect(url_for('index'))



if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=8000)

   