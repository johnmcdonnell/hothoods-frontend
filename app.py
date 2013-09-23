# vim: set fileencoding=utf-8

import os
from datetime import datetime as dt
from dateutil.relativedelta import relativedelta
from flask import Flask, g, render_template, jsonify
import numpy as np
#import pandas
#from pandas.io.sql import read_sql

import model
app = Flask("hothoods", template_folder=os.path.join(os.curdir, "templates"))

@app.before_request
def db_connect():
    """
    Create a db session after a new connection.
    """
    g.dbsession = model.SQLSession(user="mcdon", host="localhost", port=3306, db="prices")

@app.teardown_request
def db_disconnect(exception=None):
    """
    Close db session when connection is closed.
    """
    g.dbsession.close();

@app.route('/mapinfo.json')
def mapinfo():
    """
    Return general info about all zip codes on the map.
    Used to construct the map when the user lands.
    """
    # Get name of neighborhood
    hoodnames = dict(model.query_hoodnames())
    currentprices = dict(g.dbsession.resolve_query(model.currentpricequery))
    ret = []
    for row in g.dbsession.resolve_query(model.summary_query):
        zip = row[0]
        name = row[1].title()
        price = row[2]
        earlypred = np.exp(row[3])
        pred = np.exp(row[4])
        growth = (pred / earlypred)-1
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
    Used to power the graph.
    """
    if not zipcode:
        raise Exception, 'page_not_found'
    
    # Get name of neighborhood
    hoodnames = model.query_hoodnames(zip=zipcode)
    hoodname = hoodnames[zipcode]
    boroname = model.query_borough(zipcode)
    
    # Get price history
    history = []
    for row in g.dbsession.resolve_query(model.zipquery.format(zipcode=zipcode)):
        history.append({"date": row[0], "price": float(row[1])})
        lasttime = row[0]
        lastprice = float(row[1])
    
    # Get forecast
    if lasttime:
        dateformat = "%Y-%m-%d"
        forecasts = []
        #forecasts = [{"date": lasttime, "price": lastprice, "lo80": lastprice, "hi80": lastprice}]
        forecast_query = g.dbsession.resolve_query(model.forecastquery.format(zipcode=zipcode))
        junctiontime = dt.strptime(lasttime, dateformat) + relativedelta(months=forecast_query[0][0])
        history.append({"date": dt.strftime(junctiontime, dateformat), "price": np.exp(float(forecast_query[0][1]))})
        for row in forecast_query:
            forecasttime = dt.strptime(lasttime, dateformat) + relativedelta(months=row[0]+1)
            forecasts.append({"date": dt.strftime(forecasttime, dateformat), "price": np.exp(float(row[1])), "lo80": np.exp(float(row[2])), "hi80": np.exp(float(row[3]))})
    return(jsonify(boroname=boroname, hoodname=hoodname, prices=history, forecasts=forecasts))

@app.route('/')
def home():
    """
    Serve the actual homepage. 
    Not currently pulling dynamically but could readily be adapted to do so.
    """
    hoodprofiles = [{
            "hoodname": "Flatiron",
            "zipcode": "10010",
            "mapurl": "static/images/flatiron.png",
            "borough": "MANHATTAN",
            "forecast": "+18%",
            "forecast_icon": u"",
            "median_price": "$790k",
            "listing_photo_url": "http://thumbs.trulia-cdn.com/pictures/thumbs_4/ps.56/3/4/9/c/picture-uh=41f4cfb5375514124761694923e9df2-ps=349cf1e32589ec66df2915fa407d3a.jpg",
            "listing_address": "33 E 22nd St #3D",
            "listing_price": "$715,000",
            "listing_url": "http://www.trulia.com/property/3131508837-33-E-22nd-St-3D-New-York-NY-10010#photo-2"
        }, {
            "hoodname": "Central harlem",
            "zipcode": "10037",
            "mapurl": "static/images/centralharlem.png",
            "borough": "MANHATTAN",
            "forecast": "+16%",
            "forecast_icon": u"",
            "median_price": "$185k",
            "listing_photo_url": "http://thumbs.trulia-cdn.com/pictures/thumbs_4/ps.50/f/3/f/8/picture-uh=3c39eb60f81e57a9746535b9b84fd60-ps=f3f8db38d4c436b90d026b68abff647.jpg",
            "listing_address": "2090 Madison Ave #4D",
            "listing_price": "$155,000",
            "listing_url": "http://www.trulia.com/property/3030874641-2090-Madison-Ave-4D-New-York-NY-10037#photo-2"
        }, {
            "hoodname": "East Midtown",
            "zipcode": "10017",
            "mapurl": "static/images/midtowneast.png",
            "borough": "MANHATTAN",
            "forecast_icon": u"",
            "forecast": "+16%",
            "median_price": "$1,270k",
            "listing_photo_url": "http://thumbs.trulia-cdn.com/pictures/thumbs_4/ps.55/8/6/6/c/picture-uh=3475c567d5e3543b564b175b7b3a7f-ps=866cda7b2140d67f38882146d39a677.jpg",
            "listing_address": "333 E 43rd St #PH4",
            "listing_price": "$980,000",
            "listing_url": "http://www.trulia.com/property/3028155277-333-E-43rd-St-PH4-New-York-NY-10017#photo-2"
        }
    ]
    return render_template("index.html", listings=hoodprofiles)

@app.route('/robots.txt')
def robotstxt():
    response = """
    User-agent: *
    Disallow:
    """
    return response


@app.route('/<pagename>')
def regularpage(pagename=None):
    """
    Route not found by the other routes above. May point to a static template.
    """
    if pagename==None:
        raise Exception, 'page_not_found'
    return render_template(pagename)

if __name__ == '__main__':
    print "Starting debugging server."
    app.run(debug=True, host='localhost', port=8000)

