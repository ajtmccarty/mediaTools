from datetime import datetime
from DatabaseInterface import DBInterface

MEDIA_TABLE_NAME = "test"

class Media(object):
  
  """
  Class methods and variables to track all media objects
  """
  #db_attrs_dict stores the instance variables we save into the database
  db_attrs_dict = {}
  db_attrs_dict["id"] = str
  db_attrs_dict["title"] = str
  db_attrs_dict["year"] = int
  #all_objects is a list of all Media objects
  all_objects = []
  #db_interface is a link to the database interface
  db_interface = None
  
  #gets all Media objects from the database
  @staticmethod
  def build_from_database():
    if not Media.db_interface:
      Media.db_interface = DBInterface.get_interface()
    columns = {k:None for k in Media.db_attrs_dict.keys()}
    results = Media.db_interface.get_from_table(MEDIA_TABLE_NAME,columns)
    if len(results) <= 1:
      return None
    attrs = results.pop(0)
    for result in results:
      m = Media()
      for i in range(len(attrs)):
        setattr(m,attrs[i],result[i])

  #returns a list of all the Media objects
  @staticmethod
  def get_media_objects():
    return Media.all_objects
  
  #adds a Media object to Media.all_objects list
  @classmethod
  def track_media_object(cls,obj):
    cls.all_objects.append(obj)
  
  """
  CONSTRUCTOR
  """
  def __init__(self, title="",year=0):
    if not self.db_interface:
      self.db_interface = DBInterface.get_interface()
    self.id = None
    self.dirty = True
    if title:
      self.title = title
    if year:
      self.year = year
    self.extension = None
    self.track_media_object(self)
    
  def __str__(self):
    if self.title:
      return self.title + " (" + str(self.year) + ")"
    else:
      return "Untitled Media Object"
  
  """
  SAVE METHOD
  """
  def save(self):
    if not self.id:
      self.id = self.db_interface.save_to_table(MEDIA_TABLE_NAME,self.dict_translate())
    if self.dirty:
      self.db_interface.save_to_table(MEDIA_TABLE_NAME,self.dict_translate())
    self.dirty = False

  """
  GETTERS AND SETTERS
  """
  def get_title(self):
    try:
      self._title
    except:
      return None
    return self._title

  def set_title(self,title):
    self._title = str(title)
    self.dirty = True
  
  def get_year(self):
    try:
      self._year
    except:
      return None
    return self._year

  def set_year(self,year):
    try:
      year = int(year)
    except:
      print("Tried to set year value for Media object %s to %s" % (self.title, year))
      return
    if (year < 1870) or (year > (datetime.now().year + 10)):
      print("Tried to set year value for Media object %s to %s" % (self.title, year))
      return
    self._year = year
    self.dirty = True
    
  def set_extension(self,ext):
    self._extension = ext
    self.dirty = True
    
  def get_extension(self):
    try:
      self._extension
    except:
      return None
    return self._extension
    
  """
  DICTIONARY REPRESENTATION
  """
  def dict_translate(self):
    keys = self.db_attrs_dict.keys()
    the_dict = {}
    for k in keys:
      if hasattr(self,k):
        the_dict[k] = getattr(self,k,None)
    return the_dict
  
  title = property(get_title,set_title)
  year = property(get_year,set_year)
  extension = property(get_extension,set_extension)
  
if __name__ == "__main__":
  Media.build_from_database()
  for item in Media.get_media_objects():
    print(item)