# SI 507 Final Project
# Ran Bi
# Section 004, Monday, 7pm

## Something about Caching:
#if do not want to use provided caches, but to re-create them from beginning:
#       delete those two cache files('..._cache.json') in the folder before run this python file
#if do not want to use caches at all:
#       uncomment all the option B and comment all the option A in this script and then run it

import re
import requests
import json
from bs4 import BeautifulSoup
import sqlite3
import webbrowser
import pandas as pd
from pandas import Series
from prettytable import from_db_cursor
import plotly.plotly as py
import plotly.graph_objs as go


## Define Class and Functions:

CACHE_1='imdb_movies_cache.json'    #first-level cache
CACHE_2='movies_dict_cache.json'    #second-level cache
try:
    cache_file=open(CACHE_1, 'r')
    cache_contents=cache_file.read()
    CACHE_DICTION=json.loads(cache_contents)
    cache_file.close()
except:
    CACHE_DICTION={}

def make_request_using_cache(url):
    #look in the cache to see if already have this data
    if url in CACHE_DICTION:
        return CACHE_DICTION[url]
    #if not, fetch the data afresh, add it to the cache, write the cache to file
    else:
        re_page=requests.get(url).text
        CACHE_DICTION[url]=re_page
        dumped_json_cache=json.dumps(CACHE_DICTION)
        fw=open(CACHE_1,"w")
        fw.write(dumped_json_cache)
        fw.close()
        return CACHE_DICTION[url]


###################################################
## Class -- Movie                                ##
## attributes: title, year, imdb_rating, imdb_id ##
##             runtime, genre, language, trailer ##
###################################################
class Movie:
    def __init__(self, title=None, year=None, imdb_rating=None, imdb_id=None):
        self.title=title
        self.year=year
        self.imdb_rating=imdb_rating
        self.imdb_id=imdb_id
        ##crawl and scrape each movie's page
        movie_url='http://www.imdb.com/title/'+self.imdb_id
        movie_page=make_request_using_cache(movie_url)    ##option A -- use cache
        #movie_page=requests.get(movie_url).text          ##option B -- not use cache
        movie_soup=BeautifulSoup(movie_page, 'html.parser')
        #runtime
        self.runtime=movie_soup.find_all(itemprop='duration')[0].text.strip()
        #genre
        gen=[]
        g1=movie_soup.find(class_='see-more inline canwrap',itemprop='genre')
        g2=g1.find_all('a')
        for g in g2:
            gen.append(g.text.strip())
        #genre
        self.genre=gen
        #language
        l1=movie_soup.find(class_='article', id='titleDetails').text.strip()
        l2=l1.replace('\n',' ')
        l3=re.search(r'Language:(.+?)Release',l2)
        if l3 is None:
            self.language='unknown'
        else:
            l4=l3.group(1).replace(' ','')
            self.language=l4.replace('|',', ')
        #trailer
        t1=movie_soup.find(class_='slate')
        if t1 is None:
            self.trailer='no trailer'
        else:
            t2=t1.find('a',class_='slate_button prevent-ad-overlay video-modal')['href']
            t3='http://www.imdb.com/videoplayer/'+t2[12:]
            self.trailer=t3


###################################################
## Function -- get_top_movies                    ##
## return: a list of Movie instances             ##
###################################################
def get_top_movies():
    #imdb top 250 movies
    baseurl='http://www.imdb.com/chart/top'
    re_page=make_request_using_cache(baseurl)    ##option A -- use cache
    #re_page=requests.get(baseurl).text          ##option B -- not use cache
    soup=BeautifulSoup(re_page, 'html.parser')
    soup_title=soup.find_all('td', {'class': 'titleColumn'})
    soup_rating=soup.find_all('td', {'class': 'ratingColumn imdbRating'})
    movies_list=[]
    for i in range(len(soup_title)):
        ##scrape top 250 homepage
        #title
        movie_title=soup_title[i].find('a').text.strip()
        #year
        movie_year=soup_title[i].find('span').text[1:5]
        #rating
        movie_imdb_rating=soup_rating[i].text.strip()
        #crawl to each movie's page by the imdb_id (this part is in class Movie)
        #imdb_id
        movie_imdb_id=soup_title[i].find('a')['href'].split('/')[2]
        #create Movie instance for each movie
        mm=Movie(title=movie_title,year=movie_year,imdb_rating=movie_imdb_rating,imdb_id=movie_imdb_id)
        movies_list.append(mm)
    return movies_list


