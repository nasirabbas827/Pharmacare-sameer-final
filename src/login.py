import tkinter as tk
from tkinter import messagebox, ttk
from admin_dashboard import AdminDashboard
from user_dashboard import UserDashboard
from database import authenticate_user

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.state('zoomed')  # Fullscreen
        self.root.resizable(True, True)

        self.build_ui()

    def build_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg="#f0f4f7")
        main_frame.pack(fill="both", expand=True)

        # Form frame with a subtle shadow effect
        form_frame = tk.Frame(main_frame, bg="#ffffff", padx=30, pady=30, bd=2, relief="flat")
        form_frame.place(relx=0.5, rely=0.5, anchor="center")
        # Adding a canvas for shadow effect
        form_frame.config(highlightbackground="#d3d7db", highlightthickness=2)

        # Title
        tk.Label(form_frame, text="Login to PharmaCare", font=("Helvetica", 24, "bold"), bg="#ffffff", fg="#004d99").pack(pady=(0, 30))

        # Username field
        tk.Label(form_frame, text="Username:", font=("Arial", 14), bg="#ffffff", fg="#333333").pack(pady=(10, 5), anchor="w")
        self.username = tk.Entry(form_frame, font=("Arial", 14), width=30, bg="#f9f9f9", fg="#333333", bd=1, relief="solid")
        self.username.pack(pady=(0, 15), ipady=8, padx=10)
        self.username.config(highlightbackground="#d3d7db", highlightcolor="#004d99", highlightthickness=1)

        # Password field
        tk.Label(form_frame, text="Password:", font=("Arial", 14), bg="#ffffff", fg="#333333").pack(pady=(10, 5), anchor="w")
        self.password = tk.Entry(form_frame, show="*", font=("Arial", 14), width=30, bg="#f9f9f9", fg="#333333", bd=1, relief="solid")
        self.password.pack(pady=(0, 15), ipady=8, padx=10)
        self.password.config(highlightbackground="#d3d7db", highlightcolor="#004d99", highlightthickness=1)

        # Role dropdown
        tk.Label(form_frame, text="Role:", font=("Arial", 14), bg="#ffffff", fg="#333333").pack(pady=(10, 5), anchor="w")
        self.role_var = tk.StringVar()
        style = ttk.Style()
        style.configure("Custom.TCombobox", font=("Arial", 14), padding=8, background="#f9f9f9", foreground="#333333")
        style.map("Custom.TCombobox", fieldbackground=[('readonly', '#f9f9f9')], selectbackground=[('readonly', '#f9f9f9')], selectforeground=[('readonly', '#333333')])
        self.role_dropdown = ttk.Combobox(form_frame, textvariable=self.role_var, state='readonly', width=28, style="Custom.TCombobox")
        self.role_dropdown['values'] = ("Admin", "User")
        self.role_dropdown.current(0)
        self.role_dropdown.pack(pady=(0, 20), ipady=4)

        # Login button
        tk.Button(form_frame, text="Login", command=self.login, font=("Arial", 14, "bold"), bg="#004d99", fg="white", width=20, bd=0, relief="flat", activebackground="#003d80").pack(pady=20)
        # Hover effect for button
        self.login_button = form_frame.winfo_children()[-1]
        self.login_button.bind("<Enter>", lambda e: self.login_button.config(bg="#003d80"))
        self.login_button.bind("<Leave>", lambda e: self.login_button.config(bg="#004d99"))

    def login(self):
        user = self.username.get().strip()
        pwd = self.password.get().strip()
        role = self.role_var.get()

        user_data = authenticate_user(user, pwd, role)
        if user_data:
            self.root.destroy()
            new_root = tk.Tk()
            if role == "Admin":
                AdminDashboard(new_root, {'username': user, 'role': role})
            else:
                UserDashboard(new_root, {'username': user, 'role': role})
            new_root.mainloop()
        else:
            messagebox.showerror("Error", "Invalid credentials or role")

if __name__ == "__main__":
    root = tk.Tk()
    LoginWindow(root)
    root.mainloop()