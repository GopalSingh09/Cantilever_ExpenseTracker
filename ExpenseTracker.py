import tkinter as tk
from tkinter import ttk
from tkinter  import messagebox
from tkcalendar import DateEntry
import sqlite3
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from datetime import datetime
from itertools import cycle
import sys
import ttkbootstrap as tb

#connecting the database
conn = sqlite3.connect('expenses.db')
cursor = conn.cursor()
cursor.execute('''
CREATE TABLE IF NOT EXISTS
expenses (id INTEGER PRIMARY KEY,
        product_name TEXT,
        price REAL,
        date TEXT,
        category TEXT
)
''')
conn.commit()
def add_expense():
    productName = productNameEntry.get()
    price = productPriceEntry.get()
    date = dateEntry.entry.get()
    category = categoryEntry.get()
    if productName and price and date:
        cursor.execute('INSERT INTO expenses (product_name, price, date, category) VALUES (?, ?, ?, ?)',(productName, price, date, category))
        conn.commit()
        displayAllData()
        messagebox.showinfo("Information","Data Successfully Inserted")
        productNameEntry.delete(0, tk.END)
        productPriceEntry.delete(0, tk.END)
    else:
        messagebox.showerror("Error","Error, Please ensure that you have filled all fields")

def deleteExpense():
    productName = productNameEntry.get()
    if productName:
        cursor.execute('DELETE FROM expenses WHERE product_name = ?', (productName,))
        conn.commit()
        if cursor.rowcount:
            messagebox.showinfo("Information", f"Product {productName} Successfully Delete")
            productNameEntry.delete(0,tk.END)
            productPriceEntry.delete(0,tk.END)
            displayAllData()
        else:
            messagebox.showerror("Error", "Product not found")
    else:
        messagebox.showerror("Error", "Please Enter the product name")

def clear_all():
    cursor.execute('DELETE FROM expenses')
    conn.commit()
    displayAllData()
    messagebox.showinfo("Information", "All the data is deleted")

def plotExpense():
    date = dateEntry.entry.get()
    if date:
        cursor.execute('SELECT category, SUM(price) FROM expenses WHERE date = ? GROUP BY category', (date,))
        data = cursor.fetchall()

        if data:
            categories = [d[0] for d in data]
            prices = [d[1] for d in data]
            total = sum(prices)
            percentage = [f"{category} ({price/total:.1%})" for category , price in zip(categories, prices)]
            fig, ax = plt.subplots(figsize = (4.9,2.5))
            wedges, texts= ax.pie(prices, startangle = 140, colors = plt.cm.tab20.colors)
            ax.legend(wedges, percentage, title = "Categories", loc = "center left", bbox_to_anchor = (1, 0.5), fontsize = 10)
            ax.set_title("Expenses by Category")
            plt.subplots_adjust(left = 0.1, right = 0.6)
            for widget in plot_frame.winfo_children():
                widget.destroy()
            canvas = FigureCanvasTkAgg(fig, master = plot_frame)
            canvas.draw()
            canvas.get_tk_widget().pack(fill = tk.BOTH, expand = True)
        else:
            messagebox.showinfo("Information", "No expense data for this date")
    else:
        messagebox.showerror("Error", "Please select a date")

def displayAllData():
    for widget in list_frame.winfo_children():
        widget.destroy()
    columns = ('Product Name', 'Price', 'Date', 'Category')
    tree = ttk.Treeview(list_frame, columns = columns, show= 'headings')
    cursor.execute('SELECT product_name, price, date, category FROM expenses')
    data = cursor.fetchall()
    if data:
        for col in columns:
            tree.heading(col, text=col)
            tree.column(col, width=150)
            tree.pack(fill=tk.BOTH, expand=True)

        for item in data:
            tree.insert('', tk.END, values=item)
    else:
        ttk.Label(list_frame, text= "No data available").grid(row = 0, column = 0, padx = 10, pady = 5)


def onClosing():
    conn.close()
    plt.close('all')
    global root
    try:
        if root:
            root.destroy()
    except tk.TclError:
        pass


class RoundButton(tk.Button):
    def __init__(self, master =None,text = None, command = None):
        super().__init__(master)
        self.config(
            relief='flat',
            bg = 'lightblue',
            activebackground='lightgreen',
            padx = 10,
            pady = 10,
            borderwidth=0,
            highlightthickness=0,
            foreground = "white"
        )
        self.bind("<Enter>", self.on_hover)
        self.bind("<Leave>", self.on_leave)
        self.config(
            text = text,
            command=command,
            width = 10,
            height = 2
        )
    def on_hover(self, event):
        self.config(bg = 'lightgreen')
    def on_leave(self, event):
        self.config(bg='lightblue')






