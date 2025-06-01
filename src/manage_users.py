import tkinter as tk
from tkinter import messagebox, ttk
import database

def open_manage_users():
    root = tk.Tk()
    ManageUsers(root)
    root.mainloop()

class ManageUsers:
    def __init__(self, root):
        self.root = root
        self.root.title("Manage Users")
        self.root.state("zoomed")
        self.root.resizable(True, True)

        self.build_ui()

    def build_ui(self):
        # Main frame
        main_frame = tk.Frame(self.root, bg="#f0f4f7")
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title
        tk.Label(main_frame, text="Manage Users", font=("Helvetica", 24, "bold"), fg="#004d99", bg="#f0f4f7").pack(pady=(20, 30))

        # Content frame
        content_frame = tk.Frame(main_frame, bg="#f0f4f7")
        content_frame.pack(fill=tk.BOTH, expand=True)

        # Left panel - Table
        left_frame = tk.Frame(content_frame, bg="#ffffff", bd=2, relief="flat")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 10))
        left_frame.config(highlightbackground="#d3d7db", highlightthickness=2)

        tk.Label(left_frame, text="Users List", font=("Arial", 14, "bold"), bg="#ffffff", fg="#333333").pack(pady=(15, 10))

        # Treeview styling
        style = ttk.Style()
        style.configure("Custom.Treeview", font=("Arial", 12), rowheight=30)
        style.configure("Custom.Treeview.Heading", font=("Arial", 12, "bold"), background="#e0e7ed", foreground="#004d99")
        style.map("Custom.Treeview", background=[('selected', '#e0e7ed')])

        columns = ("user_id", "username", "role")
        self.user_tree = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse", style="Custom.Treeview")
        self.user_tree.heading("user_id", text="User ID")
        self.user_tree.heading("username", text="Username")
        self.user_tree.heading("role", text="Role")

        self.user_tree.column("user_id", width=80, anchor=tk.CENTER)
        self.user_tree.column("username", width=200)
        self.user_tree.column("role", width=100, anchor=tk.CENTER)

        self.user_tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.user_tree.bind("<<TreeviewSelect>>", self.on_user_select)

        # Add alternating row colors
        self.user_tree.tag_configure('oddrow', background='#f9f9f9')
        self.user_tree.tag_configure('evenrow', background='#ffffff')

        # Right panel - Form
        right_frame = tk.Frame(content_frame, bg="#ffffff", bd=2, relief="flat")
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(10, 0), pady=10)
        right_frame.config(highlightbackground="#d3d7db", highlightthickness=2)

        tk.Label(right_frame, text="User Details", font=("Arial", 14, "bold"), bg="#ffffff", fg="#333333").grid(row=0, column=0, columnspan=2, pady=(15, 10))

        # Form fields
        tk.Label(right_frame, text="Username:", font=("Arial", 12), bg="#ffffff", fg="#333333").grid(row=1, column=0, sticky="e", pady=10)
        self.username_entry = tk.Entry(right_frame, font=("Arial", 12), width=25, bg="#f9f9f9", fg="#333333", bd=1, relief="solid")
        self.username_entry.grid(row=1, column=1, pady=10, ipady=6, padx=10)
        self.username_entry.config(highlightbackground="#d3d7db", highlightcolor="#004d99", highlightthickness=1)

        tk.Label(right_frame, text="Password:", font=("Arial", 12), bg="#ffffff", fg="#333333").grid(row=2, column=0, sticky="e", pady=10)
        self.password_entry = tk.Entry(right_frame, show="*", font=("Arial", 12), width=25, bg="#f9f9f9", fg="#333333", bd=1, relief="solid")
        self.password_entry.grid(row=2, column=1, pady=10, ipady=6, padx=10)
        self.password_entry.config(highlightbackground="#d3d7db", highlightcolor="#004d99", highlightthickness=1)

        tk.Label(right_frame, text="Role:", font=("Arial", 12), bg="#ffffff", fg="#333333").grid(row=3, column=0, sticky="e", pady=10)
        self.role_var = tk.StringVar()
        style.configure("Custom.TCombobox", font=("Arial", 12), padding=6, background="#f9f9f9", foreground="#333333")
        style.map("Custom.TCombobox", fieldbackground=[('readonly', '#f9f9f9')], selectbackground=[('readonly', '#f9f9f9')], selectforeground=[('readonly', '#333333')])
        self.role_combobox = ttk.Combobox(right_frame, textvariable=self.role_var, values=["Admin", "User"], state="readonly", width=23, style="Custom.TCombobox")
        self.role_combobox.grid(row=3, column=1, pady=10, ipady=3)

        # Buttons
        self.add_button = tk.Button(right_frame, text="Add User", width=15, font=("Arial", 12, "bold"), bg="#2196F3", fg="white", bd=0, relief="flat", command=self.add_user)
        self.add_button.grid(row=4, column=0, pady=15)
        self.add_button.bind("<Enter>", lambda e: self.add_button.config(bg="#1976D2"))
        self.add_button.bind("<Leave>", lambda e: self.add_button.config(bg="#2196F3"))

        self.update_button = tk.Button(right_frame, text="Update User", width=15, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", bd=0, relief="flat", command=self.update_user, state=tk.DISABLED)
        self.update_button.grid(row=4, column=1, pady=15)
        self.update_button.bind("<Enter>", lambda e: self.update_button.config(bg="#388E3C"))
        self.update_button.bind("<Leave>", lambda e: self.update_button.config(bg="#4CAF50"))

        tk.Button(right_frame, text="Delete User", width=32, font=("Arial", 12, "bold"), bg="#f44336", fg="white", bd=0, relief="flat", command=self.delete_user).grid(row=5, column=0, columnspan=2, pady=10)
        self.delete_button = right_frame.winfo_children()[-1]
        self.delete_button.bind("<Enter>", lambda e: self.delete_button.config(bg="#d32f2f"))
        self.delete_button.bind("<Leave>", lambda e: self.delete_button.config(bg="#f44336"))

        tk.Button(right_frame, text="Back to Dashboard", width=32, font=("Arial", 12, "bold"), bg="#4CAF50", fg="white", bd=0, relief="flat", command=self.go_back).grid(row=6, column=0, columnspan=2, pady=20)
        self.back_button = right_frame.winfo_children()[-1]
        self.back_button.bind("<Enter>", lambda e: self.back_button.config(bg="#388E3C"))
        self.back_button.bind("<Leave>", lambda e: self.back_button.config(bg="#4CAF50"))

        self.selected_user_id = None
        self.load_users()

    def load_users(self):
        for item in self.user_tree.get_children():
            self.user_tree.delete(item)

        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT user_id, username, role FROM users")
        users = cursor.fetchall()
        conn.close()

        for i, user in enumerate(users):
            tag = 'evenrow' if i % 2 == 0 else 'oddrow'
            self.user_tree.insert("", tk.END, values=(user['user_id'], user['username'], user['role']), tags=(tag,))

        self.clear_form()

    def on_user_select(self, event):
        selected = self.user_tree.selection()
        if not selected:
            return
        user_id = self.user_tree.item(selected[0])['values'][0]

        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()

        if not user:
            messagebox.showerror("Error", "User not found.")
            return

        self.selected_user_id = user['user_id']
        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, user['username'])
        self.password_entry.delete(0, tk.END)
        self.role_combobox.set(user['role'])

        self.update_button.config(state=tk.NORMAL)
        self.add_button.config(state=tk.DISABLED)

    def add_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_combobox.get()

        if not username or not password or role not in ['Admin', 'User']:
            messagebox.showerror("Invalid Input", "Please enter valid username, password, and role.")
            return

        try:
            database.add_user(username, password, role)
            messagebox.showinfo("Success", "User added successfully.")
            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_user(self):
        if not self.selected_user_id:
            messagebox.showwarning("No Selection", "Please select a user to update.")
            return

        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        role = self.role_combobox.get()

        if not username or role not in ['Admin', 'User']:
            messagebox.showerror("Invalid Input", "Please enter valid username and role.")
            return

        try:
            conn = database.get_db_connection()
            cursor = conn.cursor()
            if password:
                cursor.execute(
                    "UPDATE users SET username = ?, password = ?, role = ? WHERE user_id = ?",
                    (username, password, role, self.selected_user_id)
                )
            else:
                cursor.execute(
                    "UPDATE users SET username = ?, role = ? WHERE user_id = ?",
                    (username, role, self.selected_user_id)
                )
            conn.commit()
            conn.close()
            messagebox.showinfo("Success", "User updated successfully.")
            self.load_users()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_user(self):
        selected = self.user_tree.selection()
        if not selected:
            messagebox.showwarning("Select User", "Please select a user to delete.")
            return
        user_id = self.user_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete user ID {user_id}?"):
            try:
                conn = database.get_db_connection()
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
                conn.commit()
                conn.close()
                messagebox.showinfo("Deleted", "User deleted successfully.")
                self.load_users()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def clear_form(self):
        self.selected_user_id = None
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.role_combobox.set("")
        self.update_button.config(state=tk.DISABLED)
        self.add_button.config(state=tk.NORMAL)

    def go_back(self):
        self.root.destroy()
        from admin_dashboard import AdminDashboard
        root = tk.Tk()
        AdminDashboard(root, {'username': 'admin', 'role': 'Admin'})
        root.mainloop()