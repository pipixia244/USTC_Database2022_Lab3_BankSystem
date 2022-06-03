from locale import currency
from pydoc import cli
from sqlite3 import SQLITE_DROP_TABLE
from flask import Flask, jsonify, make_response, request, redirect, session, render_template
import os
import sys
import datetime
import json
import hashlib
import jsonschema
import pymysql
import pandas
import copy

app = Flask(__name__)
app.secret_key = 'srprprpr@114514'

return_code_template = '''{
    200: Success
    302: Redirect
    400: Unknown error
    401: Not authorized
    402: Wrong password
    403: Forbidden
    404: Not found
    600: Some key cannot be empty
    601: Some key not exist
    602: SQL execution error
    603: Some key already exist
    604: Action not allowed
}

'''

return_json_template = '''{
    "code: "{code}"
    "error": "{error}",
    "{return_info_name}": {return_info_dict},
    
}'''

# 查询部分
@app.route("/api/v1/get/login", methods = ['GET'])
def login():
    username = request.args.get("username")
    hashkey = request.args.get("hashkey")
    print(username, hashkey)
    
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    
    SQL_LOGIN_SEARCH = f"select * from User where username = '{username}'"
    cursor.execute(SQL_LOGIN_SEARCH)
    
    data = cursor.fetchall()
    cursor.close()
    db.close()
    
    if not data:
        resp = make_response(jsonify(code=601, error="Username not exists.", username=username))
        #resp.set_cookie('ADMIN-TOKEN', 'error')
        return resp
    
    if data[0]['hashkey'] != hashkey:
        return jsonify(code=402, error="Wrong password.", username = username)
    else:
        session['username'] = username
        return jsonify(code=200, error="", username = username)
    
@app.route("/api/v1/get/list_user", methods = ['GET'])
def listuser():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    username = request.args.get("username")
    listall = request.args.get("listall")
    print(username, listall)
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)    
    if(listall == '1'):
        cursor.execute("Select * from User")
        userlist = cursor.fetchall()
        cursor.close()
        db.close()
        for user in userlist:
            user.pop('hashkey')
        print(userlist)
        print(type(userlist))
        return jsonify(code=200, error="", user_list=userlist, length=len(userlist))
    else:
        if(username == '' or username == None):
            cursor.execute("select * from User")
            userlist = cursor.fetchall()
            cursor.close()
            db.close()
            for user in userlist:
                user.pop('hashkey')
            return jsonify(code=200, error="", user_list=userlist, length=len(userlist))
        cursor.execute(f"select * from User where username like '%{username}%'")
        userlist = cursor.fetchall()
        cursor.close()
        db.close()
        for user in userlist:
            user.pop('hashkey')
        return jsonify(code=200, error="", user_list=userlist, length=len(userlist))
    
@app.route("/api/v1/get/list_depart", methods = ['GET'])
def list_depart():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("select * from Department")
    depart_list = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(code=200, error="", depart_list=depart_list, length=len(depart_list))

@app.route("/api/v1/get/list_bank", methods = ['GET'])
def list_bank():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("select * from Bank")
    bank_list = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(code=200, error="", bank_list=bank_list, length=len(bank_list))

@app.route("/api/v1/get/list_employ", methods = ['GET'])
def list_employ():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute("select * from Employee")
    employ_list = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(code=200, error="", employ_list=employ_list, length=len(employ_list))

@app.route("/api/v1/get/list_client", methods = ['GET'])
def list_client():
    SQL_LIST_CLIENT = "select Client.Client_ID, Client_Name, Client_Tel, Client_Address, Contact_Name, Contact_Email, Contact_Tel, Relation  from Client, Contact where Client.Client_ID = Contact.Client_ID;"
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(SQL_LIST_CLIENT)
    client_list = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(code=200, error="", client_list=client_list, length=len(client_list))

@app.route("/api/v1/get/list_account", methods = ['GET'])
def list_account():
    SQL_LIST_ACCOUNT = "select * from Account"
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(SQL_LIST_ACCOUNT)
    account_list = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(code=200, error="", account_list=account_list, length=len(account_list))

@app.route("/api/v1/get/list_own", methods = ['GET'])
def list_own():
    SQL_LIST_OWN = "select * from Own"
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(SQL_LIST_OWN)
    own_list = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(code=200, error="", own_list=own_list, length=len(own_list))

@app.route("/api/v1/get/list_checking", methods = ['GET'])
def list_checking():
    SQL_LIST_CHECKING = "select * from Checking_Account"
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(SQL_LIST_CHECKING)
    checking_list = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(code=200, error="", checking_list=checking_list, length=len(checking_list))

