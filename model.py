import MySQLdb

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
    
    def resolve_query(self, query, maxrows=0):
        """
        Return an iterator with results from the query.
        """
        self.db.query(query)
        return self.db.store_result().fetch_row(maxrows=maxrows)
