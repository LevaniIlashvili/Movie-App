import sys
import requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QGridLayout, QLabel, QPushButton, 
    QVBoxLayout, QScrollArea, QHBoxLayout, QLineEdit, QStackedWidget, QSpacerItem, QSizePolicy
)
from PyQt5.QtGui import QPixmap, QFont, QIcon
from PyQt5.QtCore import Qt, QSize
from io import BytesIO
from api_service import MovieAPI
from database import MovieDatabase

IMAGE_BASE_URL = "https://image.tmdb.org/t/p/w200"
POSTER_WIDTH = 200
GAP_SIZE = 20

class MovieApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Movie App")
        self.showMaximized()

        self.api = MovieAPI()
        self.database = MovieDatabase()

        self.current_page = 1
        self.total_pages = 1

        main_layout = QVBoxLayout(self)

        nav_bar = QHBoxLayout()
        self.trending_btn = QPushButton("Trending Movies")
        self.search_btn = QPushButton("Search Movie")
        self.watchlist_btn = QPushButton("Watchlist")
        self.favorites_btn = QPushButton("Favorites")
        self.recommendations_btn = QPushButton("Recommendations")

        self.trending_btn.clicked.connect(self.show_trending_movies)
        self.search_btn.clicked.connect(self.show_search_page)
        self.watchlist_btn.clicked.connect(self.show_watchlist_page)
        self.favorites_btn.clicked.connect(self.show_favorites_page)
        self.recommendations_btn.clicked.connect(self.show_recommendations_page)

        nav_bar.addWidget(self.trending_btn)
        nav_bar.addWidget(self.search_btn)
        nav_bar.addWidget(self.watchlist_btn)
        nav_bar.addWidget(self.favorites_btn)
        nav_bar.addWidget(self.recommendations_btn)

        main_layout.addLayout(nav_bar)

        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)

        self.trending_page = QWidget()
        self.init_trending_page()
        self.stacked_widget.addWidget(self.trending_page)

        self.search_page = QWidget()
        self.init_search_page()
        self.stacked_widget.addWidget(self.search_page)

        self.watchlist_page = QWidget()
        self.init_watchlist_page()
        self.stacked_widget.addWidget(self.watchlist_page)

        self.favorites_page = QWidget()
        self.init_favorites_page()
        self.stacked_widget.addWidget(self.favorites_page)

        self.recommendations_page = QWidget()
        self.init_recommendations_page()
        self.stacked_widget.addWidget(self.recommendations_page)

        self.movie_details_page = QWidget()
        self.init_movie_details_page()
        self.stacked_widget.addWidget(self.movie_details_page)

        self.setLayout(main_layout)
        self.show_trending_movies()

    def init_movie_details_page(self):
        layout = QVBoxLayout(self.movie_details_page)

        self.movie_title_label = QLabel()
        self.movie_title_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.movie_title_label.setFont(font)
        layout.addWidget(self.movie_title_label)

        self.movie_poster_label = QLabel()
        self.movie_poster_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.movie_poster_label)

        self.movie_overview_label = QLabel()
        self.movie_overview_label.setWordWrap(True)
        self.movie_overview_label.setAlignment(Qt.AlignTop)
        font = QFont()
        font.setPointSize(14)
        self.movie_overview_label.setFont(font)
        layout.addWidget(self.movie_overview_label)

        back_button = QPushButton("Back")
        back_button.clicked.connect(lambda: self.stacked_widget.setCurrentWidget(self.trending_page))
        layout.addWidget(back_button)
    
    def show_movie_details(self, movie):
        self.movie_title_label.setText(movie["title"])

        if movie.get("poster_path"):
            poster_url = IMAGE_BASE_URL + movie["poster_path"]
            response = requests.get(poster_url)
            pixmap = QPixmap()
            pixmap.loadFromData(BytesIO(response.content).read())
            self.movie_poster_label.setPixmap(pixmap.scaled(POSTER_WIDTH * 2, 300, Qt.KeepAspectRatio))
        else:
            self.movie_poster_label.clear()

        self.movie_overview_label.setText(movie.get("overview", "No description available."))

        self.stacked_widget.setCurrentWidget(self.movie_details_page)

    def init_trending_page(self):
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
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.scroll_widget = QWidget()
        self.movie_grid = QGridLayout(self.scroll_widget)
        self.movie_grid.setSpacing(GAP_SIZE)

        self.scroll_area.setWidget(self.scroll_widget)
        layout.addWidget(self.scroll_area)

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
        self.search_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 

        self.search_scroll_widget = QWidget()
        self.search_grid = QGridLayout(self.search_scroll_widget)
        self.search_grid.setSpacing(GAP_SIZE)

        self.search_scroll_area.setWidget(self.search_scroll_widget)
        layout.addWidget(self.search_scroll_area)

        self.search_prev_button = QPushButton("Previous")
        self.search_next_button = QPushButton("Next")
        self.search_prev_button.clicked.connect(self.load_previous_search_results)
        self.search_next_button.clicked.connect(self.load_next_search_results)

        search_layout.addWidget(self.search_prev_button)
        search_layout.addWidget(self.search_next_button)

    def init_watchlist_page(self):
        layout = QVBoxLayout(self.watchlist_page)

        self.watchlist_label = QLabel("Watchlist")
        self.watchlist_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.watchlist_label.setFont(font)
        layout.addWidget(self.watchlist_label)

        self.watchlist_scroll_area = QScrollArea()
        self.watchlist_scroll_area.setWidgetResizable(True)
        self.watchlist_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.watchlist_scroll_widget = QWidget()
        self.watchlist_grid = QGridLayout(self.watchlist_scroll_widget)
        self.watchlist_grid.setSpacing(GAP_SIZE)

        self.watchlist_scroll_area.setWidget(self.watchlist_scroll_widget)
        layout.addWidget(self.watchlist_scroll_area)

        self.load_watchlist_movies()
    
    def load_watchlist_movies(self):
        for i in reversed(range(self.watchlist_grid.count())):
            widget = self.watchlist_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        watchlist_movies = self.database.fetch_watchlist()

        grid_width = self.watchlist_scroll_area.viewport().width() - 40
        columns = max(1, grid_width // (POSTER_WIDTH + GAP_SIZE))

        row, col = 0, 0
        for movie in watchlist_movies:
            movie_id, title, poster_path = movie[1], movie[2], movie[3]
            movie_data = {"id": movie_id, "title": title, "poster_path": poster_path}
            self.add_movie_to_grid(self.watchlist_grid, movie_data, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

    def init_favorites_page(self):
        layout = QVBoxLayout(self.favorites_page)

        self.favorites_label = QLabel("Favorites")
        self.favorites_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.favorites_label.setFont(font)
        layout.addWidget(self.favorites_label)

        self.favorites_scroll_area = QScrollArea()
        self.favorites_scroll_area.setWidgetResizable(True)
        self.favorites_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff) 

        self.favorites_scroll_widget = QWidget()
        self.favorites_grid = QGridLayout(self.favorites_scroll_widget)
        self.favorites_grid.setSpacing(GAP_SIZE)

        self.favorites_scroll_area.setWidget(self.favorites_scroll_widget)
        layout.addWidget(self.favorites_scroll_area)

        self.load_favorites_movies()

    def load_favorites_movies(self):
        for i in reversed(range(self.favorites_grid.count())):
            widget = self.favorites_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        favorites_movies = self.database.fetch_favorites()

        grid_width = self.favorites_scroll_area.viewport().width() - 40
        columns = max(1, grid_width // (POSTER_WIDTH + GAP_SIZE))

        row, col = 0, 0
        for movie in favorites_movies:
            movie_id, title, poster_path = movie[1], movie[2], movie[3]
            movie_data = {"id": movie_id, "title": title, "poster_path": poster_path}
            self.add_movie_to_grid(self.favorites_grid, movie_data, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

    def init_recommendations_page(self):
        layout = QVBoxLayout(self.recommendations_page)

        self.recommendations_label = QLabel("Movie Recommendations")
        self.recommendations_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setPointSize(24)
        font.setBold(True)
        self.recommendations_label.setFont(font)
        layout.addWidget(self.recommendations_label)

        self.recommendations_scroll_area = QScrollArea()
        self.recommendations_scroll_area.setWidgetResizable(True)
        self.recommendations_scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.recommendations_scroll_widget = QWidget()
        self.recommendations_grid = QGridLayout(self.recommendations_scroll_widget)
        self.recommendations_grid.setSpacing(GAP_SIZE)

        self.recommendations_scroll_area.setWidget(self.recommendations_scroll_widget)
        layout.addWidget(self.recommendations_scroll_area)

        self.load_recommendations()

    def load_recommendations(self):
        for i in reversed(range(self.recommendations_grid.count())):
            widget = self.recommendations_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        favorite_movies = self.database.fetch_favorites()
        if(len(favorite_movies) == 0):
            return
        movie_titles = [movie[2] for movie in favorite_movies]
        recommendations = self.api.get_movie_recommendations(movie_titles)
        print(recommendations)
        for i in range(0, len(recommendations)):
            movies, _ = self.api.search_movies(recommendations[i], per_page=1)
            if (len(movies) == 0):
                continue
            recommendations[i] = movies[0]
            print(movies[0])

        grid_width = self.recommendations_scroll_area.viewport().width() - 40
        columns = max(1, grid_width // (POSTER_WIDTH + GAP_SIZE))

        row, col = 0, 0
        for movie in recommendations:
            self.add_movie_to_grid(self.recommendations_grid, movie, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

    def load_trending_movies(self):
        for i in reversed(range(self.movie_grid.count())):
            widget = self.movie_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        movies, total_pages = self.api.fetch_trending_movies(self.current_page)
        self.total_pages = total_pages

        grid_width = self.scroll_area.width() - 40
        columns = max(1, grid_width // (POSTER_WIDTH + GAP_SIZE))

        row, col = 0, 0
        for movie in movies:
            self.add_movie_to_grid(self.movie_grid, movie, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

        self.prev_button.setEnabled(self.current_page > 1)
        self.next_button.setEnabled(self.current_page < self.total_pages)

    def load_previous_trending_movies(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.load_trending_movies()

    def load_next_trending_movies(self):
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_trending_movies()

    def search_movie(self):
        query = self.search_input.text().strip()
        if not query:
            return

        self.current_page = 1
        self.load_search_results(query)

    def load_search_results(self, query):
        for i in reversed(range(self.search_grid.count())):
            widget = self.search_grid.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        movies, total_pages = self.api.search_movies(query, self.current_page)
        self.total_pages = total_pages

        grid_width = self.search_scroll_area.viewport().width() - 40
        columns = max(1, grid_width // (POSTER_WIDTH + GAP_SIZE))

        row, col = 0, 0
        for movie in movies:
            self.add_movie_to_grid(self.search_grid, movie, row, col)
            col += 1
            if col >= columns:
                col = 0
                row += 1

        self.search_prev_button.setEnabled(self.current_page > 1)
        self.search_next_button.setEnabled(self.current_page < self.total_pages)

    def load_previous_search_results(self):
        query = self.search_input.text().strip()
        if self.current_page > 1:
            self.current_page -= 1
            self.load_search_results(query)

    def load_next_search_results(self):
        query = self.search_input.text().strip()
        if self.current_page < self.total_pages:
            self.current_page += 1
            self.load_search_results(query)

    def add_movie_to_grid(self, grid, movie, row, col):
        title = movie.get("title", "Unknown")
        poster_path = movie.get("poster_path")
        movie_id = movie.get("id")
        poster_url = f"{IMAGE_BASE_URL}{poster_path}" if poster_path else ""

        item_widget = QWidget()
        item_layout = QVBoxLayout()
        item_layout.setAlignment(Qt.AlignCenter)

        if poster_url:
            pixmap = self.load_image(poster_url)
            if pixmap:
                poster_button = QPushButton()
                poster_button.setIcon(QIcon(pixmap))
                poster_button.setIconSize(QSize(POSTER_WIDTH, 300))
                poster_button.setStyleSheet("border: none;")
                poster_button.clicked.connect(lambda: self.show_movie_details(movie))
                item_layout.addWidget(poster_button)

        title_button = QPushButton(title)
        title_button.setFont(QFont("Arial", 10, QFont.Bold))
        title_button.setStyleSheet("border: none; color: blue; text-decoration: underline;")
        title_button.clicked.connect(lambda: self.show_movie_details(movie))
        item_layout.addWidget(title_button)

        watchlist_button = QPushButton("Add to Watchlist")
        if not self.is_movie_in_watchlist(movie_id):
            watchlist_button.clicked.connect(lambda: self.add_to_watchlist(movie_id, title, poster_path))
        else:
            watchlist_button.setText("Remove from Watchlist")
            watchlist_button.clicked.connect(lambda: self.remove_from_watchlist(movie_id))
        item_layout.addWidget(watchlist_button)

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
        watchlist_movies = self.database.fetch_watchlist()
        return any(movie[1] == movie_id for movie in watchlist_movies)

    def is_movie_in_favorites(self, movie_id):
        favorites_movies = self.database.fetch_favorites()
        return any(movie[1] == movie_id for movie in favorites_movies)

    def add_to_watchlist(self, movie_id, title, poster_path):
        self.database.add_to_watchlist(movie_id, title, poster_path)
        self.load_watchlist_movies()

    def remove_from_watchlist(self, movie_id):
        self.database.remove_from_watchlist(movie_id)
        self.load_watchlist_movies()

    def add_to_favorites(self, movie_id, title, poster_path):
        self.database.add_to_favorites(movie_id, title, poster_path)
        self.load_favorites_movies()
        self.load_recommendations()

    def remove_from_favorites(self, movie_id):
        self.database.remove_from_favorites(movie_id)
        self.load_favorites_movies()

    def load_image(self, url):
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

    def show_recommendations_page(self):
        self.stacked_widget.setCurrentWidget(self.recommendations_page)

    def resizeEvent(self, event):   
        if hasattr(self, "movie_grid"):
            self.load_trending_movies()
        super().resizeEvent(event)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MovieApp()
    window.show()
    sys.exit(app.exec_())