@app.route("/api/v1/get/list_saving", methods = ['GET'])
def list_saving():
    SQL_LIST_SAVING = "select * from Saving_Account"
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(SQL_LIST_SAVING)
    saving_list = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(code=200, error="", saving_list=saving_list, length=len(saving_list))

@app.route("/api/v1/get/list_loan", methods = ['GET'])
def list_loan():
    SQL_LIST_LOAN = "select * from Loan"
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(SQL_LIST_LOAN)
    loan_list = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(code=200, error="", loan_list=loan_list, length=len(loan_list))

@app.route("/api/v1/get/list_pay", methods = ['GET'])
def list_pay():
    SQL_LIST_PAY = "select * from Pay"
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    cursor.execute(SQL_LIST_PAY)
    pay_list = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(code=200, error="", pay_list=pay_list, length=len(pay_list))

@app.route("/api/v1/get/statistics", methods = ['GET'])
def statistics():
    def get_year(date):
        return str(date.year) + "年"

    def get_month(date):
        return str(date.year) + "年" + str(date.month) + "月"

    def get_quarter(date):
        return str(date.year) + "年第" + str(int((date.month - 1) / 3) + 1) + "季度"
    
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    
    SQL_SEARCH_ACCOUNT = f"select * from Account"
    SQL_SEARCH_LOAN = f"select * from Loan"
    
    cursor.execute(SQL_SEARCH_ACCOUNT)
    account_list = cursor.fetchall()
    cursor.execute(SQL_SEARCH_LOAN)
    loan_list = cursor.fetchall()
    
    cursor.close()
    db.close()
    
    bank_data = dict()
    loan_data = dict()
    
    bank_year = dict()
    bank_month = dict()
    bank_quer = dict()
    loan_year = dict()
    loan_month = dict()
    loan_quer = dict()
    
    list_year = list()
    list_month = list()
    list_quer = list()
    
    for account in account_list:
        if account['Bank_Name'] in bank_data.keys():
            bank_data[account['Bank_Name']].append({"date": account["Opening_Date"], "balance": account["Balance"]})
        else:
            bank_data[account["Bank_Name"]] = [{"date": account["Opening_Date"], "balance": account["Balance"]}]
    
    for loan in loan_list:
        if loan["Bank_Name"] in loan_data.keys():
            loan_data[loan["Bank_Name"]].append({"date": loan["Opening_Date"], "balance": loan["Loan_Amount"]})
        else:
            loan_data[loan["Bank_Name"]] = [{"date": loan["Opening_Date"], "balance": loan["Loan_Amount"]}]

    print(bank_data)
    
    for data in bank_data:
        list_year = bank_data[data]
        print(list_year)
        list_year = pandas.DataFrame(list_year)
        list_quer = copy.deepcopy(list_year)
        list_month = copy.deepcopy(list_year)
        print(list_year)
        print("------------------")
        #print(list_year["date"])
        #print(type(list_year["date"]))
        try:
            list_year["date"] = list_year["date"].apply(get_year)
            data_year = list_year.groupby('date').balance.apply(list).to_dict()
            for key in data_year.keys():
                data_year[key] = sum(data_year[key])
            bank_year[data] = data_year

            list_quer["date"] = list_quer["date"].apply(get_quarter)
            data_quer = list_quer.groupby('date').balance.apply(list).to_dict()
            for key in data_quer.keys():
                data_quer[key] = sum(data_quer[key])
            bank_quer[data] = data_quer

            list_month["date"] = list_month["date"].apply(get_month)
            date_month = list_month.groupby('date').balance.apply(list).to_dict()
            for key in date_month.keys():
                date_month[key] = sum(date_month[key])
            bank_month[data] = date_month
        except Exception as e:
            print(e)
            return jsonify(code=605, error="Time format or data not correct.")
    list_year = list()
    list_month = list()
    list_quer = list()
    
    try:
        for data in loan_data:
            list_year = loan_data[data]
            print(list_year)
            list_year = pandas.DataFrame(list_year)
            list_quer = copy.deepcopy(list_year)
            list_month = copy.deepcopy(list_year)
        
            list_year["date"] = list_year["date"].apply(get_year)
            data_year = list_year.groupby('date').balance.apply(list).to_dict()
            for key in data_year.keys():
                data_year[key] = sum(data_year[key])
            loan_year[data] = data_year

            list_quer["date"] = list_quer["date"].apply(get_quarter)
            data_quer = list_quer.groupby('date').balance.apply(list).to_dict()
            for key in data_quer.keys():
                data_quer[key] = sum(data_quer[key])
            loan_quer[data] = data_quer

            list_month["date"] = list_month["date"].apply(get_month)
            date_month = list_month.groupby('date').balance.apply(list).to_dict()
            for key in date_month.keys():
                date_month[key] = sum(date_month[key])
            loan_month[data] = date_month   
    except Exception as e:
        print(e)
        return jsonify(code=605, error="Time format or data not correct.")    
    return jsonify(code=200, error="", bank_year=bank_year, bank_quer=bank_quer, bank_month=bank_month, loan_year=loan_year, loan_quer=loan_quer, loan_month=loan_month, bank_data=bank_data, loan_data=loan_data) 
        
    
    

