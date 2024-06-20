import tkinter as tk
from tkinter import ttk, messagebox
from tkinter import simpledialog
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from datetime import datetime

# Create directories if not exist
os.makedirs('bills', exist_ok=True)
os.makedirs('Bill_Database', exist_ok=True)

# Sample data for items in the supermarket
items = {
    '001': {'name': 'Milk', 'price': 1.50},
    '002': {'name': 'Bread', 'price': 2.00},
    '003': {'name': 'Eggs', 'price': 0.20},
    '004': {'name': 'Apple', 'price': 0.30},
    '005': {'name': 'Banana', 'price': 0.25}
}

class SupermarketBillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Kingsley Chika CHUKWU Supermarket")
        self.cart = []
        self.agent_name = None

        # Initialize UI
        self.create_widgets()

    def create_widgets(self):
        self.header_label = tk.Label(self.root, text="Welcome to Kingsley Supermarket \n Where Quality Service Count", font=("Arial", 24))
        self.header_label.pack(pady=20)

        self.add_bill_button = tk.Button(self.root, text="Add Bill", command=self.add_bill)
        self.add_bill_button.pack(pady=10)

    def add_bill(self):
        self.agent_name = simpledialog.askstring("Agent Name", "Enter agent name:")
        if not self.agent_name:
            messagebox.showwarning("Input Error", "Agent name is required")
            return

        self.add_bill_button.config(state=tk.DISABLED)
        self.add_item_button = tk.Button(self.root, text="Add Item", command=self.add_item)
        self.add_item_button.pack(pady=10)

        self.bill_tree = ttk.Treeview(self.root, columns=('Item ID', 'Item Name', 'Quantity', 'Amount'), show='headings')
        self.bill_tree.heading('Item ID', text='Item ID')
        self.bill_tree.heading('Item Name', text='Item Name')
        self.bill_tree.heading('Quantity', text='Quantity')
        self.bill_tree.heading('Amount', text='Amount')
        self.bill_tree.pack(pady=20)

        self.discount_label = tk.Label(self.root, text="Discount: 3%")
        self.discount_label.pack(pady=5)
        self.total_label = tk.Label(self.root, text="Total: $0.00")
        self.total_label.pack(pady=5)

        self.print_bill_button = tk.Button(self.root, text="Print Bill", command=self.print_bill)
        self.print_bill_button.pack(pady=10)

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
        self.cart.append({'item_id': item_id, 'name': item['name'], 'quantity': quantity, 'amount': amount})

        self.bill_tree.insert('', 'end', values=(item_id, item['name'], quantity, amount))
        self.update_total()

    def update_total(self):
        total = sum(item['amount'] for item in self.cart)
        discount = total * 0.03
        total_after_discount = total - discount
        self.total_label.config(text=f"Total: ${total_after_discount:.2f}")

    def print_bill(self):
        if not self.cart:
            messagebox.showwarning("Error", "No items in the cart")
            return

        now = datetime.now()
        date_time_str = now.strftime("%Y%m%d_%H%M%S")
        customer_id = f"KCC{len(os.listdir('bills')) + 1:03d}_{date_time_str}"
        filename = f'bills/{customer_id}.pdf'

        c = canvas.Canvas(filename, pagesize=letter)
        c.drawString(30, 750, f"Kingsley Supermarket")
        c.drawString(30, 735, f"Date: {now.strftime('%Y-%m-%d %H:%M:%S')}")
        c.drawString(400, 750, f"Agent: {self.agent_name}")
        c.drawString(30, 720, "-----------------------------------------------")

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

        c.drawString(30, y, "-----------------------------------------------")
        y -= 15
        c.drawString(300, y, "Discount:")
        c.drawString(400, y, f"$-{discount:.2f}")
        y -= 15
        c.drawString(300, y, "Total:")
        c.drawString(400, y, f"${total_after_discount:.2f}")
        c.save()

        messagebox.showinfo("Success", f"Bill generated and saved as {filename}")

        self.save_to_excel(now, customer_id, total_after_discount)
        self.reset_bill()

    def save_to_excel(self, now, customer_id, total_after_discount):
        date_str = now.strftime("%Y%m%d")
        filename = f'Bill_Database/Bill_Database_{date_str}.xlsx'
        if os.path.exists(filename):
            df = pd.read_excel(filename)
        else:
            df = pd.DataFrame(columns=['Customer ID', 'Date Time', 'Agent', 'Item ID', 'Item Name', 'Quantity', 'Amount', 'Total After Discount'])

        for item in self.cart:
            df = df.append({
                'Customer ID': customer_id,
                'Date Time': now.strftime('%Y-%m-%d %H:%M:%S'),
                'Agent': self.agent_name,
                'Item ID': item['item_id'],
                'Item Name': item['name'],
                'Quantity': item['quantity'],
                'Amount': item['amount'],
                'Total After Discount': total_after_discount
            }, ignore_index=True)

        df.to_excel(filename, index=False)

    def reset_bill(self):
        self.cart.clear()
        self.agent_name = None
        self.bill_tree.delete(*self.bill_tree.get_children())
        self.total_label.config(text="Total: $0.00")
        self.add_bill_button.config(state=tk.NORMAL)
        self.add_item_button.destroy()
        self.print_bill_button.destroy()
        self.discount_label.destroy()
        self.total_label.destroy()
        self.bill_tree.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = SupermarketBillingApp(root)
    root.mainloop()
