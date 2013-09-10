import os
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

hoodnamequery = """
SELECT 
Neighborhood
FROM hoodnames 
WHERE (ZipCode='{zipcode}');
"""

zipquery = """
SELECT 
SaleDate AS SaleDate, ppsqft
FROM zipmedians 
WHERE (ZipCode='{zipcode}')
ORDER BY SaleDate;
"""

def default(obj):
    """Default JSON serializer."""
    import calendar, datetime

    if isinstance(obj, datetime.datetime):
        if obj.utcoffset() is not None:
            obj = obj - obj.utcoffset()
    millis = int(
        calendar.timegm(obj.timetuple()) * 1000 +
        obj.microsecond / 1000
    )
    return millis

@app.route('/zip/<zipcode>')
def ziptrend(zipcode=None):
    """
    Route not found by the other routes above. May point to a static template.
    """
    if not zipcode:
        raise Exception, 'page_not_found'
    
    # Get name of neighborhood
    db.query(hoodnamequery.format(zipcode=zipcode))
    dbresult = db.store_result()
    hoodname = dbresult.fetch_row(maxrows=1)[0][0].title()
    
    # Get price history
    db.query(zipquery.format(zipcode=zipcode))
    dbresult = db.store_result()
    ret = []
    for row in dbresult.fetch_row(maxrows=0):
        ret.append({"SaleDate": str(row[0]), "ppsqft": float(row[1])})
    
    return(jsonify(hoodname=hoodname, prices=ret))

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

