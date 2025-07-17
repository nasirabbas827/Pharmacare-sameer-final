import tkinter as tk
from tkinter import ttk, messagebox
from database import search_items, record_sale
from PIL import Image, ImageTk
import os

class UserItemsWindow:
    def __init__(self, root, user_data, parent_root):
        self.root = root
        self.user_data = user_data
        self.parent_root = parent_root
        self.root.title("PharmaCare Items - Sell")
        self.root.state('zoomed')  # Fullscreen
        self.root.resizable(True, True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Main container frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Left frame for Treeview and search
        left_frame = tk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)

        # Search frame
        search_frame = tk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=5)

        tk.Label(search_frame, text="Search:", font=("Arial", 12)).pack(side=tk.LEFT, padx=5)
        self.search_var = tk.StringVar()
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=5)

        self.search_by_var = tk.StringVar(value="name")
        search_options = ["name", "item_id", "category"]
        tk.OptionMenu(search_frame, self.search_by_var, *search_options).pack(side=tk.LEFT, padx=5)
        
        tk.Button(search_frame, text="Search", command=self.search_items, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)
        tk.Button(search_frame, text="Clear", command=self.clear_search, font=("Arial", 10)).pack(side=tk.LEFT, padx=5)

        # Treeview for items
        self.tree = ttk.Treeview(left_frame, columns=("ID", "Name", "Category", "Unit Price", "Stock"), show='headings')
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, width=120)
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)
        self.tree.bind('<<TreeviewSelect>>', self.display_item_image)

        # Right frame for forms, image, and button
        right_frame = tk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.Y, padx=10)

        # Form frame with enhanced styling
        form_frame = tk.LabelFrame(right_frame, text="Item Operations", font=("Arial", 14, "bold"), padx=15, pady=15)
        form_frame.pack(fill=tk.Y, pady=10)

        # Sale form
        sale_frame = tk.LabelFrame(form_frame, text="Sell Item", font=("Arial", 12), padx=10, pady=10, relief=tk.RIDGE)
        sale_frame.pack(fill=tk.X, pady=5)

        tk.Label(sale_frame, text="Item ID:", font=("Arial", 11)).grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.sale_item_id = tk.Entry(sale_frame, width=20, font=("Arial", 11))
        self.sale_item_id.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(sale_frame, text="Quantity:", font=("Arial", 11)).grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.sale_quantity = tk.Entry(sale_frame, width=20, font=("Arial", 11))
        self.sale_quantity.grid(row=1, column=1, padx=5, pady=5)

        tk.Label(sale_frame, text="Sale Price:", font=("Arial", 11)).grid(row=2, column=0, sticky=tk.W, padx=5, pady=5)
        self.sale_price = tk.Entry(sale_frame, width=20, font=("Arial", 11))
        self.sale_price.grid(row=2, column=1, padx=5, pady=5)

        tk.Button(sale_frame, text="Sell Item", command=self.sell_item, font=("Arial", 11), bg="#4CAF50", fg="white").grid(row=3, column=0, columnspan=2, pady=10)


        # Image display frame
        self.image_frame = tk.LabelFrame(right_frame, text="Item Image", font=("Arial", 12), padx=10, pady=10)
        self.image_frame.pack(fill=tk.X, pady=10)
        self.image_label = tk.Label(self.image_frame, text="No image selected", font=("Arial", 10))
        self.image_label.pack(pady=10)

        # Back to Dashboard button
        tk.Button(right_frame, text="Back to Dashboard", width=20, command=self.on_close, font=("Arial", 11), bg="#f44336", fg="white").pack(pady=20)

        self.load_items()

    def load_items(self):
        """Loads items into the Treeview."""
        self.tree.delete(*self.tree.get_children())
        items = search_items('')
        for item in items:
            self.tree.insert('', tk.END, values=(
                item['item_id'], item['name'], item['category'],
                item['unit_price'], item['stock_quantity']
            ))

    def search_items(self):
        """Searches items based on the selected criteria and updates the Treeview."""
        search_term = self.search_var.get()
        search_by = self.search_by_var.get()
        self.tree.delete(*self.tree.get_children())
        items = search_items(search_term, search_by)
        for item in items:
            self.tree.insert('', tk.END, values=(
                item['item_id'], item['name'], item['category'],
                item['unit_price'], item['stock_quantity']
            ))

    def clear_search(self):
        """Clears the search field and reloads all items."""
        self.search_var.set('')
        self.load_items()
        self.image_label.config(image='', text="No image selected")

    def display_item_image(self, event):
        """Displays the image of the selected item."""
        selected_item = self.tree.selection()
        if not selected_item:
            self.image_label.config(image='', text="No image selected")
            return

        item_id = self.tree.item(selected_item[0])['values'][0]
        items = search_items(item_id, 'item_id')
        if items and items[0]['image_path'] and os.path.exists(items[0]['image_path']):
            try:
                img = Image.open(items[0]['image_path'])
                img = img.resize((150, 150), Image.LANCZOS)
                photo = ImageTk.PhotoImage(img)
                self.image_label.config(image=photo, text='')
                self.image_label.image = photo  # Keep a reference to avoid garbage collection
            except Exception as e:
                self.image_label.config(image='', text="Error loading image")
        else:
            self.image_label.config(image='', text="No image available")

    def sell_item(self):
        """Handles the sale of an item."""
        try:
            item_id = int(self.sale_item_id.get())
            quantity = int(self.sale_quantity.get())
            sale_price = float(self.sale_price.get())

            # Validate stock before selling
            selected_stock = None
            for child in self.tree.get_children():
                values = self.tree.item(child)['values']
                if values[0] == item_id:
                    selected_stock = values[4]
                    break
            if selected_stock is None:
                messagebox.showerror("Error", "Item ID not found.")
                return
            if quantity > selected_stock:
                messagebox.showerror("Error", f"Insufficient stock. Available: {selected_stock}")
                return

            record_sale(item_id, quantity, sale_price)
            messagebox.showinfo("Success", "Item sold successfully. Stock updated.")
            self.clear_sale_form()
            self.load_items()
            self.image_label.config(image='', text="No image selected")
        except ValueError:
            messagebox.showerror("Error", "Please enter valid numeric values in sale form.")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_sale_form(self):
        """Clears the sale form fields."""
        self.sale_item_id.delete(0, tk.END)
        self.sale_quantity.delete(0, tk.END)
        self.sale_price.delete(0, tk.END)


    def on_close(self):
        """Closes the report window and returns to the dashboard."""
        self.root.destroy()
        self.parent_root.deiconify()
        self.parent_root.state("zoomed")  
