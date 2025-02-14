import sqlite3

class MovieDatabase:
    def __init__(self):
        self.db_path = "movie_app.db"
        self.create_database()

    def create_database(self):
        """Create database and tables if they don't exist."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS watchlist (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER UNIQUE,
                title TEXT,
                poster_path TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS favorites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                movie_id INTEGER UNIQUE,
                title TEXT,
                poster_path TEXT
            )
        ''')

        conn.commit()
        conn.close()

    def add_to_watchlist(self, movie_id, title, poster_path):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO watchlist (movie_id, title, poster_path)
            VALUES (?, ?, ?)
        ''', (movie_id, title, poster_path))
        conn.commit()
        conn.close()

    def remove_from_watchlist(self, movie_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM watchlist WHERE movie_id = ?
        ''', (movie_id,))
        conn.commit()
        conn.close()

    def add_to_favorites(self, movie_id, title, poster_path):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO favorites (movie_id, title, poster_path)
            VALUES (?, ?, ?)
        ''', (movie_id, title, poster_path))
        conn.commit()
        conn.close()

    def remove_from_favorites(self, movie_id):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            DELETE FROM favorites WHERE movie_id = ?
        ''', (movie_id,))
        conn.commit()
        conn.close()

    def fetch_watchlist(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM watchlist')
        movies = cursor.fetchall()
        conn.close()
        return movies

    def fetch_favorites(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM favorites')
        movies = cursor.fetchall()
        conn.close()
        return movies