###################################################
## Function -- movies_to_dict                    ##
## param: a list of Movie instances              ##
## return: a dictionary(keys are the rankings of ##
## each movie, each of which is associated value ##
## is that movie's information (title,year,etc)) ##
###################################################
def movies_to_dict(movies_list):
    movies_dict=dict()
    for i in range(len(movies_list)):
        di=dict()
        di['title']=movies_list[i].title
        di['year']=movies_list[i].year
        di['imdb_rating']=movies_list[i].imdb_rating
        di['imdb_id']=movies_list[i].imdb_id
        di['runtime']=movies_list[i].runtime
        di['genre']=movies_list[i].genre
        di['language']=movies_list[i].language
        di['trailer']=movies_list[i].trailer
        movies_dict[i+1]=di
    return movies_dict

def load_movies_dict_using_cache(dict_cache):
    try:
        with open(dict_cache) as infile:
            movies_dict1=json.load(infile)
        #load and convert the file
        movies_dict={int(key): value for key, value in movies_dict1.items()}
    except:
        movies_list=get_top_movies()
        movies_dict=movies_to_dict(movies_list)
        with open(dict_cache, 'w') as outfile:
            json.dump(movies_dict, outfile)
    return movies_dict


###################################################
## Function -- init_db()                         ##
## create the datebase                           ##
## tables contained: movie and genre             ##
## primary key: IMDb_ranking in table Movie      ##
##              Id in table Genre                ##
## foreign key: IMDb_ranking in table Genre      ##
##       (related to IMDb_ranking in table Movie)##
###################################################
def init_db():
    try:
        conn=sqlite3.connect('imdb_top_movies.sqlite')
    except:
        print("Error: fail to create the SQLite database")
    cur=conn.cursor()
    statement='''DROP TABLE IF EXISTS 'Movie';'''
    cur.execute(statement)
    statement='''DROP TABLE IF EXISTS 'Genre';'''
    cur.execute(statement)
    conn.commit()
    #create table 'Movie' (primary key: IMDb_ranking)
    st_create_movie= '''
        CREATE TABLE 'Movie' (
            'IMDb_ranking' INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            'Title' TEXT,
            'IMDb_id' TEXT,
            'IMDb_rating' REAL,
            'Year' TEXT,
            'Runtime' TEXT,
            'Language' TEXT
            );
        '''
    cur.execute(st_create_movie)
    conn.commit()
    #create table 'Genre' (primary key: Id)
    st_create_genre= '''
        CREATE TABLE 'Genre' (
            'Id' INTEGER PRIMARY KEY AUTOINCREMENT UNIQUE,
            'Genre' TEXT,
            'IMDb_id' TEXT,
            'IMDb_ranking' INTEGER
            );
        '''
    cur.execute(st_create_genre)
    conn.commit()
    #close database connection
    conn.close()


