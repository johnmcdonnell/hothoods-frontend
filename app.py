import os
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, jsonify, Response
import json
from json import JSONEncoder
import MySQLdb
import numpy as np
import pandas
from pandas.io.sql import read_sql

db = MySQLdb.connect(user="mcdon", host="localhost", port=3306, db="prices")
c = db.cursor()

app = Flask("PsiTurk", template_folder=os.path.join(os.curdir, "templates"))

lastpricequery = """
SELECT 
date AS SaleDate, smoothed
FROM smoothed 
WHERE (ZipCode='{zipcode}') AND smoothed IS NOT NULL
ORDER BY SaleDate DESC
LIMIT 1;
"""

def query_hoodnames(zip=None):
    hoodnamequery = """
    SELECT
    ZipCode, Neighborhood
    FROM hoodnames
    """
    if zip:
        hoodnamequery += "WHERE (ZipCode='{zipcode}') LIMIT 1;".format(zipcode=zip);
    else:
        hoodnamequery += ";"
    db.query(hoodnamequery)
    dbresult = db.store_result()
    ret = {}
    for results in dbresult.fetch_row(maxrows=0):
        ret[results[0]] = results[1].title()
    return ret

zipquery = """
SELECT 
date AS SaleDate, smoothed
FROM smoothed 
WHERE (ZipCode='{zipcode}') AND smoothed IS NOT NULL
ORDER BY SaleDate;
"""

forecastquery = """
SELECT 
time, mle, low80, high80
FROM zipforecasts 
WHERE (ZipCode='{zipcode}') AND mle IS NOT NULL
ORDER BY time;
"""

@app.route('/mapinfo')
def mapinfo():
    """
    Return general info about all zips on the map
    """
    # Get name of neighborhood
    hoodnames = query_hoodnames()
    for hood in hoodnames:
        pass
    
    # Get price history
    db.query(zipquery.format(zipcode=zipcode))
    dbresult = db.store_result()
    ret = []
    for row in dbresult.fetch_row(maxrows=0):
        ret.append({"SaleDate": str(row[0]), "ppsqft": float(row[1])})
        lastprice = float(row[1])
    
    return(jsonify(hoodname=hoodname, prices=ret))


@app.route('/zip/<zipcode>')
def ziptrend(zipcode=None):
    """
    Return info about a particular zip code.
    """
    if not zipcode:
        raise Exception, 'page_not_found'
    
    # Get name of neighborhood
    hoodnames = query_hoodnames(zip=zipcode)
    hoodname = hoodnames[zipcode]
    
    # Get price history
    db.query(zipquery.format(zipcode=zipcode))
    dbresult = db.store_result()
    history = []
    for row in dbresult.fetch_row(maxrows=0):
        history.append({"date": row[0], "price": float(row[1])})
        lasttime = row[0]
        lastprice = float(row[1])
    
    # Get forecast
    db.query(forecastquery.format(zipcode=zipcode))
    dbresult = db.store_result()
    dateformat = "%Y-%m-%d"
    forecasts = [{"date": lasttime, "price": lastprice, "lo80": lastprice, "hi80": lastprice}]
    for row in dbresult.fetch_row(maxrows=0):
        forecasttime = dt.strptime(lasttime, dateformat) + relativedelta(months=row[0])
        forecasts.append({"date": dt.strftime(forecasttime, dateformat), "price": np.exp(float(row[1])), "lo80": np.exp(float(row[2])), "hi80": np.exp(float(row[3]))})
    
    return(jsonify(hoodname=hoodname, prices=history, forecasts=forecasts))

@app.route('/')
def home():
    """
    Route not found by the other routes above. May point to a static template.
    """
    return render_template("index.html")

@app.route('/<pagename>')
def regularpage(pagename=None):
    """
    Route not found by the other routes above. May point to a static template.
    """
    if pagename==None:
        raise Exception, 'page_not_found'
    return render_template(pagename)

if __name__ == '__main__':
    print "Starting webserver."
    app.run(debug=True, host='localhost', port=8000)