@app.route("/api/v1/get/search_client", methods = ['GET'])
def search_client():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    client_id = request.args.get("client_id")
    client_name = request.args.get("client_name")
    client_tel = request.args.get("client_tel")
    client_addr = request.args.get("client_addr")
    if not client_id:
        client_id = ""
    if not client_name:
        client_name = ""
    if not client_tel:
        client_tel = ""
    if not client_addr:
        client_addr = ""
        
    client_list = list()
    SQL_SEARCH_CLIENT = f"select Client.Client_ID, Client_Name, Client_Tel, Client_Address, Contact_Name, Contact_Email, Contact_Tel, Relation from Client, Contact where Client.Client_ID = Contact.Client_ID"
    cursor.execute(SQL_SEARCH_CLIENT)
    client_list_pending = cursor.fetchall()
    
    for client in client_list_pending:
        if client['Client_ID'].find(client_id) == -1:
            continue
        if client['Client_Tel'].find(client_tel) == -1:
            continue
        if client['Client_Name'].find(client_name) == -1:
            continue
        if client['Client_Address'].find(client_addr) == -1:
            continue
        client_list.append(client)
        
    cursor.close()
    db.close()
    return jsonify(code=200, error="", length=len(client_list), client_list=client_list)

@app.route("/api/v1/get/search_own", methods = ['GET'])
def search_own():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    account_id = request.args.get("account_id")
    
    SQL_SEARCH_OWN = f"select * from Own where Account_ID = '{account_id}'"
    
    cursor.execute(SQL_SEARCH_OWN)
    own_list = cursor.fetchall()
    cursor.close()
    db.close()
    return jsonify(code=200, error="", own_list=own_list, length=len(own_list))

@app.route("/api/v1/get/search_account", methods = ['GET'])
def search_account():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    account_id = request.args.get("account_id")
    bank_name = request.args.get("bank_name")
    balance = request.args.get("balance")
    if not account_id:
        account_id = ""
    if not bank_name:
        bank_name = ""
    if not balance:
        balance = ""
        
    account_list = list()
    SQL_SEARCH_ACCOUNT = "select * from Account"
    cursor.execute(SQL_SEARCH_ACCOUNT)
    account_list_pending = cursor.fetchall()
    
    for account in account_list_pending:
        if account['Account_ID'].find(account_id) == -1:
            continue
        if account['Bank_Name'].find(bank_name) == -1:
            continue
        if balance != "":
            if str(account['Balance']).find(str(float(balance))) == -1 and str(account['Balance']).find(balance) == -1:
                continue
        account_list.append(account)
    cursor.close()
    db.close()
    return jsonify(code=200, error="", length=len(account_list), account_list=account_list)
    
@app.route("/api/v1/get/search_loan", methods = ['GET'])
def search_loan():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    loan_id = request.args.get("loan_id")
    bank_name = request.args.get("bank_name")
    loan_amount = request.args.get("loan_amount")
    loan_status = request.args.get("loan_status")
    pay_already = request.args.get("pay_already")
    print("111")
    print(loan_id, 1, bank_name, 2, loan_amount, 3, loan_status, 4, pay_already)
    if not loan_id:
        loan_id = ""
    if not bank_name:
        bank_name = ""
    if not loan_amount:
        loan_amount = ""
    if not loan_status:
        loan_status = ""
    if not pay_already:
        pay_already = ""
        
    loan_list = list()
    SQL_SEARCH_LOAN = "select * from Loan"
    cursor.execute(SQL_SEARCH_LOAN)
    loan_list_pending = cursor.fetchall()
    
    for loan in loan_list_pending:
        if loan['Loan_ID'].find(loan_id) == -1:
            continue
        if loan['Bank_Name'].find(bank_name) == -1:
            continue
        if loan_amount != "":
            if str(loan['Loan_Amount']).find(str(float(loan_amount))) == -1 and str(loan['Loan_Amount']).find(loan_amount) == -1:
                continue
        if loan_status != "":
            if str(loan['Loan_Status']).find(str(int(loan_status))) == -1:
                continue
        if pay_already != "":
            if str(loan['Pay_already']).find(str(float(pay_already))) == -1 and str(loan['Pay_already']).find(pay_already) == -1:
                continue
        loan_list.append(loan)
        
    cursor.close()
    db.close()
    return jsonify(code=200, error="", length=len(loan_list), loan_list=loan_list)

    

