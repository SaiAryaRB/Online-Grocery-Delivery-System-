# Online-Grocery-Delivery-System
SwiftCart - Grocery Delivery System
Overview
SwiftCart is a Python-based grocery delivery application that allows users to browse grocery items, add them to a cart, and place orders. The system features a simple and intuitive GUI built with Tkinter and uses a text file as a database to manage inventory and process orders.

Features
User-Friendly Interface: The application uses Tkinter for a clean and interactive user interface.
Dynamic Background: The app features a changing background for a more engaging experience.
Product Management: Products are stored in a text file database, making it easy to add, remove, or update items.
Shopping Cart: Users can add items to a cart, view their cart, and remove items before confirming an order.
Order Confirmation: After confirming an order, the app calculates the total price and updates the inventory.

Dataset Structure
The product information is stored in a text file (dataset.txt). Each line in the file represents an item and follows the structure:
ItenName, Price , Quantity


Usage

Adding Items to Cart:
Select the desired item from the displayed list to add it to your cart.
Viewing Cart:
Click on the "Show Cart" button to view the items in your cart.
Removing Items from Cart:
In the cart view, click the "Remove from Cart" button next to the item you want to remove.
Confirming Order:
Click the "Confirm Order" button to place your order. The total cost will be displayed, and the inventory will be updated accordingly.


Security

SSL/TLS Connection:
The connection between the client and server is secured using SSL/TLS, ensuring the safety and integrity of data during transmission.
Contributing
Feel free to fork the repository and submit pull requests. For major changes, please open an issue first to discuss what you would like to change.


License

This project is licensed under the MIT License.


Acknowledgements

Tkinter for GUI development.
Python’s socket and ssl libraries for handling server-client communication securely.
