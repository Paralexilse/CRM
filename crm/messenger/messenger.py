from flask import Blueprint, request, redirect, make_response, session, url_for, render_template, flash
from flask_login import login_required, login_user, logout_user, current_user
import psycopg2
from psycopg2 import sql
from use_db import connect_db, UseDB
import io

messenger = Blueprint('messenger', __name__, template_folder='templates', static_folder='static')




@messenger.before_request
def before_request():
    global dbase
    global menu
    db = connect_db()
    dbase = UseDB(db)
    menu = dbase.get_menu()



@messenger.route('/chat/<id>', methods = ['POST', 'GET'])
@login_required
def chat(id):
    companion = dbase.get_user_by_id(id)
    
    try:
        if request.method == 'POST':
            dbase.send_message_to_user(current_user.get_id(), id, request.form['message'])
        messages = dbase.get_chat_messages(current_user.get_id(), id)        
    except Exception as e:
        print('Ошибка при отправке сообщения ', str(e))

    return render_template('chat/chat.html', companion = companion, messages = messages, menu = menu)

@messenger.route('/users_chats', methods = ['POST', 'GET'])
@login_required
def users_chats():
    users = dbase.get_users_by_chats(current_user.get_id())
    departments = dbase.get_departments_by_user(current_user.get_id())
    return render_template('chat/users_chats.html', users = users, menu = menu, departments = departments)

@messenger.route('/add_chat/<id>')
@login_required
def add_chat(id):
    dbase.add_chat(current_user.get_id(), id)
    return redirect(url_for('user.user_list'))

@messenger.route('/delete_chat/<id>')
@login_required
def delete_chat(id):
    dbase.delete_chat(current_user.get_id(), id)
    return redirect(url_for('user.user_list'))
















