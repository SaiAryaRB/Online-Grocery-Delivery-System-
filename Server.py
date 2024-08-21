import socket
import ssl
import threading

# File containing product data
PRODUCT_FILE = "dataset.txt"
lock = threading.Lock()

def load_products():
    products = []
    with open(PRODUCT_FILE, "r") as file:
        for line in file:
            product_data = line.strip().split(",")
            if len(product_data) == 3:  # Ensure there are three elements in the list
                name = product_data[0].strip()
                try:
                    price = float(product_data[1].strip())
                    quantity = int(product_data[2].strip())
                    products.append({"name": name, "price": price, "quantity": quantity})
                except ValueError:
                    print(f"Invalid data format in line: {line.strip()}")
            else:
                print(f"Illegal data format in line: {line.strip()}")
    return products

def save_products(products):
    with open(PRODUCT_FILE, "w") as file:
        for product in products:
            file.write(f"{product['name']},{product['price']},{product['quantity']}\n")

def save_product_quantity(item_name, quantity):
    with open(PRODUCT_FILE, "r") as file:
        lines = file.readlines()
    with open(PRODUCT_FILE, "w") as file:
        for line in lines:
            name, price, old_quantity = line.strip().split(",")
            if name.strip() == item_name.strip():
                file.write(f"{name},{price},{quantity}\n")
            else:
                file.write(f"{name},{price},{old_quantity}\n")

def handle_client(client_socket, client_address):
    print(f"Connection from {client_address} established.")
    products = load_products()
    cart = []
    
    while True:
        try:
            data = client_socket.recv(1024)
            if not data:
                break
            # Parse client request and process it
            request = data.decode().strip()
            print(f"Received request from {client_address}: {request}")
            if request.startswith("ADD_TO_CART"):
                _, item_name = request.split(" ", 1)
                response = add_to_cart(products, cart, item_name)
                client_socket.sendall(response.encode())
            elif request.startswith("REMOVE_FROM_CART"):
                _, item_name = request.split(" ", 1)
                response = remove_from_cart(cart, item_name, products)
                client_socket.sendall(response.encode())
            elif request == "SHOW_CART":
                send_cart(client_socket, cart, products)
            elif request == "CONFIRM_ORDER":
                total_price = confirm_order(client_socket, products, cart)
                client_socket.sendall(f"Order confirmed. Total price: Rs.{total_price}".encode())
            elif request == "FETCH_ITEMS":
                send_items(client_socket, products)
            elif request == "CLEAR_CART":
                cart.clear()
                client_socket.sendall("Cart cleared successfully.".encode())
            else:
                client_socket.sendall("Invalid request".encode())
        except ConnectionResetError:
            print(f"Connection with {client_address} reset.")
            break
    
    print(f"Connection with {client_address} closed.")
    client_socket.close()

def add_to_cart(products, cart, item_name):
    for product in products:
        if product["name"].lower() == item_name.lower():
            if product["quantity"] > 0:
                # Decrement quantity immediately if it's possible to add the item to the cart
                product["quantity"] -= 1
                save_product_quantity(item_name, product["quantity"])  # Save modified quantity to the dataset file immediately
                cart_item = {"name": product["name"], "price": product["price"]}
                cart.append(cart_item)
                return f"Item '{item_name}' added to your cart."
            else:
                return f"Item '{item_name}' cannot be added. It is out of stock."
    return f"Item '{item_name}' not found."

def remove_from_cart(cart, item_name, products):
    for product in cart:
        if product["name"].lower() == item_name.lower():
            cart.remove(product)
            # Increment quantity of the item by 1 without refreshing stock
            for dataset_product in products:
                if dataset_product["name"].lower() == item_name.lower():
                    dataset_product["quantity"] += 1
                    save_products(products)  # Save modified products to the dataset file immediately
                    break
            return f"Item '{item_name}' removed from your cart."
    return f"Item '{item_name}' not found in your cart."

def send_cart(client_socket, cart, products):
    if cart:
        cart_items = []
        processed_items = set()  # Keep track of processed items
        for cart_item in cart:
            item_name = cart_item["name"]
            if item_name not in processed_items:
                item_quantity = sum(1 for product in cart if product["name"] == item_name)
                item_price = next(product["price"] for product in products if product["name"] == item_name)
                cart_items.append(f"{item_name} - {item_quantity} x {item_price}")
                processed_items.add(item_name)
        cart_str = "\n".join(cart_items)
        client_socket.sendall(f"{cart_str}".encode())
    else:
        client_socket.sendall("Your cart is empty.".encode())

def confirm_order(client_socket, products, cart):
    total_price = 0
    for product in cart:
        total_price += product["price"]
    save_products(products)  # Save any changes made to the products during adding to cart
    cart.clear()
    return total_price

def send_items(client_socket, products):
    items = "\n".join([f"{product['name']} - {product['price']}" for product in products])
    client_socket.sendall(items.encode())

def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(('127.0.0.1', 8081))
    server_socket.listen(5)

    print("Server listening...")

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            ssl_socket = ssl.wrap_socket(client_socket, server_side=True, certfile="server.crt", keyfile="server.key", ssl_version=ssl.PROTOCOL_TLS)
            client_thread = threading.Thread(target=handle_client, args=(ssl_socket, client_address))
            client_thread.start()
            
    except KeyboardInterrupt:
        print("Server shutting down...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    main()