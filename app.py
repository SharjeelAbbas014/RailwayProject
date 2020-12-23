import re
from flask import Flask, render_template,request,jsonify,json,session
app = Flask(__name__)
app.secret_key = "jf3j98j4jfowijf98"

@app.route('/')
def index():
    if session.get("email") == None:
        return render_template("index.html")
    else:
        return render_template("Success.html", message="Login Successful")
    

@app.route('/signup',methods=["POST","GET"])
def signup():
    if(request.method == "POST"):
        return "Account Created Sucessfully"
    else:
        return render_template("Success.html", message="Account Created Sucessfully")

@app.route('/signin',methods=["POST","GET"])
def login():
    if request.method == "POST":
        return ""
    else:
        if session.get("email") == None:
            return render_template("index.html")
        else:
            return render_template("Success.html", message="Login Successful")

@app.route('/logout',methods=["GET"])
def logout():
    session.clear()
    return render_template("index.html")
    
if __name__ == "__main__":
    app.debug = True
    app.run()