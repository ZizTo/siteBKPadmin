from flask import Flask, render_template, redirect, url_for, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired
import firebase_admin
from firebase_admin import db, credentials, firestore
from flask_login import LoginManager, UserMixin, login_user, logout_user, current_user, login_required
from app import app
from datetime import datetime, timedelta
import calendar
from dateutil.relativedelta import relativedelta


cred = credentials.Certificate("transport-aa61a-firebase-adminsdk-o5xvm-06d1ad449e.json")
firebase_admin.initialize_app(cred, {"databaseURL": "https://transport-aa61a-default-rtdb.firebaseio.com/"})



login_manager = LoginManager()
login_manager.init_app(app)


class User(UserMixin):
    def __init__(self, user_id, username):
        self.id = user_id
        self.username = username

@login_manager.user_loader
def load_user(user_id):
    username = db.reference(f"/Users/{user_id}").get()
    if username:
        user = User(user_id=user_id, username=db.reference(f"/AdminUsers/{username}/FirstName").get())
        return user
    return None

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()], render_kw={'class': 'u-input u-input-rectangle u-label u-form-group u-form-name', 'placeholder': "Введите логин"})
    password = PasswordField('Пароль', validators=[DataRequired()], render_kw={'class': 'u-input u-input-rectangle u-label u-form-group', 'placeholder': "Введите пароль"})
    submit = SubmitField('Войти',render_kw={'class':'u-btn u-btn-submit u-button-style u-btn-1'})

@app.route('/')
def ifLoggedRedirect():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    else:
        return render_template('Главная.html', form=LoginForm())

