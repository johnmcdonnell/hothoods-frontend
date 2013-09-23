import MySQLdb
from flask import g

class SQLSession:
    """
    Poor man's ORM, tracks SQL connection and performs queries.
    """
    def __init__(self, *args, **kwargs):
        """
        Args: see MySQLdb.connect
        """
        self.db = MySQLdb.connect(*args, **kwargs)
        self.c = self.db.cursor()
    
    def close(self):
        self.db.close()
    
    def resolve_query(self, query, maxrows=0):
        """
        Return an iterator with results from the query.
        """
        self.db.query(query)
        return self.db.store_result().fetch_row(maxrows=maxrows)

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
    for results in g.dbsession.resolve_query(hoodnamequery):
        ret[results[0]] = results[1].title()
    return ret

def query_borough(zip):
    boroquery = """
        SELECT Borough FROM sales 
        WHERE ZipCode={zipcode} LIMIT 1""".format(zipcode=zip)
    return g.dbsession.resolve_query(boroquery)[0][0]
