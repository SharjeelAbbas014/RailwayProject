import smtplib
from operator import itemgetter
from datetime import datetime
from flask import Flask, render_template, request, jsonify, json, session, redirect, url_for
from DBHandler import DBHandler
from authlib.integrations.flask_client import OAuth
import json
import stripe

HOST = 'localhost'
USER = 'root'
PWD = ''
DBNAME = 'railway'
YOUR_DOMAIN = 'http://127.0.0.1:5000'
app = Flask(__name__)

oauth = OAuth(app)
google = oauth.register(
    name='google',
    client_id="956018769459-v7vhg7aod95g1m18785a2eefnrvdvrbc.apps.googleusercontent.com",
    client_secret="S7n8MSmX93eHnOIqtg8ppik_",
    access_token_url='https://accounts.google.com/o/oauth2/token',
    access_token_params=None,
    authorize_url='https://accounts.google.com/o/oauth2/auth',
    authorize_params=None,
    api_base_url='https://www.googleapis.com/oauth2/v1/',
    # This is only needed if using openId to fetch user info
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    client_kwargs={'scope': 'openid email profile'},
)
app.secret_key = "jf3j98j4jfowijf98"
stripe.api_key = 'sk_test_51I1U9bLxCWtLRhQtx7wtMLdfyPb2N1jCYshldNsibfJdoO3xZQ7PKhep2pJGPtmtg5ysDcPfGd8CV6XMxazRc4OB00iBlfF2kJ'

adminUsername = "BITF18M"
adminPassword = "web12345"


@app.route('/')
def Home():
    session["sid"] = ""
    session["method"] = ""
    session["not"] = ""
    db = DBHandler(HOST, USER, PWD, DBNAME)
    res = db.getStations()
    return render_template("index.html", sched=json.dumps(res))


@app.route('/admin')
def adminPanel():
    if session.get("admin") is not None:
        db = DBHandler("localhost", "root", "", "railway")
        res = db.getStations()
        emp = db.getEmps()
        pie = db.getDataForPieChart()
        lineChart = db.getDataForLineChart()
        lineGraph = []
        for d in lineChart.keys():
            lineGraph.append({"date": d, "quant": lineChart[d]})
        res.sort(key=itemgetter('TrainName'))
        return render_template("showDetailsToAdmin.html", res=res, emp=emp,lineGraph=lineGraph,pie=pie)
        render_template('showDetailsToAdmin.html')
    else:
        return render_template("adminlogin.html")


@app.route('/editSchedTrain', methods=["POST", "GET"])
def editSchedTrain():
    if (request.args.get("schedid") != None or request.method == 'POST'):
        dbObj = DBHandler("localhost", "root", "", "railway")
        if (request.method == "GET"):
            sid = request.args.get("schedid")
            sched = dbObj.getSingleSched(sid)
            passengers = dbObj.getPassengers(sid)
            employees = dbObj.getEmployees(sid)
            employeeTrain = dbObj.getEmployeesToAdd(sid)
            return render_template("editSchedTrain.html", employeeTrain=employeeTrain, sched=sched,
                                   passengers=passengers, employees=employees)
        else:
            sid = request.form.get("schedId")
            dbObj.editSched(request.form)
            return redirect(url_for("editSchedTrain") + '?schedid=' + str(sid))
    else:
        return redirect('/admin')


@app.route('/deleteEmpFromTrain')
def deleteEmpFromTrain():
    sid = request.args.get("sid")
    eid = request.args.get("eid")
    dbObj = DBHandler("localhost", "root", "", "railway")
    dbObj.deleteEmpSched(eid, sid)

    return redirect(url_for("editSchedTrain") + '?schedid=' + str(sid))


@app.route('/addEmpToTrain', methods=["POST", "GET"])
def addEmpToTrain():
    if request.method == "POST":
        sid = request.form.get("schedId")
        empTrain = request.form.get("empTrain")
        eid = empTrain[0:empTrain.find(' ')]
        dbObj = DBHandler("localhost", "root", "", "railway")
        dbObj.addEmployToSched(eid, sid)
        return redirect(url_for("editSchedTrain") + '?schedid=' + str(sid))
    else:
        return redirect('/admin')


@app.route('/addTrain', methods=["POST"])
def addTrain():
    dbObj = DBHandler("localhost", "root", "", "railway")
    if dbObj.addTrain(request.get_json(force=True)["trainName"]):
        return "added"
    return "already"


@app.route('/addEmployee', methods=["POST"])
def addEmployee():
    dbObj = DBHandler("localhost", "root", "", "railway")
    res = dbObj.addEmployee(request.get_json(force=True))
    if res == False:
        return "already"
    return json.dumps(res)


