import tkinter as tk
from tkinter import ttk, messagebox
import csv
from datetime import datetime
from tkcalendar import DateEntry
from database import generate_report

class ReportsWindow:
    def __init__(self, root, user_data, parent_root):
        self.root = root
        self.user_data = user_data
        self.parent_root = parent_root
        self.root.title("Generate Reports")
        self.root.state("zoomed")  # Fullscreen
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        # Main frame
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Report selection and date range frame
        selection_frame = tk.LabelFrame(main_frame, text="Report Options", font=("Arial", 12, "bold"), padx=10, pady=10)
        selection_frame.pack(fill=tk.X, pady=5)

        # Report type dropdown
        tk.Label(selection_frame, text="Report Type:", font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.report_type_var = tk.StringVar(value="stock")
        report_options = ["stock", "sales"]
        tk.OptionMenu(selection_frame, self.report_type_var, *report_options).grid(row=0, column=1, padx=5, pady=5)

        # Date range (hidden for stock report)
        self.date_frame = tk.Frame(selection_frame)
        tk.Label(self.date_frame, text="Start Date:", font=("Arial", 11)).grid(row=0, column=0, padx=5, pady=5, sticky=tk.W)
        self.start_date = DateEntry(self.date_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.start_date.grid(row=0, column=1, padx=5, pady=5)

        tk.Label(self.date_frame, text="End Date:", font=("Arial", 11)).grid(row=0, column=2, padx=5, pady=5, sticky=tk.W)
        self.end_date = DateEntry(self.date_frame, width=12, background='darkblue', foreground='white', borderwidth=2, date_pattern='yyyy-mm-dd')
        self.end_date.grid(row=0, column=3, padx=5, pady=5)

        self.date_frame.grid(row=1, column=0, columnspan=2, pady=5)
        self.date_frame.grid_remove()  # Hidden by default for stock report

        # Update date frame visibility based on report type
        self.report_type_var.trace('w', self.toggle_date_frame)

        # Buttons
        tk.Button(selection_frame, text="Generate Report", command=self.generate_report, font=("Arial", 11), bg="#2196F3", fg="white").grid(row=2, column=0, padx=5, pady=10)
        tk.Button(selection_frame, text="Export as CSV", command=self.export_report, font=("Arial", 11), bg="#4CAF50", fg="white").grid(row=2, column=1, padx=5, pady=10)

        # Report display frame
        self.report_frame = tk.LabelFrame(main_frame, text="Report Output", font=("Arial", 12, "bold"), padx=10, pady=10)
        self.report_frame.pack(fill=tk.BOTH, expand=True, pady=5)

        # Treeview for report data
        self.tree = ttk.Treeview(self.report_frame)
        self.tree.pack(fill=tk.BOTH, expand=True)

        # Back button
        tk.Button(main_frame, text="Back to Dashboard", command=self.on_close, font=("Arial", 11), bg="#f44336", fg="white").pack(pady=10)

    def toggle_date_frame(self, *args):
        """Show/hide date frame based on report type."""
        if self.report_type_var.get() == "stock":
            self.date_frame.grid_remove()
        else:
            self.date_frame.grid()

    def generate_report(self):
        """Generates and displays the selected report."""
        report_type = self.report_type_var.get()
        self.tree.delete(*self.tree.get_children())
        self.tree["columns"] = ()
        self.tree["show"] = ""

        start_date = self.start_date.get() if report_type != "stock" else None
        end_date = self.end_date.get() if report_type != "stock" else None

        # Validate dates for non-stock reports
        if report_type != "stock":
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
                return

        # Fetch report data
        report_data = generate_report(report_type, start_date, end_date)

        if report_type == "stock":
            self.tree["columns"] = ("ID", "Name", "Category", "Stock Quantity")
            self.tree["show"] = "headings"
            for col in self.tree["columns"]:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=150)
            for item in report_data:
                self.tree.insert('', tk.END, values=(
                    item['item_id'], item['name'], item['category'], item['stock_quantity']
                ))

        elif report_type == "sales":
            self.tree["columns"] = ("Sale ID", "Item ID", "Name", "Quantity Sold", "Sale Price", "Date")
            self.tree["show"] = "headings"
            for col in self.tree["columns"]:
                self.tree.heading(col, text=col)
                self.tree.column(col, width=150)
            for sale in report_data:
                self.tree.insert('', tk.END, values=(
                    sale['sale_id'], sale['item_id'], sale['name'],
                    sale['quantity_sold'], sale['sale_price'], sale['sale_date']
                ))


        if not report_data:
            messagebox.showinfo("Info", "No data available for the selected report.")

    def export_report(self):
        """Exports the selected report as a CSV file."""
        report_type = self.report_type_var.get()
        start_date = self.start_date.get() if report_type != "stock" else "N/A"
        end_date = self.end_date.get() if report_type != "stock" else "N/A"

        if report_type != "stock":
            try:
                datetime.strptime(start_date, '%Y-%m-%d')
                datetime.strptime(end_date, '%Y-%m-%d')
            except ValueError:
                messagebox.showerror("Error", "Invalid date format. Please use YYYY-MM-DD.")
                return

        report_data = generate_report(report_type, start_date, end_date)
        if not report_data:
            messagebox.showerror("Error", "No data available to export.")
            return

        filename = f"{report_type}_report_{start_date}_to_{end_date}.csv" if report_type != "stock" else f"stock_report_{datetime.now().strftime('%Y-%m-%d')}.csv"

        try:
            with open(filename, 'w', newline='') as csvfile:
                writer = csv.writer(csvfile)
                if report_type == "stock":
                    writer.writerow(["ID", "Name", "Category", "Stock Quantity"])
                    for item in report_data:
                        writer.writerow([item['item_id'], item['name'], item['category'], item['stock_quantity']])
                elif report_type == "sales":
                    writer.writerow(["Sale ID", "Item ID", "Name", "Quantity Sold", "Sale Price", "Date"])
                    for sale in report_data:
                        writer.writerow([sale['sale_id'], sale['item_id'], sale['name'],
                                        sale['quantity_sold'], sale['sale_price'], sale['sale_date']])
            messagebox.showinfo("Success", f"Report exported as {filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export report: {e}")

    def on_close(self):
        """Closes the report window and returns to the dashboard."""
        self.root.destroy()
        self.parent_root.deiconify()
        self.parent_root.state("zoomed")  # Ensure dashboard is maximized again