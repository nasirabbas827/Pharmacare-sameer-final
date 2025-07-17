import tkinter as tk
from tkinter import ttk, messagebox
from database import search_items, record_purchase
from PIL import Image, ImageTk
import os

class UserPurchaseWindow:
    def __init__(self, root, user_data, parent_root):
        self.root = root
        self.user_data = user_data
        self.parent_root = parent_root
        self.root.title("PharmaCare - Purchase Items")
        self.root.state('zoomed')
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Main Frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Search and Treeview Frame
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        search_frame = tk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=5)

        tk.Label(search_frame, text="Search:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        tk.Entry(search_frame, textvariable=self.search_var, width=20).pack(side=tk.LEFT, padx=5)

        self.search_by_var = tk.StringVar(value="name")
        tk.OptionMenu(search_frame, self.search_by_var, "name", "item_id", "category").pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Search", command=self.search_items).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Clear", command=self.clear_search).pack(side=tk.LEFT, padx=5)

        self.tree = ttk.Treeview(left_frame, columns=("ID", "Name", "Category", "Unit Price", "Stock"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # Right Frame - Purchase Form
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        form_frame = tk.LabelFrame(right_frame, text="Purchase Item", font=("Arial", 14, "bold"), padx=15, pady=15)
        form_frame.pack(fill=tk.Y, pady=10)

        tk.Label(form_frame, text="Item ID:", font=("Arial", 11)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.item_id_entry = tk.Entry(form_frame, width=20)
        self.item_id_entry.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Quantity:", font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.quantity_entry = tk.Entry(form_frame, width=20)
        self.quantity_entry.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(form_frame, text="Cost Price:", font=("Arial", 11)).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.cost_price_entry = tk.Entry(form_frame, width=20)
        self.cost_price_entry.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(form_frame, text="Purchase Item", command=self.purchase_item, bg="#2196F3", fg="white").grid(row=3, column=0, columnspan=2, pady=10)

        # Image Section
        self.image_frame = tk.LabelFrame(right_frame, text="Item Image", font=("Arial", 12), padx=10, pady=10)
        self.image_frame.pack(fill=tk.X, pady=10)
        self.image_label = tk.Label(self.image_frame, text="No image selected")
        self.image_label.pack()

        # Back Button
        tk.Button(right_frame, text="Back to Dashboard", command=self.on_close, bg="#f44336", fg="white").pack(pady=20)

        self.load_items()
        self.tree.bind('<<TreeviewSelect>>', self.display_item_image)

    def load_items(self):
        self.tree.delete(*self.tree.get_children())
        items = search_items('')
        for item in items:
            self.tree.insert('', tk.END, values=(item['item_id'], item['name'], item['category'], item['unit_price'], item['stock_quantity']))

    def search_items(self):
        search_term = self.search_var.get()
        search_by = self.search_by_var.get()
        self.tree.delete(*self.tree.get_children())
        items = search_items(search_term, search_by)
        for item in items:
            self.tree.insert('', tk.END, values=(item['item_id'], item['name'], item['category'], item['unit_price'], item['stock_quantity']))

    def clear_search(self):
        self.search_var.set('')
        self.load_items()
        self.image_label.config(image='', text="No image selected")

    def display_item_image(self, event):
        selected = self.tree.selection()
        if not selected:
            self.image_label.config(image='', text="No image selected")
            return
        item_id = self.tree.item(selected[0])['values'][0]
        items = search_items(item_id, 'item_id')
        if items and items[0]['image_path'] and os.path.exists(items[0]['image_path']):
            img = Image.open(items[0]['image_path']).resize((150, 150), Image.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.image_label.config(image=photo, text='')
            self.image_label.image = photo
        else:
            self.image_label.config(image='', text="No image available")

    def purchase_item(self):
        try:
            item_id = int(self.item_id_entry.get())
            quantity = int(self.quantity_entry.get())
            cost_price = float(self.cost_price_entry.get())
            record_purchase(item_id, quantity, cost_price)
            messagebox.showinfo("Success", "Item purchased successfully.")
            self.item_id_entry.delete(0, tk.END)
            self.quantity_entry.delete(0, tk.END)
            self.cost_price_entry.delete(0, tk.END)
            self.load_items()
        except ValueError:
            messagebox.showerror("Error", "Enter valid numeric values.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def on_close(self):
        self.root.destroy()
        self.parent_root.deiconify()
        self.parent_root.state("zoomed")