@app.route('/addSched', methods=["POST"])
def addSched():
    dbObj = DBHandler("localhost", "root", "", "railway")
    if dbObj.addSched(request.get_json(force=True)):
        return "added"
    return "already"


@app.route('/login', methods=['POST', 'GET'])
def login():
    obj = DBHandler("localhost", "root", "", "railway")
    if request.method == "POST":
        user = request.form['user']
        pw = request.form['pw']
        auth = obj.getAuth(user, pw)

        if auth != None:
            session.permanent = True
            session['auth'] = auth
            if auth['role'] == 'P':
                psnger = obj.getPassenger(auth['authID'])
                session['pid'] = psnger['PID']
                if session.get("not") != None and session.get("not") != "":
                    return redirect(url_for('bookTicket'))
                return redirect(url_for('dashboard'))
            elif auth['role'] == 'A' or auth['role'] == 'a':
                session["admin"] = auth['username']
                return redirect(url_for("adminPanel"))
            else:
                return redirect(url_for('employee'))
    else:
        if 'auth' in session:
            auth = session['auth']
            if auth != None:
                if auth['role'] == 'P':
                    psnger = obj.getPassenger(auth['authID'])
                    session['pid'] = psnger['PID']
                    if session.get("not") != None and session.get("not") != "":
                        return redirect(url_for('bookTicket'))
                    return redirect(url_for('dashboard'))
                else:
                    return redirect(url_for('employee'))

    return render_template("login.html")


@app.route('/signUp', methods=['POST', 'GET'])
def signup():
    p = {}
    passenger = {}
    values = {}
    obj = DBHandler("localhost", "root", "", "railway")

    values['username'] = ""
    values['fname'] = ""
    values['lname'] = ""
    values['cnic'] = ""
    values['ph'] = ""
    values['pw'] = ""
    values['conPass'] = ""

    if request.method == "POST":
        user = request.form['user']
        pw = request.form['pw']
        conPass = request.form['conPass']
        if pw != conPass:
            err = "Password do not match"
            return render_template("signup.html", values=values)
        else:
            p['username'] = user
            p['password'] = pw
            p['role'] = "P"

            if obj.setAuth(p):

                passenger['fname'] = request.form['fname']
                passenger['lname'] = request.form['lname']
                passenger['cnic'] = request.form['cnic']
                passenger['ph'] = request.form['ph']

                authID = obj.getAuthId(user)
                passenger['authID'] = authID['authID']

                if obj.setPassenger(passenger):
                    auth = obj.getAuth(user, pw)
                    if auth != None:
                        session.permanent = True
                        session['auth'] = auth
                        return redirect(url_for('login'))

    elif "oauth" in session:
        person = session['oauth']

        values['username'] = person['user']
        values['fname'] = person['fname']
        values['lname'] = person['lname']
        values['pw'] = person['pw']
        values['conPass'] = person['pw']

        return render_template("signup.html", values=values)

    return render_template("signup.html", values=values)


@app.route('/createAccount', methods=["POST"])
def CreateNewAccount():
    abc = json.loads(request.data)
    username = abc["username"]
    firstName = abc["first"]
    lastName = abc["last"]
    CNICno = abc["CNIC"]
    PhoneNumber = abc["PhoneNumber"]
    password = abc["pass"]

    dbObj = DBHandler("localhost", "root", "", "railway")
    result = dbObj.insertRecord(username, firstName, lastName, CNICno, PhoneNumber, password)
    if result == False:
        return "False"
    else:
        session["pid"] = result
        return "True"


@app.route('/ticketDetail')
def ticketDetail():
    psnger = ''
    if request.args:
        if 'tkid' in request.args:
            tkid = int(request.args.get('tkid'))
            obj = DBHandler("localhost", "root", "", "railway")
            tks = obj.getSingleTicket(tkid)
            tmp = obj.getSchedule(tks['ScheduleID'])
            psnger = obj.getPassenger(session.get('auth').get('authID'))
            for k, v in tmp.items():
                tks[k] = v

            tmp = obj.getTrain(tks['TrainID'])
            for k, v in tmp.items():
                tks[k] = v

    tks["eLocLat"] = 24.8607
    tks["eLocLong"] = 67.0011
    tks["sLocLat"] = 31.5305
    tks["sLocLong"] = 74.3613
    print(tks)
    return render_template("ticketDetail.html", pDetail=psnger, tks=tks)


