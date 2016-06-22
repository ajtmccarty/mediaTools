import datetime

MOVIE_TITLES_FILE = "./Movies/"
MOVIE_FILE_EXTENSIONS = ['avi','mov','wmv','mp4','m4p','m4v','mpg','mpeg', \
                         'mpe','mpv']
DB_SETTINGS = {
  "hostname": "localhost",
  "db_name": "movies",
  "username": "ubuntu",
  "password": "foobar"
}
TYPE_MAPPING = {
  type(None):'NULL',
  bool:'bool',
  float:['real','double'],
  int:['smallint','integer','bigint'],
  long:['smallint','integer','bigint'],
  str:['varchar','text'],
  unicode:['varchar','text'],
  datetime.date:['date'],
  datetime.time:['time','timetz'],
  datetime.datetime:['timestamp','timestamptz'],
  datetime.timedelta:'interval',
  list:'ARRAY',
}