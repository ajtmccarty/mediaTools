import psycopg2

from config import DB_SETTINGS

class DBInterface(object):

  the_interface = None
  
  """
  CONSTRUCTOR
  Will only allow a single instance of DBInterface to exist
  Returns an instance of DBInterface, creates one if it doesn't exist
  """
  @staticmethod
  def get_interface():
    if DBInterface.the_interface:
      return DBInterface.the_interface
    DBInterface.the_interface = DBInterface()
    return DBInterface.the_interface
  
  """  
  INIT
  Saves the connection settings from DB_SETTINGS in config.py
  Sets connection and cursor to None
  """
  def __init__(self):
    self.the_connection = None
    self.the_cursor = None
    self.hostname = DB_SETTINGS["hostname"]
    self.db_name = DB_SETTINGS["db_name"]
    self.username = DB_SETTINGS["username"]
    self.password = DB_SETTINGS["password"]

  """
  SUMMARY: attempts to establish connection to database defined in config.py
  INPUT: None
  OUTPUT: None
  """
  def connect(self):
    #do nothing if the connection is already established
    if self.is_connected() and self.has_cursor():
      return
    if not self.is_connected():
      conn_string = ""
      if self.hostname:
        conn_string += "host=" + self.hostname + " "
      if self.db_name:
        conn_string += "dbname=" + self.db_name + " "
      if self.username:
        conn_string += "user=" + self.username + " "
      if self.password:
        conn_string += "password=" + self.password
      try:
        connection = psycopg2.connect(conn_string)
      except psycopg2.Error as e:
        print("Error in DatabaseInterface.connect")
        print("Unable to connect to database with given connections string")
        print("Connection parameters: " + conn_string)
        raise e
      self.the_connection = connection
    if not self.has_cursor():
      self.the_cursor = self.the_connection.cursor()
    
  """
  SUMMARY: True if open connection, False if not
  INPUT: None
  OUTPUT: None
  """
  def is_connected(self):
    if not self.the_connection:
      return False
    if self.the_connection.closed:
      return False
    return True

  """
  SUMMARY: True if open cursor, False if not
  INPUT: None
  OUTPUT: None
  """
  def has_cursor(self):
    if not self.the_cursor:
      return False
    if self.the_cursor.closed:
      return False
    return True
    
  """
  SUMMARY: Close the connection and reset the_connection instance variable
  INPUT: None
  OUTPUT: None
  """
  def close_connection(self):
    self.the_cursor.close()
    self.the_cursor = None
    self.the_connection.close()
    self.the_connection = None

  """
  SUMMARY: Checks if a table exists in the database
  INPUT: table name for query
  OUTPUT: True if table exists, False if otherwise
  """
  def does_table_exist(self,tablename):
    #make sure the connection is established
    self.connect()
    with self.the_connection.cursor() as cursor:
      query_string = """SELECT 1 
                        FROM information_schema.tables 
                        WHERE table_name=(%(tablename)s);"""
      self.the_cursor.execute(query_string,{'tablename':tablename})
      #if the query returned anythign at all, then the table exists
      if self.the_cursor.fetchone():
        return True
      else:
        return False

  """
  SUMMARY: inserts or updates a row in the given table as appropriate
           if the value_dict containes an 'id' then we can assume the row already
           exists, otherwise there would be no way to know the id
  INPUT: tablename
         value_dict containing columns and values to set in database
  OUTPUT: if this is an insert (and not an update) then return the id so the
          object can save it
  """
  def save_to_table(self,tablename,value_dict):
    the_id = None
    #if there is an id, then this row has already been inserted and should be updated
    if ("id" in value_dict) and value_dict["id"]:
      self.update_row(tablename,value_dict)
    #otherwise, we should insert the row and return its id
    else:
      #if the id is in the value_dict, it is False, None, or 0 and we should
      #delete it so that we don't try to insert it
      if "id" in value_dict: del value_dict["id"]
      the_id = self.insert_row(tablename,value_dict)
    if the_id:
      return the_id
  
  """
  SUMMARY: inserts the row and returns the id
  INPUT: tablename
         value_dict with columns and values to insert
  OUTPUT: the id of the inserted row
  """
  def insert_row(self,tablename,value_dict):
    #build string to insert row
    insert_string = "INSERT INTO " + tablename + " "
    insert_string += "(" + ",".join(value_dict.keys()) + ") "
    insert_string += "VALUES ("
    insert_string += ", ".join(["%("+key+")s" for key in value_dict.keys()])
    insert_string += ") RETURNING id;"
    #make sure connected to db
    self.connect()
    try:
      self.the_cursor.execute(insert_string,value_dict)
    except psycopg2.Error as e:
      print("Error inserting row in DatabaseInterface.insert_row")
      print("Query string: "+self.the_cursor.query)
      raise e
    the_id = self.the_cursor.fetchone()[0]
    self.the_connection.commit()
    return the_id

  """
  SUMMARY: update the row with the given id
  INPUT: tablename
         value_dict with columns and values to update
  OUTPUT: nothing
  """
  def update_row(self,tablename,value_dict):
    if ("id" not in value_dict) or (not value_dict["id"]):
      print("Error in DatabaseInterface.update_row")
      print("Cannot update a row without an id")
      print("Input table: " + tablename)
      print("Input values: " + str(value_dict))
    update_string = "UPDATE " + tablename +" SET "
    value_string_list = [key+" = %("+key+")s" for key in value_dict.keys() if key != "id"]
    update_string += ", ".join(value_string_list)
    update_string += " WHERE id = %(id)s;"
    self.connect()
    try:
      self.the_cursor.execute(update_string,value_dict)
    except psycopg2.Error as e:
      print("Error updating in DatabaseInterface.update_row")
      print("Query string: "+self.the_cursor.query)
      raise e
    self.the_connection.commit()

  """
  SUMMARY: retrieve the given column_dict from the given table
  INPUT: tablename
         column_dict, dict of column_dict to retrieve
            each key is a column for the SELECT clause
            values (optional) are used in the WHERE clause

  OUTPUT: list of tuples containing the input columns
          first tuple is a list of the columns to give the ordering
  """
  def get_from_table(self, tablename, column_dict):
    #make sure column_dict is a dictionary
    if not isinstance(column_dict,dict):
      print("Error in DatabaseInterface.get_from_table")
      print("Expected column_dict variable to be a dict")
      print("column_dict: " + str(column_dict))
    #sort the column_dict for the query so we know the order of the tuple values
    ordered_columns = sorted(column_dict.keys())
    #build the base query string
    query_string = "SELECT "
    query_string += ", ".join(ordered_columns)
    query_string += " FROM " + tablename
    #determine if a WHERE clause is necessary and get the values
    has_values = False
    where_list = []
    for col in ordered_columns:
      val = column_dict.get(col,None)
      #if this key does not have a value, remove it so that 
      if not val:
        continue
      if not has_values:
        has_values = True
      where_list.append(col)
    if has_values:
      where_string = " WHERE "
      where_string += ", ".join([col + " = %(" + col + ")s" for col in where_list])
      query_string += where_string
    query_string += ";"
    self.connect()
    try:
      self.the_cursor.execute(query_string,column_dict)
    except psycopg2.Error as e:
      print("Error in DatabaseInterface.get_from_table")
      print("Query failed")
      print("Attempted query: " + self.the_cursor.query)
      raise e
    results = self.the_cursor.fetchall()
    results.insert(0,tuple(ordered_columns))
    return results
  
if __name__ == "__main__":
  DB = DBInterface()
  DB.connect()
  print("Is connected?")
  print(DB.is_connected())
  print("Does 'test' exist?")
  print(DB.does_table_exist('test'))
  print("Does 'fake_table' exist?")
  print(DB.does_table_exist('fake_table'))
  q_dict = {"id":None,"title":"Tango and Cash","year":None}
  print DB.get_from_table("test",q_dict)
  DB.close_connection()
