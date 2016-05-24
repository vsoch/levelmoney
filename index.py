from flask import Flask, render_template, request
from datetime import datetime
import requests
import numpy
import pandas
import json
import re

# SERVER CONFIGURATION ##############################################
class MoneyServer(Flask):

    def __init__(self, *args, **kwargs):
        super(MoneyServer, self).__init__(*args, **kwargs)

        # load data on start of application
        self.api_token = self.read_auth("data/.api_token")
        self.auth_token = self.read_auth("data/.auth_token")
        self.userid = int(self.read_auth("data/.userid"))
        self.transactions = get_transactions()          
        self.accounts = get_accounts()

        def self.read_auth(auth_file):
            '''read_auth returns a single line (first) in a text file
            :param auth_file: full path to file to read
            '''
            filey = open(auth_file,"r")
            text = filey.readlines()[0].strip("\n")
            filey.close()
            return text

app = MoneyServer(__name__)

# Global functions ###################################################################################

def get_auth(json_strict,json_verbose):
    '''get_auth returns the uid, token, and api-token associated with the application
    '''
    return {"uid":app.userid,
            "token":app.auth_token,
            "api-token":app.api_token,
            "json-strict-mode":json_strict,
            "json-verbose-response":json_verbose}


def get_transaction_log(account):
    '''get_transaction_log returns a view of the users transactions, with YYYY-MM as key, and dictionary of "spent"
    and "income" as lookup
    
    ::note
 
       eg {"2014-10": {"spent": "$200.00", "income": "$500.00"}
    '''
    account_id = app.accounts["account-id"][app.accounts["institution-login-id"]==account].tolist()[0]
    entries = app.transactions[app.transactions["account-id"]==account_id]
    datetimes = [datetime.strptime(x, '%Y-%m-%dT%H:%M:%S.%fZ') for x in entries["transaction-time"]]
    # stopped here - need to run to meeting


# API Wrapper Functions ##############################################################################

def get_transactions():
    '''get_transactions returns a pandas data frame of all transactions. For this demo this will be called
    on start of application, for a live application this would not be appropriate.
    '''
    transactions = GetAllTransactions()
    return pandas.DataFrame(transactions)


def get_accounts():
    '''get_accounts returns a pandas data frame of all accounts. Ditto for called at start of application.
    '''
    accounts = GetAccounts()
    return pandas.DataFrame(accounts)

# curl -H 'Accept: application/json' -H 'Content-Type: application/json' -X POST -d '{"args": {"uid": 1110590645, "token": "0E0BDCAFD325E86FED6822BB2DA70FE7", "api-token": "AppTokenForInterview", "json-strict-mode": false, "json-verbose-response": false}}' https://prod-api.level-labs.com/api/v2/core/get-all-transactions

def api_post(url,json_strict=False,json_verbose=False):
    '''api_post posts a url to the api with appropriate headers, and data specified at
    init of the application (api_token, userid, auth_token)
    :param url: the url to post to
    :returns response: the requests response object
    '''
    headers = {'Accept': 'application/json','Content-Type':'application/json'}

    args = get_auth(json_strict=json_strict,
                    json_verbose=json_verbose)

    data = {"args":args}
    return requests.post(url, headers=headers, data=json.dumps(data))
    
    
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


# Views ##############################################################################################

@app.route("/")
def index():
    '''index asks the user for institution-login-id'''
    return render_template("index.html")

@app.route("/login",methods=["POST","GET"])
def login():
    '''login gets the institution-login-id from post, and logs in'''
    
    if request.method == "POST":
        account = request.form["login_id"]
        if account in app.accounts["institution-login-id"]:
            transaction_log = get_transaction_log(account)
            return render_template("home.html",log=transaction_log)  
        else:
            message = "Sorry, the account %s was not found." %()
            return render_template("index.html",message=message)

    else:
        message = "You must log in first before viewing account home."
    return render_template("index.html",message=message)
    

if __name__ == "__main__":
    app.debug = True
    app.run()