# 增删部分


## 注册
@app.route("/api/v1/post/register", methods = ['POST'])
def register():
    username = request.form.get("username")
    hashkey = request.form.get("hashkey")
    print(username, hashkey)
    
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    
    SQL_REGISTER_IF = f"select * from User where username = '{username}'"
    
    SQL_REGISTER_ADD = f"insert into User(username, hashkey) values('{username}','{hashkey}')"
    
    cursor.execute(SQL_REGISTER_IF)
    data = cursor.fetchall()
    if(data):
        return jsonify(code=601, error="Username already exists.", username=username) #error
    
    cursor.execute(SQL_REGISTER_ADD)
    db.commit()
    
    cursor.close()
    db.close()
    
    return jsonify(code=200, error="", username=username)

@app.route("/api/v1/post/add_user", methods = ['POST'])
def add_user():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    username = request.form.get("username")
    hashkey = request.form.get("hashkey")
    
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    
    SQL_CHECK_USER =  f"select * from User where username = '{username}'"
    SQL_ADD_USER = f"insert into User(username, hashkey) values('{username}','{hashkey}')"
    
    cursor.execute(SQL_CHECK_USER)
    res = cursor.fetchall()
    if res:
        return jsonify(code=603, error="Username already exists.", username=username)
        
    try:
        cursor.execute(SQL_ADD_USER)
        db.commit()
        code = 200
        error = ""
    except Exception as e:
        db.rollback()
        code = 602
        error = "Database error occurred."
    cursor.close()
    db.close()
    
    return jsonify(code=code, error=error, username=username)

@app.route("/api/v1/post/delete_user", methods = ['POST'])
def delete_user():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    
    username = request.form.get("username")
    
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    
    SQL_CHECK_USER =  f"select * from User where username = '{username}'"
    SQL_DELETE_USER = f"delete from User where username = '{username}'"
    
    cursor.execute(SQL_CHECK_USER)
    res = cursor.fetchall()
    if not res:
        return jsonify(code=601, error="Username not exists.")
    
    try:
        cursor.execute(SQL_DELETE_USER)
        db.commit()
        code=200
        error=""
    except Exception as e:
        db.rollback()
        code=602
        error="Database error occurred."
        print(e)
    cursor.close()
    db.close()
    return jsonify(code=code, error=error, username=username)
    
## 添加部分
@app.route("/api/v1/post/add_client", methods = ['POST'])
def add_client():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    
    Client_ID = request.form.get("client_id")
    Client_Name = request.form.get("client_name")
    Client_Tel = request.form.get("client_tel")
    Client_Address = request.form.get("client_addr")
    Contact_Name = request.form.get("contact_name")
    Contact_Email = request.form.get("contact_email")
    Contact_Tel = request.form.get("contact_tel")
    Relation = request.form.get("relation")
    
    if not Client_ID or Client_ID == "":
        return jsonify(code=600, error="Client ID cannot be empty.")
    if not Client_Name or Client_Name == "":
        return jsonify(code=600, error="Client Name cannot be empty.")
    
    SQL_CHECK_CLIENT = f"select * from Client where Client_ID = '{Client_ID}'"
    SQL_ADD_CLIENT = f"insert into Client(Client_ID, Client_Name, Client_Tel, Client_Address) values('{Client_ID}', '{Client_Name}', '{Client_Tel}', '{Client_Address}')"
    SQL_ADD_CONTACT = f"insert into Contact(Client_ID, Contact_Name, Contact_Email, Contact_Tel, Relation) values('{Client_ID}', '{Contact_Name}', '{Contact_Email}', '{Contact_Tel}', '{Relation}')"
    cursor.execute(SQL_CHECK_CLIENT)
    res = cursor.fetchall()
    if res:
        return jsonify(code=603, error="Client ID already exists.", client_id=Client_ID)
    
    try:
        cursor.execute(SQL_ADD_CLIENT)
        cursor.execute(SQL_ADD_CONTACT)
        db.commit()
        code=200
        error=""
    except Exception as e:
        db.rollback()
        code=602
        error="Database error occurred."
        print(e)
    cursor.close()
    db.close()
    return jsonify(code=code, error=error, client_id=Client_ID, client_name=Client_Name)

