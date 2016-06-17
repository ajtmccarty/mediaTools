class TableDef(object):
  
  """
  can be initialized with just a table name
  or a dictionary of columns in this format
    col["name"] = columna name
    col["python_type"] = Python type of database
    col["sql_type"] = SQL type of data
  id column is always initialized
  """
  def __init__(self,tablename,columns=[]):
    self.tablename = tablename
    self.columns = [ColumnDef("id",int,"serial PRIMARY KEY")]
    for col in columns:
      self.columns.append(ColumnDef(col["name"],col["python_type"],col["sql_type"]))

  """
  adds a column with a given name, Python type and SQL type
  """
  def add_column(self,name,python_type,sql_type):
    self.columns.append(ColumnDef(name,python_type,sql_type))

  """
  builds the statement to create the table in SQL
  """
  def get_creation_string(self):
    creation_string = "CREATE TABLE " + self.tablename + " ("
    col_list = [col.name+" "+col.sql_type for col in self.columns]
    creation_string += ", ".join(col_list) + ");"
    return creation_string

"""
simple Python class to hold column information
"""
class ColumnDef(object):
  def __init__(self,name,python_type,sql_type):
    self.name = name
    self.python_type = python_type
    self.sql_type = sql_type