root = tk.Tk()
root.title("Expense Tracker")
root.config(background="lightgrey")
root.minsize(1020, 620)
root.maxsize(1020, 620)
frame = ttk.Frame(root, padding="10")
frame.grid(row= 0, column = 0, sticky = (tk.W, tk.E, tk.N, tk.S))

style = ttk.Style()
style.configure("TEntry",
                foreground = "black",
                background = "white",
                fieldbackground = "lightgrey",
                borderwidth = 1,
                padding = 2,
                relief = "solid")
style.map("TEntry",
          background = [('active', 'white'), ('focus', 'lightblue')])

colors = ['#b3ecff', '#99e6ff', '#80dfff', '#66d9ff', '#4dd2ff','#33ccff','#1ac6ff','#00bfff','#00ace6','#00ace6','#00ace6','#00bfff','#1ac6ff','#4dd2ff', '#66d9ff', '#80dfff', '#99e6ff', '#b3ecff']
color_cycle =  cycle(colors)
red = ['#ffb3b3', '#ff9999', '#ff8080', '#ff6666', '#ff4d4d', '#ff3333','#ff1a1a','#ff0000','#e60000','#cc0000','#b30000','#b30000','#b30000','#cc0000','#e60000', '#ff0000', '#ff1a1a', '#ff3333', '#ff4d4d', '#ff6666','#ff8080','#ff9999','#ffb3b3'  ]
redColorCycle = cycle(red)
def updateColor():
    col = next(color_cycle)
    col1 = next(redColorCycle)
    label1.config(foreground = col)
    label2.config(foreground= col1)
    label3.config(foreground= col)
    label4.config(foreground= col1)

    root.after(100, updateColor)

label1 = ttk.Label(frame, text = "Product Name: ", font = ("Helvetica", 12, "bold"))
label1.grid(row = 0, column = 0, sticky=tk.W)
productNameEntry = ttk.Entry(frame, style = "TEntry", width = 25)
productNameEntry.grid(row = 0, column = 1, pady=5)

label2 = ttk.Label(frame, text = "Price: ", font = ("Helvetica", 12, "bold"))
label2.grid(row = 1, column = 0, sticky=tk.W)
productPriceEntry = ttk.Entry(frame, style = "TEntry", width = 25)
productPriceEntry.grid(row = 1, column = 1, pady = 5)

categories = ["Travel", "Food", "Assets", "Technology", "Studies", "Home-Appliance", "Cloths", "Shoes", "Others"]
label3 = ttk.Label(frame, text="Category: ", font = ("Helvetica", 12, "bold"))
label3.grid(row = 2, column = 0, sticky = tk.W)
categoryEntry = ttk.Combobox(frame,values=categories , width = 23)
categoryEntry.grid(row = 2, column = 1, pady = 5)
categoryEntry.set('Select Category')

label4 = ttk.Label(frame, text = "Date: ", font = ("Helvetica", 12, "bold"))
label4.grid(row=3,column = 0, sticky=tk.W)
dateEntry = tb.DateEntry(frame , bootstyle = "danger",width = 25)
dateEntry.grid(row = 3, column = 1, pady = 5)

btnframe = ttk.Frame(root, padding = 10)
Button1 = RoundButton(btnframe, text = "Insert Expense", command = add_expense).grid(row = 4, column = 0, padx = 10, pady = 10)
Button2 = RoundButton(btnframe, text="Delete Expense", command = deleteExpense).grid(row = 4, column = 2, padx = 10, pady = 10)
Button3 = RoundButton(btnframe, text="Plot Expense", command = plotExpense).grid(row = 4, column = 4, padx = 10, pady = 10)
Button4 = RoundButton(btnframe, text="Clear All Data", command = clear_all).grid(row = 4, column = 6, padx = 10, pady = 10)
btnframe.place(x = 0, y = 170)

plot_frame = ttk.Frame(root, padding="10")
plot_frame.grid(row = 0, column = 6, sticky=(tk.W, tk.E, tk.S, tk.N), padx = 170)

list_frame = ttk.Frame(root, padding=10)
list_frame.place(x = 40, y = 250, anchor = 'nw', width = 942, height = 350)
displayAllData()
root.protocol("WM_DELETE_WINDOW", onClosing)
updateColor()

sys.exit(root.mainloop())