@app.route("/api/v1/post/add_account", methods = ['POST'])
def add_account():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    
    client_id = request.form.get("client_id")
    account_id = request.form.get("account_id")
    bank_name = request.form.get("bank_name")
    balance = request.form.get("balance")
    opening_date = request.form.get("opening_date")
    account_type = request.form.get("type")
    nowtime = datetime.datetime.now().strftime('%Y-%m-%d')
    
    if not client_id or client_id == "":
        return jsonify(code=600, error="Client ID cannot be empty.")
    if not account_id or account_id == "":
        return jsonify(code=600, error="Account ID cannot be empty.")
    if not bank_name or bank_name == "":
        return jsonify(code=600, error="Bank Name cannot be empty.")
    if not balance or balance == "":
        return jsonify(code=600, error="Balance cannot be empty.")
    
    if account_type == "checking":
        overdraft = request.form.get("overdraft")
        SQL_ADD_CHECKING = f"insert into Checking_Account(Account_ID, Overdraft) values('{account_id}', '{overdraft}')"
    elif account_type == "saving":
        rate = request.form.get("rate")
        currency = request.form.get("currency")
        SQL_ADD_SAVING = f"insert into Saving_Account(Account_ID, Interest_Rate, Currency_Type) values('{account_id}', '{rate}', '{currency}')"
    else:
        return jsonify(code=404, error="Account type not found.", account_type=account_type)
    
    SQL_CHECK_ACCOUNT = f"select * from Account where Account_ID = '{account_id}'"
    SQL_CHECK_OWN = f"select * from Own where Client_ID = '{client_id}'"
    SQL_CHECK_BANK =  f"select * from Bank where Bank_Name = '{bank_name}'"
    SQL_ADD_ACCOUNT = f"insert into Account(Account_ID, Bank_Name, Balance, Opening_Date) values('{account_id}', '{bank_name}', '{balance}', '{opening_date}')"
    SQL_ADD_OWN = f"insert into Own(Client_ID, Visited_Date, Account_ID) values('{client_id}', '{nowtime}', '{account_id}')"
    
    cursor.execute(SQL_CHECK_ACCOUNT)
    res = cursor.fetchall()
    if res:
        return jsonify(code=603, error="Account ID already exists.", account_id=account_id)
    
    cursor.execute(SQL_CHECK_BANK)
    res = cursor.fetchall()
    if not res:
        return jsonify(code=601, error="Bank not exists.", bank_name=bank_name)
    
    cursor.execute(SQL_CHECK_OWN)
    res = cursor.fetchall()
    if res:
        return jsonify(code=604, error="This Client not allowed to add another account.", account_id=account_id)
        
    try:
        cursor.execute(SQL_ADD_ACCOUNT)
        cursor.execute(SQL_ADD_OWN)
        if account_type == "checking":
            cursor.execute(SQL_ADD_CHECKING)
        else:
            cursor.execute(SQL_ADD_SAVING)
        db.commit()
        code=200
        error=""
    except Exception as e:
        db.rollback()
        code=602
        error="Database error occurred."
        print(e)
    cursor.close()
    db.close()
    return jsonify(code=code, error=error, account_id=account_id, bank_name=bank_name)    

@app.route("/api/v1/post/add_loan", methods = ['POST'])
def add_loan():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    
    loan_id = request.form.get("loan_id")
    bank_name = request.form.get("bank_name")
    loan_amount = request.form.get("loan_amount")
    loan_date = request.form.get("opening_date")
    loan_status = 0
    pay_already = 0.0
    
    if not loan_id or loan_id == "":
        return jsonify(code=600, error="Loan ID cannot be empty.")
    if not bank_name or bank_name == "":
        return jsonify(code=600, error="Bank Name cannot be empty.")
    if not loan_amount or loan_amount == "":
        return jsonify(code=600, error="Loan Amount cannot be empty.")
    if not loan_date or loan_date == "":
        return jsonify(code=600, error="Loan Date cannot be empty.")
    
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    
    SQL_CHECK_LOAN = f"select * from Loan where Loan_ID = '{loan_id}'"
    SQL_CHECK_BANK = f"select * from Bank where Bank_Name = '{bank_name}'"
    SQL_ADD_LOAN = f"insert into Loan(Loan_ID, Bank_Name, Loan_Amount, Loan_Status, Pay_already, Opening_Date) values('{loan_id}', '{bank_name}', '{loan_amount}', '{loan_status}', '{pay_already}', '{loan_date}')"
    
    cursor.execute(SQL_CHECK_LOAN)
    ret = cursor.fetchall()
    if ret:
        return jsonify(code=603, error="Loan ID already exists.", loan_id=loan_id)
    cursor.execute(SQL_CHECK_BANK)
    ret = cursor.fetchall()
    if not ret:
        return jsonify(code=601, error="Bank Name not exists.", bank_name=bank_name)
    
    try:
        cursor.execute(SQL_ADD_LOAN)
        db.commit()
        code=200
        error=""
    except Exception as e:
        db.rollback()
        code=602
        error="Database error occurred."
        print(e)
    
    cursor.close()
    db.close()
    return jsonify(code=code, error=error, loan_id=loan_id, bank_name=bank_name, loan_amount=loan_amount)

