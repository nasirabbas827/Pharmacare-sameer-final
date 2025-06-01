import tkinter as tk
from tkinter import messagebox, ttk, filedialog
from PIL import Image, ImageTk
import os
import database

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def open_manage_items():
    root = tk.Tk()
    ManageItems(root)
    root.mainloop()

class ManageItems:
    def __init__(self, root):
        self.root = root
        self.root.title("Manage Medical Items")
        self.root.title("Admin Dashboard")
        self.root.state("zoomed")  # Fullscreen

        tk.Label(root, text="Manage Medical Items", font=("Arial", 16)).pack(pady=10)

        main_frame = tk.Frame(root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left: Treeview for item listing
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        columns = ("item_id", "name", "category", "unit_price", "cost_price", "stock_quantity")
        self.item_tree = ttk.Treeview(left_frame, columns=columns, show="headings", selectmode="browse")
        for col in columns:
            self.item_tree.heading(col, text=col.replace("_", " ").title())
            self.item_tree.column(col, anchor=tk.CENTER, width=100)

        self.item_tree.pack(fill=tk.BOTH, expand=True)
        self.item_tree.bind("<<TreeviewSelect>>", self.on_item_select)

        # Right: Form
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=(20, 0))

        labels = ["Name", "Category", "Unit Price", "Cost Price", "Stock Quantity", "Description"]
        self.entries = {}

        for i, label in enumerate(labels):
            tk.Label(right_frame, text=label + ":").grid(row=i, column=0, sticky="e", pady=5)
            entry = tk.Entry(right_frame)
            entry.grid(row=i, column=1, pady=5)
            self.entries[label.lower().replace(" ", "_")] = entry

        # Image
        tk.Button(right_frame, text="Select Image", command=self.select_image,
                  bg="#4CAF50", fg="white").grid(row=6, column=0, columnspan=2, pady=5)
        self.image_path = None
        self.image_preview = tk.Label(right_frame)
        self.image_preview.grid(row=7, column=0, columnspan=2, pady=5)

        # Buttons
        self.add_button = tk.Button(right_frame, text="Add Item", command=self.add_item,
                                    bg="#2196F3", fg="white")
        self.add_button.grid(row=8, column=0, pady=10)

        self.update_button = tk.Button(right_frame, text="Update Item", command=self.update_item,
                                       state=tk.DISABLED, bg="#FFC107", fg="black")
        self.update_button.grid(row=8, column=1, pady=10)

        tk.Button(right_frame, text="Delete Item", command=self.delete_item,
                  bg="#f44336", fg="white").grid(row=9, column=0, columnspan=2, pady=5)

        tk.Button(right_frame, text="Back to Dashboard", command=self.go_back,
                  bg="#9C27B0", fg="white").grid(row=10, column=0, columnspan=2, pady=20)

        self.selected_item_id = None
        self.load_items()

    def select_image(self):
        file_path = filedialog.askopenfilename(title="Select Item Image", filetypes=[("Image Files", "*.png *.jpg *.jpeg *.gif")])
        if file_path:
            filename = os.path.basename(file_path)
            dest_path = os.path.join(UPLOAD_DIR, filename)
            with open(file_path, 'rb') as src, open(dest_path, 'wb') as dst:
                dst.write(src.read())
            self.image_path = dest_path
            self.show_image(dest_path)

    def show_image(self, path):
        img = Image.open(path)
        img.thumbnail((100, 100))
        img_tk = ImageTk.PhotoImage(img)
        self.image_preview.configure(image=img_tk)
        self.image_preview.image = img_tk

    def load_items(self):
        for i in self.item_tree.get_children():
            self.item_tree.delete(i)

        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medical_items")
        items = cursor.fetchall()
        conn.close()

        for item in items:
            self.item_tree.insert("", tk.END, values=(
                item["item_id"], item["name"], item["category"],
                item["unit_price"], item["cost_price"], item["stock_quantity"]
            ))

        self.clear_form()

    def on_item_select(self, event):
        selected = self.item_tree.selection()
        if not selected:
            return

        item_id = self.item_tree.item(selected[0])['values'][0]

        conn = database.get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM medical_items WHERE item_id = ?", (item_id,))
        item = cursor.fetchone()
        conn.close()

        if not item:
            return

        self.selected_item_id = item["item_id"]
        self.entries["name"].delete(0, tk.END)
        self.entries["name"].insert(0, item["name"])
        self.entries["category"].delete(0, tk.END)
        self.entries["category"].insert(0, item["category"])
        self.entries["unit_price"].delete(0, tk.END)
        self.entries["unit_price"].insert(0, str(item["unit_price"]))
        self.entries["cost_price"].delete(0, tk.END)
        self.entries["cost_price"].insert(0, str(item["cost_price"]))
        self.entries["stock_quantity"].delete(0, tk.END)
        self.entries["stock_quantity"].insert(0, str(item["stock_quantity"]))
        self.entries["description"].delete(0, tk.END)
        self.entries["description"].insert(0, item["description"] or "")
        self.image_path = item["image_path"]
        if self.image_path:
            self.show_image(self.image_path)

        self.add_button.config(state=tk.DISABLED)
        self.update_button.config(state=tk.NORMAL)

    def add_item(self):
        try:
            values = {k: v.get().strip() for k, v in self.entries.items()}
            if not all([values["name"], values["category"], values["unit_price"], values["cost_price"], values["stock_quantity"]]):
                raise ValueError("All fields except description are required.")
            database.add_item(
                values["name"], values["category"],
                float(values["unit_price"]), float(values["cost_price"]),
                int(values["stock_quantity"]), self.image_path, values.get("description")
            )
            messagebox.showinfo("Success", "Item added successfully.")
            self.load_items()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def update_item(self):
        try:
            if not self.selected_item_id:
                raise ValueError("No item selected.")
            values = {k: v.get().strip() for k, v in self.entries.items()}
            database.update_item(
                self.selected_item_id,
                values["name"], values["category"],
                float(values["unit_price"]), float(values["cost_price"]),
                int(values["stock_quantity"]), self.image_path, values.get("description")
            )
            messagebox.showinfo("Success", "Item updated successfully.")
            self.load_items()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_item(self):
        selected = self.item_tree.selection()
        if not selected:
            messagebox.showwarning("Select Item", "Please select an item to delete.")
            return
        item_id = self.item_tree.item(selected[0])['values'][0]
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete item ID {item_id}?"):
            try:
                database.delete_item(item_id)
                messagebox.showinfo("Deleted", "Item deleted successfully.")
                self.load_items()
            except Exception as e:
                messagebox.showerror("Error", str(e))

    def clear_form(self):
        self.selected_item_id = None
        for entry in self.entries.values():
            entry.delete(0, tk.END)
        self.image_path = None
        self.image_preview.configure(image=None)
        self.image_preview.image = None
        self.add_button.config(state=tk.NORMAL)
        self.update_button.config(state=tk.DISABLED)

    def go_back(self):
        self.root.destroy()
        from admin_dashboard import AdminDashboard
        root = tk.Tk()
        AdminDashboard(root, {'username': 'admin', 'role': 'Admin'})
        root.mainloop()
