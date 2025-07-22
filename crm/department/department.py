from flask import Blueprint, request, redirect, make_response, session, url_for, render_template, flash
from flask_login import login_required, login_user, logout_user, current_user
import psycopg2
from psycopg2 import sql
from use_db import connect_db, UseDB
import io
from forms import CreateDepartmentForm, DepartmentSettings


department = Blueprint('department', __name__, template_folder='templates', static_folder='static')

@department.before_request
def before_request():
    global dbase
    global menu
    db = connect_db()
    dbase = UseDB(db)
    menu = dbase.get_menu()




@department.route('/department_list')
@login_required
def department_list():
    users_departments = []
    other_departments = []
    departments = dbase.get_all_departments()

    for d in departments:
        if d['deleted'] == 'true':
            pass
        elif current_user.get_id() in d['members'] or current_user.get_id() in d['owners']:
            users_departments.append(d)
        else:
            other_departments.append(d)

    search_string = request.args.get('search_string')
    if search_string != None:
        all_other_departments = other_departments
        other_departments = []
        for d in all_other_departments:
            if search_string.lower() in d['title'].lower():
                other_departments.append(d)
       
            
    return render_template('department/department_list.html', menu = menu, users_departments = users_departments, other_departments = other_departments)


@department.route('/department_logo/<id>')
def department_logo(id):
    try:  
        
        if dbase.get_department(id)['deleted'] == 'true':
            with department.open_resource(department.root_path + url_for('static', filename = 'img/deleted_department_logo.jpg'), 'rb') as file:
                img = file.read()

        elif dbase.load_department_logo(id):
            img = dbase.load_department_logo(id)
            if isinstance(img, memoryview):
                img = img.tobytes()
        else:
            with department.open_resource(department.root_path + url_for('static', filename = 'img/default_logo.png'), 'rb') as file:
                img = file.read()
                
        res = make_response(img)
        res.headers['Content-Type'] = 'image/jpeg'
        return res
    except Exception as e:
        print('Ошибка загрузки логотипа')


@department.route('/department_profile/<id>')
@login_required
def department_profile(id):
    department = dbase.get_department(id)
    owners = []
    members = []
    if department['owners']:
        owners = [dbase.get_user_by_id(id) for id in department['owners']]
    if department['members']:
        members = [dbase.get_user_by_id(id) for id in department['members']]

    return render_template('department/department_profile.html', menu = menu, department = department, owners = owners, members=members)


@department.route('/create_department', methods = ['POST', 'GET'])
@login_required
def create_department():
    form = CreateDepartmentForm()
    try:
        if form.validate_on_submit():
            title = form.title.data
            describtion = form.describtion.data
            if form.logo.data:
                file = form.logo.data
                if current_user.verify_avatar_ext(file.filename):
                    img = file.read()
            else:
                img = None
            dbase.create_department(title, describtion, img, current_user.get_id())
            flash('Отдел создан', category='success')
    except Exception as e:
        flash('Ошибка создания отдела', category='error')
        print('Ошибка создания отдела ' + str(e))

    return render_template('department/create_department.html', menu = menu, form = form)




    
@department.route('/add_user_to_department', methods = ['GET', 'POST'])
@login_required
def add_user_to_department():
    try:
        if request.method == 'POST':
            dbase.add_user_to_department(request.form['user_id'], request.form['department_id'])
            print('Пользователь добавлен в отдел')
    except Exception as e:
        print('Ошибка добавления пользователя в отдел' + str(e))

    return redirect(url_for('user.user_list'))

@department.route('/delete_department', methods = ['GET', 'POST'])
@login_required
def delete_department():
    try:
        if request.method == 'POST':
            id_department = request.form['id_department']
            department = dbase.get_department(id_department)
            if current_user.get_id() in department['owners']:
                dbase.delete_department(id_department)
                print('Отдел удален')
                return redirect(url_for('.department_list'))
          
    except Exception as e:
        print('Ошибка удаления отдела' + str(e))

    return redirect(url_for('user.user_list'))


@department.route('/department_chat/<id>', methods = ['GET', 'POST'])
@login_required
def department_chat(id):

    department = dbase.get_department(id)
    messages = dbase.get_department_messages(id)

    # try:
    #     if request.method == 'POST':
    #         message = request.form['message']
    #         dbase.send_message_to_department_chat(current_user.get_id(), id, message)
    #         print('Сообщение отправлено в чат отдела')
    # except Exception as e:
    #     print('Ошибка отправки сообщения в чат отдела')

    if current_user.get_id() in department['owners'] or current_user.get_id() in department['members'] or current_user.get_class() == 'admin'  :
        return render_template('department/department_chat.html', menu = menu, department = department, messages=messages)
    
@department.route('/department_management/<id>', methods = ['GET', 'POST'])
@login_required
def department_management(id):
    department = dbase.get_department(id)
    if current_user.get_id() in department['owners'] or current_user.get_class() == 'admin' :
        form = DepartmentSettings()
        owners = []
        members = []
        if department['owners']:
            owners = [dbase.get_user_by_id(id) for id in department['owners']]
        if department['members']:
            members = [dbase.get_user_by_id(id) for id in department['members']]

        try:
            if form.validate_on_submit():
                title = form.title.data
                describtion = form.describtion.data
                if form.logo.data:
                    file = form.logo.data
                    if current_user.verify_avatar_ext(file.filename):
                        img = file.read()
                else:
                    img = department['logo']

                dbase.change_department_data(title, describtion, img, department['id'])
        except Exception as e:
            print('Ошибка изменения отдела ' + str(e))

        form.title.data = department['title']
        form.describtion.data = department['describtion']
        

        return render_template('department/department_management.html', menu = menu, form = form, department = department, owners = owners, members = members)
                    
                

@department.route('/delete_user_from_department/<id_user>/<id_department>', methods = ['GET', 'POST'])
@login_required
def delete_user_from_department(id_user, id_department):
    try:
        department = dbase.get_department(id_department)
        if current_user.get_id() in department['owners'] or current_user.get_class() == 'admin':
            dbase.delete_user_from_department(id_user, id_department)
            print('Пользователь удален из отдела')
    except Exception as e:
        print('Ошибка удаления пользователя из отдела ' + str(e))
    return redirect(url_for('department.department_management', id = id_department))
    
@department.route('/make_owner/<id_user>/<id_department>', methods = ['GET', 'POST'])
@login_required
def make_owner(id_user, id_department):
    department = dbase.get_department(id_department)
    if current_user.get_id() in department['owners'] or current_user.get_class() == 'admin' :
        dbase.make_owner(id_user, id_department)

    return redirect(url_for('department.department_management', id = id_department))
    
@department.route('/lose_owner/<id_user>/<id_department>', methods = ['GET', 'POST'])
@login_required
def lose_owner(id_user, id_department):
    department = dbase.get_department(id_department)
    if current_user.get_id() in department['owners'] or current_user.get_class() == 'admin' :
        dbase.lose_owner(id_user, id_department)

    return redirect(url_for('department.department_management', id = id_department))
    

                
                
            



