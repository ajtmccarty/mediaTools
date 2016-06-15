# mediaTools
<h3>Tools to examine movie and tv show files with connections to a postgresql database and link to IMDB</h3>

*** WORK IN PROGRESS ***

<p>AllMovies.txt - a text file containing file and directory names of the Movie directory, one per line
                place holder until functionality to retrieve from a given directory is implemented</p>
<p>DatabaseInterface.py - has class DBInterface, which connects to a given Postgresql database using psycopg2
                        the specific database is defined in config.py</p>
<p>MediaClass.py - has class Media and defines the table to store Media objects into in Postgresql
                Media class has instance variables and methods to save into and read from Postgresql 
                table using DatabaseInterface</p>
<p>config.py - file holding configuration information for database connections, movie directory, and file extensions
            of Media objects</p>
<p>getTitles.py - functions to read movie titles from the input file or directory</p>
