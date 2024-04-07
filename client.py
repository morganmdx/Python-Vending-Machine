import threading
import tkinter as tk
import traceback
from tkinter import ttk
from tkinter import messagebox
import mysql.connector
from PIL import Image, ImageTk
import socket
import time
from datetime import datetime

server_address = ('172.20.10.4', 55000)
# Connect to the server
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.connect(server_address)

class BaseWindow(tk.Tk):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.force_maximize()

        # Create a frame for the logo with light gray background
        self.logo_frame = tk.Frame(self, bg="light grey")
        self.logo_frame.pack(fill="x")  # Fill the entire width

        # Load the image
        image_path = "images/food_express_logo.png"
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)

        # Create a label to display the image
        self.logo_label = tk.Label(self.logo_frame, image=photo, bg="light grey")
        self.logo_label.image = photo  # Keep a reference to prevent garbage collection
        self.logo_label.pack(padx=20, pady=20)  # due to this pack function we add the padding here

        self.drink_frame = tk.Frame(self)
        self.drink_frame.pack(pady=20)

        # Add text for disclaimer, credits etc
        paragraph_text = "Welcome to a vending machine or shop as a digital screen!\n\nThis program is for educational purposes only and any brands used are to demonstrate a fictional supermarket digital screen. No rights or ownership is assumed over any products added to the database - this program is not for commercial gain. For copyright enquiries contact the program developer Morgan, mm4274@live.mdx.ac.uk. "

        label = tk.Label(self, text=paragraph_text, wraplength=700)
        label.pack(fill="x",padx=20, pady=10)

        # Add a horizontal line (separator) between the logo and the drinks
        separator = ttk.Separator(self)
        separator.pack(fill="x", pady=10)

        # Add the button to toggle visibility of descriptions
        self.hide_descriptions_button = tk.Button(self, text="\u2699 TOGGLE SETTINGS", bg='#8A89C0', fg='white', highlightthickness=0,
                                       borderwidth=0, cursor="hand2", padx=10, pady=10, command=self.toggle_descriptions)
        self.hide_descriptions_button.pack(pady=2,padx=12)

        # Add a button to view transaction history
        self.transaction_button = tk.Button(self, text="\U0001F9FE View Transaction History", bg='#8A89C0', fg='white', highlightthickness=0,
                                       borderwidth=0, cursor="hand2", padx=10, pady=10, command=self.show_transaction_history)
        self.transaction_button.pack(pady=2,padx=12)

        # Variable to track whether descriptions are visible or not
        self.descriptions_visible = True

        # Add the "View Basket" button
        view_basket_button = tk.Button(self, text="\U0001F6D2 View Basket", bg='#8A89C0', fg='white', highlightthickness=0,
                                       borderwidth=0, cursor="hand2", padx=10, pady=10, command=self.show_basket)
        view_basket_button.pack(pady=2,padx=12)


    def show_transaction_history(self):
        # Create a new window for transaction history
        self.transaction_window = tk.Toplevel(self)
        self.transaction_window.title("Transaction History")
        self.force_maximize()


        # Create a frame for the logo with light gray background
        self.logo_frame = tk.Frame(self.transaction_window, bg="light grey")
        self.logo_frame.pack(fill="x")  # Fill the entire width

        # Load the image
        image_path = "images/food_express_logo.png"
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)

        # Create a label to display the image
        self.logo_label = tk.Label(self.logo_frame, image=photo, bg="light grey")
        self.logo_label.image = photo  # Keep a reference to prevent garbage collection
        self.logo_label.pack(padx=20, pady=20)  # due to this pack function we add the padding here

        # Create a blank label for line spacing
        tk.Label(self.transaction_window, text=" ", height=1, pady=10).pack()

        # Create a frame to hold the table
        table_frame = tk.Frame(self.transaction_window)
        table_frame.pack(expand=True)  # Allow table frame to expand

        # Create a blank label for line spacing
        tk.Label(self.transaction_window, text=" ", height=1, pady=10).pack()

        # Add headings for the table
        headings = ["Date", "Product(s)", "Quantity", "Total Price"]
        for col, heading in enumerate(headings):
            tk.Label(table_frame, text=heading, font=("Arial", 12, "bold")).grid(row=0, column=col, padx=5, pady=5)

        # Read transactions from the "transactions.txt" file and display them in a table
        with open("transactions.txt", "r") as f:
            transactions = f.readlines()
            for row, transaction in enumerate(transactions, start=1):
                transaction_data = transaction.strip().split(",")
                for col, data in enumerate(transaction_data):
                    tk.Label(table_frame, text=data, font=("Arial", 10)).grid(row=row, column=col, padx=5, pady=5)

    def force_maximize(self):
        self.state('zoomed')  # Maximize the main window

        # Loop through all child widgets
        for widget in self.winfo_children():
            # If a child widget is a frame, maximize its master window
            if isinstance(widget, tk.Frame):
                widget.master.state('zoomed')

        # Loop through all Toplevel windows
        for window in self.winfo_children():
            if isinstance(window, tk.Toplevel):
                window.state('zoomed')


