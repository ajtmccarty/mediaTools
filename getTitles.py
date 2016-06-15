import config

'''
SUMMARY
-------
Read in a list of file names from a plain text file with one file name per line
-------
INPUT: optional path to titles file, defaults to config.MOVIE_TITLES_FILE
OUTPUT: list of strings stripped of white space
'''
def get_titles_from_file(titles_file=""):
  if not titles_file:
    titles_file = config.MOVIE_TITLES_FILE
  try:
    f = open(titles_file,'r')
  except IOError:
    print("No such file as %s" % titles_file)
    return None
  raw_titles = []
  for line in f:
    raw_titles.append(line.strip())
  f.close()
  return raw_titles


'''
SUMMARY
-------
Take in a list of raw titles and return 3-tuples with the title, year, and 
file extension
-------
INPUT: list of raw title strings
OUTPUT: list of 3-tuples (title,year,file extension)
'''
def parse_titles(title_list):
  parsed_titles = []
  for raw_title in title_list:
    raw_title, ext = parse_extension(raw_title)
    raw_title, year = parse_year(raw_title)
    raw_title = raw_title.strip()
    parsed_titles.append((raw_title,year,ext))
    if not year:
      print("WARNING:File %s does not appear to have a year" % raw_title)
  return parsed_titles
  
'''
SUMMARY
-------
Parse the file extension, if it exists, from the title and return title
without the extension
-------
INPUT: raw title
OUTPUT: 2-tuple (title without extension, parsed extension)
        ie ("This movie (1999)","mp4")
'''
def parse_extension(title):
  last_period_ind = title.rfind('.')
  #if there's a period, check if it's for a file extension
  if last_period_ind == -1:
      return (title,"")
  poss_extension = title[last_period_ind+1:]
  #if file extension, save the extension, and remove it from title
  if poss_extension in config.MOVIE_FILE_EXTENSIONS:
    title = title[:last_period_ind]
    return (title,poss_extension)
  else:
    return (title, "")

'''
SUMMARY
-------
Parse the file year, if it exists, from the title and return title
without the year
-------
INPUT: raw title
OUTPUT: 2-tuple (title without year, parsed year as an int)
        ie ("This movie",1999)
'''
def parse_year(title):
  left_par_ind = title.rfind('(')
  right_par_ind = title.rfind(')')
  if (left_par_ind == -1) or (right_par_ind == -1):
    return (title, 0)
  year = title[left_par_ind+1:right_par_ind].strip()
  if len(year) != 4:
    return (title, 0)
  try:
    year = int(year)
  except:
    return (title, 0)
  title = title[:left_par_ind].strip()
  return (title,year)

if __name__ == "__main__":
  x = get_titles_from_file()
  y = parse_titles(x)
#  for item in y:
#    print item