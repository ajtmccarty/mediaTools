import getTitles
import sys

from MediaClass import Media

def print_usage():
  print("There is only one option right now:")
  print("extract file(optional)")

if __name__ == "__main__":
  for i in range(1,len(sys.argv)):
    arg = sys.argv[i]
    if arg.lower() == "extract":
      the_file = None
      if i < (len(sys.argv)-1):
        the_file = sys.argv[i+1]
        i += 2
      else:
        i += 1
      if the_file:
        raw_titles = getTitles.get_titles_from_file(the_file)
      else:
        raw_titles = getTitles.get_titles_from_file()
      parsed_titles = getTitles.parse_titles(raw_titles)
      for item in parsed_titles:
        m = Media()
        m.title = item[0]
        m.year = item[1]
        m.save()
    else:
      print_usage()