class BasketWindow(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.title("Basket")
        self.maximized = False  # Track maximized state
        self.force_maximize()  # Maximize the basket window
        self.is_maximized = self.maximized  # Assign the value directly

        # Create a frame for the logo with light gray background
        self.logo_frame = tk.Frame(self, bg="light grey")
        self.logo_frame.pack(fill="x")  # Fill the entire width

        # Load the image
        image_path = "images/food_express_logo.png"
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)

        # Create a label to display the image
        self.logo_label = tk.Label(self.logo_frame, image=photo, bg="light grey")
        self.logo_label.image = photo  # Keep a reference to prevent garbage collection
        self.logo_label.pack(padx=20, pady=20)  # due to this pack function we add the padding here

        self.basket_items = master.basket_items

        # Create a frame to hold basket items
        self.basket_frame = tk.Frame(self)
        self.basket_frame.pack()

        self.total_price_label = tk.Label(self.basket_frame, text="")
        self.total_price_label.pack()

        close_button = tk.Button(self.basket_frame, text="Close", bg='#8A89C0', fg='white', highlightthickness=0,
                                 borderwidth=0, cursor="hand2", padx=10, pady=10, command=self.close_window)
        close_button.pack(pady=10)

        self.update_basket()

    def send_transaction(self, transaction_with_card_details):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                server_socket.connect(server_address)
                server_socket.sendall(f"process_transaction {transaction_with_card_details}".encode())
                response = server_socket.recv(1024).decode()
                print("Server response:", response)

                # Handle the response from the server
                if response == 'Transaction processed successfully.':
                    messagebox.showinfo("Successful!", "All good, payment successful")
                    self.checkout_window.destroy()
                    self.basket_items.clear()  # Clear basket after successful purchase
                    self.update_basket()
                else:
                    messagebox.showerror("Error", "Failed to process transaction.")
        except Exception as e:
            # Print the full traceback of the exception
            traceback.print_exc()
            messagebox.showerror("Error", "An error occurred while processing the transaction.")

    # Move the process_transaction method here
    def process_transaction(self, drink_id, quantity):
        try:
            transaction_data = f"{drink_id},{quantity}"
            self.master.server_socket.sendall(f"process_transaction {transaction_data}".encode())
            response = self.master.server_socket.recv(1024).decode()
            if response == 'Transaction processed successfully.':
                return True
            else:
                messagebox.showerror("Error", "hello"+response)  # Show the error message received from the server
                return False
        except Exception as e:
            print("Error:", e)
            messagebox.showerror("Error", "2222222An error occurred while processing the transaction.")
            return False

    def force_maximize(self):
        self.state('zoomed')  # Maximize the window
        self.maximized = True

    def update_basket(self):
        # Clear previous basket items
        for widget in self.basket_frame.winfo_children():
            widget.destroy()

        if not self.basket_items:
            # Create a blank label for line spacing
            tk.Label(self.basket_frame, text=" ", height=1, pady=10).pack()
            tk.Label(self.basket_frame, text="Basket is empty").pack()
            # Check if total_price_label is properly initialized
            if hasattr(self, 'total_price_label'):
                if isinstance(self.total_price_label, tk.Label) and self.total_price_label.winfo_exists():
                    self.total_price_label.config(text="")
        else:
            total_price = 0  # Initialize total price variable

            # Loop through basket items and display them in the basket
            for item in self.basket_items:
                drink_id, drink_name, image_path, price, quantity = item

                # Calculate the total price for each unique item
                item_total_price = price * quantity
                total_price += item_total_price

                basket_item_frame = tk.Frame(self.basket_frame, bd=1, relief=tk.SOLID)
                basket_item_frame.pack(fill="both", padx=20, pady=10)

                image = Image.open(image_path)
                image = image.resize((50, 50))
                photo = ImageTk.PhotoImage(image)
                label_image = tk.Label(basket_item_frame, image=photo, compound=tk.LEFT)
                label_image.photo = photo
                label_image.pack(side=tk.LEFT, padx=(10, 5))

                tk.Label(basket_item_frame, text=f"{drink_name} x {quantity}").pack(side=tk.LEFT, padx=(0, 10))
                tk.Label(basket_item_frame, text=f"Price: £{price}").pack(side=tk.LEFT)

                remove_button = tk.Button(basket_item_frame, text="Remove", bg='#8A89C0', fg='white',
                                          highlightthickness=0, borderwidth=0, cursor="hand2", padx=10, pady=10,
                                          command=lambda i=item: self.remove_from_basket(i))
                remove_button.pack(side=tk.LEFT, padx=(5, 10))

                # Check if total_price_label is properly initialized before configuring it
                if hasattr(self, 'total_price_label'):
                    if isinstance(self.total_price_label, tk.Label) and self.total_price_label.winfo_exists():
                        self.total_price_label.config(text=f"Total Price: £{total_price}")

                # Update or create the "Checkout" button
                if hasattr(self, 'total_price_label'):
                    self.checkout_button = tk.Button(self.basket_frame, text="Checkout", bg='#8A89C0', fg='white',
                                                     highlightthickness=0, borderwidth=0, cursor="hand2",
                                                     padx=10, pady=10, command=self.checkout)
                    self.checkout_button.pack(pady=10)

            # Update the checkout button only once
            if not hasattr(self, 'checkout_button'):
                self.checkout_button = tk.Button(self.basket_frame, text="Checkout", bg='#8A89C0', fg='white',
                                                 highlightthickness=0, borderwidth=0, cursor="hand2",
                                                 padx=10, pady=10, command=self.checkout)
                self.checkout_button.pack(pady=10)

    def close_window(self):
        self.master.hide_basket()  # Hide the basket window
        self.destroy()  # Destroy the window
        self.master.basket_window = None  # Set basket_window to None after destruction

    def remove_from_basket(self, item):
        self.basket_items.remove(item)
        self.update_basket()

    def process_purchase(self):
        # Get card details entered by the user
        card_number = self.card_number_entry.get()
        csv = self.csv_entry.get()
        name = self.name_entry.get()

        # Perform validation of card details if needed

        print("Card Number:", card_number)
        print("CSV:", csv)
        print("Name:", name)

        # Get the current date and time
        current_date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        try:
            self.connection = mysql.connector.connect(
                host="127.0.0.1",
                port="3306",
                user="root",
                password="1234",
                database="vending_machine"
            )
            print("Connection successful!")
        except mysql.connector.Error as error:
            # Handle any errors that occur during the connection process
            print("Error connecting to MySQL:", error)

        # Fetch drink names from the database based on drink IDs
        cursor = self.connection.cursor()
        drink_names = {}
        for item in self.basket_items:
            drink_id, _, _, _, _ = item
            cursor.execute("SELECT DrinkName FROM drinks_program WHERE DrinkID = %s", (drink_id,))
            result = cursor.fetchone()
            if result:
                drink_names[drink_id] = result[0]
        cursor.close()

        # Prepare transaction data for all items in the basket
        transaction_data = ";".join([f"{item[0]},{item[4]}" for item in self.basket_items])

        # Write the transaction details to the "transactions.txt" file
        try:
            with open("transactions.txt", "a") as f:
                for item in self.basket_items:
                    drink_id, _, _, price, quantity = item
                    drink_name = drink_names.get(drink_id, 'Unknown')
                    total_price = price * quantity
                    transaction_entry = f"{current_date_time},{drink_name},{quantity},{total_price}\n"
                    f.write(transaction_entry)
                    print(transaction_entry)
            print("Transaction details written to file successfully.")
        except Exception as e:
            print("Error writing transaction details to file:", e)
            return

        # Send the transaction data along with card details to the server
        # threading.Thread(target=self.send_transaction_thread, args=(transaction_with_card_details,)).start()
        self.send_transaction(transaction_data)  # Call send_transaction directly

        # Close the database connection
        self.connection.close()

    def checkout(self):
        # Create a new window for card details entry
        self.checkout_window = tk.Toplevel(self)
        self.checkout_window.title("Checkout")
        self.force_maximize()

        # Configure the window to be maximized
        self.checkout_window.attributes("-fullscreen", True)

        # Create a frame for the logo with light gray background
        self.logo_frame = tk.Frame(self.checkout_window, bg="light grey")
        self.logo_frame.pack(fill="x")  # Fill the entire width

        # Load the image
        image_path = "images/food_express_logo.png"
        image = Image.open(image_path)
        photo = ImageTk.PhotoImage(image)

        # Create a label to display the image
        self.logo_label = tk.Label(self.logo_frame, image=photo, bg="light grey")
        self.logo_label.image = photo  # Keep a reference to prevent garbage collection
        self.logo_label.pack(padx=20, pady=20)  # due to this pack function we add the padding here

        # Create a blank label for line spacing
        tk.Label(self.checkout_window, text=" ", height=1, pady=10).pack()

        # Display items in the basket with quantities
        for item in self.basket_items:
            drink_name, quantity, price, image_path = item[1], item[4], item[3] * item[4], item[2]

            # Create a frame to hold each product information
            product_frame = tk.Frame(self.checkout_window, padx=20, pady=10)
            product_frame.pack(anchor="center", pady=10)  # Center the frame horizontally

            # Load and display the product image
            image = Image.open(image_path)
            image = image.resize((30, 30))
            photo = ImageTk.PhotoImage(image)
            image_label = tk.Label(product_frame, image=photo)
            image_label.image = photo  # Keep a reference to prevent garbage collection
            image_label.pack(side=tk.LEFT, padx=10)  # Pack the image label to the left

            # Display the product name, quantity, and total price
            product_info = f"{drink_name} x {quantity} - £{price}"
            item_label = tk.Label(product_frame, text=product_info, font=("Arial", 10))
            item_label.pack(side=tk.LEFT, padx=10)  # Pack the item label to the left

        # Display the total amount label
        total_amount = sum(item[3] * item[4] for item in self.basket_items)
        total_label = tk.Label(self.checkout_window, text=f"Total Amount: £{total_amount}", font=("Arial", 12))
        total_label.pack(pady=10)

        # Create a blank label for line spacing
        tk.Label(self.checkout_window, text=" ", height=1, pady=10).pack()

        # Create entry fields for card details
        tk.Label(self.checkout_window, text="Credit Card Number:", pady=10).pack()
        self.card_no = tk.StringVar()
        self.card_number_entry = ttk.Entry(self.checkout_window, textvariable=self.card_no)
        self.card_number_entry.pack()

        # Set up validation to allow only numeric input
        self.card_number_entry.config(validate="key", validatecommand=(self.register(self.validate_card), "%P"))

        tk.Label(self.checkout_window, text="CSV (3-digit number):", pady=10).pack()
        # Create the CSV entry widget
        self.csv_var = tk.StringVar()
        self.csv_entry = ttk.Entry(self.checkout_window, textvariable=self.csv_var)
        self.csv_entry.pack()
        # Set up validation to allow only numeric input
        self.csv_entry.config(validate="key", validatecommand=(self.register(self.validate_csv), "%P"))

        # Configure the appearance of the entry widget to space out the numbers
        style = ttk.Style()
        style.configure("TEntry", padding=(10, 5), font=("Arial", 12), letterspacing=25)

        tk.Label(self.checkout_window, text="Name on Card:", pady=10).pack()
        # Create the name on card entry widget
        self.name_entry = ttk.Entry(self.checkout_window)
        self.name_entry.pack()

        # Create a blank label for line spacing
        tk.Label(self.checkout_window, text=" ", height=1, pady=10).pack()

        # Create a purchase button
        purchase_button = tk.Button(self.checkout_window, text="Purchase", bg='#8A89C0', fg='white',
                                    highlightthickness=0, borderwidth=0, cursor="hand2",
                                    padx=10, pady=10, command=self.process_purchase)
        purchase_button.pack()

        # Add my Food Express logo to the checkout window
        self.logo_frame.pack(fill="x")

        self.update_basket()

    def validate_card(self, new_value):
        # Check if the new value contains only numeric characters
        if new_value.isdigit():
            # Check if the length of the new value is less than or equal to 12 (to restrict to 12 digits)
            if len(new_value) <= 12:
                return True
        return False

    def validate_csv(self, new_value):
        if new_value.isdigit() and len(new_value) <= 3:
            return True
        return False


