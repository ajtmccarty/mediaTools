import config
from datetime import datetime
from ModelBase import ModelBase

def year_validator(year):
  if not isinstance(year,int):
    try:
      year = int(year)
    except:
      return False
  if (year < 1870) or (year > datetime.now().year + 10):
    return False
  return True

class RawMediaFile(ModelBase):
  """
  Class methods and variables to track all media objects
  """
  id = (None,int,"serial PRIMARY KEY")
  title = (None,str,"varchar")
  release_year = (None,int,"integer",year_validator)
  filename = (None,str,"varchar")

if __name__ == "__main__":
  m = RawMediaFile.create()
  assert(m.id == None)
  assert(m.release_year == None)
  m.release_year = "2090"
  assert (m.release_year == None)
  m.release_year = 1850
  assert (m.release_year == None)
  m.release_year = "2000"
  assert (m.release_year == 2000)