import tkinter as tk
from reports import ReportsWindow
from database import get_db_connection

class AdminDashboard:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        self.root.title("Admin Dashboard")
        self.root.state("zoomed")  # Fullscreen
        self.root.resizable(True, True)

        self.build_ui()

    def fetch_metrics(self):
        """Fetches Total Sales, Total Items, and Total Purchases from the database."""
        conn = get_db_connection()
        cursor = conn.cursor()

        # Total Sales (sum of quantity_sold * sale_price)
        cursor.execute('SELECT SUM(quantity_sold * sale_price) as total_sales FROM sales')
        total_sales = cursor.fetchone()[0] or 0.0

        # Total Items (count of items in medical_items)
        cursor.execute('SELECT COUNT(*) FROM medical_items')
        total_items = cursor.fetchone()[0] or 0

        # Total Purchases (sum of quantity_purchased * cost_price)
        cursor.execute('SELECT SUM(quantity_purchased * cost_price) as total_purchases FROM purchases')
        total_purchases = cursor.fetchone()[0] or 0.0

        conn.close()
        return total_sales, total_items, total_purchases

    def build_ui(self):
        main_frame = tk.Frame(self.root, bg="#f0f4f7")
        main_frame.pack(fill="both", expand=True)

        content_frame = tk.Frame(main_frame, bg="#f0f4f7")
        content_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Welcome label
        tk.Label(content_frame, text=f"Welcome, {self.user_data['username']}",
                 font=("Helvetica", 24, "bold"), fg="#004d99", bg="#f0f4f7").pack(pady=(20, 30))

        # Metrics frame for cards
        metrics_frame = tk.Frame(content_frame, bg="#f0f4f7")
        metrics_frame.pack(pady=(0, 30))

        # Fetch metrics
        total_sales, total_items, total_purchases = self.fetch_metrics()

        # Metric cards
        cards = [
            ("Total Sales", f"Rs {total_sales:,.2f}", "#2196F3"),
            ("Total Items", f"{total_items:,}", "#4CAF50"),
            ("Total Purchases", f"Rs {total_purchases:,.2f}", "#FF9800"),
        ]

        for i, (title, value, color) in enumerate(cards):
            card_frame = tk.Frame(metrics_frame, bg="#ffffff", bd=2, relief="flat")
            card_frame.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
            card_frame.config(highlightbackground="#d3d7db", highlightthickness=2)

            tk.Label(card_frame, text=title, font=("Arial", 14, "bold"), bg="#ffffff", fg="#333333").pack(pady=(15, 5))
            tk.Label(card_frame, text=value, font=("Arial", 18, "bold"), bg="#ffffff", fg=color).pack(pady=(0, 15))

        # Buttons frame
        buttons_frame = tk.Frame(content_frame, bg="#f0f4f7")
        buttons_frame.pack()

        # Buttons with hover effects
        buttons = [
            ("Manage Users", self.open_manage_users, "#2196F3"),
            ("Manage Medical Items", self.open_manage_items, "#2196F3"),
            ("Generate Reports", self.open_reports_window, "#4CAF50"),
            ("Logout", self.logout, "#f44336"),
        ]

        for text, command, color in buttons:
            btn = tk.Button(buttons_frame, text=text, width=25, height=2, command=command,
                            font=("Arial", 14, "bold"), bg=color, fg="white", bd=0, relief="flat")
            btn.pack(pady=10)
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=self.darken_color(c)))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))

    def darken_color(self, hex_color):
        """Returns a darker shade of the given hex color."""
        hex_color = hex_color.lstrip('#')
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(max(0, c - 30) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

    def open_manage_users(self):
        self.root.destroy()
        import manage_users
        manage_users.open_manage_users()

    def open_manage_items(self):
        self.root.destroy()
        import manage_items
        manage_items.open_manage_items()

    def open_reports_window(self):
        self.root.withdraw()
        reports_window = tk.Toplevel()
        ReportsWindow(reports_window, self.user_data, self.root)

    def logout(self):
        self.root.destroy()
        import login
        root = tk.Tk()
        login.LoginWindow(root)
        root.mainloop()