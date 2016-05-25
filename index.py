from flask import Flask, render_template, request
from numpy.random import choice
from datetime import datetime
import requests
import numpy
import pandas
import json
import re

# API Wrapper Functions ##############################################################################

def get_transactions(convert_to_dollar=True):
    '''get_transactions returns a pandas data frame of all transactions. For this demo this will be called
    on start of application, for a live application this would not be appropriate.
    :param convert_to_dollar: if True, converts "centocents" to dollars (20000 centocents = $2) or 10000 = $1
    '''
    transactions = GetAllTransactions()
    transactions = pandas.DataFrame(transactions)
    if convert_to_dollar == True:
        transactions["amount"] = transactions["amount"]/10000.0
    return transactions


def get_accounts():
    '''get_accounts returns a pandas data frame of all accounts. Ditto for called at start of application.
    '''
    accounts = GetAccounts()
    return pandas.DataFrame(accounts)

# curl -H 'Accept: application/json' -H 'Content-Type: application/json' -X POST -d '{"args": {"uid": 1110590645, "token": "0E0BDCAFD325E86FED6822BB2DA70FE7", "api-token": "AppTokenForInterview", "json-strict-mode": false, "json-verbose-response": false}}' https://prod-api.level-labs.com/api/v2/core/get-all-transactions

def api_post(url,json_strict=False,json_verbose=False,data=None):
    '''api_post posts a url to the api with appropriate headers, and data specified at
    init of the application (api_token, userid, auth_token)
    :param data: a dictionary of key:value items to add to the data args variable
    :param url: the url to post to
    :returns response: the requests response object
    '''
    headers = {'Accept': 'application/json','Content-Type':'application/json'}

    args = get_auth(json_strict=json_strict,
                    json_verbose=json_verbose)

    args = {"args":args}

    if data != None:
        args.update(data)

    return requests.post(url, headers=headers, data=json.dumps(args))
    
    
def GetAllTransactions():
    '''GetAllTransactions is a wrapper for the level money api function GetAllTransactions
    to get data structure organized by user id, please use get_*_transactions()
    :returns transactions: json object of all transactions
    ''' 
    url = "https://prod-api.level-labs.com/api/v2/core/get-all-transactions"
    response = api_post(url)
    if response.status_code == 200:
        return response.json()["transactions"]
    else:
        print "Error with GetAllTransactions: %s" %(response.reason)


# curl -H 'Accept: application/json' -H 'Content-Type: application/json' -X POST -d '{"args": {"uid": 1110590645, "token": "0E0BDCAFD325E86FED6822BB2DA70FE7", "api-token": "AppTokenForInterview", "json-strict-mode": false, "json-verbose-response": false}}' https://prod-api.level-labs.com/api/v2/core/get-accounts

def GetAccounts():
    '''getAccounts returns a list of valid user accounts - also loaded on app start, but not ideal for
    anything other than a demo
    :returns accounts: 
    '''
    url = "https://prod-api.level-labs.com/api/v2/core/get-accounts"   
    response = api_post(url)
    if response.status_code == 200:
        return response.json()["accounts"]
    else:
        print "Error with GetAccounts: %s" %(response.reason)


# curl -H 'Accept: application/json' -H 'Content-Type: application/json' -X POST -d '{"email": "level@example.com", "password": "incorrect_password", "args": {"uid": 1110590645, "token": "0E0BDCAFD325E86FED6822BB2DA70FE7", "api-token": "AppTokenForInterview", "json-strict-mode": false, "json-verbose-response": false}}' https://prod-api.level-labs.com/api/v2/core/login

def Login(email,password):
    '''Login returns a token for a user account (login request) [I don't think I need to implement this]
    :param email: the email address associated with an account
    :returns accounts: 
    '''
    data = {"email":email,"password":password}
    url = "https://prod-api.level-labs.com/api/v2/core/login"
    response = api_post(url,data=data)
    if response.status_code == 200:
        return response.json()

# curl -H 'Accept: application/json' -H 'Content-Type: application/json' -X POST -d '{"args": {"uid": 1110590645, "token": "0E0BDCAFD325E86FED6822BB2DA70FE7", "api-token": "AppTokenForInterview", "json-strict-mode": false, "json-verbose-response": false}, "year": 2015, "month": 3}' https://prod-api.level-labs.com/api/v2/core/projected-transactions-for-month

