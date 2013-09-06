import os
from flask import Flask, render_template, jsonify, Response
import json
from json import JSONEncoder
import MySQLdb
from pandas.io.sql import read_sql

db = MySQLdb.connect(user="mcdon", host="localhost", port=3306, db="prices")
c = db.cursor()

app = Flask("PsiTurk", template_folder=os.path.join(os.curdir, "templates"))

zipquery = """
SELECT 
MAX(SaleDate) AS SaleDate,
AVG(SalePrice),
GrossSquareFeet,
AVG(SalePrice / GrossSquareFeet) AS ppsqft
FROM sales 
WHERE 
       GrossSquareFeet > 100
   AND SalePrice > 5000 
   AND TotalUnits > 0 
   AND NOT Address = 0 
   AND (SalePrice / GrossSquareFeet) > 30
   AND (ZipCode='{zipcode}')
GROUP BY YEAR(SaleDate), MONTH(SaleDate)
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
    if zipcode==None:
        raise Exception, 'page_not_found'
    #ret_frame = read_sql(zipquery.format(zipcode=zipcode), db)
    #ret = {}
    #ret["ppsqft"] = JSONEncoder.default(ret_frame["ppsqft"])
    #ret["SaleDate"] = ret_frame["SaleDate"]
    db.query(zipquery.format(zipcode=zipcode))
    dbresult = db.store_result()
    #cols = ["SaleDate", "SalePrice", "GrossSquareFeet", "ppsqft"]
    ret = []
    for row in dbresult.fetch_row(maxrows=0):
        #ret["SaleDate"].append(str(row[0]))
        #ret["ppsqft"].append(float(row[3]))
        ret.append({"SaleDate": str(row[0]), "ppsqft": float(row[3])})
    #ret = ret.fetch_row(maxrows=0);
    #print ret
    #ret = [dict(zip(cols, r)) for r in ret.
    #return(Response(json.dumps(ret, default=default), mimetype="text/json"))
    
    return(jsonify(prices=ret))

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

