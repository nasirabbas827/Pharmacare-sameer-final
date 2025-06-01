import tkinter as tk
from user_items import UserItemsWindow
from reports import ReportsWindow  # New module for report generation

class UserDashboard:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        self.root.title("User Dashboard")
        self.root.state('zoomed')  # Fullscreen
        self.root.resizable(True, True)

        tk.Label(self.root, text=f"Welcome, {self.user_data.get('username', 'User')}", font=("Arial", 16)).pack(pady=20)

        tk.Button(self.root, text="View Items", width=20, command=self.open_items_window, font=("Arial", 11), bg="#2196F3", fg="white").pack(pady=10)
        tk.Button(self.root, text="Generate Reports", width=20, command=self.open_reports_window, font=("Arial", 11), bg="#4CAF50", fg="white").pack(pady=10)
        tk.Button(self.root, text="Logout", width=20, command=self.logout, font=("Arial", 11), bg="#f44336", fg="white").pack(pady=30)

    def open_items_window(self):
        self.root.withdraw()
        items_window = tk.Toplevel()
        UserItemsWindow(items_window, self.user_data, self.root)

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