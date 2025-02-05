import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QPushButton, 
    QVBoxLayout, QScrollArea, QHBoxLayout, QLineEdit, QStackedWidget, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont
from PyQt5.QtCore import Qt
from io import BytesIO
from api_service import MovieAPI  # Make sure the api_service is correctly imported
from database import MovieDatabase  # Import the MovieDatabase class

# Constants for UI layout
IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w200"
POSTER_WIDTH = 200  # Approximate width of each movie poster
GAP_SIZE = 20  # Space between items

# Movie App GUI
class MovieApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Movie App")
        self.showMaximized()

        self.api = MovieAPI()  # Initialize API
        self.database = MovieDatabase()

        # Initialize pagination
        self.current_page = 1
        self.total_pages = 1

        # Main Layout
        main_layout = QVBoxLayout(self)

        # Navigation Bar
        nav_bar = QHBoxLayout()
        self.trending_btn = QPushButton("Trending Movies")
        self.search_btn = QPushButton("Search Movie")
        self.watchlist_btn = QPushButton("Watchlist")
        self.favorites_btn = QPushButton("Favorites")

        self.trending_btn.clicked.connect(self.show_trending_movies)
        self.search_btn.clicked.connect(self.show_search_page)
        self.watchlist_btn.clicked.connect(self.show_watchlist_page)
        self.favorites_btn.clicked.connect(self.show_favorites_page)

        # Add the buttons to the navbar layout
        nav_bar.addWidget(self.trending_btn)
        nav_bar.addWidget(self.search_btn)
        nav_bar.addWidget(self.watchlist_btn)
        nav_bar.addWidget(self.favorites_btn)

        main_layout.addLayout(nav_bar)

        # Stacked Widget for Pages
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        # Trending Movies Page
        self.trending_page = QWidget()
        self.init_trending_page()
        self.stacked_widget.addWidget(self.trending_page)

        # Search Page
        self.search_page = QWidget()
        self.init_search_page()
        self.stacked_widget.addWidget(self.search_page)

        # Watchlist Page
        self.watchlist_page = QWidget()
        self.init_watchlist_page()
        self.stacked_widget.addWidget(self.watchlist_page)

        # Favorites Page
        self.favorites_page = QWidget()
        self.init_favorites_page()
        self.stacked_widget.addWidget(self.favorites_page)

        self.setLayout(main_layout)
        self.show_trending_movies()

    def init_trending_page(self):
        """Initialize the trending movies page."""
        layout = QVBoxLayout(self.trending_page)

        self.title_label = QLabel("Trending Movies")
        self.title_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.title_label.setFont(font)
        layout.addWidget(self.title_label)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scrolling

        self.scroll_widget = QWidget()
        self.movie_grid = QGridLayout(self.scroll_widget)
        self.movie_grid.setSpacing(GAP_SIZE)

        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)

        # Pagination Buttons
        pagination_layout = QHBoxLayout()
        self.prev_button = QPushButton("Previous")
        self.next_button = QPushButton("Next")
        self.prev_button.clicked.connect(self.load_previous_trending_movies)
        self.next_button.clicked.connect(self.load_next_trending_movies)

        pagination_layout.addWidget(self.prev_button)
        pagination_layout.addWidget(self.next_button)
        layout.addLayout(pagination_layout)

        self.load_trending_movies()

    def init_search_page(self):
        """Initialize the search page."""
        layout = QVBoxLayout(self.search_page)

        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter movie name...")
        self.search_button = QPushButton("Search")
        self.search_button.clicked.connect(self.search_movie)

        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)
        layout.addLayout(search_layout)

        self.search_scroll_area = QScrollArea()
        self.search_scroll_area.setWidgetResizable(True)
        self.search_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scrolling

        self.search_scroll_widget = QWidget()
        self.search_grid = QGridLayout(self.search_scroll_widget)
        self.search_grid.setSpacing(GAP_SIZE)

        self.search_scroll_area.setWidget(self.search_scroll_widget)
        layout.addWidget(self.search_scroll_area)

        # Pagination Buttons
        self.search_prev_button = QPushButton("Previous")
        self.search_next_button = QPushButton("Next")
        self.search_prev_button.clicked.connect(self.load_previous_search_results)
        self.search_next_button.clicked.connect(self.load_next_search_results)

        search_layout.addWidget(self.search_prev_button)
        search_layout.addWidget(self.search_next_button)

    def init_watchlist_page(self):
        """Initialize the watchlist page."""
        layout = QVBoxLayout(self.watchlist_page)

        self.watchlist_label = QLabel("Watchlist")
        self.watchlist_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.watchlist_label.setFont(font)
        layout.addWidget(self.watchlist_label)

        # Scroll Area for Watchlist
        self.watchlist_scroll_area = QScrollArea()
        self.watchlist_scroll_area.setWidgetResizable(True)
        self.watchlist_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scrolling

        self.watchlist_scroll_widget = QWidget()
        self.watchlist_grid = QGridLayout(self.watchlist_scroll_widget)
        self.watchlist_grid.setSpacing(GAP_SIZE)

        self.watchlist_scroll_area.setWidget(self.watchlist_scroll_widget)
        layout.addWidget(self.watchlist_scroll_area)

        # Load watchlist movies
        self.load_watchlist_movies()
    
    def load_watchlist_movies(self):
        """Fetch and display movies in the watchlist with dynamic columns."""
        for i in reversed(range(self.watchlist_grid.count())):
            widget = self.watchlist_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        watchlist_movies = self.database.fetch_watchlist()  # Fetch watchlist from database

        # Calculate the number of columns dynamically based on the scroll area width
        grid_width = self.watchlist_scroll_area.viewport().width() - 40  # Adjust for padding
        columns = max(1, grid_width // (POSTER_WIDTH + GAP_SIZE))

        row, col = 0, 0
        for movie in watchlist_movies:
            movie_id, title, poster_path = movie[1], movie[2], movie[3]  # Extract movie details
            movie_data = {"id": movie_id, "title": title, "poster_path": poster_path}  # Create a dictionary for the movie
            self.add_movie_to_grid(self.watchlist_grid, movie_data, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

    def init_favorites_page(self):
        """Initialize the favorites page."""
        layout = QVBoxLayout(self.favorites_page)

        self.favorites_label = QLabel("Favorites")
        self.favorites_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.favorites_label.setFont(font)
        layout.addWidget(self.favorites_label)

        # Scroll Area for Favorites
        self.favorites_scroll_area = QScrollArea()
        self.favorites_scroll_area.setWidgetResizable(True)
        self.favorites_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)  # Disable horizontal scrolling

        self.favorites_scroll_widget = QWidget()
        self.favorites_grid = QGridLayout(self.favorites_scroll_widget)
        self.favorites_grid.setSpacing(GAP_SIZE)

        self.favorites_scroll_area.setWidget(self.favorites_scroll_widget)
        layout.addWidget(self.favorites_scroll_area)

        # Load favorite movies
        self.load_favorites_movies()

    def load_favorites_movies(self):
        """Fetch and display movies in the favorites with dynamic columns."""
        for i in reversed(range(self.favorites_grid.count())):
            widget = self.favorites_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        favorites_movies = self.database.fetch_favorites()  # Fetch favorites from database

        grid_width = self.favorites_scroll_area.viewport().width() - 40  # Adjust for padding
        columns = max(1, grid_width // (POSTER_WIDTH + GAP_SIZE))

        row, col = 0, 0
        for movie in favorites_movies:
            movie_id, title, poster_path = movie[1], movie[2], movie[3]  # Extract movie details
            movie_data = {"title": title, "poster_path": poster_path}  # Create a dictionary for the movie
            self.add_movie_to_grid(self.favorites_grid, movie_data, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

    def load_trending_movies(self):
        """Fetch and display trending movies with uniform spacing."""
        for i in reversed(range(self.movie_grid.count())):
            widget = self.movie_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        movies, total_pages = self.api.fetch_trending_movies(self.current_page)
        self.total_pages = total_pages  # Set total pages for pagination

        grid_width = self.scroll_area.width() - 40  # Adjust for padding
        columns = max(1, grid_width // (POSTER_WIDTH + GAP_SIZE))

        row, col = 0, 0
        for movie in movies:
            self.add_movie_to_grid(self.movie_grid, movie, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

        # Enable/disable pagination buttons based on current page
        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)

    def load_previous_trending_movies(self):
        """Load previous page of trending movies."""
        if self.current_page > 1:
            self.current_page -= 1
            self.load_trending_movies()

    def load_next_trending_movies(self):
        """Load next page of trending movies."""
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_trending_movies()

    def search_movie(self):
        """Search for movies and maintain uniform spacing."""
        query = self.search_input.text().strip()
        if not query:
            return

        self.current_page = 1  # Reset to the first page for new search
        self.load_search_results(query)

    def load_search_results(self, query):
        """Fetch and display search results with pagination."""
        for i in reversed(range(self.search_grid.count())):
            widget = self.search_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        movies, total_pages = self.api.search_movies(query, self.current_page)
        self.total_pages = total_pages  # Set total pages for pagination

        grid_width = self.search_scroll_area.viewport().width() - 40  # Adjust for padding
        columns = max(1, grid_width // (POSTER_WIDTH + GAP_SIZE))

        row, col = 0, 0
        for movie in movies:
            self.add_movie_to_grid(self.search_grid, movie, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

        # Enable/disable pagination buttons based on current page
        self.search_prev_button.setEnabled(self.current_page > 1)
        self.search_next_button.setEnabled(self.current_page < self.total_pages)

    def load_previous_search_results(self):
        """Load previous page of search results."""
        query = self.search_input.text().strip()
        if self.current_page > 1:
            self.current_page -= 1
            self.load_search_results(query)

    def load_next_search_results(self):
        """Load next page of search results."""
        query = self.search_input.text().strip()
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_search_results(query)

    def add_movie_to_grid(self, grid, movie, row, col):
        """Helper method to add a movie to the grid with proper alignment."""
        title = movie.get("title", "Unknown")
        poster_path = movie.get("poster_path")
        movie_id = movie.get("id")  # Assuming movie has an 'id' field
        poster_url = f"{IMAGE_BASE_URL}{poster_path}" if poster_path else ""

        item_widget = QWidget()
        item_layout = QVBoxLayout()
        item_layout.setAlignment(Qt.AlignCenter)

        if poster_url:
            pixmap = self.load_image(poster_url)
            if pixmap:
                image_label = QLabel()
                image_label.setPixmap(pixmap.scaled(POSTER_WIDTH, 300, Qt.KeepAspectRatio, Qt.SmoothTransformation))
                image_label.setAlignment(Qt.AlignCenter)
                item_layout.addWidget(image_label)

        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignCenter)

        font = QFont()
        font.setPointSize(10)  # Increase font size
        font.setBold(True)  # Make font bolder
        title_label.setFont(font)

        item_layout.addWidget(title_label)

        # Add 'Add to Watchlist' button
        watchlist_button = QPushButton("Add to Watchlist")
        if not self.is_movie_in_watchlist(movie_id):
            watchlist_button.clicked.connect(lambda: self.add_to_watchlist(movie_id, title, poster_path))
        else:
            watchlist_button.setText("Remove from Watchlist")
            watchlist_button.clicked.connect(lambda: self.remove_from_watchlist(movie_id))
        item_layout.addWidget(watchlist_button)

        # Add 'Add to Favorites' button
        favorites_button = QPushButton("Add to Favorites")
        if not self.is_movie_in_favorites(movie_id):
            favorites_button.clicked.connect(lambda: self.add_to_favorites(movie_id, title, poster_path))
        else:
            favorites_button.setText("Remove from Favorites")
            favorites_button.clicked.connect(lambda: self.remove_from_favorites(movie_id))
        item_layout.addWidget(favorites_button)

        item_widget.setLayout(item_layout)
        grid.addWidget(item_widget, row, col, Qt.AlignCenter)

    def is_movie_in_watchlist(self, movie_id):
        """Check if a movie is already in the watchlist."""
        watchlist_movies = self.database.fetch_watchlist()
        return any(movie[1] == movie_id for movie in watchlist_movies)

    def is_movie_in_favorites(self, movie_id):
        """Check if a movie is already in the favorites."""
        favorites_movies = self.database.fetch_favorites()
        return any(movie[1] == movie_id for movie in favorites_movies)

    def add_to_watchlist(self, movie_id, title, poster_path):
        """Add movie to the watchlist and update the UI."""
        self.database.add_to_watchlist(movie_id, title, poster_path)
        self.load_watchlist_movies()  # Reload the watchlist to reflect changes

    def remove_from_watchlist(self, movie_id):
        """Remove movie from the watchlist and update the UI."""
        self.database.remove_from_watchlist(movie_id)
        self.load_watchlist_movies()  # Reload the watchlist to reflect changes

    def add_to_favorites(self, movie_id, title, poster_path):
        """Add movie to the favorites and update the UI."""
        self.database.add_to_favorites(movie_id, title, poster_path)
        self.load_favorites_movies()  # Reload the favorites to reflect changes

    def remove_from_favorites(self, movie_id):
        """Remove movie from the favorites and update the UI."""
        self.database.remove_from_favorites(movie_id)
        self.load_favorites_movies()  # Reload the favorites to reflect changes

    def load_image(self, url):
        """Fetch and return a QPixmap from the given URL."""
        try:
            response = requests.get(url)
            if response.status_code == 200:
                image = QPixmap()
                image.loadFromData(BytesIO(response.content).read())
                return image
        except Exception as e:
            print("Error loading image:", e)
        return None

    def show_trending_movies(self):
        self.stacked_widget.setCurrentWidget(self.trending_page)

    def show_search_page(self):
        self.stacked_widget.setCurrentWidget(self.search_page)

    def show_watchlist_page(self):
        self.stacked_widget.setCurrentWidget(self.watchlist_page)

    def show_favorites_page(self):
        self.stacked_widget.setCurrentWidget(self.favorites_page)

    def resizeEvent(self, event):
        """Handle window resize event to adjust movie grid layout."""
        if hasattr(self, "movie_grid"):  # Ensure movie_grid is initialized
            self.load_trending_movies()  # Recalculate layout based on new width
        super().resizeEvent(event)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MovieApp()
    window.show()
    sys.exit(app.exec_())
