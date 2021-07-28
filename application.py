from __future__ import print_function

import os,sys

from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash
from helpers import apology, login_required, lookup, usd, validate

PR = file=sys.stdout

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/")
@login_required
def index():
    data = db.execute("""SELECT SUM(SHAREQTY) AS QTY,
    CAST(SUM(AMOUNT*SHAREQTY) AS FLOAT)/ CAST(SUM(SHAREQTY) AS FLOAT) AS PRICE,
    (CAST(SUM(AMOUNT*SHAREQTY) AS FLOAT)/ CAST(SUM(SHAREQTY) AS FLOAT) * SUM(SHAREQTY)) as TOTAL,
    SHARESYMBOL,
    SHARE
    FROM BUY B
    INNER JOIN USERS S ON S.ID = B.USERID
    WHERE S.ID = ?
    GROUP BY SHARESYMBOL;
    """, 1)
    #print(data,PR)
    totalshare = 0

    #FOR LOOP TO CHANGE AMOUNT FORMATTING AND GETTING TOTAL VALUE OF HOLINGS
    for d in data:
        totalshare = totalshare + d["TOTAL"]
        d["PRICE"]=usd(d["PRICE"])
        d["TOTAL"]=usd(d["TOTAL"])

    balance = db.execute("SELECT CASH FROM USERS where id = ?", 1)
    print(balance,PR)
    #HOLDINGS + CASH
    grandtotal = usd((balance[0]['cash']) + totalshare)
    balance = usd(balance[0]['cash'])


    return render_template("index.html",data=data,balance=balance,grandtotal=grandtotal)
    """Show portfolio of stocks"""
    #return apology("TODO")


@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    if request.method == "POST":
        method = 'post'
        share = lookup(request.form.get("symbol"))
        if not share:
            return apology("invald symbol")
        qty = int(request.form.get("share"))

        if qty <= 0:
            return apology("insert positive number")

        tamount = (share["price"] * qty)
        print(session["user_id"],PR)
        #check balance
        cash = db.execute("select cash from users where id = ?", session["user_id"])
        #print(balance[0]['cash'],PR)
        balance = cash[0]['cash']
        #print(type(balance),PR)
        if balance < tamount:
            return apology("you do not have enough money")

        #update balance
        balance = balance - tamount
        db.execute("update users set cash = ? where id = ?", balance, session["user_id"])

        #insert record into BUY table
        db.execute("insert into BUY (TRANDATE,AMOUNT,SHAREQTY,USERID,SHARE,SHARESYMBOL,ISSELL) values (datetime(),?,?,?,?,?,?)",
        share["price"],qty,session["user_id"],share["name"],share["symbol"],0)

        return redirect("/")

    elif request.method == 'GET':
        method='get'
        return render_template("buy.html", method=method)
    """Buy shares of stock"""
    return apology("TODO")


@app.route("/history")
@login_required
def history():
    data = db.execute(""" SELECT SHARE,
                            SHARESYMBOL,
                            SHAREQTY,
                            CASE WHEN ISSELL = 0 THEN 'BUY' ELSE 'SELL' END AS TRANSACTIONTYPE,
                            AMOUNT,
                            TRANDATE
                            FROM BUY
                            WHERE USERID = ?
                            ORDER BY TRANDATE DESC;
                            """, session["user_id"])
    """Show history of transactions"""

    for d in data:
        d["AMOUNT"] = usd(d["AMOUNT"])

    print(data,PR)

    return render_template("history.html",data=data)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    if request.method == "GET":
        method='get'
        return render_template("quote.html",method=method)

    elif request.method == "POST":
        method = 'post'
        share = lookup(request.form.get("symbol"))
        if not share:
            return apology("TODO invald symbol")
        amount=usd(share["price"])
        return render_template("quote.html",share=share,method=method,amount=amount)
    """Get stock quote."""
    return apology("TODO")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    elif request.method == "POST":
        username = request.form.get("username")
        if not username:
            return apology("Blank User Name is invalid", 404)
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        elif validate(request.form.get("password")) != 0:
            return apology(validate(request.form.get("password")), 403)
        else:
            validation = db.execute("select 1 from users where username =:username",username=username)
            #print(f"validation = {validation}", file=sys.stderr)
            #print('This is standard output', file=sys.stdout)
        if validation == 1:
            return apology("USER NAME EXISTS, SELECT A DIFFERENT USERNAME",405)

        if request.form.get("password") != request.form.get("confirmation"):
            return apology("password do not match",500)

        # Hashing the password
        hashpassword = generate_password_hash(request.form.get("password"),method='pbkdf2:sha256', salt_length=8)

        # Insert into table
        db.execute("insert into users (username,hash) values (?,?)",username, hashpassword)
        print(f"hash passowrd = {hashpassword} ",PR)

        return redirect("/")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    if request.method == 'POST':
        symbol = request.form.get("symbol")
        qty = request.form.get("shares")
        share = db.execute("select sum(shareqty) as qty from buy where sharesymbol = ? and userid = ?", symbol,session["user_id"])


        #check if user has enough share
        if int(share[0]["qty"])-int(qty) < 0:
            return apology("you do not have enough shares to sell")


        #SELL TRANSACTION STARTS HERE

        #get the latest rates
        latest=lookup(symbol)

        #INSERT INTO SELL
        db.execute(""" INSERT INTO SELL
                        (TRANDATE,SELLPRICE,SHAREQTY,USERID,SHARE,SHARESYMBOL) VALUES
                        (DATETIME(),?,?,?,?,?)""",latest["price"],qty,session["user_id"],latest["name"],latest["symbol"])


       #INSERT INTO BUY
        negativeqty = -1 * int(qty)
        print(f"negativeqty{negativeqty}",PR)
        db.execute(""" INSERT INTO BUY
                        (TRANDATE,AMOUNT,SHAREQTY,USERID,SHARE,SHARESYMBOL,ISSELL) VALUES
                        (DATETIME(),?,?,?,?,?,1)""", latest["price"],negativeqty,session["user_id"],latest["name"],latest["symbol"])

        #UPDATE CASH
        cash = db.execute("select cash from users where id = ?", session["user_id"])
        balance = float(cash[0]['cash']) + (float(latest["price"]) * float(qty))
        db.execute("UPDATE USERS SET CASH = ? WHERE ID = ?",balance, session["user_id"])


        return redirect("/")
    symbols = db.execute("select distinct sharesymbol from buy where issell <> 1 and userid = ?", session["user_id"])
    #print(symbols,PR)
    return render_template("sell.html",symbols=symbols)

    """Sell shares of stock"""


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