@app.route("/api/v1/post/add_pay", methods = ['POST'])
def add_pay():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    
    client_id = request.form.get("client_id")
    loan_id = request.form.get("loan_id")
    pay_id = request.form.get("pay_id")
    pay_amount = request.form.get("pay_amount")
    pay_date = request.form.get("pay_date")
    
    if not client_id or client_id == "":
        return jsonify(code=600, error="Client ID cannot be empty.")
    if not loan_id or loan_id == "":
        return jsonify(code=600, error="Loan ID cannot be empty.")
    if not pay_id or pay_id == "":
        return jsonify(code=600, error="Pay ID cannot be empty.")
    if not pay_amount or pay_amount == "":
        return jsonify(code=600, error="Pay Amount cannot be empty")
    
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    
    SQL_CHECK_PAY = f"select * from Pay where Client_ID = '{client_id}' and Loan_ID = '{loan_id}' and Pay_ID = '{pay_id}'"
    SQL_CHECK_CLIENT = f"select * from Client where Client_ID = '{client_id}'"
    SQL_CHECK_LOAN = f"select * from Loan where Loan_ID = '{loan_id}'"
    SQL_ADD_PAY = f"insert into Pay(Client_ID, Loan_ID, Pay_ID, Pay_Amount, Pay_Date) values('{client_id}', '{loan_id}', '{pay_id}', '{pay_amount}', '{pay_date}')"    
    
    cursor.execute(SQL_CHECK_PAY)
    ret = cursor.fetchall()
    if ret:
        return jsonify(code=603, error="Pay info already exists.", client_id=client_id, loan_id=loan_id, pay_id=pay_id)    
    
    cursor.execute(SQL_CHECK_CLIENT)
    ret = cursor.fetchall()
    if not ret:
        return jsonify(code=601, error="Client ID not exists.", client_id=client_id)
    cursor.execute(SQL_CHECK_LOAN)
    ret = cursor.fetchall()
    if not ret:
        return jsonify(code=601, error="Loan ID not exists.", loan_id=loan_id)
    
    try:
        cursor.execute(SQL_ADD_PAY)
        cursor.execute(SQL_CHECK_LOAN)
        ret = cursor.fetchall()
        data = ret[0]
        pay_already = float(data['Pay_already'])
        pay_already_new = pay_already + float(pay_amount)
        loan_amount = float(data['Loan_Amount'])
        loan_status = 1
        if pay_already_new >= loan_amount:
            loan_status = 2
        cursor.execute(f"update Loan set Loan_Status = '{loan_status}', Pay_already = '{pay_already_new}' where Loan_ID = '{loan_id}'")
        db.commit()
        code=200
        error=""
    except Exception as e:
        db.rollback()
        code=602
        error="Database error occurred."
        print(e)
        
    cursor.close()
    db.close()
    return jsonify(code=code, error=error, client_id=client_id, loan_id=loan_id, pay_id=pay_id, pay_amount=pay_amount)
        
## 删除部分

@app.route("/api/v1/post/delete_client", methods = ['POST'])
def delete_client():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    
    client_id = request.form.get("client_id")
    
    SQL_CHECK_OWN = f"select * from Own where Client_ID = '{client_id}'"
    SQL_CHECK_PAY = f"select * from Pay where Client_ID = '{client_id}'"
    SQL_CHECK_CLIENT = f"select * from Client where Client_ID = '{client_id}'"
    SQL_DELETE_CLIENT = f"delete from Client where Client_ID = '{client_id}'"
    SQL_DELETE_CONTACT = f"delete from Contact where Client_ID = '{client_id}'"

    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    
    
    cursor.execute(SQL_CHECK_CLIENT)
    ret = cursor.fetchall()
    if not ret:
        return jsonify(code=601, error="Client not exists.")
    cursor.execute(SQL_CHECK_OWN)
    ret = cursor.fetchall()
    if ret:
        return jsonify(code=604, error="Client not allowed to be deleted.", client_id=client_id)
    cursor.execute(SQL_CHECK_PAY)
    ret = cursor.fetchall()
    if ret:
        return jsonify(code=604, error="Client not allowed to be deleted.", client_id=client_id)
    
    try:
        cursor.execute("SET foreign_key_checks = 0")
        cursor.execute(SQL_DELETE_CLIENT)
        print(1)
        cursor.execute(SQL_DELETE_CONTACT)
        cursor.execute("SET foreign_key_checks = 1")
        print(2)
        db.commit()
        code=200
        error=""
    except Exception as e:
        db.rollback()
        cursor.execute("SET foreign_key_checks = 1")
        code=602
        error="Database error occurred."
        print(e)
    cursor.close()
    db.close()
    
    return jsonify(code=code, error=error, client_id=client_id)

