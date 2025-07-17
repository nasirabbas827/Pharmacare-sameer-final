import tkinter as tk
from reports import ReportsWindow
from database import get_db_connection
from admin_purchase import UserPurchaseWindow  

class AdminDashboard:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        self.root.title("Pharmacy Management System - Admin Dashboard")
        self.root.state("zoomed")
        self.root.resizable(True, True)
        self.build_ui()

    def fetch_metrics(self):
        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute('SELECT SUM(quantity_sold * sale_price) FROM sales')
        total_sales = cursor.fetchone()[0] or 0.0

        cursor.execute('SELECT COUNT(*) FROM medical_items')
        total_items = cursor.fetchone()[0] or 0

        cursor.execute('SELECT SUM(quantity_purchased * cost_price) FROM purchases')
        total_purchases = cursor.fetchone()[0] or 0.0

        conn.close()
        return total_sales, total_items, total_purchases

    def build_ui(self):
        main_frame = tk.Frame(self.root, bg="#f0f4f7")
        main_frame.pack(fill="both", expand=True)

        tk.Label(main_frame, text="Pharmacy Management System - Admin Dashboard",
                 font=("Arial", 22, "bold"), fg="#004d99", bg="#f0f4f7").pack(pady=(30, 10))

        tk.Label(main_frame, text=f"Welcome, {self.user_data['username']}",
                 font=("Arial", 14), bg="#f0f4f7").pack(pady=(0, 30))

        metrics_frame = tk.Frame(main_frame, bg="#f0f4f7")
        metrics_frame.pack()

        total_sales, total_items, total_purchases = self.fetch_metrics()

        cards = [
            ("Total Sales", f"Rs {total_sales:,.2f}", "#2196F3"),
            ("Total Items", f"{total_items:,}", "#4CAF50"),
            ("Total Purchases", f"Rs {total_purchases:,.2f}", "#FF9800"),
        ]

        for i, (title, value, color) in enumerate(cards):
            card_frame = tk.Frame(metrics_frame, bg="#ffffff", bd=2, relief="flat", highlightbackground="#d3d7db", highlightthickness=2)
            card_frame.grid(row=0, column=i, padx=10, pady=10)
            tk.Label(card_frame, text=title, font=("Arial", 14, "bold"), bg="#ffffff", fg="#333").pack(pady=(15, 5))
            tk.Label(card_frame, text=value, font=("Arial", 18, "bold"), bg="#ffffff", fg=color).pack(pady=(0, 15))

        # Button row
        button_frame = tk.Frame(main_frame, bg="#f0f4f7")
        button_frame.pack(pady=40)

        buttons = [
            ("Manage Users", self.open_manage_users, "#2196F3"),
            ("Manage Medical Items", self.open_manage_items, "#2196F3"),
            ("Purchase Items", self.open_user_purchase, "#FF9800"),  # NEW BUTTON
            ("Generate Reports", self.open_reports_window, "#4CAF50"),
            ("Logout", self.logout, "#f44336"),
        ]

        for i, (text, command, color) in enumerate(buttons):
            btn = tk.Button(button_frame, text=text, width=20, height=2, command=command,
                            font=("Arial", 12, "bold"), bg=color, fg="white", bd=0, relief="flat")
            btn.grid(row=0, column=i, padx=10)
            btn.bind("<Enter>", lambda e, b=btn, c=color: b.config(bg=self.darken_color(c)))
            btn.bind("<Leave>", lambda e, b=btn, c=color: b.config(bg=c))

    def darken_color(self, hex_color):
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

    def open_user_purchase(self):
        self.root.withdraw()
        purchase_root = tk.Toplevel()
        UserPurchaseWindow(purchase_root, self.user_data, self.root)

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
