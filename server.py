# Import libraries...
import socket  # library allows interaction/connection with a network, e.g. over TCP protocol
import mysql.connector  # Python interface for MySQL databases: connection to database for products and stock


# get stock information from database table called "drinks program" and returns as a dictionary
def get_stock_info_from_database(connection):
    try:
        cursor = connection.cursor()
        cursor.execute("SELECT DrinkName, Stock_Quantity FROM drinks_program")
        # above is a command to execute for a SELECT statement for 2 attributes from our Drinks Program table
        rows = cursor.fetchall()  # fetches all rows  returned by SQL query
        # create a dictionary called stock info, keys are drink names and values are stock quantities:
        stock_info = {drink_name: stock_quantity for drink_name, stock_quantity in rows}
        return stock_info  # return the dictionary from the function
    except mysql.connector.Error as error:  # if there is an SQL error then do the following
        print("Failed to fetch stock info from database:", error)  # print error message to terminal
        return {}


def process_transaction(connection, client_socket, transaction_data):
    # try is error handling in Python - contains code I wish compiler to execute
    try:
        drink_id, quantity = map(int, transaction_data.split(','))  # extract drink_id and quantity from string 'transaction_data'
        cursor = connection.cursor()  # cursors used to execute SQL queries and aid connection to database
        cursor.execute("SELECT Stock_Quantity FROM drinks_program WHERE DrinkID = %s", (drink_id,))  # execute SQL command with conditional WHERE statement. Drink ID is a tuple
        current_stock = cursor.fetchone()[0]  # get first row of query result, result is a single value for stock quantity

        if current_stock < quantity:  # if logic - if current stock is less than quantity
            client_socket.sendall(b'Insufficient stock.')  # client socket will return the message of Insufficient Stock
        else:  # if the above is not true then..
            new_stock = current_stock - quantity  # minus current stock from quantity in database query
            cursor.execute("UPDATE drinks_program SET Stock_Quantity = %s WHERE DrinkID = %s", (new_stock, drink_id))   # execute SQL update query to update data in database table
            connection.commit()
            client_socket.sendall(b'Transaction processed successfully.')

    except Exception as e:
        print("Error processing transaction:", e)
        client_socket.sendall(b'Failed to process transaction.')

def update_stock(connection, client_socket):
    try:
        print("Received request to update client stock")
        stock_info = get_stock_info_from_database(connection)
        stock_info_str = ", ".join(f"{drink}: {quantity}" for drink, quantity in stock_info.items())
        client_socket.sendall(stock_info_str.encode())
        print("Sent stock information to client:", stock_info_str)
    except Exception as e:
        print("Error updating stock:", e)

def main():
    server_address = ('100.70.136.78', 12348)

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(server_address)
        server_socket.listen(1)
        print("Server listening on", server_address)

        try:
            database_connection = mysql.connector.connect(
                host="127.0.0.1",
                port="3306",
                user="root",
                password="1234",
                database="vending_machine"
            )
            print("Database connection successful!")
        except mysql.connector.Error as error:
            print("Error connecting to MySQL:", error)
            return

        while True:
            client_socket, client_address = server_socket.accept()
            with client_socket:
                print("Connection from", client_address)

                while True:
                    data = client_socket.recv(1024)
                    if not data:
                        break
                    request = data.decode().split(maxsplit=1)  # Split at most once to separate command from data
                    command = request[0]
                    print("Received command:", command)

                    if command == 'update_client_stock':
                        update_stock(database_connection, client_socket)
                    elif command == 'process_transaction':
                        if len(request) == 2:
                            transaction_data = request[1]
                            process_transaction(database_connection, client_socket, transaction_data)
                        else:
                            client_socket.sendall(b'Missing transaction data.')
                    else:
                        client_socket.sendall(b'Invalid command.')

if __name__ == "__main__":
    main()
