import tkinter as tk
from tkinter import ttk, messagebox
from pymongo import MongoClient
from bson import ObjectId
import certifi
from datetime import datetime, timedelta
from tkcalendar import DateEntry
import os
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch

class MongoDBCRUDApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MongoDB CRUD Operations")
        self.root.geometry("1500x900")
        self.root.configure(bg="#f0f0f0")
        self.invoice_dir = os.path.join(os.path.expanduser("~"), "Invoices")
        if not os.path.exists(self.invoice_dir):
            os.makedirs(self.invoice_dir)
        connection_string = "mongodb+srv://AliZamanKhan:AliZaman15@cluster0.fuhk5.mongodb.net/"
        self.client = MongoClient(connection_string, tlsCAFile=certifi.where())
        self.db = self.client["New"]
        self.collection = self.db["Table1"]
        self.stock_collection = self.db["Stock"]
        self.cash_history = self.db["Cash History"]
        self.customers_collection = self.db["Customers"]
        self.create_ui()  

    def create_ui(self):
        self.main_container = ttk.Frame(self.root, padding="20", style="Main.TFrame")
        self.main_container.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.button_frame = ttk.Frame(self.main_container, padding="10", style="ButtonFrame.TFrame")
        self.button_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        self.create_toggle_buttons()
        self.create_original_data_section()
        self.create_stock_management_section()
        self.cash_history_view = CashHistoryView(self.main_container, self.cash_history)
        self.cash_history_view.frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.cash_history_view.frame.grid_remove()
        self.customers_history_view = CustomerHistoryView(self.main_container, self.customers_collection)
        self.customers_history_view.frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.customers_history_view.frame.grid_remove()  
        self.apply_custom_styles()

    def record_cash_history(self, item_name, qty, price, transaction_type):
        try:
            if isinstance(price, str):
                price = price.replace('$', '').replace(',', '')
                try:
                    price = float(price)
                except ValueError:
                    price = 0.0
            transaction = {
                "Name": item_name,
                "QTY": int(qty) if qty else 0,
                "Price": price,
                "Type": transaction_type,
                "Date": datetime.now()  
            }            
            self.cash_history.insert_one(transaction)
        except Exception as e:
            messagebox.showerror("Error", f"Error recording cash history: {str(e)}")
    def create_toggle_buttons(self):
        self.original_button = ttk.Button(
            self.button_frame,
            text="Original Data",
            style="ToggleButton.TButton",
            command=self.show_original_data
        )
        self.stock_button = ttk.Button(
            self.button_frame,
            text="Stock Management",
            style="ToggleButton.TButton",
            command=self.show_stock_management
        )
        self.cash_history_button = ttk.Button(
            self.button_frame,
            text="Cash History",
            style="ToggleButton.TButton",
            command=self.show_cash_history
        )
        self.customers_history_button = ttk.Button(
        self.button_frame,
        text="Customers History",
        style="ToggleButton.TButton",
        command=self.show_customers_history
        )
        self.customers_history_button.grid(row=0, column=3, padx=5)

        self.original_button.grid(row=0, column=0, padx=5)
        self.stock_button.grid(row=0, column=1, padx=5)
        self.cash_history_button.grid(row=0, column=2, padx=5)
        self.highlight_button(self.original_button)

    def show_customers_history(self):
    # Hide other sections
        self.original_frame.grid_remove()
        self.stock_frame.grid_remove()
        self.cash_history_view.frame.grid_remove()
    
    # Show customers history view
        self.customers_history_view.frame.grid()
    
    # Update button styles
        self.highlight_button(self.customers_history_button)
        self.original_button.configure(style="ToggleButton.TButton")
        self.stock_button.configure(style="ToggleButton.TButton")
        self.cash_history_button.configure(style="ToggleButton.TButton")
   
    def create_quality_diesel_invoice(self, transaction_data, customer_data, stock_item):
        # Generate unique invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        filename = os.path.join(self.invoice_dir, f"{invoice_number}_QualityDiesel.pdf")

        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontSize=14, fontName='Helvetica-Bold', alignment=1)
        field_label_style = ParagraphStyle('FieldLabel', parent=styles['Normal'], fontSize=12, fontName='Courier-Bold')
        field_value_style = ParagraphStyle('FieldValue', parent=styles['Normal'], fontSize=12, fontName='Courier')

        # Header
        elements.append(Paragraph("=== QUALITY DIESEL SPARES INVOICE ===", title_style))
        elements.append(Spacer(1, 12))

        # Transaction Details Section
        elements.append(Paragraph("Transaction Details:", field_label_style))
        transaction_details = [
            f"Ref Number:       {transaction_data.get('Ref Number', 'N/A')}",
            f"Date:             {transaction_data.get('Date', 'N/A')}",
            f"Description:      {transaction_data.get('Description', 'N/A')}",
            f"Item Number:      {transaction_data.get('Item Number', 'N/A')}",
            f"QTY:              {transaction_data.get('QTY', 'N/A')}",
            f"Sale Price:       {transaction_data.get('Sale Price', 'N/A')}",
        ]
        for detail in transaction_details:
            elements.append(Paragraph(detail, field_value_style))

        elements.append(Spacer(1, 10))

        # Customer Details Section
        elements.append(Paragraph("Customer Details:", field_label_style))
        customer_details = [
            f"Customer Name:    {customer_data.get('Name', 'N/A')}",
            f"Phone:            {customer_data.get('Phone', 'N/A')}",
            f"Email:            {customer_data.get('Email', 'N/A')}",
            f"Address:          {customer_data.get('Address', 'N/A')}",
            f"City:             {customer_data.get('City', 'N/A')}",
            f"State:            {customer_data.get('State', 'N/A')}",
            f"Zip:              {customer_data.get('Zip', 'N/A')}",
        ]
        for detail in customer_details:
            elements.append(Paragraph(detail, field_value_style))

        # Build PDF
        doc.build(elements)
        return filename

    def create_sn_invoice(self, transaction_data, customer_data, stock_item):
        # Generate unique invoice number
        invoice_number = f"INV-{datetime.now().strftime('%Y%m%d%H%M%S')}"
        filename = os.path.join(self.invoice_dir, f"{invoice_number}_SNInternational.pdf")

        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=letter)
        elements = []

        # Styles
        styles = getSampleStyleSheet()
        title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontSize=14, fontName='Helvetica-Bold', alignment=1)
        details_style = ParagraphStyle('DetailsStyle', parent=styles['Normal'], fontSize=10, fontName='Helvetica', alignment=0)
        divider = "-" * 120

        # Header Section
        elements.append(Paragraph("=== SN INTERNATIONAL INVOICE ===", title_style))
        elements.append(Spacer(1, 12))
        header_details = (
            "FAWAD AHMED<br/>"
            "11 IKRAM AUTO MARKET<br/>"
            "HEAD OFFICE<br/>"
            "03334426608<br/>"
            "kfawada05@gmail.com"
        )
        elements.append(Paragraph(header_details, details_style))
        elements.append(Spacer(1, 12))
        elements.append(Paragraph(divider, details_style))
        elements.append(Spacer(1, 12))

        # Customer Info with Border
        customer_table_data = [
            [
                Paragraph(f"Customer Name: {customer_data.get('Name', 'N/A')}", details_style),
                Paragraph(f"{'Customer ID:'.ljust(30)} {customer_data.get('Customer ID', 'N/A')}", details_style)
            ]
        ]
        customer_table = Table(customer_table_data, colWidths=[4.0 * inch, 2.0 * inch])
        customer_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (0, 0), 'LEFT'),  # Align Customer Name to the left
            ('ALIGN', (1, 0), (1, 0), 'RIGHT'),  # Align Customer ID to the right
            ('PADDING', (0, 0), (-1, -1), 5)
        ]))
        elements.append(customer_table)
        elements.append(Spacer(1, 12))

        # Table of Transaction Details
        table_data = [['#', 'DESCRIPTION', 'QTY', 'PRICE', 'TOTAL']]
        qty = int(transaction_data.get("QTY", 0))
        price = float(transaction_data.get("Sale Price", "0").replace("Rs", "").replace(",", ""))
        total = qty * price

        # Transaction Details Table Data
        table_data.append([
            '1',
            stock_item.get('Name', 'N/A'),
            str(qty),
            f"Rs{price:,.2f}",
            f"Rs{total:,.2f}"
        ])
        table = Table(table_data, colWidths=[0.5 * inch, 2.8 * inch, 0.8 * inch, 1.3 * inch, 1.3 * inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold')
        ]))
        elements.append(table)
        elements.append(Spacer(1, 12))

        # Grand Total Row
        grand_total_data = [
            ['', '', '', 'GRAND TOTAL', f"Rs{total:,.2f}"]
        ]
        grand_total_table = Table(grand_total_data, colWidths=[0.5 * inch, 2.8 * inch, 0.8 * inch, 1.3 * inch, 1.3 * inch])
        grand_total_table.setStyle(TableStyle([
            ('BACKGROUND', (3, 0), (4, 0), colors.lightgrey),
            ('ALIGN', (3, 0), (4, 0), 'CENTER'),
            ('GRID', (3, 0), (4, 0), 0.5, colors.black),
            ('FONTNAME', (3, 0), (4, 0), 'Helvetica-Bold')
        ]))
        elements.append(grand_total_table)

        # Build PDF
        doc.build(elements)
        return filename

    def highlight_button(self, button):
        style = ttk.Style()
        style.configure("ToggleButton.TButton", background="#e0e0e0", font=("Roboto", 12, "bold"))
        style.configure("ActiveToggleButton.TButton", background="#c0c0c0", font=("Roboto", 12, "bold"))
        button.configure(style="ActiveToggleButton.TButton")

    def show_original_data(self):
        self.stock_frame.grid_remove()
        self.cash_history_view.frame.grid_remove()
        self.original_frame.grid()
        self.highlight_button(self.original_button)
        self.customers_history_view.frame.grid_remove()
        self.stock_button.configure(style="ToggleButton.TButton")
        self.cash_history_button.configure(style="ToggleButton.TButton")
        self.customers_history_button.configure(style="ToggleButton.TButton")

    def show_cash_history(self):
        self.original_frame.grid_remove()
        self.stock_frame.grid_remove()
        self.customers_history_view.frame.grid_remove()  # Add this line
        self.cash_history_view.frame.grid()
        self.highlight_button(self.cash_history_button)
        self.original_button.configure(style="ToggleButton.TButton")
        self.stock_button.configure(style="ToggleButton.TButton")
        self.customers_history_button.configure(style="ToggleButton.TButton")

    def show_stock_management(self):
        self.original_frame.grid_remove()
        self.cash_history_view.frame.grid_remove()
        self.customers_history_view.frame.grid_remove()  # Add this line
        self.stock_frame.grid()
        self.highlight_button(self.stock_button)
        self.original_button.configure(style="ToggleButton.TButton")
        self.cash_history_button.configure(style="ToggleButton.TButton")
        self.customers_history_button.configure(style="ToggleButton.TButton")

    def create_original_data_section(self):
        self.original_frame = ttk.Frame(self.main_container, padding="10", style="OriginalData.TFrame")
        self.original_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        self.create_data_fields(self.original_frame)
        self.create_original_tree()

    def create_stock_management_section(self):
        self.stock_frame = ttk.Frame(self.main_container, padding="10", style="StockManagement.TFrame")
        self.stock_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.stock_frame.grid_remove()  # Initially hidden

        self.create_stock_fields()
        self.create_stock_tree()

    def create_data_fields(self, parent):
        transaction_frame = ttk.LabelFrame(parent, text="Transaction Details", padding="5")
        transaction_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5, padx=5)

        self.field_vars = [
            ("Ref Number:", tk.StringVar()),
            ("Date:", tk.StringVar()),
            ("Description:", tk.StringVar()),
            ("Item Number:", tk.StringVar()),
            ("QTY:", tk.StringVar()),
            ("Sale Price:", tk.StringVar()),
            ("BAC:", tk.StringVar()),
        ]
        for i, (text, var) in enumerate(self.field_vars):
            ttk.Label(transaction_frame, text=text, style="FieldLabel.TLabel").grid(row=i, column=0, sticky=tk.W, pady=2)
            ttk.Entry(transaction_frame, textvariable=var, style="FieldEntry.TEntry").grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2)
        customer_frame = ttk.LabelFrame(parent, text="Customer Details", padding="5")
        customer_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=5, padx=5)
        self.customer_vars = [
            ("Customer ID:", tk.StringVar()),
            ("Name:", tk.StringVar()),
            ("Phone:", tk.StringVar()),
            ("Email:", tk.StringVar()),
            ("Address:", tk.StringVar()),
            ("City:", tk.StringVar()),
            ("State:", tk.StringVar()),
            ("ZIP:", tk.StringVar()),
        ]

        for i, (text, var) in enumerate(self.customer_vars):
            ttk.Label(customer_frame, text=text, style="FieldLabel.TLabel").grid(row=i, column=0, sticky=tk.W, pady=2)
            ttk.Entry(customer_frame, textvariable=var, style="FieldEntry.TEntry").grid(row=i, column=1, sticky=(tk.W, tk.E), pady=2)

        # Buttons
        button_frame = ttk.Frame(parent, style="ButtonFrame.TFrame")
        button_frame.grid(row=1, column=0, columnspan=2, pady=10)

        buttons = [
            ("Create", self.create_record),
            ("Find", self.find_record),
            ("Update", self.update_record),
            ("Delete", self.delete_record),
            ("Clear", self.clear_fields),
            ("Sold", self.mark_as_sold),
            ("Find Customer", self.find_customer),
            ("Generate Invoice", self.generate_invoice)
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=command, style="ActionButton.TButton").grid(row=0, column=i, padx=5)

    def create_stock_fields(self):
        self.stock_field_vars = [
            ("Part Number:", tk.StringVar()),
            ("Name:", tk.StringVar()),
            ("Brand:", tk.StringVar()),
            ("Purchase Price:", tk.StringVar()),
            ("Date of Purchase:", tk.StringVar()),
            ("Sale Price:", tk.StringVar()),
            ("Sale Date:", tk.StringVar()),
            ("Location:", tk.StringVar()),
            ("Quantity:", tk.StringVar()),  # Added Quantity field
        ]

        for i, (text, var) in enumerate(self.stock_field_vars):
            row = i % 5  # Changed to 5 to accommodate the new field
            col = (i // 5) * 2
            ttk.Label(self.stock_frame, text=text, style="FieldLabel.TLabel").grid(row=row, column=col, sticky=tk.W, pady=5)
            ttk.Entry(self.stock_frame, textvariable=var, style="FieldEntry.TEntry").grid(row=row, column=col+1, sticky=(tk.W, tk.E), pady=5, padx=(0, 10))

        button_frame = ttk.Frame(self.stock_frame, style="ButtonFrame.TFrame")
        button_frame.grid(row=5, column=0, columnspan=4, pady=10)

        buttons = [
            ("Find", self.find_stock),
            ("Create", self.create_stock),
            ("Update", self.update_stock),
            ("Delete", self.delete_stock),
            ("Clear", self.clear_stock_fields),
            ("Calculate Total", self.calculate_total)
        ]

        for i, (text, command) in enumerate(buttons):
            ttk.Button(button_frame, text=text, command=command, style="ActionButton.TButton").grid(row=0, column=i, padx=5)

    # def generate_invoice(self):
    #     try:
    #         # Get current record data
    #         record_data = {
    #             name.replace(":", ""): var.get()
    #             for name, var in self.field_vars
    #         }
    #         customer_data = {
    #             name.replace(":", ""): var.get()
    #             for name, var in self.customer_vars
    #         }

    #         if not record_data["Ref Number"]:
    #             messagebox.showerror("Error", "Please select a record first!")
    #             return

    #         qty_to_deduct = int(record_data.get("QTY", 0))
    #         stock_item = self.stock_collection.find_one({"Part Number": record_data["Ref Number"]})

    #         if not stock_item:
    #             messagebox.showerror("Error", "Stock item not found!")
    #             return

    #         # Show popup modal with transaction and customer details
    #         #changed
    #         # self.show_invoice_preview(record_data, customer_data, stock_item)
    #         self.show_invoice_modal(record_data, customer_data, stock_item)


    #     except Exception as e:
    #         messagebox.showerror("Error", f"Error generating invoice: {str(e)}")

    def generate_invoice(self):
        try:
            # Get current record data
            record_data = {
                name.replace(":", ""): var.get()
                for name, var in self.field_vars
            }
            customer_data = {
                name.replace(":", ""): var.get()
                for name, var in self.customer_vars
            }

            if not record_data["Ref Number"]:
                messagebox.showerror("Error", "Please select a record first!")
                return

            qty_to_deduct = int(record_data.get("QTY", 0))
            stock_item = self.stock_collection.find_one({"Part Number": record_data["Ref Number"]})

            if not stock_item:
                messagebox.showerror("Error", "Stock item not found!")
                return

            # Save customer data to the database
            customer_id = customer_data["Customer ID"]
            if not customer_id:  # If no Customer ID, generate one
                customer_id = str(ObjectId())
                customer_data["Customer ID"] = customer_id

            customer_data.update({
             "Ref Number": record_data["Ref Number"],
             "Date": record_data["Date"],
             "Item Number": record_data["Item Number"],
             "Sale Price": record_data["Sale Price"],
             "BAC": record_data["BAC"],
            })
            # Update customer in database
            self.customers_collection.update_one(
                {"Customer ID": customer_id},
                {"$set": customer_data},
                upsert=True  # Insert if not found
            )

            # Update the Customer History view
            self.customers_history_view.search_records()  # Refresh the table

            # Proceed with the rest of the logic (e.g., generating PDF, updating stock, etc.)
            self.show_invoice_modal(record_data, customer_data, stock_item)

        except Exception as e:
            messagebox.showerror("Error", f"Error generating invoice: {str(e)}")


    def show_invoice_modal(self, record_data, customer_data, stock_item):
        # Create a popup window
        popup = tk.Toplevel(self.root)
        popup.title("Invoice Details")
        popup.geometry("500x600")
        popup.transient(self.root)  # Make it a modal dialog
        popup.grab_set()

        # Create a frame for the popup content
        frame = ttk.Frame(popup, padding="10")
        frame.pack(fill="both", expand=True)

        # Dropdown for selecting invoice type
        invoice_type_label = ttk.Label(frame, text="Select Invoice Type:", font=("Helvetica", 10, "bold"))
        invoice_type_label.pack(pady=5)

        invoice_type = tk.StringVar()
        invoice_type_dropdown = ttk.Combobox(frame, textvariable=invoice_type, state="readonly", font=("Helvetica", 10))
        invoice_type_dropdown['values'] = ["Quality Diesel Spares", "SN International"]
        invoice_type_dropdown.pack(pady=5)
        invoice_type_dropdown.current(0)  # Set default selection

        # Frame for dynamic view
        dynamic_frame = ttk.Frame(frame)
        dynamic_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Text area for Quality Diesel Spares view
        diesel_view = tk.Text(dynamic_frame, wrap="word", font=("Courier", 10))
        diesel_view.pack(fill="both", expand=True)

        # Populate initial Quality Diesel Spares view content
        def update_diesel_view():
            diesel_content = (
                 "=== QUALITY DIESEL SPARES INVOICE ===\n\n"
                f"Transaction Details:\n"
                f"{'Ref Number:'.ljust(15)} {record_data.get('Ref Number', 'N/A')}\n"
                f"{'Date:'.ljust(15)} {record_data.get('Date', 'N/A')}\n"
                f"{'Description:'.ljust(15)} {record_data.get('Description', 'N/A')}\n"
                f"{'Item Number:'.ljust(15)} {record_data.get('Item Number', 'N/A')}\n"
                f"{'QTY:'.ljust(15)} {record_data.get('QTY', 'N/A')}\n"
                f"{'Sale Price:'.ljust(15)} {record_data.get('Sale Price', 'N/A')}\n\n"
                f"Customer Details:\n"
                f"{'Customer Name:'.ljust(15)} {customer_data.get('Name', 'N/A')}\n"
                f"{'Phone:'.ljust(15)} {customer_data.get('Phone', 'N/A')}\n"
                f"{'Email:'.ljust(15)} {customer_data.get('Email', 'N/A')}\n"
                f"{'Address:'.ljust(15)} {customer_data.get('Address', 'N/A')}\n"
                f"{'City:'.ljust(15)} {customer_data.get('City', 'N/A')}\n"
                f"{'State:'.ljust(15)} {customer_data.get('State', 'N/A')}\n"
                f"{'Zip:'.ljust(15)} {customer_data.get('Zip', 'N/A')}\n"
            )
            diesel_view.configure(state="normal")
            diesel_view.delete("1.0", tk.END)
            diesel_view.insert("1.0", diesel_content)
            diesel_view.configure(state="disabled")
            diesel_view.tag_add("bold", "1.0", "1.end")  
            diesel_view.configure(state="disabled")

        # Text area for SN International view (hidden initially)
        sn_view = tk.Text(dynamic_frame, wrap="word", font=("Courier", 10))
        sn_view.pack(fill="both", expand=True)
        sn_view.pack_forget()  # Hide initially

        def update_sn_view():
            # Generate the divider
            divider = "-" * 55
            qty = int(record_data.get("QTY", 0))
            price = float(record_data.get("Sale Price", "0").replace("Rs", "").replace(",", ""))
            total = qty * price

            table_headers = f"{'#'.ljust(5)}{'DESCRIPTION'.ljust(20)}{'QTY'.ljust(10)}{'PRICE'.ljust(10)}{'TOTAL'.ljust(10)}\n"
            table_row = f"{'1'.ljust(5)}{stock_item.get('Name', 'N/A').ljust(20)}{str(qty).ljust(10)}{'Rs' + f'{price:,.2f}'.ljust(10)}{'Rs' + f'{total:,.2f}'.ljust(10)}\n"
            # Format the content
            sn_content = (
                "=== SN International Invoice ===\n"  # Header
                f"{'FAWAD AHMED'.ljust(10)}\n"
                f"{'11 IKRAM AUTO MARKET'.ljust(10)}\n"
                f"{'HEAD OFFICE'.ljust(10)}\n"
                f"{'📞 03334426608'.ljust(10)}\n"
                f"{'kfawada05@gmail.com'.ljust(10)}\n"
                f"{divider}\n"  
                f"To: {customer_data.get('Name', 'N/A')}{' ' * 50}"  
                f"{'Date: ' + datetime.now().strftime('%d-%m-%Y')}\n" 
                f"{'Customer ID: ' + customer_data.get('Customer ID', 'N/A')}\n\n"  # Customer ID on the right

                f"Transaction Details:\n"
                f"{table_headers}" 
                f"{table_row}"
                f"{divider}\n"  
                f"{'Item:'.ljust(15)} {stock_item.get('Name', 'N/A')}\n"
                f"{'Price:'.ljust(15)} Rs.{record_data.get('Sale Price', 'N/A')}\n\n"
            )

            # Configure the view
            sn_view.configure(state="normal")
            sn_view.delete("1.0", tk.END)
            sn_view.insert("1.0", sn_content)
            sn_view.configure(state="disabled")

        # Update the view based on dropdown selection
        def update_view(*args):
            if invoice_type.get() == "Quality Diesel Spares":
                sn_view.pack_forget()
                diesel_view.pack(fill="both", expand=True)
                update_diesel_view()
            elif invoice_type.get() == "SN International":
                diesel_view.pack_forget()
                sn_view.pack(fill="both", expand=True)
                update_sn_view()

        # Bind dropdown selection to update view
        invoice_type.trace_add("write", update_view)

        # Initialize the default view
        update_view()

        # Buttons to generate and close the popup
        button_frame = ttk.Frame(frame, padding="10")
        button_frame.pack(fill="x", pady=10)

        ttk.Button(button_frame, text="Generate PDF", command=lambda: self.generate_invoice_with_type(invoice_type.get(), record_data, customer_data, stock_item, popup)).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Close", command=popup.destroy).pack(side="right", padx=5)

    def generate_invoice_with_type(self, invoice_type, record_data, customer_data, stock_item, popup):
        if not invoice_type:
            messagebox.showerror("Error", "Please select an invoice type!")
            return

        try:
            if invoice_type == "Quality Diesel Spares":
                invoice_file = self.create_quality_diesel_invoice(record_data, customer_data, stock_item)
            elif invoice_type == "SN International":
                invoice_file = self.create_sn_invoice(record_data, customer_data, stock_item)
            else:
                messagebox.showerror("Error", "Invalid invoice type selected!")
                return

            popup.destroy()
            messagebox.showinfo("Invoice Generated", f"Invoice ({invoice_type}) saved at: {invoice_file}")
        except Exception as e:
            messagebox.showerror("Error", f"Error generating invoice: {str(e)}")


    def save_and_close_popup(self, record_data, customer_data, stock_item, popup):
        # Generate the PDF invoice
        invoice_file = self.create_invoice(record_data, customer_data, stock_item)
        popup.destroy()  # Close the popup window

        # Show success message
        messagebox.showinfo("Success", f"Invoice saved successfully!\nSaved to: {invoice_file}")


    def generate_and_close_popup(self, record_data, customer_data, stock_item, popup):
        # Generate the PDF invoice
        invoice_file = self.create_invoice(record_data, customer_data, stock_item)
        popup.destroy()  # Close the popup window

        # Show success message and ask if the user wants to print
        if messagebox.askyesno("Invoice Generated", f"Invoice saved at: {invoice_file}\nDo you want to print the invoice?"):
            self.print_invoice(invoice_file)

        messagebox.showinfo("Success", f"Invoice generated successfully!\nSaved to: {invoice_file}")


    def create_original_tree(self):
        columns = ("Ref Number", "Date", "Description", "Item Number", "QTY", "Sale Price", "BAC", 
                  "Customer ID", "Customer Name", "Phone", "Email")
        self.original_tree = ttk.Treeview(
            self.original_frame,
            columns=columns,
            show="headings",
            style="OriginalTree.Treeview"
        )

        for col in columns:
            self.original_tree.heading(col, text=col)
            width = 150 if col in ("Description", "Item Number", "Customer Name","Email") else 100
            self.original_tree.column(col, width=width, anchor=tk.CENTER)

        self.original_tree.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        scrollbar = ttk.Scrollbar(self.original_frame, orient=tk.VERTICAL, command=self.original_tree.yview)
        scrollbar.grid(row=2, column=2, sticky=(tk.N, tk.S))
        self.original_tree.configure(yscrollcommand=scrollbar.set)
        
        self.original_tree.bind('<<TreeviewSelect>>', self.on_original_tree_select)

    def create_record(self):
        record_data = {
            name.replace(":", ""): var.get()
            for name, var in self.field_vars
        }
        
        if not record_data["Ref Number"]:
            messagebox.showerror("Error", "Ref Number is required!")
            return
            
        try:
            qty_to_deduct = int(record_data["QTY"])
            stock_item = self.stock_collection.find_one({"Part Number": record_data["Ref Number"]})
            
            if stock_item:
                current_qty = int(stock_item.get("Quantity", 0))
                
                if current_qty >= qty_to_deduct:
                    new_qty = current_qty - qty_to_deduct
                    self.stock_collection.update_one(
                        {"Part Number": record_data["Ref Number"]},
                        {"$set": {"Quantity": new_qty}}
                    )
                    self.collection.insert_one(record_data)
                    
                    self.record_cash_history(
                        stock_item["Name"],
                        qty_to_deduct,
                        record_data["Sale Price"],
                        "sale"
                    )
                    
                    messagebox.showinfo("Success", 
                        f"Record created successfully!\nStock updated: {current_qty} - {qty_to_deduct} = {new_qty}")
                    self.clear_fields()
                    self.find_record()
                else:
                    messagebox.showerror("Error", 
                        f"Insufficient stock! Available: {current_qty}, Requested: {qty_to_deduct}")
            else:
                messagebox.showwarning("Warning", "No matching item found in stock!")
                
        except ValueError:
            messagebox.showerror("Error", "QTY must be a valid number!")
        except Exception as e:
            messagebox.showerror("Error", f"Error creating record: {str(e)}")
    def find_customer(self):
        try:
            customer_id = self.customer_vars[0][1].get()  
            if not customer_id:
                messagebox.showerror("Error", "Please enter a Customer ID.")
                return
            customer = self.customers_collection.find_one({"Customer ID": customer_id})        
            if customer:
                for i, (label, var) in enumerate(self.customer_vars):
                    var.set(customer.get(label.replace(":", ""), ""))
            else:
                messagebox.showinfo("Info", "No customer found with the provided Customer ID.")
        except Exception as e:
            messagebox.showerror("Error", f"Error finding customer: {str(e)}")

    def clear_fields(self):
        for _, var in self.field_vars:
            var.set("")
        for _, var in self.customer_vars:
            var.set("")
    def on_original_tree_select(self, event):
        selected_items = self.original_tree.selection()
        if not selected_items:
            return
        item = selected_items[0]
        values = self.original_tree.item(item)["values"]
        for (_, var), value in zip(self.field_vars, values[:7]):  
            var.set(value)
        if len(values) > 7:  
            customer_id = values[7] 
            try:
                customer = self.customers_collection.find_one({"Customer ID": customer_id})
                if customer:
                    for (name, var) in self.customer_vars:
                        field_name = name.replace(":", "")
                        var.set(customer.get(field_name, ""))
            except Exception as e:
                messagebox.showerror("Error", f"Error loading customer data: {str(e)}")
    def create_stock_tree(self):
        columns = ("Part Number", "Name", "Brand", "Purchase Price", "Date of Purchase", 
                  "Sale Price", "Sale Date", "Location", "Quantity")  # Added Quantity
        self.stock_tree = ttk.Treeview(
            self.stock_frame,
            columns=columns,
            show="headings",
            style="StockTree.Treeview"
        )
        for col in columns:
            self.stock_tree.heading(col, text=col)
            self.stock_tree.column(col, width=150, anchor=tk.CENTER)
        self.stock_tree.grid(row=6, column=0, columnspan=6, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)        
        scrollbar = ttk.Scrollbar(self.stock_frame, orient=tk.VERTICAL, command=self.stock_tree.yview)
        scrollbar.grid(row=6, column=6, sticky=(tk.N, tk.S))
        self.stock_tree.configure(yscrollcommand=scrollbar.set)        
        self.stock_tree.bind('<<TreeviewSelect>>', self.on_stock_tree_select)
    def create_stock(self):
        stock_data = {
            name.replace(":", ""): var.get()
            for name, var in self.stock_field_vars
        }        
        if not stock_data["Part Number"]:
            messagebox.showerror("Error", "Part Number is required!")
            return
        try:
            result = self.stock_collection.insert_one(stock_data)
            if result.inserted_id: 
                self.record_cash_history(
                    stock_data["Name"],
                    stock_data.get("Quantity", 0),
                    stock_data.get("Purchase Price", "0"),
                    "purchase"
                )            
            messagebox.showinfo("Success", "New stock item created successfully!")
            self.clear_stock_fields()
            self.find_stock()
        except Exception as e:
            messagebox.showerror("Error", f"Error creating stock item: {str(e)}")
    def create_record(self):
        transaction_data = {
            name.replace(":", ""): var.get()
            for name, var in self.field_vars
        }
        customer_data = {
            name.replace(":", ""): var.get()
            for name, var in self.customer_vars
        }
        if not transaction_data["Ref Number"]:
            messagebox.showerror("Error", "Ref Number is required!")
            return 

        try:
            customer_id = customer_data["Customer ID"]
            if not customer_id:  
                customer_id = str(ObjectId())
                customer_data["Customer ID"] = customer_id
            
            self.customers_collection.update_one(
                {"Customer ID": customer_id},
                {"$set": customer_data},
                upsert=True  
            )
        
            transaction_data.update({
                "Customer ID": customer_id,
                "Customer Name": customer_data["Name"],
                "Phone": customer_data["Phone"],
                "Email": customer_data["Email"]
            })
        
            qty_to_deduct = int(transaction_data["QTY"])
            stock_item = self.stock_collection.find_one({"Part Number": transaction_data["Ref Number"]})
        
            if not stock_item:
                messagebox.showwarning("Warning", "No matching item found in stock!")
                return  
            
            current_qty = int(stock_item.get("Quantity", 0))   
            if current_qty >= qty_to_deduct:
                new_qty = current_qty - qty_to_deduct
                self.stock_collection.update_one(
                    {"Part Number": transaction_data["Ref Number"]},
                    {"$set": {"Quantity": new_qty}}
                )
            
                self.collection.insert_one(transaction_data)
                self.record_cash_history(
                    stock_item["Name"],
                    qty_to_deduct,
                    transaction_data["Sale Price"],
                    "sale"
                )
                invoice_file = self.create_invoice(transaction_data, customer_data, stock_item)
                if messagebox.askyesno("Print Invoice", "Invoice generated successfully. Would you like to print it?"):
                    self.print_invoice(invoice_file)
            
                messagebox.showinfo("Success", 
                    f"Record created successfully!\nStock updated: {current_qty} - {qty_to_deduct} = {new_qty}\nCustomer data saved.")
                self.clear_fields()
                self.find_record()
            else:
                messagebox.showerror("Error", 
                    f"Insufficient stock! Available: {current_qty}, Requested: {qty_to_deduct}")    
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")
            return
    
    def print_invoice(self, filename):
        try:
            if os.name == 'nt':  # For Windows
                os.startfile(filename, "print")
            else:  # For Unix/Linux/MacOS
                os.system(f"lpr {filename}")
            messagebox.showinfo("Success", "Invoice sent to printer!")
        except Exception as e:
            messagebox.showerror("Error", f"Error printing invoice: {str(e)}")
    def clear_fields(self):
        for _, var in self.field_vars:
            var.set("")
    def clear_stock_fields(self):
        for _, var in self.stock_field_vars:
            var.set("")
    def find_record(self):
        self.clear_tree(self.original_tree)
        ref_number = self.field_vars[0][1].get()
        if ref_number:
            query = {"Ref Number": ref_number}
        else:
            query = {
                key.replace(":", ""): {"$regex": f".*{value}.*", "$options": "i"}
                for key, value in [(name, var.get()) for name, var in self.field_vars]
                if value
            }
        self.add_records_to_tree(self.original_tree, self.collection, query)
    def find_stock(self):
        self.clear_tree(self.stock_tree)
        query = {
            key.replace(":", ""): {"$regex": f".*{value}.*", "$options": "i"}
            for key, value in [(name, var.get()) for name, var in self.stock_field_vars]
            if value
        }
        self.add_records_to_tree(self.stock_tree, self.stock_collection, query)
    def create_stock(self):
        stock_data = {
            name.replace(":", ""): var.get()
            for name, var in self.stock_field_vars
        }        
        if not stock_data["Part Number"]:
            messagebox.showerror("Error", "Part Number is required!")
            return

        try:
            self.stock_collection.insert_one(stock_data)
            messagebox.showinfo("Success", "New stock item created successfully!")
            self.clear_stock_fields()
            self.find_stock()
        except Exception as e:
            messagebox.showerror("Error", f"Error creating stock item: {str(e)}")
    def update_record(self):
        ref_number = self.field_vars[0][1].get()
        if not ref_number:
            messagebox.showerror("Error", "Ref Number is required for updating!")
            return
        update_data = {
            name.replace(":", ""): var.get()
            for name, var in self.field_vars
        }
        try:
            result = self.collection.update_one(
                {"Ref Number": ref_number},
                {"$set": update_data}
            )
            if result.modified_count:
                messagebox.showinfo("Success", "Record updated successfully!")
                self.clear_fields()
                self.find_record()
            else:
                messagebox.showwarning("Warning", "No matching record found to update!")
        except Exception as e:
            messagebox.showerror("Error", f"Error updating record: {str(e)}")
    def update_stock(self):
        part_number = self.stock_field_vars[0][1].get()
        if not part_number:
            messagebox.showerror("Error", "Part Number is required for updating!")
            return
        update_data = {
            name.replace(":", ""): var.get()
            for name, var in self.stock_field_vars
        }
        try:
            result = self.stock_collection.update_one(
                {"Part Number": part_number},
                {"$set": update_data}
                )
            if result.modified_count:
                messagebox.showinfo("Success", "Stock item updated successfully!")
                self.clear_stock_fields()
                self.find_stock()
            else:
                messagebox.showwarning("Warning", "No matching stock item found to update!")
        except Exception as e:
            messagebox.showerror("Error", f"Error updating stock item: {str(e)}")
    def delete_record(self):
        ref_number = self.field_vars[0][1].get()
        if not ref_number:
            messagebox.showerror("Error", "Ref Number is required for deletion!")
            return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this record?"):
            try:
                result = self.collection.delete_one({"Ref Number": ref_number})
                if result.deleted_count:
                    messagebox.showinfo("Success", "Record deleted successfully!")
                    self.clear_fields()
                    self.find_record()
                else:
                    messagebox.showwarning("Warning", "No matching record found to delete!")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting record: {str(e)}")
    def delete_stock(self):
        part_number = self.stock_field_vars[0][1].get()
        if not part_number:
            messagebox.showerror("Error", "Part Number is required for deletion!")
            return
        if messagebox.askyesno("Confirm Delete", "Are you sure you want to delete this stock item?"):
            try:
                result = self.stock_collection.delete_one({"Part Number": part_number})
                if result.deleted_count:
                    messagebox.showinfo("Success", "Stock item deleted successfully!")
                    self.clear_stock_fields()
                    self.find_stock()
                else:
                    messagebox.showwarning("Warning", "No matching stock item found to delete!")
            except Exception as e:
                messagebox.showerror("Error", f"Error deleting stock item: {str(e)}")
    def mark_as_sold(self):
        ref_number = self.field_vars[0][1].get()
        if not ref_number:
            messagebox.showerror("Error", "Ref Number is required!")
            return
        try:
            result = self.collection.update_one(
                {"Ref Number": ref_number},
                {"$set": {"Sold": True}}
            )
            if result.modified_count:
                messagebox.showinfo("Success", "Record marked as sold!")
                self.clear_fields()
                self.find_record()
            else:
                messagebox.showwarning("Warning", "No matching record found!")
        except Exception as e:
            messagebox.showerror("Error", f"Error marking record as sold: {str(e)}")
    def calculate_total(self):
        try:
            total = 0
            cursor = self.stock_collection.find({}, {"Purchase Price": 1})
            for doc in cursor:
                price = doc.get("Purchase Price", "0")
                price = float(price.replace("$", "").replace(",", ""))
                total += price
            messagebox.showinfo("Total", f"Total Purchase Price: ${total:,.2f}")
        except Exception as e:
            messagebox.showerror("Error", f"Error calculating total: {str(e)}")
    def clear_tree(self, tree):
        for item in tree.get_children():
            tree.delete(item)
    def add_records_to_tree(self, tree, collection, query):
        try:
            records = collection.find(query)
            for record in records:
                if "_id" in record:
                    del record["_id"]
                tree.insert("", tk.END, values=list(record.values()))
        except Exception as e:
            messagebox.showerror("Error", f"Error retrieving records: {str(e)}")
    def on_original_tree_select(self, event):
        selected_items = self.original_tree.selection()
        if not selected_items:
            return
        
        # Get the selected item values
        item = selected_items[0]
        values = self.original_tree.item(item)["values"]

        # Populate Transaction Details
        for (_, var), value in zip(self.field_vars, values[:7]):  # Transaction fields are the first 7 columns
            var.set(value)
        
        # Fetch Customer Details using Customer ID
        if len(values) > 7:  # Check if Customer ID is available
            customer_id = values[7]  # Assuming Customer ID is at index 7
            try:
                customer = self.customers_collection.find_one({"Customer ID": customer_id})
                if customer:
                    # Populate Customer Details
                    for (label, var) in self.customer_vars:
                        field_name = label.replace(":", "")
                        var.set(customer.get(field_name, ""))
                else:
                    # Clear the Customer Details if no customer found
                    for _, var in self.customer_vars:
                        var.set("")
            except Exception as e:
                messagebox.showerror("Error", f"Error loading customer data: {str(e)}")

    def on_stock_tree_select(self, event):
        selected_items = self.stock_tree.selection()
        if not selected_items:
            return        
        item = selected_items[0]
        values = self.stock_tree.item(item)["values"]        
        for (_, var), value in zip(self.stock_field_vars, values):
            var.set(value)
    def apply_custom_styles(self):
        style = ttk.Style()
        style.theme_use("default")
        style.configure("Main.TFrame", background="#f0f0f0")
        style.configure("ButtonFrame.TFrame", background="#f0f0f0")
        style.configure("OriginalData.TFrame", background="#f0f0f0")
        style.configure("StockManagement.TFrame", background="#f0f0f0")
        style.configure("ToggleButton.TButton",
                       font=("Roboto", 12, "bold"),
                       padding=5)
        style.configure("ActiveToggleButton.TButton",
                       background="#c0c0c0",
                       font=("Roboto", 12, "bold"),
                       padding=5)
        style.configure("ActionButton.TButton",
                       font=("Roboto", 12),
                       padding=5)
        style.configure("FieldLabel.TLabel",
                       font=("Roboto", 12),
                       background="#f0f0f0")
        style.configure("FieldEntry.TEntry",
                       font=("Roboto", 12))
        style.configure("Treeview",
                       font=("Roboto", 12),
                       rowheight=25)
        style.configure("Treeview.Heading",
                       font=("Roboto", 12, "bold"))
        style.configure("OriginalTree.Treeview",
                       background="#ffffff",
                       fieldbackground="#ffffff")
        style.configure("StockTree.Treeview",
                       background="#ffffff",
                       fieldbackground="#ffffff")
        style.configure("TScrollbar",
                       background="#f0f0f0",
                       bordercolor="#f0f0f0",
                       arrowcolor="#333333")
class CustomerHistoryView:
    def __init__(self, parent, customers_collection):
        self.parent = parent
        self.customers_collection = customers_collection
        self.frame = ttk.Frame(parent, padding="10", style="CustomerHistory.TFrame")
        self.create_search_section()
        self.create_tree()
        self.create_summary_section()
    def create_search_section(self):
        search_frame = ttk.LabelFrame(self.frame, text="Search Customers", padding="10")
        search_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        ttk.Label(search_frame, text="Customer ID:").grid(row=0, column=0, padx=5)
        self.customer_id_search = ttk.Entry(search_frame, width=20)
        self.customer_id_search.grid(row=0, column=1, padx=5)
        ttk.Label(search_frame, text="Name:").grid(row=0, column=2, padx=5)
        self.name_search = ttk.Entry(search_frame, width=20)
        self.name_search.grid(row=0, column=3, padx=5)
        ttk.Label(search_frame, text="Phone:").grid(row=1, column=0, padx=5, pady=10)
        self.phone_search = ttk.Entry(search_frame, width=20)
        self.phone_search.grid(row=1, column=1, padx=5, pady=10)
        ttk.Label(search_frame, text="Email:").grid(row=1, column=2, padx=5, pady=10)
        self.email_search = ttk.Entry(search_frame, width=20)
        self.email_search.grid(row=1, column=3, padx=5, pady=10)
        button_frame = ttk.Frame(search_frame)
        button_frame.grid(row=2, column=0, columnspan=4, pady=10)
        ttk.Button(button_frame, text="Search", 
                  command=self.search_records).grid(row=0, column=0, padx=5)
        ttk.Button(button_frame, text="Clear", 
                  command=self.clear_filters).grid(row=0, column=1, padx=5)
        ttk.Button(button_frame, text="Show All", 
                  command=self.show_all_records).grid(row=0, column=2, padx=5)
    def create_tree(self):
        columns = ("Customer ID", "Name", "Phone", "Email", "Address", "City", "State", "ZIP", "Ref Number","Date","Item Number","Sale Price","BAC")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            width = 150 if col in ("Name", "Email", "Address") else 100
            self.tree.column(col, width=width)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        scrollbar.grid(row=1, column=1, sticky="ns")
        self.tree.bind('<Double-1>', self.show_customer_details)
    def create_summary_section(self):
        summary_frame = ttk.LabelFrame(self.frame, text="Summary", padding="10")
        summary_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        self.total_customers_var = tk.StringVar(value="Total Customers: 0")
        ttk.Label(summary_frame, textvariable=self.total_customers_var).grid(row=0, column=0, padx=10)
    def clear_filters(self):
        self.customer_id_search.delete(0, tk.END)
        self.name_search.delete(0, tk.END)
        self.phone_search.delete(0, tk.END)
        self.email_search.delete(0, tk.END)
        self.search_records()
    def search_records(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = {}
        if self.customer_id_search.get().strip():
            query['Customer ID'] = {'$regex': f'.*{self.customer_id_search.get().strip()}.*', '$options': 'i'}        
        if self.name_search.get().strip():
            query['Name'] = {'$regex': f'.*{self.name_search.get().strip()}.*', '$options': 'i'}            
        if self.phone_search.get().strip():
            query['Phone'] = {'$regex': f'.*{self.phone_search.get().strip()}.*', '$options': 'i'}            
        if self.email_search.get().strip():
            query['Email'] = {'$regex': f'.*{self.email_search.get().strip()}.*', '$options': 'i'}
        try:
            customers = self.customers_collection.find(query, {
                "Customer ID": 1,
                "Name": 1,
                "Phone": 1,
                "Email": 1,
                "Address": 1,
                "City": 1,
                "State": 1,
                "ZIP": 1,
                "Ref Number": 1,
                "Date": 1,
                "Item Number": 1,
                "Sale Price": 1,
                "BAC": 1
            })
            customer_count = 0
            for customer in customers:
                self.tree.insert('', 'end', values=(
                    customer.get('Customer ID', ''),
                    customer.get('Name', ''),
                    customer.get('Phone', ''),
                    customer.get('Email', ''),
                    customer.get('Address', ''),
                    customer.get('City', ''),
                    customer.get('State', ''),
                    customer.get('ZIP', ''),
                    customer.get('Ref Number', ''),
                    customer.get('Date', ''),
                    customer.get('Item Number', ''),
                    customer.get('Sale Price', ''),
                    customer.get('BAC', ''),
                ))
                customer_count += 1
            self.total_customers_var.set(f"Total Customers: {customer_count}")
        except Exception as e:
            messagebox.showerror("Error", f"Error searching records: {str(e)}")
    def show_all_records(self):
        self.clear_filters()
        self.search_records()
    def show_customer_details(self, event):
        selected_item = self.tree.selection()[0]
        customer_id = self.tree.item(selected_item)['values'][0]        
        try:
            customer = self.customers_collection.find_one({'Customer ID': customer_id})
            if customer:
                details_window = tk.Toplevel(self.parent)
                details_window.title(f"Customer Details - {customer.get('Name', '')}")
                details_window.geometry("400x300")
                details_frame = ttk.Frame(details_window, padding="20")
                details_frame.grid(row=0, column=0, sticky='nsew')
                fields = [
                    ("Customer ID:", customer.get('Customer ID', '')),
                    ("Name:", customer.get('Name', '')),
                    ("Phone:", customer.get('Phone', '')),
                    ("Email:", customer.get('Email', '')),
                    ("Address:", customer.get('Address', '')),
                    ("City:", customer.get('City', '')),
                    ("State:", customer.get('State', '')),
                    ("ZIP:", customer.get('ZIP', ''))
                ]
                for i, (label, value) in enumerate(fields):
                    ttk.Label(details_frame, text=label, font=('Helvetica', 10, 'bold')).grid(row=i, column=0, sticky='w', pady=5)
                    ttk.Label(details_frame, text=value).grid(row=i, column=1, sticky='w', pady=5, padx=10)                
                ttk.Button(details_frame, text="Close", 
                          command=details_window.destroy).grid(row=len(fields), column=0, columnspan=2, pady=20)                
        except Exception as e:
            messagebox.showerror("Error", f"Error displaying customer details: {str(e)}")
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
class CashHistoryView:
    def __init__(self, parent, cash_history_collection):
        self.parent = parent
        self.cash_history = cash_history_collection
        self.frame = ttk.Frame(parent, padding="10", style="CashHistory.TFrame")
        self.create_filter_section()
        self.create_tree()
        self.create_summary_section()
    def create_filter_section(self):
        filter_frame = ttk.LabelFrame(self.frame, text="Filters", padding="10")
        filter_frame.grid(row=0, column=0, sticky='ew', padx=5, pady=5)
        ttk.Label(filter_frame, text="Date Range:").grid(row=0, column=0, padx=5)
        self.start_date = DateEntry(filter_frame, width=12, background='darkblue',
                                  foreground='white', borderwidth=2)
        self.start_date.grid(row=0, column=1, padx=5)
        
        ttk.Label(filter_frame, text="to").grid(row=0, column=2, padx=5)
        self.end_date = DateEntry(filter_frame, width=12, background='darkblue',
                                foreground='white', borderwidth=2)
        self.end_date.grid(row=0, column=3, padx=5)
        ttk.Button(filter_frame, text="Today", 
                  command=lambda: self.set_date_range('today')).grid(row=0, column=4, padx=5)
        ttk.Button(filter_frame, text="This Week", 
                  command=lambda: self.set_date_range('week')).grid(row=0, column=5, padx=5)
        ttk.Button(filter_frame, text="This Month", 
                  command=lambda: self.set_date_range('month')).grid(row=0, column=6, padx=5)
        ttk.Label(filter_frame, text="Item Name/Number:").grid(row=1, column=0, padx=5, pady=10)
        self.item_search = ttk.Entry(filter_frame, width=20)
        self.item_search.grid(row=1, column=1, columnspan=2, padx=5, pady=10)
        ttk.Label(filter_frame, text="Transaction Type:").grid(row=1, column=3, padx=5)
        self.transaction_type = ttk.Combobox(filter_frame, values=['All', 'Purchase', 'Sale'])
        self.transaction_type.set('All')
        self.transaction_type.grid(row=1, column=4, padx=5)
        ttk.Button(filter_frame, text="Search", 
                  command=self.search_records).grid(row=1, column=5, padx=5)
        ttk.Button(filter_frame, text="Clear Filters", 
                  command=self.clear_filters).grid(row=1, column=6, padx=5)
    def create_tree(self):
        columns = ("Date", "Item Name/Number", "Transaction Type", "Quantity", "Price", "Total")
        self.tree = ttk.Treeview(self.frame, columns=columns, show="headings", height=15)
        for col in columns:
            self.tree.heading(col, text=col)
            width = 250 if col in ("Date", "Item Name/Number") else 200
            self.tree.column(col, width=width)
        scrollbar = ttk.Scrollbar(self.frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        self.tree.grid(row=1, column=0, sticky="nsew", padx=5, pady=5)
        scrollbar.grid(row=1, column=1, sticky="ns")
    def create_summary_section(self):
        summary_frame = ttk.LabelFrame(self.frame, text="Summary", padding="10")
        summary_frame.grid(row=2, column=0, sticky='ew', padx=5, pady=5)
        self.total_sales_var = tk.StringVar(value="Total Sales: $0.00")
        self.total_purchases_var = tk.StringVar(value="Total Purchases: $0.00")
        self.net_cash_flow_var = tk.StringVar(value="Net Cash Flow: $0.00")
        self.total_transactions_var = tk.StringVar(value="Total Transactions: 0")
        ttk.Label(summary_frame, textvariable=self.total_sales_var).grid(row=0, column=0, padx=10)
        ttk.Label(summary_frame, textvariable=self.total_purchases_var).grid(row=0, column=1, padx=10)
        ttk.Label(summary_frame, textvariable=self.net_cash_flow_var).grid(row=0, column=2, padx=10)
        ttk.Label(summary_frame, textvariable=self.total_transactions_var).grid(row=0, column=3, padx=10)
    def set_date_range(self, range_type):
        today = datetime.now()
        if range_type == 'today':
            self.start_date.set_date(today)
            self.end_date.set_date(today)
        elif range_type == 'week':
            start = today - timedelta(days=today.weekday())
            self.start_date.set_date(start)
            self.end_date.set_date(today)
        elif range_type == 'month':
            start = today.replace(day=1)
            self.start_date.set_date(start)
            self.end_date.set_date(today)
    def clear_filters(self):
        self.start_date.set_date(datetime.now())
        self.end_date.set_date(datetime.now())
        self.item_search.delete(0, tk.END)
        self.transaction_type.set('All')
        self.search_records()
    def search_records(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        query = {}
        start_date = datetime.combine(self.start_date.get_date(), datetime.min.time())
        end_date = datetime.combine(self.end_date.get_date(), datetime.max.time())
        query['Date'] = {'$gte': start_date, '$lte': end_date}
        if self.item_search.get().strip():
            search_term = self.item_search.get().strip()
            query['Name'] = {'$regex': f'.*{search_term}.*', '$options': 'i'}
        if self.transaction_type.get() != 'All':
            query['Type'] = self.transaction_type.get().lower()
        try:
            records = self.cash_history.find(query)            
            total_sales = 0
            total_purchases = 0
            transaction_count = 0
            for record in records:
                quantity = float(record.get('QTY', 0))
                price = float(record.get('Price', 0))
                total = quantity * price
                if record['Type'].lower() == 'sale':
                    total_sales += total
                else:
                    total_purchases += total
                transaction_count += 1
                date_str = record['Date'].strftime('%Y-%m-%d %H:%M')
                self.tree.insert('', 'end', values=(
                    date_str,
                    record['Name'],
                    record['Type'].capitalize(),
                    quantity,
                    f"${price:,.2f}",
                    f"${total:,.2f}"
                ))
            self.update_summary(total_sales, total_purchases, transaction_count)
        except Exception as e:
            messagebox.showerror("Error", f"Error searching records: {str(e)}")
    def update_summary(self, total_sales, total_purchases, transaction_count):
        self.total_sales_var.set(f"Total Sales: ${total_sales:,.2f}")
        self.total_purchases_var.set(f"Total Purchases: ${total_purchases:,.2f}")
        self.net_cash_flow_var.set(f"Net Cash Flow: ${(total_sales - total_purchases):,.2f}")
        self.total_transactions_var.set(f"Total Transactions: {transaction_count}")
    def grid(self, **kwargs):
        self.frame.grid(**kwargs)
if __name__ == "__main__":
    root = tk.Tk()
    app = MongoDBCRUDApp(root)
    root.mainloop()
    root.update_idletasks()  # For pending tasks
    root.update()            # For general refresh