# SI507 Final Project
This project crawls and scrapes IMDb.com with the goal of aggregating top rated movies data. It provides an interactive command line prompt for users to select movies satisfying certain condition, see graphical charts of movie genres and watch related trailers.
## Data Sources
IMDb: Highest Rated IMDb "Top 250"
<br><http://www.imdb.com/chart/top>
<br> The project starts scraping and crawling at this page and from here crawls the detail page for each movie on the IMdb chart to extract additional information.
<br> p.s. do not need any API key or client secret
## Getting Started
### set up an environment using requirements.txt
1. create a virtual environment `$ virtualenv venv` 
2. activate the virtual environment `$ source venv/bin/activate`
3. do a pip install from requirements.txt `(venv) $ pip install -r requirements.txt`
### initialize Plotly 
instruction: <https://plot.ly/python/getting-started/>
1. create an account: <https://plot.ly/> 
2. set credentials
```python
import plotly
plotly.tools.set_credentials_file(username='your Plotly username', api_key='your Plotly API key')
```
(find your API key: <https://plot.ly/settings/api>)

## Code Structure
1. implement Movie class
<br> - each Movie instance is created by given the values of title, year, IMDb_rating and IMDb_id 
<br> - each Movie instance has the attributions: title, year, IMDb_rating, IMDb_id, runtime, genre, language and trailer   

2. crawl and scrape the related IMDb website with cache
<br> - function: get_top_movies() 
<br> - access the IMDb top 250 movies homepage and each movie's detail page, get the HTML associated with them, cache the data in the file imdb_movies_cache.json (first-level cache), use Beautiful Soup to parse HTML and search particular elements to retrieve the needed information

3. create a dictionary named movies_dict from a list of Movie instances
<br> - function: movies_to_dict(movies_list):
<br> - dictionary keys: IMDb rankings of each movie on the top 250 chart
<br> - dictionary values: dictionaries that record movie information, such as year and so on
<br> - sample movies_dict: `{1: {"title": "The Shawshank Redemption", "year": "1994", "imdb_rating": "9.2", "imdb_id": "tt0111161", "runtime": "2h 22min", "genre": ["Crime", "Drama"], "language": "English", "trailer": "http://www.imdb.com/videoplayer/vi3877612057?playlistId=tt0111161&ref_=tt_ov_vi"},...}` 
<br> - write out the dictionary to a file movies_dict_cache.json (second-level cache)    

4. create database (imdb_top_movies.sqlite) and populate it
<br> - function: init_db(); insert_movies_data(movies_dict)
<br> - database contains two tables: movie, genre
<br> - when write data into database, load the dictionary movies_dict from movies_dict_cache.json to shorten the running time of the program

## User Guide
### run the test file (unit testing)
`$ python3 movies_test.py`
### run the program
`$ python3 movies.py`
<br> (if do not want to use the provided caches, but re-create them from beginning: delete those two cache files('..._cache.json') in the folder before run this python file)
### choose command line options
* **exit**
<br> - description: exits the program
* **help**
<br> - description: lists available commands
* **all**
<br> - description: displays all the top 250 movies with their information in tabular form
<br> - sample command: `Enter command (or 'help' for options): all`
* **genre \<name of a genre>**
<br> - description: lists top 5 movies belonging to the specified genre with their information in tabular form
<br> - valid input range: crime, drama, action, thriller, biography, history, adventure, fantasy, western, romance, sci-fi, mystery, family, comedy, war, animation, horror, music, musical, film-noir, sport
<br> - sample command: `Enter command (or 'help' for options): genre action`
* **year \<a year>**
<br> - description: lists top 5 movies that released in the specified year with their information in tabular form
<br> - sample command: `Enter command (or 'help' for options): year 2000`
* **watch \<IMDb_ranking of a movie>**
<br> - description: launchs the IMDb video page of the movie in a web browser (user could watch its trailer on that page)
<br> - valid input range: from 1 to 250
<br> - sample command: `Enter command (or 'help' for options): watch 1`
* **visualization genre proportion**
<br> - description: displays a pie chart of the genres of these top movies on plotly page in web browser
<br> - sample command: `Enter command (or 'help' for options): visualization genre proportion`
* **visualization genre rating**
<br> - description: displays a graph of the average ratings for different genres on plotly page in web browser
<br> - sample command: `Enter command (or 'help' for options): visualization genre rating`
