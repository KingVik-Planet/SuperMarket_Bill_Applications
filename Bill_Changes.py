import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from PIL import Image, ImageTk
import os
from datetime import datetime
import qrcode


# Create directories if not exist
os.makedirs('bills', exist_ok=True)
os.makedirs('Bill_Database', exist_ok=True)

#Data for items in the supermarket
items = {
    '001': {'name': 'Milk', 'price': 700.00},
    '002': {'name': 'Bread', 'price': 600.00},
    '003': {'name': 'Eggs', 'price': 200.00},
    '004': {'name': 'Apple', 'price': 500.00},
    '005': {'name': 'Banana', 'price': 100.00}
}

class SupermarketBillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kingsley Chika CHUKWU Supermarket")
        self.cart = []
        self.agent_name = None

        # Initialize UI
        self.create_widgets()
        self.update_time()

    def create_widgets(self):
        self.header_frame = tk.Frame(self.root)
        self.header_frame.pack(fill=tk.X, pady=0.001)

        # Load and display the logo image
        logo_path = "image/MWB.png"
        if os.path.exists(logo_path):
            self.logo_image = Image.open(logo_path)
            self.logo_image = self.logo_image.resize((100, 100))
            self.logo_photo = ImageTk.PhotoImage(self.logo_image)
            self.logo_label = tk.Label(self.header_frame, image=self.logo_photo)
            self.logo_label.pack(side=tk.LEFT, padx=10)
        else:
            self.logo_label = tk.Label(self.header_frame, text="Kingsley Chika CHUKWU \nSupermarket", font=("Arial", 24))
            self.logo_label.pack(side=tk.LEFT, padx=10)

        self.header_label = tk.Label(self.root, text="Welcome to KingVik Planet Supermarket \nWe are here to "
                                                     "serve you better", font=("Arial Rounded MT Bold", 28), borderwidth =10, background= "gray")
        self.header_label.pack(pady=10)

        self.date_time_label = tk.Label(self.header_frame, font=("Arial Rounded MT Bold", 15))
        self.date_time_label.pack(side=tk.RIGHT, padx=10)

        self.add_bill_button = tk.Button(self.root, text="Add Bill",borderwidth =2, background= "gray",font=("Arial Rounded MT Bold", 15), command=self.add_bill)
        self.add_bill_button.pack(pady=5)

    def update_time(self):
        now = datetime.now()
        date_str = now.strftime("Date: %d-%m-%Y")
        time_str = now.strftime("Time: %H:%M:%S")
        self.date_time_label.config(text=f"{date_str}\n{time_str}")
        self.root.after(1000, self.update_time)

    def add_bill(self):
        self.agent_name = simpledialog.askstring("Agent Name", "Enter agent name:")
        if not self.agent_name:
            messagebox.showwarning("Input Error", "Agent name is required \nKindly Enter your Name or ID")
            return

        self.add_bill_button.config(state=tk.DISABLED)
        self.add_item_button = tk.Button(self.root, text="Add Item" ,borderwidth =2, background= "gray",font=("Arial Rounded MT Bold", 10), command=self.add_item)
        self.add_item_button.pack(pady=10)

        self.bill_tree = ttk.Treeview(self.root, columns=('Item ID', 'Item Name', 'Quantity', 'Amount'), show='headings')
        self.bill_tree.heading('Item ID', text='Item ID')
        self.bill_tree.heading('Item Name', text='Item Name')
        self.bill_tree.heading('Quantity', text='Quantity')
        self.bill_tree.heading('Amount', text='Amount')
        self.bill_tree.pack(pady=2)

        self.edit_button = tk.Button(self.root, text="Edit Item", borderwidth =2, background= "cyan",font=("Arial Rounded MT Bold", 15), command=self.edit_item)
        self.edit_button.pack(side=tk.RIGHT, anchor='ne', pady=5)

        self.delete_button = tk.Button(self.root, text="Delete Item",borderwidth =2, background= "Red",font=("Arial Rounded MT Bold", 15), command=self.delete_item)
        self.delete_button.pack(side=tk.RIGHT, anchor='ne', pady=5)
        self.complete_button = tk.Button(self.root, text="Complete",borderwidth =2, background= "green",font=("Arial Rounded MT Bold", 15), command=self.complete)
        self.complete_button.pack(side=tk.LEFT, anchor='ne', pady=5)
        self.print_bill_button = tk.Button(self.root, text="Print Bill",borderwidth =2, background= "gray",font=("Arial Rounded MT Bold", 15), command=self.print_bill)
        self.print_bill_button.pack(side=tk.LEFT, anchor='ne', pady=5)

        self.discount_label = tk.Label(self.root, text="Discount: 3%",borderwidth =2, background= "gray",font=("Arial Rounded MT Bold", 15))
        self.discount_label.pack(pady=5)
        self.total_label = tk.Label(self.root, text="Total: $0.00", borderwidth =2, background= "gray",font=("Arial Rounded MT Bold", 15))
        self.total_label.pack(pady=5)



    def add_item(self):
        item_id = simpledialog.askstring("Item ID", "Enter item ID:")
        if item_id not in items:
            messagebox.showwarning("Input Error", "Item ID not found")
            return

        quantity = simpledialog.askinteger("Quantity", "Enter quantity:")
        if not quantity or quantity <= 0:
            messagebox.showwarning("Input Error", "Invalid quantity")
            return

        item = items[item_id]
        amount = item['price'] * quantity

        # To Check if item already exists in the cart
        for cart_item in self.cart:
            if cart_item['item_id'] == item_id:
                cart_item['quantity'] += quantity
                cart_item['amount'] += amount
                self.update_treeview()
                self.update_total()
                return

        self.cart.append({'item_id': item_id, 'name': item['name'], 'quantity': quantity, 'amount': amount})
        self.bill_tree.insert('', 'end', values=(item_id, item['name'], quantity, amount))
        self.update_total()

    def update_treeview(self):
        for i in self.bill_tree.get_children():
            self.bill_tree.delete(i)
        for item in self.cart:
            self.bill_tree.insert('', 'end', values=(item['item_id'], item['name'], item['quantity'], item['amount']))

    def update_total(self):
        total = sum(item['amount'] for item in self.cart)
        discount = total * 0.03
        total_after_discount = total - discount
        self.total_label.config(text=f"Total: ${total_after_discount:.2f}")

    def edit_item(self):
        selected_item = self.bill_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No item selected")
            return

        item_id = self.bill_tree.item(selected_item, 'values')[0]
        new_quantity = simpledialog.askinteger("Edit Quantity", "Enter new quantity:")
        if not new_quantity or new_quantity <= 0:
            messagebox.showwarning("Input Error", "Invalid quantity")
            return

        for cart_item in self.cart:
            if cart_item['item_id'] == item_id:
                cart_item['quantity'] = new_quantity
                cart_item['amount'] = new_quantity * items[item_id]['price']
                self.update_treeview()
                self.update_total()
                return

    def delete_item(self):
        selected_item = self.bill_tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "No item selected")
            return

        item_id = self.bill_tree.item(selected_item, 'values')[0]
        self.cart = [item for item in self.cart if item['item_id'] != item_id]
        self.update_treeview()
        self.update_total()

    def complete(self):
        self.cart.clear()
        self.update_treeview()
        self.update_total()
        self.add_bill_button.config(state=tk.NORMAL)
        self.add_item_button.destroy()
        self.edit_button.destroy()
        self.delete_button.destroy()
        self.complete_button.destroy()
        self.discount_label.destroy()
        self.total_label.destroy()
        self.bill_tree.destroy()
        self.print_bill_button.destroy()



    def print_bill(self):
        if not self.cart:
            messagebox.showwarning("There is an Error", "No items in the cart")
            return

        now = datetime.now()
        date_time_str = now.strftime("%Y%m%d_%H%M%S")
        customer_id = f"Kingsley{len(os.listdir('bills')) + 1:03d}_{date_time_str}"
        filename = f'bills/{customer_id}.pdf'

        c = canvas.Canvas(filename, pagesize=letter)
        c.drawString(30, 750, f"Kingsley Supermarket")
        c.drawString(30, 735, f"Date: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(400, 750, f"Agent: {self.agent_name}")
        c.drawString(30, 720, "-----------------Unverified------------------------------")

        c.drawString(30, 705, "Item ID")
        c.drawString(100, 705, "Item Name")
        c.drawString(300, 705, "Quantity")
        c.drawString(400, 705, "Amount")

        y = 690
        for item in self.cart:
            c.drawString(30, y, item['item_id'])
            c.drawString(100, y, item['name'])
            c.drawString(300, y, str(item['quantity']))
            c.drawString(400, y, f"${item['amount']:.2f}")
            y -= 15

        total = sum(item['amount'] for item in self.cart)
        discount = total * 0.03
        total_after_discount = total - discount

        c.drawString(30, y, "-------------------Verified----------------------------")
        y -= 15
        c.drawString(300, y, "Discount:")
        c.drawString(400, y, f"$-{discount:.2f}")
        y -= 15
        c.drawString(300, y, "Total:")
        c.drawString(400, y, f"${total_after_discount:.2f}")

        # Generate QR code
        qr_code_path = f'bills/{customer_id}.png'
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(customer_id)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')
        img.save(qr_code_path)

        # Draw QR code on the PDF
        if os.path.exists(qr_code_path):
            c.drawImage(qr_code_path, 30, y - 100, width=100, height=100)

        # Save the PDF
        c.save()

        # Delete the QR code image file
        if os.path.exists(qr_code_path):
            os.remove(qr_code_path)

        messagebox.showinfo("Success", f"Bill generated and saved as {filename}")

        self.save_to_excel(now, customer_id, total_after_discount)
        # self.reset_bill()

    def save_to_excel(self, now, customer_id, total_after_discount):
        # Check if the Excel file exists else create it
        excel_file = 'sales_data.xlsx'
        if not os.path.exists(excel_file):
            df = pd.DataFrame(columns=['Date', 'Customer ID', 'Total'])
        else:
            df = pd.read_excel(excel_file)

        # Append data to the DataFrame
        new_data = pd.DataFrame({
            'Date': [now.strftime('%Y-%m-%d %H:%M:%S')],
            'Customer ID': [customer_id],
            'Total': [total_after_discount]
        })

        # Concatenate the new data with the existing DataFrame
        df = pd.concat([df, new_data], ignore_index=True)

        # Save to Excel
        df.to_excel(excel_file, index=False)


if __name__ == "__main__":
    root = tk.Tk()
    app = SupermarketBillingApp(root)
    root.mainloop()
