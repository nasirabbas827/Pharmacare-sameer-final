import tkinter as tk
from tkinter import ttk
from tkinter import PhotoImage
from login import LoginWindow
import os

class SplashScreen:
    def __init__(self, root):
        self.root = root
        self.root.title("PharmaCare - Splash")

        # Maximize window
        self.root.state('zoomed')
        self.root.resizable(True, True)

        self.build_ui()

    def build_ui(self):
        # Main frame fills entire window
        splash_frame = tk.Frame(self.root, bg="#f0f4f7")
        splash_frame.pack(fill="both", expand=True)

        splash_inner = tk.Frame(splash_frame, bg="#f0f4f7", padx=20, pady=20)
        splash_inner.place(relx=0.5, rely=0.5, anchor="center")

        # Title
        tk.Label(
            splash_inner,
            text="PharmaCare Management System",
            font=("Helvetica", 24, "bold"),
            fg="#004d99",
            bg="#f0f4f7"
        ).pack(pady=(20, 10))

        # Tagline
        tk.Label(
            splash_inner,
            text="Your Trusted Pharmacy Solution",
            font=("Helvetica", 16, "italic"),
            fg="#333333",
            bg="#f0f4f7"
        ).pack(pady=(0, 20))

        # Logo image
        logo_path = os.path.join("logos", "logo.png")
        if os.path.exists(logo_path):
            self.logo_img = PhotoImage(file=logo_path)
            tk.Label(splash_inner, image=self.logo_img, bg="#f0f4f7").pack(pady=10)
        else:
            logo_frame = tk.Frame(splash_inner, width=100, height=100, bg="#d9d9d9", relief="ridge", bd=2)
            logo_frame.pack(pady=10)
            tk.Label(logo_frame, text="LOGO", bg="#d9d9d9", fg="#666", font=("Arial", 12)).place(relx=0.5, rely=0.5, anchor="center")

        # Loading text
        tk.Label(
            splash_inner,
            text="Loading, please wait...",
            font=("Arial", 12),
            fg="#555555",
            bg="#f0f4f7"
        ).pack(pady=(20, 5))

        # Progress bar
        self.progress = ttk.Progressbar(splash_inner, mode="indeterminate", length=300)
        self.progress.pack(pady=10)
        self.progress.start()

        # Redirect to login after 3 seconds
        self.root.after(3000, self.redirect_to_login)

    def redirect_to_login(self):
        self.progress.stop()  # Stop progress bar to prevent error
        self.root.destroy()
        root = tk.Tk()
        app = LoginWindow(root)
        root.mainloop()

if __name__ == '__main__':
    root = tk.Tk()
    app = SplashScreen(root)
    root.mainloop()