@app.route('/employee')
def employee():
    data = ""
    check = False

    if 'auth' in session:
        auth = session['auth']
        obj = DBHandler("localhost", "root", "", "railway")
        emp = obj.getEmployee(auth['authID'])
        if auth != None and emp != None:
            session['empid'] = emp['empid']

            data = obj.employeeTrains(emp['empid'])
            if data == "No Train Alloted":
                check = False
            else:
                check = True
        print(data)
        return render_template("employeeMenu.html", empData=data, check=check)

    return redirect(url_for('login'))


@app.route('/employeeMenu')
def employeeMenu():
    session["empID"] = 11
    if session.get("empID") != None:
        dbObj = DBHandler("localhost", "root", "", "railway")
        data = dbObj.employeeTrains(session.get("empID"))
        if data == "No Train Alloted":
            check = False
        else:
            check = True
        return render_template("employeeMenu.html", empData=data, check=check)
    else:
        return redirect(url_for('showLogin'))


@app.route('/googleLogin')
def googleLogin():
    redirect_uri = url_for('authorize', _external=True)
    google = oauth.create_client('google')
    return google.authorize_redirect(redirect_uri)


@app.route('/authorize')
def authorize():
    passenger = {}
    obj = DBHandler("localhost", "root", "", "railway")

    google = oauth.create_client('google')
    token = google.authorize_access_token()
    resp = google.get('userinfo')
    user_info = resp.json()
    user = oauth.google.userinfo()
    auth = obj.getAuth(user['email'], user['sub'])
    if auth == None:
        passenger['user'] = user['email']
        passenger['pw'] = user['sub']
        passenger['fname'] = user['given_name']
        passenger['lname'] = user['family_name']
        session['oauth'] = passenger
        return redirect(url_for('signup'))
    else:
        session.permanent = True
        session['auth'] = auth
        return redirect(url_for('login'))


@app.route("/sendMailTicket", methods=["POST"])
def sendMailTicket():
    try:
        ticketDetailsJson = request.get_json(force=True)
        receiverEmail = ticketDetailsJson["email"]
        s = smtplib.SMTP('smtp.gmail.com', 587)
        s.starttls()
        subject = "Your Ticket from " + ticketDetailsJson["From"] + " to " + ticketDetailsJson["To"]
        body = "Here's you ticket Details: \n Train Name: {} \n From: {} \n To: {} \n Time: {} \n Number of Tickets: {} \n Method: {} \n Total Dues: {} \n Class: {} \n Payable: {}".format(
            ticketDetailsJson["Train"], ticketDetailsJson["From"], ticketDetailsJson["To"], ticketDetailsJson["Time"],
            ticketDetailsJson["NumOfTick"], ticketDetailsJson["Method"], ticketDetailsJson["fee"], ticketDetailsJson["busOrEco"],
            ticketDetailsJson["RemainingP"])
        myEmail = "sharjeelabbas014@gmail.com"
        s.login("sharjeelabbas014@gmail.com", "tkpvyteorhiqacod")
        message = """From: %s\nTo: %s\nSubject: %s\n\n%s
            """ % (myEmail, ", ".join(receiverEmail), subject, body)
        s.sendmail(myEmail, receiverEmail, message)
        s.quit()
        return "sent"
    except Exception as e:
        print(str(e))
        return ""

@app.route('/dashboard')
def dashboard():
    obj = DBHandler("localhost", "root", "", "railway")

    if 'auth' in session:
        auth = session['auth']

        psnger = obj.getPassenger(auth['authID'])

        if auth != None and psnger != None:
            session['pid'] = psnger['PID']
            for k, v in auth.items():
                psnger[k] = v

            tks = obj.getTickets(psnger['PID'])
            if len(tks) > 0:
                for t in tks:
                    tmp = obj.getSchedule(t['ScheduleID'])
                    for k, v in tmp.items():
                        t[k] = v
                i = 1
                for t in tks:

                    t['no'] = i
                    i += 1
                    tmp = obj.getTrain(t['TrainID'])
                    for k, v in tmp.items():
                        t[k] = v
                    t['class'] = ""
                tks[0]['class'] = "active"

            return render_template("dashboard.html", psnger=psnger, tks=tks)

    return redirect(url_for('login'))

@app.route('/logout')
def logout():
    session.pop('auth', None)
    session.clear()
    return redirect(url_for('login'))


@app.route('/adminLoginRequest', methods=["POST"])
def AdminLogIn():
    username = request.form["username"]
    password = request.form["password"]

    if username == adminUsername and password == adminPassword:
        session["admin"] = username
        return redirect(url_for("adminPanel"))
    else:
        return render_template("adminlogin.html", message="Invalid Username or Password.")


@app.route('/showAllPassengers', methods=["POST"])
def showPassengers():
    SID = json.loads(request.data)

    session["scheduleID"] = SID
    return render_template("passengersToEmp.html")