def GetProjectedTransactionsForMonth(year=2015,month=3):
    '''getProjectedTransactionsForMonth returns a list of actual (or expected) transactions for a given month. For this demo,it only works for this month (and I think the inputs of year/month are meaningless)
    :returns transactions: 
    '''
    url = "https://prod-api.level-labs.com/api/v2/core/projected-transactions-for-month"   
    args = {"year": year, "month": month}
    response = api_post(url,data=args)
    if response.status_code == 200:
        return response.json()["transactions"]
    else:
        print "Error with GetProjectedTransactions: %s" %(response.reason)


# Global functions ###################################################################################

def get_auth(json_strict,json_verbose):
    '''get_auth returns the uid, token, and api-token associated with the application
    '''
    return {"uid":app.userid,
            "token":app.auth_token,
            "api-token":app.api_token,
            "json-strict-mode":json_strict,
            "json-verbose-response":json_verbose}

def get_account_transactions(institution_login_id,crystal_ball=False):
    '''get_account_transactions returns a data frame of transactions for a particular institution-login-id
    :param institution_login_id: the institution login id
    :returns entries: a data frame of transaction entries for the account
    '''
    account_id = app.accounts["account-id"][app.accounts["institution-id"]==institution_login_id].tolist()[0]
    entries = app.transactions[app.transactions["account-id"]==account_id].copy()
    if crystal_ball == True:
        future_transactions = GetProjectedTransactionsForMonth() #just use their year/month defaults
        entries = entries.append(pandas.DataFrame(future_transactions))

    datetimes = [datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.%fZ') for x in entries["transaction-time"]]
    year_month = ["%s-%s" %(date.year,date.month) for date in datetimes] 
    entries["datetime"] = year_month
    return entries

def get_transaction_log(account,ignore_regex=None,crystal_ball=False):
    '''get_transaction_log returns a view of the users transactions, with YYYY-MM as key, and dictionary of "spent"
    and "income" as lookup
    :param ignore_regex: a regular expression to filter (ignore) a subset of transactions
    ::note
 
       eg {"2014-10": {"spent": "$200.00", "income": "$500.00"}
    '''
    entries = get_account_transactions(account,crystal_ball=crystal_ball)
    unique_datetimes = numpy.unique(entries["datetime"]).tolist()

    log = dict()
    spent_sum = 0  # An average month should include all months
    income_sum = 0 # (even xmas when spending is higher)
    for date in unique_datetimes:
        subset = entries[entries["datetime"]==date]    
        if ignore_regex != None:
            idx = [x for x in range(len(subset.merchant)) if re.search(ignore_regex,subset.merchant.tolist()[x])]
            ignore_fields = subset.index[idx].tolist()
            print "ignoring costs %s" %(",".join(subset.merchant.loc[ignore_fields]))
            subset = subset.drop(ignore_fields)
        spent = subset['amount'][subset["amount"]<0].sum() # negative amount is debit
        income = subset['amount'][subset["amount"]>0].sum() # negative amount is debit
        log[date] = {"spent":"$%.2f" %(numpy.abs(spent)),"income":"$%.2f" %(income)}
        spent_sum+=spent
        income_sum+=income         

    # calculate an average for all months
    average_spent = spent_sum / float(len(unique_datetimes))
    average_income = income_sum / float(len(unique_datetimes))
    log["average"] = {"spent":"$%.2f" %(numpy.abs(average_spent)),"income":"$%.2f" %(numpy.abs(average_income))}
    return log


def get_account_name(account):
    '''get_account_name returns the user name based on an institution ID
    :param account: the institution id
    '''
    # nonce:comfy-cc/hdhehe <-- checking account, institution account name
    account_name = app.accounts["account-id"][app.accounts["institution-id"]==account][0]
    return account_name.split("/")[1]

# SERVER CONFIGURATION ##############################################
class MoneyServer(Flask):

    def __init__(self, *args, **kwargs):
        super(MoneyServer, self).__init__(*args, **kwargs)

        # load data on start of application
        self.api_token = self.read_auth("data/.api_token")
        self.auth_token = self.read_auth("data/.auth_token")
        self.userid = int(self.read_auth("data/.userid"))

    def read_auth(self,auth_file):
        '''read_auth returns a single line (first) in a text file
        :param auth_file: full path to file to read
        '''
        filey = open(auth_file,"r")
        text = filey.readlines()[0].strip("\n")
        filey.close()
        return text

# Start application
app = MoneyServer(__name__)
app.transactions = get_transactions()          
app.accounts = get_accounts()


# Views ##############################################################################################

@app.route("/")
def index():
    '''index asks the user for institution-login-id'''
    message_options = ["Check all your accounts. One place.",
                       "Be smart about managing your money.",
                       "Personal finance at your fingertips."]
    message = choice(message_options)
    return render_template("index.html",message=message)

def base_login(account_id,ignore_regex=None,crystal_ball=False):
    '''base is a general function for "authenticating" a user, meaning retrieving transactions,
    and an account name (and message) given an account_id. A dictionary is returned with these fields
    and if not successful, the "success" key is False, and the message field should be shown to user
    '''
    result = dict()
    if account_id in app.accounts["institution-id"].tolist():
        result["log"] = get_transaction_log(account_id,
                                            ignore_regex=ignore_regex,
                                            crystal_ball=crystal_ball)

        result["name"] = get_account_name(account_id)
        result["message"] = "Welcome to your account, %s" %(result["name"])
        result["success"] = True
        result["id"] = account_id
    else:
        result["message"] = "Sorry, the account %s was not found." %(account_id)
        result["success"] = False
    return result

@app.route("/home/<account_id>")
def home(account_id):
    '''home is the login view after the user has logged in'''    
    account_id = int(account_id)
    result = base_login(account_id)
    if result["success"] == True:
        return render_template("home.html",log=result["log"],
                                           message=result["message"],
                                           account_id=result["id"])  
    else:
        return render_template("index.html",message=result["message"])

@app.route("/login",methods=["POST","GET"])
def login():
    '''login is the first view seen after login'''
    
    if request.method == "POST":
        account = int(request.form["account_id"])
        result = base_login(account)
        if result["success"] == True:
            return render_template("home.html",log=result["log"],
                                               message=result["message"],
                                               account_id=result["id"])  
        else:
            return render_template("index.html",message=result["message"])
    else:
        message = "You must log in first before viewing account home."
    return render_template("index.html",message=message)
    
#--ignore-donuts: The user is so enthusiastic about donuts that they don't want donut spending to come out of their budget. Disregard all donut-related transactions from the spending. You can just use the merchant field to determine what's a donut

@app.route("/donut/<account_id>")
def donut(account_id):
    '''ignore donuts does not include donut costs'''
    account_id = int(account_id)
    result = base_login(account_id,ignore_regex="Krispy Kreme Donuts|DUNKIN")
    if result["success"] == True:
        message = "Your transactions not including donut spending, your majesty!"
        return render_template("home.html",log=result["log"],
                                           message=message,
                                           account_id=result["id"],
                                           ignore_donuts="anything")  
    else:
        return render_template("index.html",message=result["message"])
    return render_template("index.html",message=message)    

# --crystal-ball: We expose a  endpoint, which returns all the transactions that have happened or are expected to happen for a given month. It looks like right now it only works for this month, but that's OK. Merge the results of this API call with the full list from GetAllTransactions and use it to generate predicted spending and income numbers for the rest of this month, in addition to previous months.

@app.route("/crystalball/<account_id>")
def crystalball(account_id):
    '''include projected transactions for future'''
    account_id = int(account_id)
    result = base_login(account_id,crystal_ball=True)
    if result["success"] == True:
        now = datetime.now()
        message = "We've predicted the future for %s-%s!" %(now.year,now.month)
        return render_template("home.html",log=result["log"],
                                           message=message,
                                           account_id=result["id"],
                                           crystal_ball="anything")  
    else:
        return render_template("index.html",message=result["message"])
    return render_template("index.html",message=message)    



if __name__ == "__main__":
    app.debug = True
    app.run()
