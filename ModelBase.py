from inspect import getmembers
from DatabaseInterface import DBInterface

class ModelBase(object):
  """
  The Base Model class
  
  All other models should be based on this class
  
  Creates an 'id' value and initializes it to None
  Models can set their own instance variables by declaring them as class
    variables and setting a specification tuple like so
    
    class TheClass(ModelBase):
      title = (default,pythonType,SQLType,validationFunction)
    
    where 
      default is a default value for intialization
      pythonType is a Python type for the value, used in validation
      SQLType is a string representing an SQL type such as "integer" or "varchar"
        used when saving the value to the database or creating the table
      validationFunction (optional) a function that takes one argument and
        returns either True or an error message
        
  Instances should only be created using the "create" method of the model, such as
    
    the_class_instance = TheClass.create()
  """
  #holds the one database connection for all models
  db_interface = DBInterface.get_interface()
  
  #dict to track all model instances
  #key is the class and value is a list of all instances
  all_models = {}
  
  #holds model-specific information
  model_data = {}
  
  @classmethod
  def get_all_models(cls):
    """
    returns a list of all instances of a given model class
    instances are tracked in ModelBase.all_models
    """
    if not ModelBase.all_models.has_key(cls):
      return []
    return ModelBase.all_models[cls][:]
    
  @classmethod
  def track_model(cls,model):
    """
    adds an instance of a model to the tracking dictionary, ModelBase.all_models
    """
    if ModelBase.all_models.has_key(cls):
      ModelBase.all_models[cls].append(model)
    else:
      ModelBase.all_models[cls] = [model]
  
  @classmethod
  def create(cls):
    """
    returns a new instance of the Model
    initializes the __dict__ attribute using the specification tuple from the 
    class from which it is called
    """
    m = ModelBase()
    m.__dict__['attrs'] = {'id':None}
    m.__dict__['status'] = {'_is_dirty':True}
    m.__dict__['status']['child_class'] = cls
    for attr in cls.get_super_attrs():
      m.__dict__['attrs'][attr] = getattr(cls,attr)[0]
    cls.track_model(m)
    m.set_tablename()
    return m
  
  @classmethod
  def get_super_attrs(cls):
    """
    returns strings representing the attribute names of the calling class
    only returns attributes that are not part of ModelClass
    it should only return the names of the specification tuples
    uses inspect.getmembers
    """
    all_attrs = [x[0] for x in getmembers(cls)]
    model_base_attrs = [x[0] for x in getmembers(ModelBase)]
    super_attrs = []
    for attr in all_attrs:
      #skip it if it's a builtin
      if attr.startswith('__'):
        continue
      #skip it if it's in ModelBase
      if attr in model_base_attrs:
        continue
      super_attrs.append(attr)
    return super_attrs

  def set_tablename(self):
    """
    creates the tablename and saves it into the ModelBase.model_data dict at 
    model_data['tablename']
    the tablename is just the all lowercase classname with '_table' appended
    """
    the_class = self.child_class
    if not ModelBase.model_data.has_key(the_class):
      ModelBase.model_data[the_class] = {}
    if not ModelBase.model_data[the_class].has_key("tablename"):
      the_name = the_class.__name__.lower() + "_table"
      ModelBase.model_data[the_class]["tablename"] = the_name
    
    
  def get_tablename(self):
    """
    retrieves the tablename from ModelBase.model_data["tablename"]
    """
    return ModelBase.model_data[self.child_class]['tablename']
    
  def __getattr__(self,attr):
    """
    overrides base __getattr__ functionality to use __dict__
    """
    if attr.lower() == 'tablename':
      return self.get_tablename()
    if self.__dict__['status'].has_key(attr):
      return self.__dict__['status'].get(attr)
    if self.__dict__['attrs'].has_key(attr):
      return self.__dict__['attrs'].get(attr)
    return None

  def __setattr__(self,name,value):
    """
    overrides base __setattr__ functionality to use __dict__
    uses the Python type defined in the specification tuple of the class for 
      validation and will case the 'value' as the Python type if necessary
    uses the optional custom validation function defined in the specification
      tuple if it exists
    prints error messages if it encounters an issue
    """
    #don't allow direct setting of __dict__
    if name == "__dict__":
      return
    if self.__dict__['status'].has_key(name):
      self.__dict__['status'][name] = value
      return None
    if not self.__dict__['attrs'].has_key(name):
      print("WARNING in ModelBase.__setattr__")
      print("\tNo attr '%s' in this model" % name)
      print("\tSuperclass: %s" % self.superclass)
      return None
    #TYPE VALIDATION
    specification = getattr(self.child_class,name)
    correct_type = specification[1]
    if not isinstance(value,correct_type):
      try:
        value = correct_type(value)
      except:
        print("ERROR in ModelBase.__setattr__")
        print("\tvalue '%s' is of wrong type and cannot be cast as '%s'" % (value,correct_type))
        print("\tclass: %s" % self.child_class)
        return None
    if len(specification) <= 3:
      #set the value if there is not custom validation
      self.__dict__['attrs'][name] = value
      return None
    #CUSTOM VALIDATION
    validator = specification[3]
    result = validator(value)
    if result == True:
      self.__dict__['attrs'][name] = value
    else:
        print("ERROR in ModelBase.__setattr__")
        print("\tvalue '%s' failed custom validation in '%s'" % (value,validator))
        print("\terror message: " + result)
        print("\tclass: %s" % self.child_class)
        return None

### NOTES ###
#class-wide database connection
#id
#isDirty
#attrs/columns
#   name
#   python data type
#   SQL data type
#   default value
#tablename
#SQL table
#   check existence
#   create table
#   update table with new or removed attributes
#   reset table
#   save
#   retrieve



### EVERYTHING BELOW THIS LINE IS FOR TESTING ###
def year_validator(year):
  if year < 1870:
    return "Year must be greater than 1869"
  return True

class RealClass(ModelBase):
  title = (None,str,"varchar")
  year = (None,int,"integer",year_validator)

if __name__ == "__main__":
  m1 = RealClass.create()
  m2 = RealClass.create()
  m1.title = "Back to the Future"
  m1.year = "1850"
  m1.fake = 17
  assert (m1.title == "Back to the Future")
  assert (m1.year == None)
  assert (m1.fake == None)
  assert (m1 != m2)
  assert (m1.db_interface == m2.db_interface)
  assert (m1 in RealClass.get_all_models())
  assert (m2 in RealClass.get_all_models())
  m2.year = "2000"
  assert (m2.year == 2000)
  assert (m1._is_dirty)
  assert (m2._is_dirty)
  assert (m1.get_tablename() == "realclass_table")