import requests
import os
from dotenv import load_dotenv  

load_dotenv()

BASE_URL = "https://api.themoviedb.org/3"
API_KEY = os.getenv("TMDB_API_KEY")

class MovieAPI:
    def fetch_trending_movies(self):
        url = f"{BASE_URL}/trending/movie/week?api_key={API_KEY}"
        response = requests.get(url)

        if response.status_code != 200:
            print("Error fetching trending movies:", response.json())
            return []
        
        return response.json()
    
    def search_movies(self, query):
        url = f"{BASE_URL}/search/movie?api_key={API_KEY}&query={query}"
        response = requests.get(url)
        return response.json()