###################################################
## Function -- insert_movies_data(movie_dict)    ##
## populate the database                         ##
## param: a dictionary                           ##
###################################################
def insert_movies_data(movie_dict):
    conn=sqlite3.connect('imdb_top_movies.sqlite')
    cur=conn.cursor()
    #insert data to the Movie table
    for i in range(len(movie_dict)):
        m=movie_dict[i+1]
        insertion=(None,m['title'],m['imdb_id'],float(m['imdb_rating']),m['year'],m['runtime'],m['language'])
        st_save_movie='INSERT INTO "Movie" '
        st_save_movie+='VALUES (?, ?, ?, ?, ?, ?, ?)'
        cur.execute(st_save_movie, insertion)
    conn.commit()
    #insert data to the Genre table
    m_genre=[]
    m_rank=list(range(1,251))
    for i in range(len(movie_dict)):
        m=movie_dict[i+1]
        m_genre.append(' '.join(m['genre']))
    df1={'rank':m_rank, 'genre':m_genre}
    df2=pd.DataFrame(df1)
    df3=pd.concat([Series(row['rank'], row['genre'].split(' ')) for _, row in df2.iterrows()]).reset_index()
    df4=df3.as_matrix()
    for d in df4:
        insertion_g=(None,d[0].lower(),None,int(d[1]))
        st_save_genre='INSERT INTO "Genre" '
        st_save_genre+='VALUES (?, ?, ?, ?)'
        cur.execute(st_save_genre, insertion_g)
    conn.commit()
    st_imdb_id="UPDATE Genre SET IMDb_id = (SELECT Movie.IMDb_id FROM Movie WHERE Genre.IMDb_ranking=Movie.IMDb_ranking)"
    cur.execute(st_imdb_id)
    conn.commit()
    #close database connection
    conn.close()


###################################################
## Function -- process_command                   ##
## implement logic to process commands           ##
## param: a string                               ##
## return: print selected movies in tabular form ##
###################################################
def process_command(command):
    conn=sqlite3.connect('imdb_top_movies.sqlite')
    cur=conn.cursor()
    command_s=command.lower().split()
    if command_s[0]=='all':
        st_c="SELECT IMDb_ranking, Title, IMDb_rating, Runtime, Language FROM Movie"
    if command_s[0]=='year':
        st_c="SELECT IMDb_ranking, Title, IMDb_rating, Runtime, Language FROM Movie WHERE Year='"
        st_c+=command_s[1]
        st_c+="' ORDER BY IMDb_ranking LIMIT 5"
    if command_s[0]=='genre':
        st_c="SELECT Movie.IMDb_ranking, Title, IMDb_rating, Year, Runtime, Language FROM Movie "
        st_c+="JOIN Genre ON Genre.IMDb_id=Movie.IMDb_id WHERE Genre.Genre='"
        st_c+=command_s[1]
        st_c+="' ORDER BY Movie.IMDb_ranking LIMIT 5"
    cur.execute(st_c)
    movies_selected=from_db_cursor(cur)
    print(movies_selected)
    conn.close()


###################################################
## Function -- plot_genre_proportion             ##
## pie chart of genres                           ##
## return: nothing                               ##
## side effect:launch plotly page in web browser ##
###################################################
def plot_genre_proportion():
    conn=sqlite3.connect('imdb_top_movies.sqlite')
    cur=conn.cursor()
    st_a="SELECT Genre, COUNT(*) FROM Genre GROUP BY Genre"
    cur.execute(st_a)
    genre1=[]
    g_c=[]
    for i in cur:
        genre1.append(i[0])
        g_c.append(int(i[1]))
    conn.close()
    #pie chart
    trace=go.Pie(labels=genre1, values=g_c)
    layout={'title': 'Genres of Top Rated Movies'}
    data=[trace]
    fig_c=dict(data=data, layout=layout)
    py.plot(fig_c, filename='genre_count_pie_chart')


###################################################
## Function -- plot_genre_rating                 ##
## line chart of avg ratings for genres          ##
## return: nothing                               ##
## side effect:launch plotly page in web browser ##
###################################################
def plot_genre_rating():
    conn=sqlite3.connect('imdb_top_movies.sqlite')
    cur=conn.cursor()
    st_b="SELECT Genre.Genre, AVG(Movie.IMDb_rating) FROM Genre JOIN Movie ON Genre.IMDb_id=Movie.IMDb_id GROUP BY Genre.Genre"
    cur.execute(st_b)
    genre2=[]
    g_r=[]
    for j in cur:
        genre2.append(j[0])
        g_r.append(round(float(j[1]),3))
    conn.close()
    trace=go.Scatter(x=genre2,y=g_r,mode='lines+markers')
    layout=dict(title='Average IMDb Ratings for Genres',xaxis=dict(title='Genre'),yaxis=dict(title='IMDb Rating'),)
    data=[trace]
    fig_r= dict(data=data, layout=layout)
    py.plot(fig_r, filename='genre_rating_line_chart')



