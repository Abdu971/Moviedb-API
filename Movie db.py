import tkinter as tk
from tkinter import messagebox
import requests
from PIL import Image, ImageTk
from io import BytesIO

# ==================== THEME COLORS ====================
BG_COLOR = "#1c1f26"
HEADER_COLOR = "#14161d"
CARD_COLOR = "#2a2f3a"
TEXT_COLOR = "#ffffff"
MUTED_TEXT = "#b0b3b8"
ACCENT = "#1db954"
BUTTON_HOVER = "#17a74a"


class MovieDBApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MovieDB Explorer")
        self.root.geometry("900x600")
        self.root.configure(bg=BG_COLOR)
        self.root.resizable(False, False)

        # ==================== TMDB CONFIG ====================
        self.api_key = "ad68bee58afcd5e639529e3ece150615"
        self.base_url = "https://api.themoviedb.org/3"
        self.image_base_url = "https://image.tmdb.org/t/p/w200"

        self.poster_images = []  # prevent garbage collection

        self.create_widgets()

    # ==================== UI ====================
    def create_widgets(self):
        # ---------- HEADER ----------
        header = tk.Frame(self.root, bg=HEADER_COLOR, height=60)
        header.pack(fill="x")

        tk.Label(
            header,
            text="🎬 MovieDB Explorer",
            font=("Segoe UI", 18, "bold"),
            bg=HEADER_COLOR,
            fg=TEXT_COLOR
        ).pack(side="left", padx=20)

        # ---------- SEARCH BAR ----------
        search_frame = tk.Frame(self.root, bg=BG_COLOR)
        search_frame.pack(fill="x", pady=15)

        self.search_entry = tk.Entry(
            search_frame,
            width=40,
            font=("Segoe UI", 12),
            bg=CARD_COLOR,
            fg=TEXT_COLOR,
            insertbackground=TEXT_COLOR,
            relief="flat"
        )
        self.search_entry.pack(side="left", padx=20, ipady=6)

        search_btn = tk.Button(
            search_frame,
            text="Search",
            font=("Segoe UI", 11, "bold"),
            bg=ACCENT,
            fg="black",
            relief="flat",
            padx=25,
            pady=6,
            command=self.search_movies
        )
        search_btn.pack(side="left")

        # ---------- RESULTS AREA ----------
        container = tk.Frame(self.root, bg=BG_COLOR)
        container.pack(fill="both", expand=True)

        self.canvas = tk.Canvas(container, bg=BG_COLOR, highlightthickness=0)
        scrollbar = tk.Scrollbar(container, orient="vertical", command=self.canvas.yview)

        self.scrollable_frame = tk.Frame(self.canvas, bg=BG_COLOR)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

    # ==================== SEARCH ====================
    def search_movies(self):
        query = self.search_entry.get().strip()

        if not query:
            messagebox.showwarning("Input Error", "Please enter a movie title.")
            return

        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        self.poster_images.clear()

        try:
            movies = self.fetch_movies(query)

            if not movies:
                tk.Label(
                    self.scrollable_frame,
                    text="No results found.",
                    bg=BG_COLOR,
                    fg=MUTED_TEXT,
                    font=("Segoe UI", 12)
                ).pack(pady=30)
                return

            for movie in movies[:10]:
                self.create_movie_card(movie)

        except requests.exceptions.RequestException:
            messagebox.showerror("Error", "Unable to connect to MovieDB API.")

    # ==================== API ====================
    def fetch_movies(self, query):
        endpoint = f"{self.base_url}/search/movie"
        params = {
            "api_key": self.api_key,
            "query": query
        }
        response = requests.get(endpoint, params=params, timeout=10)
        response.raise_for_status()
        return response.json().get("results", [])

    # ==================== MOVIE CARD ====================
    def create_movie_card(self, movie):
        card = tk.Frame(
            self.scrollable_frame,
            bg=CARD_COLOR,
            padx=15,
            pady=15
        )
        card.pack(fill="x", padx=20, pady=10)

        # ---------- POSTER ----------
        poster_path = movie.get("poster_path")

        if poster_path:
            poster_url = self.image_base_url + poster_path
            image_data = requests.get(poster_url).content
            image = Image.open(BytesIO(image_data)).resize((120, 180))
            photo = ImageTk.PhotoImage(image)
            self.poster_images.append(photo)

            tk.Label(card, image=photo, bg=CARD_COLOR).pack(side="left", padx=10)
        else:
            tk.Label(
                card,
                text="No Image",
                bg="#3a3f4b",
                fg=MUTED_TEXT,
                width=15,
                height=10
            ).pack(side="left", padx=10)

        # ---------- DETAILS ----------
        details = tk.Frame(card, bg=CARD_COLOR)
        details.pack(side="left", fill="both", expand=True, padx=10)

        title = movie.get("title", "N/A")
        year = movie.get("release_date", "")[:4]
        rating = movie.get("vote_average", "N/A")
        overview = movie.get("overview", "No overview available.")

        tk.Label(
            details,
            text=title,
            font=("Segoe UI", 14, "bold"),
            bg=CARD_COLOR,
            fg=TEXT_COLOR
        ).pack(anchor="w")

        tk.Label(
            details,
            text=f"{year}   ⭐ {rating}/10",
            font=("Segoe UI", 10),
            bg=CARD_COLOR,
            fg=ACCENT
        ).pack(anchor="w", pady=5)

        tk.Label(
            details,
            text=overview,
            wraplength=550,
            justify="left",
            bg=CARD_COLOR,
            fg=MUTED_TEXT
        ).pack(anchor="w")


# ==================== RUN APP ====================
if __name__ == "__main__":
    root = tk.Tk()
    app = MovieDBApp(root)
    root.mainloop()
