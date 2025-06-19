from flask import Blueprint, request, redirect, make_response, session, url_for, render_template, flash
from flask_login import login_required, login_user, logout_user, current_user
from werkzeug.security import generate_password_hash
import psycopg2
from psycopg2 import sql
from use_db import connect_db, UseDB
from forms import ProfileSettings
import io

user = Blueprint('user', __name__, template_folder='templates', static_folder='static')

@user.before_request
def before_request():
    global dbase
    global menu
    db = connect_db()
    dbase = UseDB(db)
    menu = dbase.get_menu()

@user.route('/profile/<id>')
@user.route('/profile')
@login_required
def profile(id = None):
    if not id:
        id = current_user.get_id()
    user = dbase.get_user_by_id(id)
    departments = dbase.get_departments_by_owner(current_user.get_id()) if current_user.get_class() == 'leader' else []
    return render_template('user/profile.html', menu = menu, user = user, departments = departments)



@user.route('/user_list', methods = ['POST', 'GET'])
@login_required
def user_list():
    users = dbase.get_all_users()
    search_string = request.args.get('search_string')
    if search_string != None:
        search_string = search_string.lower()
        all_users = users
        users = []
        for u in all_users:
            if f"{u['first_name'].lower()} {u['last_name'].lower()}" == search_string:
                users.append(u)
        for u in all_users:
            if f"{u['last_name'].lower()} {u['first_name'].lower()}" == search_string:
                users.append(u)
        for u in all_users:
            if search_string in u['first_name'].lower():
                users.append(u)
            elif search_string in u['last_name'].lower():
                users.append(u)
        
    if current_user.get_class() == 'leader':
        departments = [d for d in dbase.get_departments_by_owner(current_user.get_id()) if d['deleted'] == 'false']
    elif current_user.get_class() == 'admin':
        departments = dbase.get_all_departments()
    else: 
        departments = []
    return render_template('user/user_list.html', menu = menu, users = users, departments = departments)



@user.route('/user_avatar<id>')
@login_required
def user_avatar(id):
    try:
        if dbase.get_user_by_id(id)['deleted'] == 'true':
            with user.open_resource(user.root_path + url_for('static', filename = 'img/deleted_user_avatar.jpg'), 'rb') as file:
                img = file.read()

        elif dbase.load_user_avatar(id):
            img = dbase.load_user_avatar(id)
            if isinstance(img, memoryview):
                img = img.tobytes()
        else:
            with user.open_resource(user.root_path + url_for('static', filename = 'img/default_avatar.jpg'), 'rb') as file:
                img = file.read()
                
        res = make_response(img)
        res.headers['Content-Type'] = 'image/jpeg'
        return res
    except Exception as e:
        print('Ошибка загрузки аватара' + str(e))

@user.route('/upload_avatar', methods = ['POST'])
@login_required
def upload_avatar():
    try:
        if request.method == 'POST':
            file = request.files['file']
            user_id = request.form['user_id']
            if current_user.verify_avatar_ext(file.filename):
                img = file.read()
                dbase.upload_user_avatar(user_id, img)
                print('Аватар загружен')
            else:
                print('Неверное расширение аватара')
    except Exception as e:
        print('Ошибка выгрузки аватара ' + str(e))
    return redirect(url_for('.profile', id = user_id)) 


@user.route('/profile_settings/<id>', methods = ['POST', 'GET'])
@login_required
def profile_settings(id):
    user = dbase.get_user_by_id(id)
    form = ProfileSettings()
    password_hash = user['password_hash']
    
    try:
        if form.validate_on_submit():
            if form.password.data:
                password_hash = generate_password_hash(form.password.data)
                
            dbase.change_user_data(id, form.first_name.data, form.last_name.data, form.position.data, form.email.data, form.date_of_birth.data, form.gender.data, form.user_class.data, password_hash )
    except Exception as e:
        print('Ошибка обновления данных пользователя ' + str(e))

    
    form.first_name.data = user['first_name']
    form.last_name.data = user['last_name']
    form.gender.data = user['gender']
    form.date_of_birth.data = user['date_of_birth']
    form.position.data = user['position'] 
    form.user_class.data = user['class'] 
    form.email.data = user['email'] 


    return render_template('user/profile_settings.html', menu = menu, user = user, form = form)