## Create and Populate Database imdb_top_movies.sqlite:

movies_dict=load_movies_dict_using_cache(CACHE_2)    ##option A -- use cache
#movies_dict=movies_to_dict(get_top_movies())        ##option B -- not use cache
init_db()
insert_movies_data(movies_dict)



## Interactive Search Interface:

if __name__ == "__main__":
    response=''
    while True:
        response=input("Enter command (or 'help' for options): ")
        r=response.lower().split()
        genre_range=['crime','drama','action','thriller','biography','history','adventure','fantasy','western','romance','sci-fi','mystery','family','comedy','war','animation','horror','music','musical','film-noir','sport']
        ranking_range=[str(x) for x in list((range(1, 251)))]
        year_range=['1921','1924','1925','1926','1927','1928','1931','1934','1936','1939']+[str(x) for x in list((range(1940, 2018)))]
        year_range.remove('1970')
        year_range.remove('1956')
        year_range.remove('1951')
        year_range.remove('1947')
        year_range.remove('1945')
        year_range.remove('1943')
        #command 'exit'
        if r[0]=='exit':
            print("\n Bye!\n")
            break
        #command 'help'
        elif r[0]=='help':
            print("\n")
            print("     all \n         description: displays all the top 250 movies in tabular form\n")
            print("     genre <name of a genre> \n         description: lists top 5 movies belonging to the specified genre in tabular form \n         sample command: genre action\n")
            print("     year <a year> \n         description: lists top 5 movies that released in the specified year in tabular form \n         sample command: year 2000\n")
            print("     watch <IMDb_rank of a movie> \n         description: launchs the IMDb video page of the movie in a web browser \n         sample command: watch 1\n")
            print("     visualization genre proportion \n         description: displays a pie chart of the genres of top movies on plotly page\n")
            print("     visualization genre rating \n         description: displays a graph of the average ratings for different genres on plotly page\n")
            print("     exit \n         description: exits the program\n")
            print("     help \n         description: lists available commands\n")
        ##command option 1
        elif r[0]=='all' and len(r)==1:
            print("\n IMDb Top 250 Rated Movies: ")
            process_command(response)
            print("\n")
        ##command option 2
        elif r[0]=='genre' and len(r)==2:
            if r[1] in genre_range:
                print("\n Top 5 "+r[1].capitalize()+" Movies: ")
                process_command(response)
                print("\n")
            else:
                print("\n No result found for "+response+"\n")
        ##command option 3
        elif r[0]=='year' and len(r)==2:
            if r[1] in year_range:
                print("\n Top 5 Movies Released in "+str(r[1])+": ")
                process_command(response)
                print("\n")
            else:
                print("\n No result found for "+response+"\n")
        ##command option 4
        elif r[0]=='watch' and len(r)==2:
            if r[1] in ranking_range:
                movie_trailer=movies_dict[int(r[1])]['trailer']
                if movie_trailer=='no trailer':
                    print("\n Sorry! This movie does not have a trailer \n")
                else:
                    print("\n Launching in web browser \n")
                    webbrowser.open(movie_trailer)
            else:
                print("\n Command not recognized \n")
        ##command option 5
        elif r[0]=='visualization' and r[1]=='genre' and len(r)==3:
            if r[2]=='rating':
                print("\n Launching the plotly page in web browser \n")
                plot_genre_rating()
            elif r[2]=='proportion':
                print("\n Launching the plotly page in web browser \n")
                plot_genre_proportion()
            else:
                print("\n Command not recognized \n")
        else:
            print("\n Command not recognized \n")
