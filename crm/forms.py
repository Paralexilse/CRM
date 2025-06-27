from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, SelectField, FileField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Optional


class LoginForm(FlaskForm):
    email = StringField('Почта', validators=[Email(message='Неккоректная почта')])
    password = PasswordField('Пароль', validators=[Length(min=4, max=30, message='Пароль должен быть от 4 до 30 символов'), DataRequired()])
    remember = BooleanField('Запомнить')
    submit = SubmitField('Войти')

class RegisterForm(FlaskForm):
    first_name = StringField('Имя', validators=[Length(min=3, max=30, message='Имя должно быть от 3 до 30 символов')])
    last_name = StringField('Фамилия', validators=[Length(min=3, max=30, message='Фамилия должна быть от 3 до 30 символов')])
    position = StringField('Должность', validators=[Length(min=3, max=30, message='Должность должна быть от 3 до 70 символов')])
    email = StringField('Почта', validators=[Email(message='Неккоректная почта')])
    date_of_birth = DateField('Дата рождения', format='%Y-%m-%d')
    gender = SelectField('Пол', choices=['Мужской', 'Женский'])
    password = PasswordField('Пароль', validators=[Length(min=4, max=30, message='Пароль должен быть от 4 до 30 символов'), DataRequired()])
    password2 = PasswordField('Повторите пароль', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Зарегистрироваться')

class ProfileSettings(FlaskForm):
    first_name = StringField('Имя', validators=[Length(min=3, max=30, message='Имя должно быть от 3 до 30 символов')])
    last_name = StringField('Фамилия', validators=[Length(min=3, max=30, message='Фамилия должна быть от 3 до 30 символов')])
    position = StringField('Должность', validators=[Optional(), Length(min=3, max=70, message='Должность должна быть от 3 до 70 символов')])
    email = StringField('Почта', validators=[Email(message='Неккоректная почта')])
    date_of_birth = DateField('Дата рождения', format='%Y-%m-%d')
    gender = SelectField('Пол', choices=['Мужской', 'Женский'])
    password = PasswordField('Пароль', validators=[Optional(), Length(min=4, max=30, message='Пароль должен быть от 4 до 30 символов')])
    password2 = PasswordField('Повторите пароль', validators=[ EqualTo('password')])
    user_class = SelectField('Класс пользователя', choices=['user', 'leader'])
    submit = SubmitField('Сохранить')


class CreateDepartmentForm(FlaskForm):
    title = StringField('Название отдела', validators=[Length(min=3, max=50, message='Название должно быть от 3 до 30 символов'), DataRequired()])
    describtion = TextAreaField('Описание отдела', validators=[Length(min=0, max=300, message='Название должно быть до 300 символов')])
    logo = FileField('Логотип отдела')
    submit = SubmitField('Создать отдел')

class DepartmentSettings(FlaskForm):
    title = StringField('Название отдела', validators=[Length(min=3, max=50, message='Название должно быть от 3 до 30 символов'), DataRequired()])
    describtion = TextAreaField('Описание отдела', validators=[Length(min=0, max=300, message='Название должно быть до 300 символов')])
    logo = FileField('Логотип отдела')
    submit = SubmitField('Сохранить')



