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

    def delete(self, id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM food WHERE id = ?''', (str(id),))
        cursor.close()
        self.connection.commit()

    def get(self, food_id):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM food WHERE id = ?", (str(food_id),))
        row = cursor.fetchone()
        return row

    def get_type(self, type):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM food WHERE food_type = ?", (str(type),))
        row = cursor.fetchall()
        return row

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM food")
        rows = cursor.fetchall()
        return rows


class Zacaz:
    def __init__(self, connection):
        self.connection = connection

    def init_table(self):
        cursor = self.connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS zacaz 
                            (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                             foods VARCHAR(1000),
                             address VARCHAR(100),
                             telephone_number VARCHAR(20),
                             sum INTEGER
                             )''')
        cursor.close()
        self.connection.commit()

    def insert(self, foods, address, telephone_number, sum):
        cursor = self.connection.cursor()
        cursor.execute('''INSERT INTO food 
                          (foods, address, telephone_number, sum) 
                          VALUES (?,?,?,?)''', (foods, address, telephone_number, sum))
        cursor.close()
        self.connection.commit()

    def delete(self, id):
        cursor = self.connection.cursor()
        cursor.execute('''DELETE FROM zacaz WHERE id = ?''', (str(id),))
        cursor.close()
        self.connection.commit()

    def get_all(self):
        cursor = self.connection.cursor()
        cursor.execute("SELECT * FROM zacaz")
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


class AddFoodBasketForm(FlaskForm):
    kolvo = IntegerField('Количество', validators=[DataRequired()])
    submit = SubmitField('Готово')


def basketToList(basketstr):
    l1 = basketstr.split(' шт; ')
    l1 = l1[0:-1]
    l2 = [s.split(" : ") for s in l1]
    l3 = [[foodDB.get(int(s[0])), s[1]] for s in l2]
    return l3


def basketToStr(basketlist):
    s = ''
    for z in basketlist:
        s += str(z[0][0]) + " : " + str(z[1]) + ' шт; '
    return s


def deliteBasket(id):
    basket = basketToList(session['basket'])
    for i in range(len(basket)):
        print (basket[i][0][0])
        print(id)
        print(" ")
        if basket[i][0][0] == int(id):
            del basket[i]
            session['basket'] = basketToStr(basket)
            break


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


@app.route('/show_food/<type>')
def showFoodFunc(type):
    return render_template('show_food.html', title='меню', food=foodDB.get_type(type))


@app.route('/delete_food/<id>')
def deleteFoodFunc(id):
    foodDB.delete(id)
    return '<script>document.location.href = document.referrer</script>'


@app.route('/add_food_basket/<id>', methods=['GET', 'POST'])
def addFoodBasketFunk(id):
    form = AddFoodBasketForm()
    if form.validate_on_submit():
        if not 'basket' in session:
            session['basket'] = ''
        deliteBasket(id)
        session['basket'] += str(id) + ' : ' + str(form.kolvo.data) + ' шт; '
        print(session['basket'])
        return redirect('/')
    return render_template('add_food_basket.html', title='Добавление товара', form=form, food=foodDB.get(id))


@app.route('/show_food_basket')
def showFoodBasketFunc():
    return render_template('show_food_basket.html', title='меню', food=basketToList(session['basket']))

@app.route('/delete_food_basket/<id>')
def deleteFoodBasketFunc(id):
    deliteBasket(id)
    print(session['basket'])
    return redirect('/show_food_basket')




db = DB()
userDB = UsersModel(db.get_connection())
userDB.init_table()
foodDB = FoodModel(db.get_connection())
foodDB.init_table()
# print(userDB.get_all())
print(foodDB.get_type("Суши"))
if __name__ == '__main__':
    app.run(port=8088, host='127.0.0.1')