@app.route("/api/v1/post/delete_account", methods = ['POST'])
def delete_account():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    
    account_id = request.form.get("account_id")
    
    SQL_CHECK_ACCOUNT = f"select * from Account where Account_ID = '{account_id}'"
    SQL_DELETE_ACCOUNT = f"delete from Account where Account_ID = '{account_id}'"
    SQL_DELETE_OWN = f"delete from Own where Account_ID = '{account_id}'"
    SQL_DELETE_CHECKING = f"delete from Checking_Account where Account_ID = '{account_id}'"
    SQL_DELETE_SAVING = f"delete from Saving_Account where Account_ID = '{account_id}'"
    SQL_CHECK_CHECKING = f"select * from Checking_Account where Account_ID = '{account_id}'"
    SQL_CHECK_SAVING = f"select * from Saving_Account where Account_ID = '{account_id}'"
    
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    
    checking = 0
    saving = 0
    cursor.execute(SQL_CHECK_ACCOUNT)
    ret = cursor.fetchall()
    if not ret:
        return jsonify(code=601, error="Account ID not exists.")
    cursor.execute(SQL_CHECK_CHECKING)
    ret = cursor.fetchall()
    if ret:
        checking = 1
    cursor.execute(SQL_CHECK_SAVING)
    ret = cursor.fetchall()
    if ret:
        saving = 1
        
    try:
        cursor.execute("SET foreign_key_checks = 0")
        cursor.execute(SQL_DELETE_ACCOUNT)
        cursor.execute(SQL_DELETE_OWN)
        if checking:
            cursor.execute(SQL_DELETE_CHECKING)
        if saving:
            cursor.execute(SQL_DELETE_SAVING)
        cursor.execute("SET foreign_key_checks = 1")
        db.commit()
        code=200
        error=""
    except Exception as e:
        db.rollback()
        cursor.execute("SET foreign_key_checks = 1")
        code=602
        error="Database error occurred."
        print(e)
        
    cursor.close()
    db.close()
    
    return jsonify(code=code, error=error, account_id=account_id)

@app.route("/api/v1/post/delete_loan", methods = ['POST'])
def delete_loan():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    
    loan_id = request.form.get("loan_id")
    
    SQL_CHECK_LOAN = f"select * from Loan where Loan_ID = '{loan_id}'"
    SQL_DELETE_LOAN = f"delete from Loan where Loan_ID = '{loan_id}'"
    SQL_DELETE_PAY = f"delete from Pay where Loan_ID = '{loan_id}'"
    
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    
    cursor.execute(SQL_CHECK_LOAN)
    ret = cursor.fetchall()
    if not ret:
        return jsonify(code=601, error="Loan ID not exists.")
    if ret[0]['Loan_Status'] == 1:
        return jsonify(code=604, error="Loan ID not allowed to delete for being processed.")
    
    try:
        cursor.execute("SET foreign_key_checks = 0")
        cursor.execute(SQL_DELETE_LOAN)
        cursor.execute(SQL_DELETE_PAY)
        cursor.execute("SET foreign_key_checks = 1")
        db.commit()
        code=200
        error=""
    except Exception as e:
        db.rollback()
        cursor.execute("SET foreign_key_checks = 1")
        code=602
        error="Database error occurred."
        print(e)
    
    cursor.close()
    db.close()
    
    return jsonify(code=code, error=error, loan_id=loan_id)
    
## 修改部分

@app.route("/api/v1/post/edit_user", methods = ['POST'])
def edit_user():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    
    username = request.form.get("username")
    hashkey = request.form.get("hashkey")
    
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    
    SQL_ADD_USER = f"insert into User(username, hashkey) values('{username}','{hashkey}')"
    SQL_DELETE_USER = f"delete from User where username='{username}'"
        
    try:
        cursor.execute(SQL_DELETE_USER)
        cursor.execute(SQL_ADD_USER)
        db.commit()
        code = 200
        error = ""
    except Exception as e:
        db.rollback()
        code = 602
        error = "Database error occurred."
    cursor.close()
    db.close()
    
    return jsonify(code=code, error=error, username=username)
    

