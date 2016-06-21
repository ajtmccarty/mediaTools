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
    m = cls()
    m.__dict__['id'] = None
    m.__dict__['_is_dirty'] = True
    for attr in cls.get_super_attrs():
      m.__dict__[attr] = getattr(cls,attr)[0]
    cls.track_model(m)
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

  def __getattr__(self,attr):
    """
    overrides base __getattr__ functionality to use __dict__
    """
    return self.__dict__.get(attr)

  def __setattr__(self,name,value):
    """
    overrides base __setattr__ functionality to use __dict__
    uses the Python type defined in the specification tuple of the class for 
      validation and will case the 'value' as the Python type if necessary
    uses the optional custom validation function defined in the specification
      tuple if it exists
    prints error messages if it encounters an issue
    """
    #don't allow direct manipulation of __dict__
    if name == "__dict__":
      return True
    if not self.__dict__.has_key(name):
      print("WARNING in ModelBase.__setattr__")
      print("\tNo attr '%s' in this model" % name)
      print("\tSuperclass: %s" % self.superclass)
      return None
    #TYPE VALIDATION
    specification = getattr(self.__class__,name)
    correct_type = specification[1]
    if not isinstance(value,correct_type):
      try:
        value = correct_type(value)
      except:
        print("ERROR in ModelBase.__setattr__")
        print("\tvalue '%s' is of wrong type and cannot be cast as '%s'" % (value,correct_type))
        print("\tclass: %s" % self.__class__)
        return None
    #CUSTOM VALIDATION
    if len(specification) > 3: 
      validator = specification[3]
      result = validator(value)
      if result == True:
        self.__dict__[name] = value
      else:
          print("ERROR in ModelBase.__setattr__")
          print("\tvalue '%s' failed custom validation in '%s'" % (value,validator))
          print("\terror message: " + result)
          print("\tclass: %s" % self.__class__)
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
  the_model = RealClass.create()
  print the_model.title
  print the_model.year
  the_model.title = "Back to the Future"
  the_model.year = "1850"
  the_model.fake = 17
  print the_model.title
  print the_model.year
