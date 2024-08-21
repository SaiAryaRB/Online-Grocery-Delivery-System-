import tkinter as tk
from tkinter import messagebox
import socket
import ssl

class GroceryClientGUI:
    def _init_(self, root):
        self.root = root
        self.root.title("Swiftcart")

        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_address = ('127.0.0.1', 8081)
        self.connect_to_server()

        # Set up dynamic background
        self.colors = ['#FF5733', '#FFBD33', '#C8FF33', '#33FF57', '#33FFBD', '#333CFF']
        self.current_color_index = 0
        self.change_background()

        self.create_widgets()

    def change_background(self):
        self.root.configure(background=self.colors[self.current_color_index])
        self.current_color_index = (self.current_color_index + 1) % len(self.colors)
        self.root.after(5000, self.change_background)

    def connect_to_server(self):
        try:
            self.client_socket =ssl.wrap_socket(self.client_socket, cert_reqs=ssl.CERT_REQUIRED, ca_certs='server.crt')
            self.client_socket.connect(self.server_address)
            print("Connection established.")
        except ConnectionRefusedError:
            messagebox.showerror("Error", "Connection to server failed. Please make sure the server is running.")
            self.root.destroy()

    def create_widgets(self):
        # Confirm Order button
        confirm_order_button = tk.Button(self.root, text="Confirm Order", command=self.confirm_order, bg="black", fg="white")
        confirm_order_button.pack(side=tk.TOP, pady=10)

        # Show Cart button
        show_cart_button = tk.Button(self.root, text="Show Cart", command=self.show_cart, bg="black", fg="white")
        show_cart_button.pack(side=tk.TOP)

        # Create a frame for the buttons
        button_frame = tk.Frame(self.root, background=self.root.cget('background'))
        button_frame.pack()

        # Fetch and display items
        self.items = self.fetch_items()
        if self.items:
            row, col = 0, 0
            for i, item in enumerate(self.items):
                if i % 6 == 0:
                    row += 1
                    col = 0
                item_name, item_price = item.split(" - ")
                button = tk.Button(button_frame, text=f"{item_name}\n{item_price}", command=lambda item=item: self.add_to_cart(item),
                                   width=15, height=5, bg="green")
                button.grid(row=row, column=col, padx=25, pady=25)
                col += 1

    def fetch_items(self):
        try:
            self.client_socket.sendall("FETCH_ITEMS".encode())
            response = self.client_socket.recv(1024).decode()
            items = response.split('\n')
            return items
        except ConnectionResetError:
            messagebox.showerror("Error", "Lost connection to server.")
            self.root.destroy()

    def add_to_cart(self, item):
        try:
            item_name, item_price = item.split(" - ")
            command = f"ADD_TO_CART {item_name}"
            self.client_socket.sendall(command.encode())
            response = self.client_socket.recv(1024).decode()
            if "added to your cart" in response:
                # Update GUI to reflect addition to cart
                messagebox.showinfo("Response", response)
            else:
                # Item out of stock or not found
                messagebox.showerror("Error", response)
        except ConnectionResetError:
            messagebox.showerror("Error", "Lost connection to server.")
            self.root.destroy()

    def show_cart(self):
        try:
            command = "SHOW_CART"
            self.client_socket.sendall(command.encode())
            response = self.client_socket.recv(1024).decode()

            cart_window = tk.Toplevel(self.root)
            cart_window.title("Your Cart")

            cart_text = tk.Text(cart_window, width=40, height=20)
            cart_text.pack()

            if response.strip() == "Your cart is empty.":
                cart_text.insert(tk.END, response)
            else:
                lines = response.split('\n')
                for line in lines:
                    item_name = line.split("-")[0].strip()  # Extract item name
                    cart_text.insert(tk.END, line.strip())
                    if item_name:  # Exclude empty lines
                        cart_text.window_create(tk.END, window=tk.Button(cart_text, text="Remove from Cart", command=lambda name=item_name: self.remove_from_cart(name)))
                        cart_text.insert(tk.END, '\n')  # Newline for spacing
        except ConnectionResetError:
            messagebox.showerror("Error", "Lost connection to server.")
            self.root.destroy()

    def remove_from_cart(self, item_name):
        try:
            command = f"REMOVE_FROM_CART {item_name}"
            self.client_socket.sendall(command.encode())
            response = self.client_socket.recv(1024).decode()
            messagebox.showinfo("Response", response)
        except ConnectionResetError:
            messagebox.showerror("Error", "Lost connection to server.")
            self.root.destroy()

    def confirm_order(self):
        try:
            command = "CONFIRM_ORDER"
            self.client_socket.sendall(command.encode())
            response = self.client_socket.recv(1024).decode()
            messagebox.showinfo("Response", response)
        except ConnectionResetError:
            messagebox.showerror("Error", "Lost connection to server.")
            self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = GroceryClientGUI(root)
    root.mainloop()