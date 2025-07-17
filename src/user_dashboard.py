import tkinter as tk
from user_items import UserItemsWindow
from user_reports import ReportsWindow

class UserDashboard:
    def __init__(self, root, user_data):
        self.root = root
        self.user_data = user_data
        self.root.title("Pharmacy Management System - User Dashboard")
        self.root.state('zoomed')
        self.root.resizable(True, True)

        # Dashboard Heading
        tk.Label(self.root, text="Pharmacy Management System - User Dashboard",
                 font=("Arial", 20, "bold"), fg="#333").pack(pady=20)

        # Welcome message with username
        username = self.user_data.get('username', 'User')
        tk.Label(self.root, text=f"Welcome, {username}", font=("Arial", 14)).pack(pady=10)

        # Frame to hold buttons in a single row
        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=50)

        # Buttons in a row with larger size
        tk.Button(button_frame, text="View & Sale Items", width=25, height=2, command=self.open_items_window,
                  font=("Arial", 11), bg="#2196F3", fg="white").grid(row=0, column=0, padx=20)

        tk.Button(button_frame, text="Generate Reports", width=25, height=2, command=self.open_reports_window,
                  font=("Arial", 11), bg="#4CAF50", fg="white").grid(row=0, column=1, padx=20)

        tk.Button(button_frame, text="Logout", width=25, height=2, command=self.logout,
                  font=("Arial", 11), bg="#f44336", fg="white").grid(row=0, column=2, padx=20)

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
