import os
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from flask import Flask, render_template, jsonify
import numpy as np
#import pandas
#from pandas.io.sql import read_sql

import model

app = Flask("PsiTurk", template_folder=os.path.join(os.curdir, "templates"))
dbsession = model.SQLSession(user="mcdon", host="localhost", port=3306, db="prices")

# Huge query joins many tables to get a summary of each neighborhood: Neighborhood name, The most recent smoothed price estimate, and MLE price forecast.
summary_query = """
SELECT hood.ZipCode, hood.neighborhood, price.smoothed, minpred.mle, maxpred.mle
FROM hoodnames hood, (
	SELECT s.ZipCode, s.smoothed
	FROM smoothed s
	INNER JOIN (
    	SELECT max(date) as date, zipCode, smoothed
    	FROM smoothed
    	WHERE smoothed IS NOT NULL
		GROUP BY ZipCode) ss 
	ON s.date = ss.date AND s.ZipCode = ss.ZipCode
	) price, (
	SELECT f.ZipCode, f.mle
	FROM zipforecasts f
	INNER JOIN (
    	SELECT min(time) as time, zipCode, mle
    	FROM zipforecasts
    	WHERE mle IS NOT NULL
        GROUP BY ZipCode) ff 
        ON f.time = ff.time AND f.ZipCode = ff.ZipCode
	) minpred, (
	SELECT f.ZipCode, f.mle  FROM zipforecasts f
	INNER JOIN (SELECT max(time) as time, ZipCode, mle
    	FROM zipforecasts
    	WHERE mle IS NOT NULL
    	GROUP BY ZipCode) lastdate
	ON lastdate.time = f.time AND lastdate.ZipCode = f.ZipCode) maxpred
WHERE hood.ZipCode = price.ZipCode AND hood.ZipCode = minpred.ZipCode AND hood.ZipCode = maxpred.ZipCode
"""

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
    
    ret = {}
    for results in dbsession.resolve_query(hoodnamequery):
        ret[results[0]] = results[1].title()
    return ret

def query_borough(zip):
    boroquery = """
        SELECT Borough FROM sales 
        WHERE ZipCode={zipcode} LIMIT 1""".format(zipcode=zip)
    return dbsession.resolve_query(boroquery)[0][0]

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

currentpricequery = """
SELECT s.ZipCode, s.smoothed
FROM smoothed s
INNER JOIN(
        SELECT max(date) as date, zipCode, smoothed
        FROM smoothed
        WHERE smoothed IS NOT NULL
        GROUP BY ZipCode
) ss ON s.date = ss.date AND s.ZipCode = ss.ZipCode
"""

@app.route('/mapinfo.json')
def mapinfo():
    """
    Return general info about all zip codes on the map.
    """
    # Get name of neighborhood
    hoodnames = dict(query_hoodnames())
    currentprices = dict(dbsession.resolve_query(currentpricequery))
    ret = []
    for row in dbsession.resolve_query(summary_query):
        zip = row[0]
        name = row[1].title()
        price = row[2]
        earlypred = np.exp(row[3])
        pred = np.exp(row[4])
        growth = (pred / earlypred)-1
        if zip == '10004':
            print zip
            print price
            print earlypred
            print pred
            print growth
        ret.append({
            "zip": zip,
            "hoodname": name,
            "price": price,
            "earlypred": earlypred,
            "prediction": pred,
            "growth": growth})
    return(jsonify(zips=ret))


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
    boroname = query_borough(zipcode)
    
    # Get price history
    history = []
    for row in dbsession.resolve_query(zipquery.format(zipcode=zipcode)):
        history.append({"date": row[0], "price": float(row[1])})
        lasttime = row[0]
        lastprice = float(row[1])
    
    # Get forecast
    if lasttime:
        dateformat = "%Y-%m-%d"
        forecasts = [{"date": lasttime, "price": lastprice, "lo80": lastprice, "hi80": lastprice}]
        for row in dbsession.resolve_query(forecastquery.format(zipcode=zipcode)):
            forecasttime = dt.strptime(lasttime, dateformat) + relativedelta(months=row[0])
            forecasts.append({"date": dt.strftime(forecasttime, dateformat), "price": np.exp(float(row[1])), "lo80": np.exp(float(row[2])), "hi80": np.exp(float(row[3]))})
        return(jsonify(boroname=boroname, hoodname=hoodname, prices=history, forecasts=forecasts))

@app.route('/')
def home():
    """
    Route not found by the other routes above. May point to a static template.
    """
    hoods = [{"zip": "10009", "houses": [
        {"src": "http://p.rdcpix.com/v01/lfa275a44-m0s.jpg"}, 
        {"src": "http://p.rdcpix.com/v01/le8cf4b44-m0s.jpg"}, 
        {"src": "http://p.rdcpix.com/v01/lb3aa5344-m0s.jpg"}]}]
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

