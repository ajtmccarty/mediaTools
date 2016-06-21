from inspect import getmembers
from DatabaseInterface import DBInterface
from config import TYPE_MAPPING

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
    result = cls.check_model()
    if result != True:
      print(result)
      return None
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
  def check_model(cls):
    this_func_name = "ModelBase.check_model"
    if ModelBase.model_data.has_key(cls) and  \
       ModelBase.model_data[cls].has_key("has_been_checked") and \
       ModelBase.model_data[cls]["has_been_checked"] == True:
        return True
    for attr in cls.get_super_attrs():
      spec_tuple = getattr(cls,attr)
      if type(spec_tuple[0]) not in TYPE_MAPPING.keys():
        #error message 0
        return error_message(this_func_name,0,(cls,spec_tuple[0],type(spec_tuple[0])))
      if spec_tuple[1] not in TYPE_MAPPING.keys():
        #error message 1
        return error_message(this_func_name,1,(cls,spec_tuple[1]))
      sql_types = []
      for val in TYPE_MAPPING.values():
        if isinstance(val,list):
          sql_types += val
        else:
          sql_types.append(val)
      if spec_tuple[2] not in sql_types:
        #error message 2
        return error_message(this_func_name,2,(cls,spec_tuple[2]))
      if len(spec_tuple) > 3:
        if not hasattr(spec_tuple[3],'__call__'):
          #error message 3
          return error_message(this_func_name,3,(cls,spec_tuple[3]))
      if spec_tuple[0] != None:
        if type(spec_tuple[0]) != spec_tuple[1]:
          #error message 4
          return error_message(this_func_name,4,(cls,spec_tuple[0],spec_tuple[1]))
    if not ModelBase.model_data.has_key(cls): 
      ModelBase.model_data[cls] = {}
    if not ModelBase.model_data[cls].has_key("has_been_checked"): 
      ModelBase.model_data[cls]["has_been_checked"] = True
    return True
  
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
    this_func_name = "ModelBase.__setattr__"
    if name == "__dict__":
      return
    if self.__dict__['status'].has_key(name):
      self.__dict__['status'][name] = value
      return None
    if not self.__dict__['attrs'].has_key(name):
      #error message 5
      print(error_message(this_func_name,5,(name,self.child_class)))
      return None
    #TYPE VALIDATION
    specification = getattr(self.child_class,name)
    correct_type = specification[1]
    if not isinstance(value,correct_type):
      try:
        value = correct_type(value)
      except:
        #error message 6
        print(error_message(this_func_name,6,(value,correct_type,self.child_class)))
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
        #error message 7
        print(error_message(this_func_name,7,(value,validator,result,self.child_class)))
        return None

def error_message(caller,err_num,tup):
  err_dict = {}
  err_dict[0] =  ["Class: %s has a default value of %s with type %s", \
                  "Supported default value types are the keys in config.TYPE_MAPPING"]
  err_dict[1] = ["Class: %s has a Python type of %s, which is not supported", \
                 "Supported Python types are the keys in config.TYPE_MAPPING"]
  err_dict[2] = ["Class: %s has an SQL type of %s, which is not supported", \
                 "Supported SQL types are the values in config.TYPE_MAPPING"]
  err_dict[3] = ["Class: %s has validator %s, which is not a function", \
                 "Item 4 must a function that takes one arg and returns a boolean"]
  err_dict[4] = ["Class: %s has has default value %s, which is not of Python type %s", \
                 "The default value must be None or the Python type in item 2"]
  err_dict[5] = ["No attr '%s' in this model",\
                 "Class: %s"]
  err_dict[6] = ["Value '%s' is of wrong type and cannot be cast as '%s'",\
                 "Class: %s"]
  err_dict[7] = ["Value '%s' failed custom validation in '%s'", \
                 "Error message from validator: %s", \
                 "Class: %s"]
  final_message = "ERROR in " + caller + "\n"
  for line in err_dict[err_num]:
    final_message += "\t" + line + "\n"
  return final_message % tup


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
if __name__ == "__main__":
  def year_validator(year):
    if year < 1870:
      return "Year must be greater than 1869"
    return True
  
  class RealClass(ModelBase):
    title = (None,str,"varchar")
    year = (None,int,"integer",year_validator)
  
  class GoodModel(ModelBase):
    valid_attr = ("valid",str,"varchar")
    valid_attr2 = (True,bool,"bool")
    valid_attr3 = (17,int,"smallint",lambda x:x>10)
  
  class BadModel1(ModelBase):
    invalid_attr = (type,str,"varchar")
    
  class BadModel2(ModelBase):
    invalid_attr2 = (None,17,"text")
  
  class BadModel3(ModelBase):
    invalid_attr3 = (None,str,"NOTSQL")
  
  class BadModel4(ModelBase):
    invalid_attr4 = (17,str,"integer")

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
  assert (GoodModel.check_model() == True)
  assert (BadModel1.create() == None)
  assert (BadModel2.create() == None)
  assert (BadModel3.create() == None)
  assert (BadModel4.create() == None)
