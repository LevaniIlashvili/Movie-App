import requests
import os
from dotenv import load_dotenv  

load_dotenv()

BASE_URL = "https://api.themoviedb.org/3"
API_KEY = os.getenv("TMDB_API_KEY")

# MovieAPI Service
class MovieAPI:
    def fetch_trending_movies(self, page=1):
        url = f"{BASE_URL}/trending/movie/week?api_key={API_KEY}&page={page}"
        response = requests.get(url)
        if response.status_code != 200:
            print("Error fetching trending movies:", response.json())
            return []
        data = response.json()

        # Ensure we are returning exactly two values: list of movies and total number of pages
        movies = data['results']  # List of movies
        total_pages = data['total_pages']  # Total number of pages
        return movies, total_pages  # Return exactly two values

    def search_movies(self, query, page=1):
        url = f"{BASE_URL}/search/movie?api_key={API_KEY}&query={query}&page={page}"
        response = requests.get(url)
        return response.json().get("results", []), response.json().get("total_pages", 1)