class VendingMachineApp(BaseWindow):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title("Vending Machine")  # Set title for the VendingMachineApp window

        try:
            self.connection = mysql.connector.connect(
                host="127.0.0.1",
                port="3306",
                user="root",
                password="1234",
                database="vending_machine"
            )
            print("Connection successful!")
        except mysql.connector.Error as error:
            # Handle any errors that occur during the connection process
            print("Error connecting to MySQL:", error)

        buttons_container = tk.Frame(self.drink_frame)
        buttons_container.pack(side=tk.LEFT, padx=10)

        # Add button to refresh stock availability
        self.refresh_button = tk.Button(self, text="\u21BB Refresh Stock Availability", bg='#8A89C0', fg='white',
                                        highlightthickness=0,
                                        borderwidth=0, cursor="hand2", padx=10, pady=10, command=self.refresh_widgets)
        self.refresh_button.pack(padx=10, pady=2)

        self.create_drinks_table()
        self.basket_items = []
        self.basket_window = None  # Initialize basket window variable

        self.create_widgets()


    def create_drinks_table(self):
        cursor = self.connection.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS drinks_program (
                DrinkID INT AUTO_INCREMENT PRIMARY KEY,
                DrinkName VARCHAR(255),
                Description VARCHAR(255),
                Stock_Quantity INT,
                ImagePath VARCHAR(255),
                Price DECIMAL(10, 2),  -- Add Price column
                Last_Updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        self.connection.commit()

    def create_widgets(self):

        # Add label to display stock information
        self.drink_labels = []  # Initialize drink labels list

        cursor = self.connection.cursor()
        cursor.execute("SELECT DrinkID, DrinkName, Description, ImagePath, Price, stock_quantity FROM drinks_program")
        drinks = cursor.fetchall()
        cursor.close()  # Close the cursor after fetching data

        # Clear existing drink frames
        for widget in self.drink_frame.winfo_children():
            widget.destroy()

        self.description_labels = []  # description labels for toggling
        self.drink_id_labels = []  # drink ID labels for toggling

        # Iterate through the fetched drinks data
        for drink_id, drink_name, description, image_path, price, stock_quantity in drinks:
            image = Image.open(image_path)
            image = image.resize((100, 100))
            photo = ImageTk.PhotoImage(image)

            drink_column = tk.Frame(self.drink_frame)
            drink_column.pack(side=tk.LEFT, padx=10)

            if stock_quantity <= 0:
                out_of_stock_label = tk.Label(drink_column, text="Out of Stock", bg="#FFCCCB", fg="red")
                out_of_stock_label.pack()  # Display out of stock label
                name_label = tk.Label(drink_column, text=drink_name, width=20, font=("Arial", 12), fg="light grey")
                name_label.pack()  # Set width of the name column

                # Product ID label
                drink_id_label = tk.Label(drink_column, text=f"ID: {drink_id}", width=20, font=("Arial", 10),
                                          fg="light grey")
                drink_id_label.pack()
                drink_id_label.pack_forget()  # Hide the ID initially
                self.drink_id_labels.append(drink_id_label)  # Add to the list

                description_label = tk.Label(drink_column, text=description, width=30, wraplength=150,
                                             font=("Arial", 9), fg="light grey")
                description_label.pack()  # Set wraplength for text wrapping
                description_label.pack_forget()  # Hide the description initially
                self.description_labels.append(description_label)  # Add to the list

                price_label = tk.Label(drink_column, text=f"£{price}", width=10, font=("Arial", 13), fg="light grey")
                price_label.pack()  # Display price
            elif stock_quantity > 0 and stock_quantity < 6:
                out_of_stock_label = tk.Label(drink_column, text=f"\U0001F525 Low stock: {stock_quantity}", fg="orange", bg="#FFDAB9")
                out_of_stock_label.pack()  # Display out of stock label
                name_label = tk.Label(drink_column, text=drink_name, width=20, font=("Arial", 12))
                name_label.pack()  # Set width of the name column

                # Product ID label
                drink_id_label = tk.Label(drink_column, text=f"ID: {drink_id}", width=20, font=("Arial", 10))
                drink_id_label.pack()
                drink_id_label.pack_forget()  # Hide the ID initially
                self.drink_id_labels.append(drink_id_label)  # Add to the list

                description_label = tk.Label(drink_column, text=description, width=30, wraplength=150,
                                             font=("Arial", 9))
                description_label.pack()  # Set wraplength for text wrapping
                description_label.pack_forget()  # Hide the description initially
                self.description_labels.append(description_label)  # Add to the list

                price_label = tk.Label(drink_column, text=f"£{price}", width=10, font=("Arial", 13))
                price_label.pack()  # Display price
            else:
                name_label = tk.Label(drink_column, text=drink_name, width=20, font=("Arial", 12))
                name_label.pack()  # Set width of the name column

                # Product ID label
                drink_id_label = tk.Label(drink_column, text=f"ID: {drink_id}", width=20, font=("Arial", 10))
                drink_id_label.pack()
                drink_id_label.pack_forget()  # Hide the ID initially
                self.drink_id_labels.append(drink_id_label)  # Add to the list

                description_label = tk.Label(drink_column, text=description, width=30, wraplength=150,
                                             font=("Arial", 9))
                description_label.pack()  # Set wraplength for text wrapping
                description_label.pack_forget()  # Hide the description initially
                self.description_labels.append(description_label)  # Add to the list

                price_label = tk.Label(drink_column, text=f"£{price}", width=10, font=("Arial", 13))
                price_label.pack()  # Display price

            # Create a label to display the product image
            label_image = tk.Label(drink_column, image=photo, pady=10, width=100, height=100, anchor="center",
                                   compound="center", cursor="hand2")
            label_image.photo = photo  # Keep a reference to prevent garbage collection
            label_image.pack()

            if stock_quantity > 0:
                current_stock = tk.Label(drink_column, text=f"{stock_quantity} left", width=20, font=("Arial", 10))
                current_stock.pack()  # Set width of the name column
            else:
                current_stock = tk.Label(drink_column, text="0 left. Back soon!", width=20, font=("Arial", 10))
                current_stock.pack()  # Set width of the name column

            if stock_quantity > 0:
                # Bind the selection event to a function to add the product to the basket
                label_image.bind("<Button-1>",
                                 lambda event, id=drink_id, n=drink_name, p=image_path, pr=price: self.add_to_basket(id,
                                                                                                                     n,
                                                                                                                     p,
                                                                                                                     pr))

            # Start a new row after every third column
            if len(drink_column.winfo_children()) >= 4:
                new_row = tk.Frame(self.drink_frame)
                new_row.pack()  # Start a new row

        # Call update_stock to fetch and display initial stock information
        self.update_stock()

    import time

    def refresh_widgets(self):
        for _ in range(3):  # Retry up to 3 times
            try:
                # Clear existing drink frames
                for widget in self.drink_frame.winfo_children():
                    widget.destroy()

                self.update_stock()
                # Call create_widgets again to recreate the widgets with updated stock information
                self.create_widgets()
                break  # Break out of the retry loop if successful
            except ConnectionRefusedError:
                print("Connection refused. Retrying...")
                time.sleep(1)  # Wait for 1 second before retrying
        else:
            print("Failed to refresh widgets after multiple attempts.")

    def show_basket(self):
        if self.basket_window is None:
            self.basket_window = BasketWindow(self)
            self.basket_window.protocol("WM_DELETE_WINDOW", self.hide_basket)
        else:
            self.basket_window.update_basket()  # Update the basket before displaying it
            self.basket_window.deiconify()

    def write_stock_info(self, stock_info):
        try:
            with open('stock_info.txt', 'w') as file:
                for drink, quantity in stock_info.items():
                    file.write(f"{drink}: {quantity}, ")
            print("Stock info written to file successfully.")
        except Exception as e:
            print("Error writing stock info to file:", e)

    # Update stock availability
    def update_stock(self):
        try:
            # Execute SQL query to fetch current stock information
            cursor = self.connection.cursor()
            cursor.execute("SELECT DrinkName, Stock_Quantity FROM drinks_program WHERE Stock_Quantity >= 0")
            stock_info = cursor.fetchall()

            # Update stock information for each individual drink label
            for label, (drink_name, quantity) in zip(self.drink_labels, stock_info):
                label.config(text=f"{drink_name}: {quantity} left")

            # Commit the transaction and close the cursor
            self.connection.commit()
            cursor.close()

        except mysql.connector.Error as error:
            print("Error updating stock availability:", error)

    def send_transaction_to_server(self, drink_id, quantity):
        # Connect to the server and send the transaction data
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
                client_socket.connect(('100.70.136.78', 12348))
                transaction_data = f"process_transaction {drink_id},{quantity}"
                client_socket.sendall(transaction_data.encode())
                response = client_socket.recv(1024).decode()
                if response == 'Transaction processed successfully.':
                    return True
                else:
                    return False
        except Exception as e:
            print("Error:", e)
            return False

    def hide_basket(self):
        if self.basket_window is not None:
            self.basket_window.withdraw()

    def add_to_basket(self, drink_id, drink_name, image_path, price):
        # Fetch the available stock quantity for the selected drink
        cursor = self.connection.cursor()
        cursor.execute("SELECT Stock_Quantity FROM drinks_program WHERE DrinkID = %s", (drink_id,))
        stock_quantity = cursor.fetchone()[0]
        cursor.close()

        # Check if the item already exists in the basket
        for index, item in enumerate(self.basket_items):
            if item[:4] == (drink_id, drink_name, image_path, price):
                current_quantity = item[4]  # Get the current quantity in the basket
                remaining_stock = stock_quantity - current_quantity  # Calculate remaining stock
                if remaining_stock <= 0:
                    messagebox.showwarning("Warning - Product Stock", f"You already have {stock_quantity} in your basket for {drink_name}. There is only {stock_quantity} left in stock!")
                    return
                else:
                    # Update the quantity
                    self.basket_items[index] = item[:4] + (current_quantity + 1,)
                    messagebox.showinfo("Success", "Quantity updated in basket!")
                    if self.basket_window:
                        self.basket_window.update_basket()  # Update the basket display
                    return

        # Add the item to the basket with quantity 1
        self.basket_items.append((drink_id, drink_name, image_path, price, 1))
        messagebox.showinfo("Success", "Selected drink added to basket!")
        if self.basket_window:
            self.basket_window.update_basket()  # Update the basket display

    def toggle_descriptions(self):
        for label in self.description_labels:
            if self.descriptions_visible:
                label.pack_forget()  # Hide the description
            else:
                label.pack()  # Show the description
        for label in self.drink_id_labels:
            if self.descriptions_visible:
                label.pack_forget()  # Hide the drink ID
            else:
                label.pack()  # Show the drink ID
        self.descriptions_visible = not self.descriptions_visible
        if self.descriptions_visible:
            self.hide_descriptions_button.config(text="HIDE PRODUCT DESCRIPTIONS", bg='#8A89C0', fg='white',
                                                 highlightthickness=0,
                                                 borderwidth=0, cursor="hand2", padx=10, pady=10)
        else:
            self.hide_descriptions_button.config(text="VIEW PRODUCT INFO", bg='#8A89C0', fg='white', highlightthickness=0,
                                                 borderwidth=0, cursor="hand2", padx=10, pady=10)


if __name__ == "__main__":
    app = VendingMachineApp()
    app.mainloop()
