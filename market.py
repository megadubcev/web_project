from flask import Flask, request, render_template, redirect, session
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, TextAreaField, RadioField, IntegerField, SelectField
from wtforms.validators import DataRequired
import sqlite3

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


class DB:
    def __init__(self):
        conn = sqlite3.connect('shop.db', check_same_thread=False)
        self.conn = conn

    def get_connection(self):
        return self.conn

    def __del__(self):
        self.conn.close()


class UsersModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             user_name VARCHAR(50),
                             password_hash VARCHAR(128)
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO users 
                          (user_name, password_hash) 
                          VALUES (?,?)''', (user_name, password_hash))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id),))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users")
        rows = cursor.fetchall()
        return rows

    def exists(self, user_name, password_hash):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE user_name = ? AND password_hash = ?",
                       (user_name, password_hash))
        row = cursor.fetchone()
        return (True, row[0]) if row else (False,)


class FoodModel:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS food 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             food_name VARCHAR(50),
                             food_type VARCHAR(50),
                             food_description VARCHAR(200),
                             food_price INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, food_name, food_type, food_description, food_price):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO food 
                          (food_name, food_type, food_description, food_price) 
                          VALUES (?,?,?,?)''', (food_name, food_type, food_description, food_price))
        cursor.close()
        self.connection.commit()

    def get(self, user_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM users WHERE id = ?", (str(user_id),))
        row = cursor.fetchone()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM food")
        rows = cursor.fetchall()
        return rows


class LoginForm(FlaskForm):
    username = StringField('Логин', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')


class AddFoodForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    type = SelectField('Тип', choices=[("Суши", "Суши"), ("Роллы", "Роллы"), ("Напитки", "Напитки")],
                       validators=[DataRequired()])
    description = TextAreaField('Описание', validators=[DataRequired()])
    price = IntegerField('Цена', validators=[DataRequired()])
    submit = SubmitField('Добавить')


@app.route('/')
def main():
    return render_template('main.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user_name = form.username.data
        password = form.password.data
        user_model = UsersModel(db.get_connection())
        exists = user_model.exists(user_name, password)
        if (exists[0]):
            session['username'] = user_name
            session['user_id'] = exists[1]
            print(userDB.get_all(), session['username'], session['user_id'])
            return redirect("/")
        else:
            return render_template('login.html', title='Авторизация', form=form, not_found=True)

    return render_template('login.html', title='Авторизация', form=form, not_found=False)


@app.route('/logout')
def logout():
    session.pop('username', 0)
    session.pop('user_id', 0)
    return redirect('/')


@app.route('/add_food', methods=['GET', 'POST'])
def addFoodFunc():
    form = AddFoodForm()
    if form.validate_on_submit():
        foodDB.insert(form.name.data, form.type.data, form.description.data, form.price.data)
        print("продукты:")
        print(foodDB.get_all())
        return redirect("/")

    return render_template('add_food.html', title='Добавление товара', form=form)


db = DB()
userDB = UsersModel(db.get_connection())
userDB.init_table()
foodDB = FoodModel(db.get_connection())
foodDB.init_table()
# print(userDB.get_all())
print(foodDB.get_all())
if __name__ == '__main__':
    app.run(port=8888, host='127.0.0.1')
