# SI 507 Final Project
# Ran Bi
# Section 004, Monday, 7pm

import unittest
from movies import *

class TestClassMovie(unittest.TestCase):
    def test_constructor_1(self):
        m1=Movie(title='The Shawshank Redemption', year='1994', imdb_rating='9.2', imdb_id='tt0111161')
        self.assertEqual(m1.runtime, '2h 22min')
        self.assertIn('Crime', m1.genre)
        self.assertEqual(m1.language, 'English')
    def test_constructor_2(self):
        m2=Movie(title='Forrest Gump', year='1994', imdb_rating='8.7', imdb_id='tt0109830')
        self.assertEqual(m2.genre, ["Drama", "Romance"])
        self.assertIsInstance(m2, Movie)

class TestGetMovies(unittest.TestCase):
    def test_get_movies_type(self):
        self.assertEqual(len(movies_dict), 250)
        self.assertIsInstance(movies_dict[10], dict)
    def test_get_movies_value(self):
        self.assertIn(200, list(movies_dict.keys()))
        self.assertGreater(9.5, float(list(movies_dict.values())[0]['imdb_rating']))

class TestDatabase(unittest.TestCase):
    def test_movie_table_length(self):
        conn=sqlite3.connect('imdb_top_movies.sqlite')
        cur=conn.cursor()
        sql1='SELECT Title FROM Movie'
        result1=cur.execute(sql1)
        result_list1=result1.fetchall()
        self.assertEqual(len(result_list1), 250)
        conn.close()
    def test_movie_table_value_1(self):
        conn=sqlite3.connect('imdb_top_movies.sqlite')
        cur=conn.cursor()
        sql2='SELECT Title FROM Movie'
        result2=cur.execute(sql2)
        result_list2=result2.fetchall()
        self.assertIn(('The Godfather',), result_list2)
        conn.close()
    def test_movie_table_value_2(self):
        conn=sqlite3.connect('imdb_top_movies.sqlite')
        cur=conn.cursor()
        sql3='SELECT IMDb_rating FROM Movie'
        result3=cur.execute(sql3)
        result_list3=result3.fetchall()
        self.assertGreater(result_list3[1][0], 9.0)
        conn.close()
    def test_movie_table_value_3(self):
        conn=sqlite3.connect('imdb_top_movies.sqlite')
        cur=conn.cursor()
        sql4='SELECT Title, IMDb_rating FROM Movie WHERE Year="1994" ORDER BY IMDb_ranking LIMIT 5'
        result4=cur.execute(sql4)
        result_list4=result4.fetchall()
        self.assertEqual(result_list4[0][0], 'The Shawshank Redemption')
        self.assertGreater(result_list4[0][1], 9.0)
        conn.close()
    def test_table_join(self):
        conn=sqlite3.connect('imdb_top_movies.sqlite')
        cur=conn.cursor()
        sql5='SELECT Title FROM Movie JOIN Genre ON Genre.IMDb_id=Movie.IMDb_id WHERE Genre.Genre="crime"'
        result5=cur.execute(sql5)
        result_list5=result5.fetchall()
        self.assertIn(('The Godfather',),result_list5)
        conn.close()
    def test_genre_table_length(self):
        conn=sqlite3.connect('imdb_top_movies.sqlite')
        cur=conn.cursor()
        sql6='SELECT Genre FROM Genre'
        result6=cur.execute(sql6)
        result_list6=result6.fetchall()
        self.assertGreater(len(result_list6), 250)
        conn.close()
    def test_genre_table_value_1(self):
        conn=sqlite3.connect('imdb_top_movies.sqlite')
        cur=conn.cursor()
        sql7='SELECT Genre FROM Genre'
        result7=cur.execute(sql7)
        result_list7=result7.fetchall()
        self.assertIn(('crime',), result_list7)
        conn.close()
    def test_genre_table_value_2(self):
        conn=sqlite3.connect('imdb_top_movies.sqlite')
        cur=conn.cursor()
        sql8='SELECT DISTINCT IMDb_id FROM Genre'
        result8=cur.execute(sql8)
        result_list8=result8.fetchall()
        self.assertIn(('tt0111161',), result_list8)
        self.assertEqual(len(result_list8), 250)
        conn.close()

class TestProcessCommand(unittest.TestCase):
    def test_command_all(self):
        try:
            process_command('all')
        except:
            self.fail()
    def test_command_year(self):
        try:
            process_command('year 2000')
        except:
            self.fail()
    def test_command_genre(self):
        try:
            process_command('genre action')
        except:
            self.fail()

unittest.main(buffer=True)
