from api_service import MovieAPI
from pprint import pprint

movie_api =  MovieAPI()

pprint(movie_api.search_movies("fight club"))