@app.route('/showPassengersToEmp')
def showPassengersToEmp():
    SID = session["scheduleID"]
    db = DBHandler(HOST, USER, PWD, DBNAME)
    res = db.PasssengersWithCash(SID)
    if res == "No":
        check = False
    else:
        check = True
    return render_template("passengersToEmp.html", data=res, check=check)


@app.route('/traindetails')
def trainDetails():
    session["sid"] = ""
    session["method"] = ""
    session["not"] = ""
    db = DBHandler(HOST, USER, PWD, DBNAME)
    res = db.getStations()
    return render_template("trainDetails.html", sched=json.dumps(res))


ticketDetails = ""


@app.route('/paymentSelection', methods=["POST", "GET"])
def bookTicket():
    global ticketDetails
    print(session)
    if session.get('auth').get("role") == "E":
        session.clear()
    if request.method == "POST":
        ticketDetails = request.get_json(force=True)
        session["sid"] = ticketDetails["sid"]
        session["not"] = ticketDetails["numOfTickets"]
        session["busOrEco"] = ticketDetails["busOrEco"]
        det = ticketDetails["others"]
        if(session["busOrEco"] == "bus"):
            num = det[-4:]
            final = ""
            if num[0] == ":":
                final = det[0:-4]
                num = det[-3:]
                num = int(int(int(num) * 0.2) + int(num))
                final = final + " " + str(num)
            else:
                if num[0] == " ":
                    final = det[0:-5]
                    num = int(int(int(num) * 0.2) + int(num))
                    final = final + " " + str(num)
                else:
                    final = det[0:-5]
                    num = int(int(int(num) * 0.2) + int(num))
                    final = final + " " + str(num)
            ticketDetails["others"] = final
        print(ticketDetails["others"])
        if session.get("pid") is not None:
            return "GOTIT"
        return "LOGIN"
    else:
        if session.get("not") != None and session.get('not')!="":
            return render_template("paymentSelection.html")
        else:
            return redirect(url_for('Home'))


@app.route('/paywithmastercard')
def paywithmastercard():
    session["method"] = "Card"
    return render_template("paywithmastercard.html", ticketDetails=ticketDetails)


@app.route('/paywithjazzcash')
def paywithjazzcash():
    d = datetime.today()
    session["method"] = "Jazz"
    ticketDetails["date"] = str(d.second + d.minute + d.hour + d.day + d.month)
    fare = 0
    if ((ticketDetails["others"][-4:])[0] == ':'):
        fare = int(ticketDetails["others"][-3:])
    else:
        fare = int(ticketDetails["others"][-4:])
    return render_template("paywithjazzcash.html", ticketDetails=ticketDetails, fare=fare * int(session["not"]))


@app.route('/deleteEmp', methods=["POST"])
def deleteEmp():
    empid = request.get_json(force=True)["empId"]
    db = DBHandler("localhost", "root", "", "railway")
    if db.deleteEmp(empid):
        return "success"
    return "error"


@app.route('/editEmp', methods=["POST"])
def editEmp():
    emp = request.get_json(force=True)
    db = DBHandler("localhost", "root", "", "railway")
    if db.editEmp(emp):
        return "success"
    return "error"


@app.route('/success')
def masterSucc():
    db = DBHandler(HOST, USER, PWD, DBNAME)
    bookid = db.addTicket(session)
    return render_template('success.html', bookid=bookid)


@app.route('/jazzcashsuccess', methods=["POST", "GET"])
def jazzcashsuccess():
    db = DBHandler(HOST, USER, PWD, DBNAME)
    bookid = db.addTicket(session)
    return render_template('success.html', bookid=bookid)


@app.route('/showTicket', methods=["GET"])
def showTicket():
    ticketId = request.args.get("ticket")
    db = DBHandler(HOST, USER, PWD, DBNAME)
    res = db.getTicket(ticketId)
    return render_template("showTicket.html", ticket=res)


@app.route('/create-checkout-session', methods=["POST"])
def create_checkout_session():
    amm = 0
    if ((ticketDetails["others"][-4:])[0] == ':'):
        amm = int(ticketDetails["others"][-3:])
    else:
        amm = int(ticketDetails["others"][-4:])
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'pkr',
                        'unit_amount': amm * 100,
                        'product_data': {
                            'name': ticketDetails["others"],
                        },
                    },
                    'quantity': int(ticketDetails["numOfTickets"]),
                },
            ],
            mode='payment',
            success_url=YOUR_DOMAIN + '/success',
            cancel_url=YOUR_DOMAIN + '/cancel',
        )
        return jsonify({'id': checkout_session.id})
    except Exception as e:
        print(str(e))
        return jsonify(error=str(e)), 403