@app.route('/', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = db.reference(f"/AdminUsers/{form.username.data}").get()
        if username != None and db.reference(f"/AdminUsers/{form.username.data}/password").get() == form.password.data:
            if db.reference(f"/AdminUsers/{form.username.data}/id").get() == None:
                user_id = db.reference("/Users/kol").get()
                db.reference("/Users/kol").set(user_id + 1)
                db.reference(f"/Users/{user_id}").set(form.username.data)
                db.reference(f"/AdminUsers/{form.username.data}/id").set(user_id)
            else:
                user_id = db.reference(f"/AdminUsers/{form.username.data}/id").get()
            user = User(user_id=user_id, username=form.username.data)
            login_user(user)
            return redirect(url_for('dashboard'))
        else:
            flash('Неправильное имя пользователя или пароль', 'error')
    return render_template('Главная.html', form=form)

class ChoiceForm(FlaskForm):
    choice0 = SelectField(name='choiceee',choices=[('0', ' '), ('1', 'РБ'), ('2', 'РФ'), ('3', 'РЕФ'), ('4', 'ADR'), ('5', '0,5')])
    choice1 = SelectField(name='choiceee',choices=[('0', ' '), ('1', 'РБ'), ('2', 'РФ'), ('3', 'РЕФ'), ('4', 'ADR'), ('5', '0,5')])
    choice2 = SelectField(name='choiceee',choices=[('0', ' '), ('1', 'РБ'), ('2', 'РФ'), ('3', 'РЕФ'), ('4', 'ADR'), ('5', '0,5')])
    choice4 = SelectField(name='choiceee',choices=[('0', ' '), ('1', 'РБ'), ('2', 'РФ'), ('3', 'РЕФ'), ('4', 'ADR'), ('5', '0,5')])
    choice5 = SelectField(name='choiceee',choices=[('0', ' '), ('1', 'РБ'), ('2', 'РФ'), ('3', 'РЕФ'), ('4', 'ADR'), ('5', '0,5')])
    choice3 = SelectField(name='choiceee',choices=[('0', ' '), ('1', 'РБ'), ('2', 'РФ'), ('3', 'РЕФ'), ('4', 'ADR'), ('5', '0,5')])

    nameInp = StringField(name='nameInput')
    telInp = StringField(name='telInput')

    RBstr = StringField(name='RB')
    RFstr = StringField(name='RF')
    REFstr = StringField(name='REF')
    ADRstr = StringField(name='ADR')
    Halfstr = StringField(name='Half')

    monthchoice = SelectField(name='monthch',choices=[('01', 'январь'), ('02', 'февраль'), ('03', 'март'), ('04', 'апрель'),
                                                      ('05', 'май'), ('06', 'июнь'), ('07', 'июль'), ('08', 'август'),
                                                      ('09', 'сентябрь'), ('10', 'октябрь'), ('11', 'ноябрь'), ('12', 'декабрь')])
    choicesyear = []
    for i in range(2023, datetime.now().year + 1):
        choicesyear.append((f'{i}', f'{i}'))
    print(choicesyear)
    yearch = SelectField(name='yearch', choices=choicesyear)

def dashboardInit(month, year, sort):
    drivers = db.reference('/Driver').get()
    Costs = db.reference('/Cost').get()

    dateweek = []
    for i in range(0, calendar.monthrange(int(year), int(month))[1]):
        dateweek.append(datetime(int(year), int(month), int(i+1)).strftime('%Y-%m-%d'))
    dateweekname = []
    for i in range(0, len(dateweek)):
        dateweekname.append(str(int(f'{dateweek[i][8]}{dateweek[i][9]}')))

    workDays = {}
    fullInfoDays = {}

    for i in range(1, len(drivers)):
        kolWorkDays = 0
        kolRBDays = 0
        kolRFDays = 0
        kolREFDays = 0
        kolADRDays = 0
        kolHalfDays = 0
        for date in dateweek:
            try:
                if drivers[str(i)]['state'][str(date)] != 0:
                    kolWorkDays += 1
                    if drivers[str(i)]['state'][str(date)] == 1 or drivers[str(i)]['state'][str(date)] == 11:
                        kolRBDays += 1
                    if drivers[str(i)]['state'][str(date)] == 2 or drivers[str(i)]['state'][str(date)] == 12:
                        kolRFDays += 1
                    if drivers[str(i)]['state'][str(date)] == 3 or drivers[str(i)]['state'][str(date)] == 13:
                        kolREFDays += 1
                    if drivers[str(i)]['state'][str(date)] == 4 or drivers[str(i)]['state'][str(date)] == 14:
                        kolADRDays += 1
                    if drivers[str(i)]['state'][str(date)] == 5 or drivers[str(i)]['state'][str(date)] == 15:
                        kolHalfDays += 1
            except:
                pass
        workDays[str(i)] = kolWorkDays
        fullInfoDays[str(i)] = {}
        fullInfoDays[str(i)]['RB'] = kolRBDays
        fullInfoDays[str(i)]['RF'] = kolRFDays
        fullInfoDays[str(i)]['REF'] = kolREFDays
        fullInfoDays[str(i)]['ADR'] = kolADRDays
        fullInfoDays[str(i)]['Half'] = kolHalfDays
        fullInfoDays[str(i)]['Money'] = kolRBDays * Costs['RB'] + kolRFDays * Costs['RF'] + kolREFDays * Costs['REF'] \
                                        + kolADRDays * Costs['ADR'] + kolHalfDays * Costs['Half']

    inraceDay = []
    for dat in dateweek:
        kolinrace = 0
        for i in range(1, len(drivers)):
            try:
                if drivers[str(i)]['state'][str(dat)] != 0:
                    kolinrace += 1
            except:
                pass
        inraceDay.append(kolinrace)
    allkolrace = 0
    for race in inraceDay:
        allkolrace += race

    kolRBDays = 0
    kolRFDays = 0
    kolREFDays = 0
    kolADRDays = 0
    kolHalfDays = 0
    allMoney = 0
    for id in fullInfoDays:
        kolRBDays += fullInfoDays[id]['RB']
        kolRFDays += fullInfoDays[id]['RF']
        kolREFDays += fullInfoDays[id]['REF']
        kolADRDays += fullInfoDays[id]['ADR']
        kolHalfDays += fullInfoDays[id]['Half']
        allMoney += fullInfoDays[id]['Money']
    inraceDay.append(kolRBDays)
    inraceDay.append(kolRFDays)
    inraceDay.append(kolREFDays)
    inraceDay.append(kolADRDays)
    inraceDay.append(kolHalfDays)
    inraceDay.append(allMoney)


    return render_template('Dashboard.html', drivers=drivers, dateweek=dateweek, inraceDay=inraceDay,
                           form=ChoiceForm(choice0=0, choice1=1, choice3=3, choice4=4, choice2=2, choice5=5,
                                           monthchoice=month, yearch=year),
                           workDays=workDays, dateweekname=dateweekname, fullInfoDays=fullInfoDays,
                           monthchoosed=month, yearchoosed=year, costs=Costs, allkolrace=allkolrace,
                           sortchoosed = sort)


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    try:
        month = request.args['month']
        year = request.args['year']
    except:
        if datetime.now().month < 10:
            month = f'0{datetime.now().month}'
        else:
            month = f'{datetime.now().month}'
        year = str(datetime.now().year)
    try:
        sort = request.args['sort']
    except:
        sort = 1

    return dashboardInit(month, year, sort)

@app.route('/update_choice', methods=['POST'])
def update_choice():
    driver_day_id = request.form['driverDayId']
    choice_value = request.form['choiceee']

    i = 0
    id = 0
    while driver_day_id[i] != '-':
        id *= 10
        id += int(driver_day_id[i])
        i+=1
    print(id)
    i+=1
    date = driver_day_id[i:len(driver_day_id)]

    db.reference(f"/Driver/{id}/state/{date}").set(int(choice_value))

    monthch = str(request.form['monthchoosed'])
    yearch = str(request.form['yearchoosed'])
    sortch = request.form['sortchoosed']
    if int(monthch) == datetime.now().month and int(yearch) == datetime.now().year:
        if sortch == '1':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard', sort=sortch))
    else:
        if sortch == '1':
            return redirect(url_for('dashboard', month=monthch, year=yearch))
        else:
            return redirect(url_for('dashboard', month=monthch, year=yearch, sort=sortch))

@app.route('/new_name', methods=['POST'])
def new_name():
    newName = request.form['nameInput']
    id = request.form['driverId']

    db.reference(f"/Driver/{id}/Name").set(newName)

    monthch = str(request.form['monthchoosed'])
    yearch = str(request.form['yearchoosed'])
    sortch = request.form['sortchoosed']
    if int(monthch) == datetime.now().month and int(yearch) == datetime.now().year:
        if sortch == '1':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard', sort=sortch))
    else:
        if sortch == '1':
            return redirect(url_for('dashboard', month=monthch, year=yearch))
        else:
            return redirect(url_for('dashboard', month=monthch, year=yearch, sort=sortch))

@app.route('/new_tel', methods=['POST'])
def new_tel():
    newTel = request.form['telInput']
    id = request.form['driverId']

    db.reference(f"/Driver/{id}/Tel").set(newTel)

    monthch = str(request.form['monthchoosed'])
    yearch = str(request.form['yearchoosed'])
    sortch = request.form['sortchoosed']
    if int(monthch) == datetime.now().month and int(yearch) == datetime.now().year:
        if sortch == '1':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard', sort=sortch))
    else:
        if sortch == '1':
            return redirect(url_for('dashboard', month=monthch, year=yearch))
        else:
            return redirect(url_for('dashboard', month=monthch, year=yearch, sort=sortch))

@app.route('/newCosts', methods=['POST'])
def newCosts():
    Cost = {}
    Cost['RB'] = int(request.form['RB'])
    Cost['RF'] = int(request.form['RF'])
    Cost['REF'] = int(request.form['REF'])
    Cost['ADR'] = int(request.form['ADR'])
    Cost['Half'] = int(request.form['Half'])

    db.reference(f"/Cost").set(Cost)

    monthch = str(request.form['monthchoosed'])
    yearch = str(request.form['yearchoosed'])
    sortch = request.form['sortchoosed']
    if int(monthch) == datetime.now().month and int(yearch) == datetime.now().year:
        if sortch == '1':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard', sort=sortch))
    else:
        if sortch == '1':
            return redirect(url_for('dashboard', month=monthch, year=yearch))
        else:
            return redirect(url_for('dashboard', month=monthch, year=yearch, sort=sortch))

@app.route('/addUser', methods=['POST'])
def addUser():
    datetoday = datetime.today().date().strftime('%Y-%m-%d')

    kol = db.reference(f'/Driver/kol').get()
    kolallid = db.reference(f'/Driver/kolallid').get()
    kol += 1
    kolallid += 1
    db.reference(f'/Driver/kol').set(kol)
    db.reference(f'/Driver/kolallid').set(kolallid)
    db.reference(f'/Driver/{kol}/Name').set('Name')
    db.reference(f'/Driver/{kol}/Tel').set('375001112233')
    db.reference(f'/Driver/{kol}/state/{datetoday}').set(0)
    db.reference(f'/Driver/{kol}/allid').set(kolallid)
    db.reference(f'/Driver/{kol}/OnJobFrom').set(datetoday)

    monthch = str(request.form['monthchoosed'])
    yearch = str(request.form['yearchoosed'])
    sortch = request.form['sortchoosed']
    if int(monthch) == datetime.now().month and int(yearch) == datetime.now().year:
        if sortch == '1':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard', sort=sortch))
    else:
        if sortch == '1':
            return redirect(url_for('dashboard', month=monthch, year=yearch))
        else:
            return redirect(url_for('dashboard', month=monthch, year=yearch, sort=sortch))

@app.route('/delUser', methods=['POST'])
def delUser():
    id = int(request.form['driverId'])
    driver = db.reference('/Driver').get()
    archive = db.reference('/Archive').get()
    changes = db.reference('/Changes').get()

    archive[str(archive['kol'] + 1)] = driver[str(id)]
    archive['kol'] += 1
    try:
        del changes[str(driver[str(id)]['allid'])]
    except:
        pass

    changes[str(driver[str(id)]['allid'])] = 'del'
    for i in range(id, driver['kol']):
        try:
            changes[str(driver[str(i+1)]['allid'])] -= 1
        except:
            changes[str(driver[str(i+1)]['allid'])] = i
        driver[str(i)] = driver[str(i + 1)]


    del driver[str(driver['kol'])]
    driver['kol'] = driver['kol'] - 1

    print(driver)

    db.reference('/Driver').set(driver)
    db.reference('/Archive').set(archive)
    db.reference('/Changes').set(changes)

    monthch = str(request.form['monthchoosed'])
    yearch = str(request.form['yearchoosed'])
    sortch = request.form['sortchoosed']
    if int(monthch) == datetime.now().month and int(yearch) == datetime.now().year:
        if sortch == '1':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard', sort=sortch))
    else:
        if sortch == '1':
            return redirect(url_for('dashboard', month=monthch, year=yearch))
        else:
            return redirect(url_for('dashboard', month=monthch, year=yearch, sort=sortch))

@app.route('/anotherDate', methods=['GET', 'POST'])
def anotherDate():
    month = request.form['monthch']
    year = request.form['yearch']

    sortch = request.form['sortchoosed']
    if int(month) == datetime.now().month and int(year) == datetime.now().year:
        if sortch == '1':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard', sort=sortch))
    else:
        if sortch == '1':
            return redirect(url_for('dashboard', month=month, year=year))
        else:
            return redirect(url_for('dashboard', month=month, year=year, sort=sortch))


@app.route('/sortByNumber', methods=['GET', 'POST'])
def sortByNumber():
    monthch = str(request.form['monthchoosed'])
    yearch = str(request.form['yearchoosed'])
    sortch = request.form['sortchoosed']

    if sortch == '1':
        sortch = '2'
    else:
        sortch = '1'


    if int(monthch) == datetime.now().month and int(yearch) == datetime.now().year:
        if sortch == '1':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard', sort=sortch))
    else:
        if sortch == '1':
            return redirect(url_for('dashboard', month=monthch, year=yearch))
        else:
            return redirect(url_for('dashboard', month=monthch, year=yearch, sort=sortch))

@app.route('/sortByName', methods=['GET', 'POST'])
def sortByName():
    monthch = str(request.form['monthchoosed'])
    yearch = str(request.form['yearchoosed'])
    sortch = request.form['sortchoosed']

    if sortch == '3':
        sortch = '4'
    else:
        sortch = '3'


    if int(monthch) == datetime.now().month and int(yearch) == datetime.now().year:
        if sortch == '1':
            return redirect(url_for('dashboard'))
        else:
            return redirect(url_for('dashboard', sort=sortch))
    else:
        if sortch == '1':
            return redirect(url_for('dashboard', month=monthch, year=yearch))
        else:
            return redirect(url_for('dashboard', month=monthch, year=yearch, sort=sortch))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

def archiveInit(month, year, sort):
    drivers = db.reference('/Archive').get()
    Costs = db.reference('/Cost').get()

    dateweek = []
    for i in range(0, calendar.monthrange(int(year), int(month))[1]):
        dateweek.append(datetime(int(year), int(month), int(i+1)).strftime('%Y-%m-%d'))
    dateweekname = []
    for i in range(0, len(dateweek)):
        dateweekname.append(str(int(f'{dateweek[i][8]}{dateweek[i][9]}')))

    workDays = {}
    fullInfoDays = {}

    for i in range(1, len(drivers)):
        kolWorkDays = 0
        kolRBDays = 0
        kolRFDays = 0
        kolREFDays = 0
        kolADRDays = 0
        kolHalfDays = 0
        for date in dateweek:
            try:
                if drivers[str(i)]['state'][str(date)] != 0:
                    kolWorkDays += 1
                    if drivers[str(i)]['state'][str(date)] == 1 or drivers[str(i)]['state'][str(date)] == 11:
                        kolRBDays += 1
                    if drivers[str(i)]['state'][str(date)] == 2 or drivers[str(i)]['state'][str(date)] == 12:
                        kolRFDays += 1
                    if drivers[str(i)]['state'][str(date)] == 3 or drivers[str(i)]['state'][str(date)] == 13:
                        kolREFDays += 1
                    if drivers[str(i)]['state'][str(date)] == 4 or drivers[str(i)]['state'][str(date)] == 14:
                        kolADRDays += 1
                    if drivers[str(i)]['state'][str(date)] == 5 or drivers[str(i)]['state'][str(date)] == 15:
                        kolHalfDays += 1
            except:
                pass
        workDays[str(i)] = kolWorkDays
        fullInfoDays[str(i)] = {}
        fullInfoDays[str(i)]['RB'] = kolRBDays
        fullInfoDays[str(i)]['RF'] = kolRFDays
        fullInfoDays[str(i)]['REF'] = kolREFDays
        fullInfoDays[str(i)]['ADR'] = kolADRDays
        fullInfoDays[str(i)]['Half'] = kolHalfDays
        fullInfoDays[str(i)]['Money'] = kolRBDays * Costs['RB'] + kolRFDays * Costs['RF'] + kolREFDays * Costs['REF'] \
                                        + kolADRDays * Costs['ADR'] + kolHalfDays * Costs['Half']

    inraceDay = []
    for dat in dateweek:
        kolinrace = 0
        for i in range(1, len(drivers)):
            try:
                if drivers[str(i)]['state'][str(dat)] != 0:
                    kolinrace += 1
            except:
                pass
        inraceDay.append(kolinrace)
    allkolrace = 0
    for race in inraceDay:
        allkolrace += race

    kolRBDays = 0
    kolRFDays = 0
    kolREFDays = 0
    kolADRDays = 0
    kolHalfDays = 0
    allMoney = 0
    for id in fullInfoDays:
        kolRBDays += fullInfoDays[id]['RB']
        kolRFDays += fullInfoDays[id]['RF']
        kolREFDays += fullInfoDays[id]['REF']
        kolADRDays += fullInfoDays[id]['ADR']
        kolHalfDays += fullInfoDays[id]['Half']
        allMoney += fullInfoDays[id]['Money']
    inraceDay.append(kolRBDays)
    inraceDay.append(kolRFDays)
    inraceDay.append(kolREFDays)
    inraceDay.append(kolADRDays)
    inraceDay.append(kolHalfDays)
    inraceDay.append(allMoney)


    return render_template('Archive.html', drivers=drivers, dateweek=dateweek, inraceDay=inraceDay,
                           form=ChoiceForm(choice0=0, choice1=1, choice3=3, choice4=4, choice2=2, choice5=5,
                                           monthchoice=month, yearch=year),
                           workDays=workDays, dateweekname=dateweekname, fullInfoDays=fullInfoDays,
                           monthchoosed=month, yearchoosed=year, costs=Costs, allkolrace=allkolrace,
                           sortchoosed = sort)


@app.route('/archive')
@login_required
def archive():
    try:
        month = request.args['month']
        year = request.args['year']
    except:
        if datetime.now().month < 10:
            month = f'0{datetime.now().month}'
        else:
            month = f'{datetime.now().month}'
        year = str(datetime.now().year)
    try:
        sort = request.args['sort']
    except:
        sort = 1

    return archiveInit(month, year, sort)

@app.route('/anotherDateArch', methods=['GET', 'POST'])
def anotherDateArch():
    month = request.form['monthch']
    year = request.form['yearch']

    sortch = request.form['sortchoosed']
    if int(month) == datetime.now().month and int(year) == datetime.now().year:
        if sortch == '1':
            return redirect(url_for('archive'))
        else:
            return redirect(url_for('archive', sort=sortch))
    else:
        if sortch == '1':
            return redirect(url_for('archive', month=month, year=year))
        else:
            return redirect(url_for('archive', month=month, year=year, sort=sortch))