@app.route("/api/v1/post/edit_client", methods = ['POST'])
def edit_client():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    
    client_id = request.form.get("client_id")
    client_name = request.form.get("client_name")
    client_tel = request.form.get("client_tel")
    client_addr = request.form.get("client_addr")
    contact_name = request.form.get("contact_name")
    contact_email = request.form.get("contact_email")
    contact_tel = request.form.get("contact_tel")
    relation = request.form.get("relation")
    
    if not client_name or client_name == "":
        return jsonify(code=600, error="Client Name cannot be empty.")
    
    SQL_UPDATE_CLIENT = f"update Client set Client_Name = '{client_name}', Client_Tel = '{client_tel}', Client_Address = '{client_addr}' where Client_ID = '{client_id}'"
    SQL_UPDATE_CONTACT = f"update Contact set Contact_Name = '{contact_name}', Contact_Email = '{contact_email}', Contact_Tel = '{contact_tel}', Relation = '{relation}' where Client_ID = '{client_id}'"
    
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    
    try:
        cursor.execute(SQL_UPDATE_CLIENT)
        cursor.execute(SQL_UPDATE_CONTACT)
        db.commit()
        code=200
        error=""
    except Exception as e:
        db.rollback()
        code=602
        error="Database error occurred."
        print(e)
    
    cursor.close()
    db.close()
    
    return jsonify(code=code, error=error, client_id=client_id)

@app.route("/api/v1/post/edit_account", methods = ['POST'])
def edit_account():
    if not session.get("username"):
        return jsonify(code=401, error="Unauthorized. Please login first.")
    
    account_id = request.form.get("account_id")
    visited_date = datetime.datetime.now().strftime('%Y-%m-%d') #request.form.get("visited_date")
    account_type = request.form.get("account_type")
    
    SQL_UPDATE_OWN = f"update Own set Visited_Date = '{visited_date}' where Account_ID = '{account_id}'"
    SQL_CHECK_CHECKING = f"select * from Checking_Account where Account_ID = '{account_id}'"
    SQL_CHECK_SAVING = f"select * from Saving_Account where Account_ID = '{account_id}'"
        
    db = pymysql.connect(host="127.0.0.1", port=3306, user='dblab3', passwd="xH2WTHsnN3reYsiT", charset='utf8', db='dblab3')
    cursor = db.cursor(cursor=pymysql.cursors.DictCursor)
    
    checking = 0
    saving = 0
    cursor.execute(SQL_CHECK_CHECKING)
    ret = cursor.fetchall()
    if ret:
        checking = 1
        overdraft = request.form.get("overdraft")
        if not overdraft or overdraft == "":
            checking = 0
        SQL_UPDATE_CHECKING = f"update Checking_Account set Overdraft = '{overdraft}' where Account_ID = '{account_id}'"
    cursor.execute(SQL_CHECK_SAVING)
    ret = cursor.fetchall()
    if ret:
        saving = 1
        interest_rate = request.form.get("interest_rate")
        currency_type = request.form.get("currency_type")
        if not interest_rate or not currency_type or interest_rate == "" or currency_type == "":
            saving = 0
        SQL_UPDATE_SAVING = f"update Saving_Account set Interest_Rate = '{interest_rate}', Currency_Type = '{currency_type}' where Account_ID = '{account_id}'"
    
    try:
        cursor.execute(SQL_UPDATE_OWN)
        if checking:
            cursor.execute(SQL_UPDATE_CHECKING)
        if saving:
            cursor.execute(SQL_UPDATE_SAVING)
        db.commit()
        code=200
        error=""
    except Exception as e:
        db.rollback()
        code=602
        error="Database error occurred."
        print(e)
    
    cursor.close()
    db.close()
    
    return jsonify(code=code, error=error, account_id=account_id)     

@app.route("/api/v1/post/test", methods = ['POST'])
def test():
    username = request.form.get("username")
    hashkey = request.form.get("hashkey")
    print(username, hashkey)
    return jsonify(username=username, hashkey=hashkey)

@app.route("/")
def root():
    return jsonify(code=200, error="", message="Ping! I am Online.")

@app.route("/favicon.ico")
def img():
    return redirect("https://od.srpr.cc/sust0/favicon.ico")

@app.route("/api")
def api():
    return render_template("README.html")


if __name__ == '__main__':
    app.run(port=5001, debug=True)
    