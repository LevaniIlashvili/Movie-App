import requests
import os
from dotenv import load_dotenv  
import google.generativeai as genai
import ast

load_dotenv()

BASE_URL = "https://api.themoviedb.org/3"
API_KEY = os.getenv("TMDB_API_KEY")
GEMINI_KEY=os.getenv("GEMINI_KEY")
genai.configure(api_key=GEMINI_KEY)

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

    def search_movies(self, query, page=1, per_page=20):
        url = f"{BASE_URL}/search/movie?api_key={API_KEY}&query={query}&page={page}&per_page={per_page}"
        response = requests.get(url)
        return response.json().get("results", []), response.json().get("total_pages", 1)
    
    def get_movie_recommendations(self, movie_titles):
        model = genai.GenerativeModel("gemini-pro")
        response = model.generate_content(
            f'For each movie in {movie_titles}, recommend exactly 5 similar movies. '
            'Return only a single Python list containing all recommended movie names as strings, without any categories, headers, or extra text. '
            'The output should be formatted exactly like this: '
            '["Movie 1", "Movie 2", "Movie 3", "Movie 4", "Movie 5", "Movie 6", "Movie 7", "Movie 8", "Movie 9", "Movie 10"]'
        )
        return ast.literal_eval(response.text) if response else "No recommendations available."