import datetime
import json
import os

# File paths
login_data_file = "login_data.txt"
customer_data_file = "customer_data.txt"
inventory_data_file = "inventory_data.txt"
repair_data_file = "repair_data.txt"
supplier_order_data_file = "supplier_order_data.txt"
user_activity_log_file = "user_activity_log.txt"
load_sup_purchase_order = "supplier_orders.txt"
inventory_file = 'inventory.json'
customer_data_file = 'customer_data.json'
order_file = 'orders.json'

# Sample users for demonstration 
superuser_credentials = ["superuser@123", "superusernotsuperman"]

# Inventory Staff
["felixdiu","INV@3004","Approved","3"],    
["tanyawatson","INV@2412","Approved","3"]

def read_file(file_path):
    try:
        with open(file_path, "r") as file:
            return [line.strip().split(",") for line in file.readlines()]
    except FileNotFoundError:
        return []
    
def write_file(file_path, data): 
    with open(file_path, "w") as file: 
        for line in data: 
            file.write(",".join(line) + "\n")

def get_next_admin_username(login_data):
    # Find the highest existing admin username
    admin_usernames = [user[0] for user in login_data if user[3] == "2" and user[0].startswith("ADMIN")]
    if not admin_usernames:
        return "ADMIN001"
    
    # Extract numbers from existing admin usernames, find the highest, and increment it
    max_number = max(int(username[5:]) for username in admin_usernames)
    next_number = max_number + 1
    return f"ADMIN{next_number:03d}"

def sign_up():
    user_type = input("Are you signing up as:\n(1) Customer\n(2) Admin\n(3) Inventory Staff\n")

    if user_type not in ["1", "2", "3"]:
        print("Invalid selection!")
        return

    login_data = read_file(login_data_file)

    if user_type == "2":
        username = get_next_admin_username(login_data)
        print(f"Generated admin username: {username}")
    else:
        username = input("Create a username: ")

    password = input("Create a password: ")

    if user_type == "1": 
        if not (len(password) >= 8 and any(c.isupper() for c in password) and sum(c.isdigit() for c in password) >= 3): 
            print("Customer password must be at least 8 characters long, including 1 UPPER CASE and 3 NUMBERS.")
            return

        # NATIONALITY
        nationality = input("Are you Malaysian or non-Malaysian? Enter 'M' for Malaysian or 'N' for Non-Malaysian: ").strip().upper()

        if nationality == "M":
            ic_number = input("Enter IC number (excluding '-')").strip()
            if len(ic_number) != 12:
                print("Invalid IC number format.")
                return
            phone_number = input("Enter your phone number (12 characters starting with +60): ").strip()
            if len(phone_number) != 12 or not phone_number.startswith("60"): 
                print("Phone number must start with +60 and be 12 characters long.") 
                return
            customer_info = ["Malaysian", ic_number, phone_number]

        elif nationality == "N":
            passport_number = input("Enter your passport number: ").strip()
            phone_number = input("Enter your phone number (either Malaysia phone number or international phone number): ").strip()
            customer_info = ["Non-Malaysian", passport_number, phone_number]

        else:
            print("Invalid nationality!")
            return

        registration_date = input("Enter your registration date (YYYY-MM-DD): ").strip()
        try:
            datetime.datetime.strptime(registration_date, "%Y-%m-%d")
        except ValueError:
            print("Invalid date format! Please use YYYY-MM-DD.")
            return

        customer_data = [username, password, "Pending", user_type] + customer_info + [registration_date]
        login_data.append(customer_data)

    elif user_type == "2": 
        if not (len(password) >= 10 and password.startswith("ADMIN@")):
            print("Admin password must be at least 10 characters long and start with 'ADMIN@'.") 
            return
        login_data.append([username, password, "Pending", user_type])

    elif user_type == "3": 
        if not (len(password) >= 8 and password.startswith("INV@") and sum(c.isdigit() for c in password) == 4):
            print("Inventory staff password must be at least 8 characters long, start with 'INV@' and followed by 4 numbers.")
            return
        login_data.append([username, password, "Pending", user_type])

    write_file(login_data_file, login_data)
    print("Registration successful. Waiting for approval.")

#login
def login():
    username = input("Enter username: ")
    password = input("Enter password: ")

    login_data = read_file(login_data_file)
    superuser_credentials = ("superuser@123", "superusernotsuperman")

    if username == superuser_credentials[0] and password == superuser_credentials[1]:
        superuser_menu()
        return

    found = False
    for user in login_data:
        if user[0] == username and user[1] == password:
            found = True
            if user[2] == "Approved":
                if user[3] == "1":
                    customer_menu()
                elif user[3] == "2":
                    log_activity(username, "Logged in")
                    admin_menu()
                elif user[3] == "3":
                    log_activity(username, "Logged in")
                    inventory_menu()
                else:
                    print("Invalid role.")
            else:
                print("You do not have access to this feature.")
            break

    if not found:
        print("Invalid login credentials!")
        log_activity(username, "Failed login attempt")


def customer_menu():
    welcome_customer = (
        "````````````````````````````````````````````````````````````````````````````````````````````````\n" 
        "                                Welcome to Customer Menu\n" 
        "````````````````````````````````````````````````````````````````````````````````````````````````"
    )
    print(welcome_customer)

    inventory_file = "inventory_item.txt"  # Specify the inventory file name
    username = "customer"

    while True:
        print("\n1. Purchase Order")
        print("2. Repair/Service Order")
        print("3. Modify Purchase Order/Repair/Service Order")
        print("4. Payment for orders placed")
        print("5. Inquiry of order status")
        print("6. Cancel Order")
        print("7. Reports")
        print("8. Logout")

        choice = input("Enter choice: ").strip()

        if choice == "1":
            purchase_order(username, inventory_file)
        elif choice == "2":
            service_repair_order(username)
        elif choice == "3":
            modify_order(username, inventory)
        elif choice == "4":
            make_payment(username)
        elif choice == "5":
            inquire_order_status(username)
        elif choice == "6":
            cancel_order(username)
        elif choice == "7":
            reports("1")
        elif choice == "8":
            break
        else:
            print("Invalid choice!")


def save_inventory_to_file(inventory, filename):
    with open(filename, "w") as file:
        for item in inventory:
            # Convert each item list to a string and write it to the file
            file.write(", ".join(map(str, item)) + "\n")

inventory = [
        ["ItemID", "Item Name", "Brand", "Category", "Model Number", "Description", "Specification", "Warranty(Year)", "Stock Keeping Unit", "Price/Unit(RM)", "Quantity In Stock"],
        ["101", "Laptop", "Dell", "Laptop", "Inspiron 15 3000", "15.6-inch laptop with Intel i5 processor", "8GB RAM, 256GB SSD", 2, "SKU101", 2300.00, 25],
        ["102", "Desktop", "HP", "Desktop", "Pavilion 590", "Powerful desktop for everyday use", "16GB RAM, 1TB HDD", 3, "SKU102", 3200.00, 10],
        ["103", "Monitor", "Samsung", "Monitor", "LC24F396FHNXZA", "Curved 24-inch monitor", "1920x1080 resolution, 60Hz", 2, "SKU103", 650.00, 15],
        ["104", "Mouse", "Logitech", "Accessory", "M330", "Silent wireless mouse", "Wireless, ergonomic design", 1, "SKU104", 75.00, 50],
        ["105", "Keyboard", "Corsair", "Accessory", "K95 RGB", "Mechanical gaming keyboard", "RGB backlight, Cherry MX switches", 2, "SKU105", 550.00, 20],
        ["106", "Printer", "Canon", "Printer", "PIXMA G2020", "High-efficiency color printer", "Ink tank system, USB 2.0", 1, "SKU106", 450.00, 30],
        ["107", "External Hard Drive", "Seagate", "Storage", "Backup Plus", "Portable external hard drive", "2TB storage, USB 3.0", 2, "SKU107", 350.00, 40],
        ["108", "SSD", "Samsung", "Storage", "970 EVO", "High-speed SSD for gaming", "1TB NVMe, M.2", 5, "SKU108", 750.00, 25],
        ["109", "Graphics Card", "NVIDIA", "Component", "RTX 3070", "Powerful GPU for gaming", "8GB GDDR6, Ray tracing support", 3, "SKU109", 2500.00, 15],
        ["110", "Power Supply", "Corsair", "Component", "RM850x", "High-performance power supply", "850W, 80+ Gold certified", 3, "SKU110", 450.00, 35],
        ["111", "Motherboard", "ASUS", "Component", "ROG Strix Z490-E", "Gaming motherboard", "LGA 1200, ATX, DDR4 support", 3, "SKU111", 900.00, 10],
        ["112", "RAM", "Kingston", "Component", "HyperX Fury", "High-speed RAM for gaming", "16GB DDR4, 3200MHz", 5, "SKU112", 350.00, 60],
        ["113", "CPU", "Intel", "Component", "Core i7-10700K", "High-performance CPU", "8 cores, 16 threads, 3.8GHz", 3, "SKU113", 1500.00, 20],
        ["114", "Laptop Charger", "Dell", "Accessory", "LA65NS2-01", "65W power adapter for laptops", "65W, 19.5V", 2, "SKU114", 150.00, 50],
        ["115", "Webcam", "Logitech", "Accessory", "C920 HD Pro", "Full HD webcam", "1080p, 30fps", 2, "SKU115", 350.00, 20],
        ["116", "Wireless Router", "TP-Link", "Networking", "Archer AX6000", "High-speed Wi-Fi 6 router", "8-stream, 1.8GHz quad-core CPU", 3, "SKU116", 600.00, 15],
        ["117", "Laptop Cooling Pad", "Cooler Master", "Accessory", "Notepal X3", "Cooling pad for laptops", "120mm fan, adjustable height", 2, "SKU117", 120.00, 40],
        ["118", "USB Flash Drive", "SanDisk", "Storage", "Ultra Flair", "High-speed USB flash drive", "128GB, USB 3.0", 1, "SKU118", 65.00, 75],
        ["119", "Headset", "Razer", "Accessory", "Kraken X", "Wired gaming headset", "7.1 surround sound, lightweight design", 2, "SKU119", 250.00, 30],
        ["120", "Gaming Chair", "Secretlab", "Furniture", "Omega 2020", "Comfortable gaming chair", "Adjustable armrests, lumbar support", 5, "SKU120", 1200.00, 10]
    ]
save_inventory_to_file(inventory, "inventory_item.txt")

def view_inventory(filename):
    with open(filename, "r") as file:
        lines = file.readlines()  # Read all lines from the file
    
    # Print the header
    headers = lines[0].strip().split(", ")
    print(f"{' | '.join(headers)}")
    print("-" * 100)  # Print a separator line for readability
    
    # Print the item details
    for line in lines[1:]:  # Skip the header row
        item = line.strip().split(", ")
        if len(item) != len(headers):
            print(f"Skipping malformed line: {line.strip()}")
            continue  # Skip malformed lines
        
        print(f"ItemID: {item[0]}")
        print(f"Item Name: {item[1]}")
        print(f"Brand: {item[2]}")
        print(f"Category: {item[3]}")
        print(f"Model Number: {item[4]}")
        print(f"Description: {item[5]}")
        print(f"Specification: {item[6]}")
        print(f"Warranty (Year): {item[7]}")
        print(f"Stock Keeping Unit: {item[8]}")
        print(f"Price/Unit (RM): {item[9]}")
        print(f"Quantity In Stock: {item[10]}")
        print("-" * 100)  # Print a separator line for readability

def purchase_order(username, inventory_file):
    view_inventory(inventory_file)  # Display the inventory

    order_items = []
    total_amount = 0.0

    while True:
        item_id = input("Enter the ItemID to purchase (or type 'done' to finish): ").strip()

        if item_id.lower() == 'done':
            break

        try:
            quantity = int(input("Enter the quantity: ").strip())
        except ValueError:
            print("Invalid quantity. Please enter a number.")
            continue

        item_found = False
        updated_inventory = []

        with open(inventory_file, "r") as file:
            lines = file.readlines()
        
        for line in lines:
            item = line.strip().split(", ")
            if len(item) != 11:
                continue  # Skip malformed lines without printing a message
            
            if item[0].strip() == item_id:
                item_name = item[1].strip()
                try:
                    price = float(item[9].strip())  # Convert price to float
                    stock = int(item[10].strip())  # Convert stock to int
                except ValueError:
                    continue  # Skip malformed data without printing a message
                
                item_found = True

                if quantity > stock:
                    print(f"Insufficient stock for {item_name}. Only {stock} available.")
                    updated_inventory.append(line.strip())
                    continue

                # Update the order
                order_items.append((item_id, item_name, quantity, price))
                total_amount += price * quantity
                item[10] = str(stock - quantity)  # Decrease the stock
                updated_inventory.append(", ".join(item))
                print(f"Added {quantity} of {item_name} to your order.")
            else:
                updated_inventory.append(line.strip())

        if not item_found:
            print(f"ItemID {item_id} not found.")
        
        # Save the updated inventory back to the file
        with open(inventory_file, "w") as file:
            for item_line in updated_inventory:
                file.write(item_line + "\n")

    # Display the order summary
    print("\nOrder Summary:")
    for item in order_items:
        print(f"ItemID: {item[0]}")
        print(f"Item Name: {item[1]}")
        print(f"Quantity: {item[2]}")
        print(f"Price/Unit: RM{item[3]:.2f}")
        print(f"Total: RM{item[3] * item[2]:.2f}")
    print(f"Total Amount: RM{total_amount:.2f}")

    confirm = input("Are you sure you want to place the order? (yes/no): ").strip().lower()
    if confirm == 'yes':
        save_order(username, order_items, total_amount)  # Save the order with the username
        print("Order placed successfully.")
    else:
        print("Order canceled.")

def save_order(username, order_items, total_amount):
    order_id = get_next_order_id([]) 
    with open("orders.txt", "a") as file:
        file.write(f"OrderID: {order_id}, Username: {username}, Total Amount: RM{total_amount:.2f}\n")
        for item in order_items:
            file.write(f"{item[0]}, {item[1]}, {item[2]}, RM{item[3]:.2f}\n")
        file.write("\n")

def generate_order_id():
    counter_file = 'order_id_counter.txt'

    if not os.path.isfile(counter_file):
        with open(counter_file, 'w') as f:
            f.write('10000000')

    with open(counter_file, 'r') as f:
        current_value = int(f.read().strip())

    new_value = current_value + 1

    with open(counter_file, 'w') as f:
        f.write(str(new_value))

    order_id = f"{new_value:08d}"

    return order_id

def display_options(options):
    for key, value in options.items():
        print(f"{key}. {value}")

def display_service_options():
    service_options = {
        "1": {
            "name": "Hardware Services",
            "options": {
                "a": "Memory RAM (2GB)                  RM100",
                "b": "Memory RAM (4GB)                  RM200",
                "c": "Memory RAM (8GB)                  RM300",
                "d": "Computer performance upgrade      RM300",
                "e": "HDD (500GB)                       RM150",
                "f": "HDD (1TB)                         RM250",
                "g": "SSD (500GB)                       RM250",
                "h": "SSD (1TB)                         RM450",
            }
        },
        "2": {
            "name": "Software Services",
            "options": {
                "a": "Computer cleaning service:        RM100",
                "b": "Operating system updates:         RM150",
                "c": "Operating system installation:    RM150",
                "d": "Window/OS upgrade:                RM150",
                "e": "Backup and Data Recovery:         RM200"
            }
        },
        "3": {
            "name": "IT Services and Support",
            "options": {
                "a": "Battery:                          RM200",
                "b": "IT product technical support:     RM300",
                "c": "IT maintenance:                   RM300",
                "d": "Hard Disk (500GB):                RM200",
                "e": "Hard Disk (1TB):                  RM300",
                "f": "Solid State Drive (500GB):        RM300",
                "g": "Solid State Drive (1TB):          RM500",
                "h": "LED / LCD display screen:         RM500"
            }
        },
        "4": {
            "name": "Networking Services",
            "options": {
                "a": "Wi-Fi/LAN networking setup:       RM100",
                "b": "Wi-Fi/LAN networking upgrades:    RM100",
                "c": "Wireless setup or installation:   RM150",
                "d": "Extend internet/Wi-Fi coverage:   RM300"
            }
        }
    }
    return service_options

def display_repair_options():
    repair_options = {
        "1": {
            "name": "Hardware Services",
            "options": {
                "a": "PC start-up issue:                    RM100",
                "b": "Disk drive defragmentation service:   RM100",
                "c": "Charging problem repair:              RM100",
                "d": "Keyboard replacement:                 RM200",
                "e": "Battery replacement:                  RM200",
                "f": "Tablet screen replacement:            RM200",
                "g": "HDD/SSD installation:                 RM300",
                "h": "Laptop screen repair:                 RM300",
                "i": "Water or liquid damage repair:        RM300",
                "j": "Fix graphic card:                     RM300",
                "k": "Fix damaged motherboard:              RM300"
            }
        },
        "2": {
            "name": "Software Services",
            "options": {
                "a": "Basic maintenance:           RM100",
                "b": "Anti-virus installation:     RM100",
                "c": "Operating System Updates:    RM150",
                "d": "Malware removal:             RM150",
                "e": "Remove trojans and spyware:  RM150",
                "f": "Fix networking issues:       RM150",
                "g": "Diagnose software issues:    RM150",
                "h": "Reformat computer:           RM200",
                "i": "Virus removal:               RM200",
                "j": "Data recovery:               RM300",
            }
        }
    }
    return repair_options

def service_repair_order(username):
    service_options = display_service_options()
    repair_options = display_repair_options()
    service_name = ""
    repair_name = ""

    print("Service/Repair Order Menu")
    print("1. Service")
    print("2. Repair")

    choice = input("Choose an option (1 for Service, 2 for Repair): ")

    if choice == '1':
        print("Available Service Options:")
        for key, value in service_options.items():
            print(f"{key}. {value['name']}")

        service_choice = input("Select a service option (1-4): ")

        if service_choice in service_options:
            print(f"--- {service_options[service_choice]['name']} ---")
            display_options(service_options[service_choice]['options'])
            specific_choice = input("Select a specific service option (a-h): ")

            if specific_choice in service_options[service_choice]['options']:
                service_name = service_options[service_choice]['name']
                option_details = service_options[service_choice]['options'][specific_choice]
                amount = int(option_details.split('RM')[1].strip())
            else:
                print("Invalid choice. Returning to customer menu.")
                return

    elif choice == '2':
        print("Available Repair Options:")
        for key, value in repair_options.items():
            print(f"{key}. {value['name']}")

        repair_choice = input("Select a repair option (1-2): ")

        if repair_choice in repair_options:
            print(f"--- {repair_options[repair_choice]['name']} ---")
            display_options(repair_options[repair_choice]['options'])
            specific_choice = input("Select a specific repair option (a-k): ")

            if specific_choice in repair_options[repair_choice]['options']:
                repair_name = repair_options[repair_choice]['name']
                option_details = repair_options[repair_choice]['options'][specific_choice]
                amount = int(option_details.split('RM')[1].strip())
            else:
                print("Invalid choice. Returning to customer menu.")
                return
    else:
        print("Invalid choice. Returning to customer menu.")
        return

    print("Please select your Device Transfer Method:")
    print("1. Drop off")
    print("2. Pickup (additional RM30)")

    transfer_method = input("Enter your choice (1 or 2): ")
    additional_charge = 0

    if transfer_method == '1':
        print("Business hours: Mon-Fri 9AM - 6PM")
    elif transfer_method == '2':
        additional_charge = 30
        pickup_address = input("Enter pickup address: ")
        pickup_time = input("Enter pickup time: ")
    else:
        print("Invalid choice. Returning to customer menu.")
        return

    total_amount = amount + additional_charge
    print(f"Total Amount (including additional charges): RM{total_amount:.2f}")

    confirm = input("Are you sure you want to place the order? (yes/no): ")
    if confirm.lower() == 'yes':
        order_id = generate_order_id()
        order_date = datetime.datetime.now().strftime('%Y-%m-%d')

        order_data = {
            "username": username,
            "order_id": order_id,
            "order_date": order_date,
            "service_or_repair": {"type": "Service" if choice == '1' else "Repair"},
            "service_or_repair_name": service_name if choice == '1' else repair_name,
            "selected_option": option_details,
            "total_amount": f"RM{total_amount:.2f}",
            "transfer_method": "Drop off" if transfer_method == '1' else "Pickup",
            "status": "Unpaid"
        }

        if transfer_method == '2':
            order_data["pickup_address"] = pickup_address
            order_data["pickup_time"] = pickup_time

        try:
            with open("orders.json", "r+") as file:
                try:
                    orders = json.load(file)
                except json.JSONDecodeError as e:
                    print(f"Error loading JSON data: {e}")
                    orders = []
                orders.append(order_data)
                file.seek(0)
                json.dump(orders, file, indent=4)
                file.truncate()
            print(f"Order placed successfully! Your order ID is {order_id}.")
            print("Please proceed to make payment.")
        except IOError:
            print("Error saving order. Please try again later.")
    else:
        print("Order cancelled.")

def load_inventory(filename):
    inventory_list = []
    try:
        with open(filename, "r") as file:
            for line in file:
                data = line.strip().split(", ")
                inventory_list.append(data)
    except FileNotFoundError:
        print("Inventory file not found, starting with an empty list.")
    
    return inventory_list

def load_inventory_data():
    """Load the inventory from the inventory.txt file."""
    inventory = []
    try:
        with open("inventory.txt", "r") as file:
            for line in file:
                item = line.strip().split(",")
                inventory.append(item)
    except FileNotFoundError:
        print("Inventory file not found.")
    except IOError:
        print("Error reading inventory file.")
    return inventory

def modify_order(username, inventory):
    order_id = input("Enter the Order ID to modify: ").strip()

    try:
        # Read orders from the file
        orders = []
        with open("save_order.txt", "r") as file:
            order = []
            for line in file:
                if line.strip() == "-" * 40:
                    if order:
                        orders.append(order)
                    order = []
                else:
                    order.append(line.strip())
            if order:
                orders.append(order)

        order_found = False
        for order in orders:
            if len(order) >= 2:
                order_username = order[1].split(": ")
                order_id_check = order[0].split(": ")

                if len(order_username) > 1 and len(order_id_check) > 1:
                    if order_username[1] == username and order_id_check[1] == order_id:
                        order_found = True
                        print("Order found. You can modify it now.")
                        print("Order details:")
                        for line in order:
                            print(line)

                        while True:
                            print("\n1. Modify Item ID")
                            print("2. Modify Quantity")
                            print("3. Modify Service/Repair")
                            print("4. Done")
                            modify_choice = input("Enter your choice: ").strip()

                            if modify_choice == "1":
                                # Modify Item ID
                                item_id = input("Which ItemID do you want to modify: ").strip()
                                new_item_id = input("Enter the new ItemID: ").strip()
                                new_quantity = input("Enter the new quantity: ").strip()
                                for i, line in enumerate(order):
                                    if line.startswith("ItemID: " + item_id):
                                        item_details = line.split(", ")
                                        item_details[0] = f"ItemID: {new_item_id}"
                                        item_details[2] = f"Quantity: {new_quantity}"
                                        order[i] = ", ".join(item_details)
                                        break
                                print("Item ID modified successfully.")

                            elif modify_choice == "2":
                                # Modify Quantity
                                item_id = input("Enter the ItemID to modify quantity: ").strip()
                                new_quantity = input("Enter the new quantity: ").strip()
                                for i, line in enumerate(order):
                                    if line.startswith("ItemID: " + item_id):
                                        item_details = line.split(", ")
                                        item_details[2] = f"Quantity: {new_quantity}"
                                        order[i] = ", ".join(item_details)
                                        break
                                print("Item quantity modified successfully.")

                            elif modify_choice == "3":
                                # Modify Service/Repair Order
                                print("\n1. Modify Service")
                                print("2. Modify Repair")
                                print("3. Modify Device Transfer Method")
                                service_choice = input("Enter your choice: ").strip()

                                if service_choice == "1":
                                    # Modify Service
                                    service_options = display_service_options()
                                    print("Available Service Options:")
                                    for key, value in service_options.items():
                                        print(f"{key}: {value['name']}")
                                    selected_service = input("Select a service option (1-4): ").strip()
                                    if selected_service in service_options:
                                        print("Specific Options:")
                                        for option_key, option_value in service_options[selected_service]['options'].items():
                                            print(f"{option_key}: {option_value}")
                                        specific_choice = input("Select a specific service option (a-h): ").strip()
                                        if specific_choice in service_options[selected_service]['options']:
                                            service_name = service_options[selected_service]['name']
                                            option_details = service_options[selected_service]['options'][specific_choice]
                                            amount = float(option_details.split('RM')[1].strip())
                                            for i, line in enumerate(order):
                                                if line.startswith("Service/Repair Option: "):
                                                    order[i] = f"Service/Repair Option: {service_name}"
                                                elif line.startswith("Specific Option: "):
                                                    order[i] = f"Specific Option: {option_details}"
                                                elif line.startswith("Total Amount: "):
                                                    order[i] = f"Total Amount: RM{amount:.2f}"
                                            print("Service order modified successfully.")
                                    else:
                                        print("Invalid service option.")

                                elif service_choice == "2":
                                    # Modify Repair
                                    repair_options = display_repair_options()
                                    print("Available Repair Options:")
                                    for key, value in repair_options.items():
                                        print(f"{key}: {value['name']}")
                                    selected_repair = input("Select a repair option (1-2): ").strip()
                                    if selected_repair in repair_options:
                                        print("Specific Options:")
                                        for option_key, option_value in repair_options[selected_repair]['options'].items():
                                            print(f"{option_key}: {option_value}")
                                        specific_choice = input("Select a specific repair option (a-k): ").strip()
                                        if specific_choice in repair_options[selected_repair]['options']:
                                            repair_name = repair_options[selected_repair]['name']
                                            option_details = repair_options[selected_repair]['options'][specific_choice]
                                            amount = float(option_details.split('RM')[1].strip())
                                            for i, line in enumerate(order):
                                                if line.startswith("Service/Repair Option: "):
                                                    order[i] = f"Service/Repair Option: {repair_name}"
                                                elif line.startswith("Specific Option: "):
                                                    order[i] = f"Specific Option: {option_details}"
                                                elif line.startswith("Total Amount: "):
                                                    order[i] = f"Total Amount: RM{amount:.2f}"
                                            print("Repair order modified successfully.")
                                    else:
                                        print("Invalid repair option.")

                                elif service_choice == "3":
                                    # Modify Device Transfer Method
                                    print("\n1. Drop Off")
                                    print("2. Pick Up")
                                    transfer_method = input("Enter your choice: ").strip()

                                    if transfer_method == "1":
                                        for i, line in enumerate(order):
                                            if line.startswith("Device Transfer Method: "):
                                                order[i] = f"Device Transfer Method: Drop Off"
                                        print("Device transfer method modified to Drop Off.")

                                    elif transfer_method == "2":
                                        additional_charge = 30
                                        pickup_address = input("Enter pickup address: ")
                                        pickup_time = input("Enter pickup time: ")
                                        for i, line in enumerate(order):
                                            if line.startswith("Device Transfer Method: "):
                                                order[i] = f"Device Transfer Method: Pick Up (Address: {pickup_address}, Time: {pickup_time}, Additional Charge: RM{additional_charge})"
                                        print("Device transfer method modified to Pick Up.")

                                else:
                                    print("Invalid choice. Returning to customer menu.")
                                    break

                            elif modify_choice.lower() == "4":
                                # Save changes to the file
                                with open("save_order.txt", "w") as file:
                                    for o in orders:
                                        for line in o:
                                            file.write(line + "\n")
                                        file.write("-" * 40 + "\n")
                                print("Purchase order modified successfully. Returning to customer menu.")
                                customer_menu()  # Call without parameters if globals are used
                                return

                            else:
                                print("Invalid choice. Please try again.")

        if not order_found:
            print("Order ID not found or already paid. Please make an order first.")
            return

    except FileNotFoundError:
        print("Order file not found. Please make an order first.")



def make_payment(username):
    order_id = input("Enter the Order ID for payment: ").strip()

    try:
        with open('orders.json', 'r') as file:
            orders = json.load(file)

        order_found = False
        for order in orders:
            if order["username"] == username and order["order_id"] == order_id and order.get("status", "") == "Unpaid":
                order_found = True
                payment_amount = float(input("Enter payment amount: ").strip())

                if payment_amount <= 0:
                    print("Invalid payment amount. Returning to menu.")
                    return
                
                if payment_amount != order.get("total_amount", 0):
                    print("Payment amount does not match the order total. Payment not processed.")
                    return

                order["status"] = "Paid"
                print(f"Payment processed successfully for Order ID {order_id}.")

                # Generate the invoice after payment is processed
                generate_invoice(order)
                break

        if not order_found:
            print("Order ID not found or already paid. Payment not allowed.")
            return

        with open('orders.json', 'w') as file:
            json.dump(orders, file, indent=4)

    except IOError:
        print("Error accessing orders file.")


def inquire_order_status(username):
    order_summary = {
        'To Pay': [],
        'Packing': [],
        'Shipping': [],
        'Delivered': [],
        'Cancelled': []
    }

    # Check if the order files exist
    if not os.path.exists('save_order.txt'):
        print("No orders found.")
        return

    try:
        with open('save_order.txt', 'r') as file:
            lines = file.readlines()
    except IOError:
        print("Error reading orders file.")
        return

    # Initialize variables to store the current order information
    current_order = {}

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Debugging: print the raw line for inspection
        print(f"Processing line: '{line}'")

        if line.startswith('Order ID:'):
            current_order['order_id'] = line.split(': ')[1]
        elif line.startswith('Order by:'):
            current_order['username'] = line.split(': ')[1]
        elif line.startswith('Status:'):
            current_order['status'] = line.split(': ')[1]
        elif line.startswith('Total Amount:'):
            current_order['total_amount'] = line.split(': ')[1]
        elif line.startswith('----------------------------------------'):
            # End of order, process it
            if current_order.get('username') == username:
                order_id = current_order.get('order_id')
                status = current_order.get('status')

                if status == 'Unpaid':
                    order_summary['To Pay'].append(order_id)
                elif status == 'Paid':
                    # Extracting date from `order_id` for demonstration; adjust as needed
                    try:
                        order_date_str = current_order.get('order_id')[-8:]
                        order_date = datetime.strptime(order_date_str, '%Y%m%d')
                    except ValueError:
                        order_date = datetime.now()
                    
                    order_age = (datetime.now() - order_date).days

                    if order_age <= 1:
                        order_summary['Packing'].append(order_id)
                    elif order_age == 2:
                        order_summary['Shipping'].append(order_id)
                    elif order_age > 3:
                        order_summary['Delivered'].append(order_id)
                elif status == 'Cancelled':
                    order_summary['Cancelled'].append(order_id)

            # Reset for the next order
            current_order = {}

    # Display the order status summary
    print("Order Status Summary:")
    for category, orders in order_summary.items():
        if orders:
            print(f"{category}: {', '.join(orders)}")
        else:
            print(f"{category}: -")



def cancel_order(username):
    order_id = input("Enter the Order ID to cancel: ").strip()
    
    try:
        with open('orders.json', 'r') as file:
            orders = json.load(file)
        
        found = False
        updated_orders = []

        for order in orders:
            if order['order_id'] == order_id and order.get('status') == 'Unpaid':
                found = True
                print(f"Order with ID {order_id} canceled successfully.")
            else:
                updated_orders.append(order)

        if not found:
            print(f"No un-paid order found with ID {order_id}.")

        # Write the updated orders back to the JSON file
        with open('orders.json', 'w') as file:
            json.dump(updated_orders, file, indent=4)

    except IOError:
        print("Error accessing orders file.")

#Admin Menu
def admin_menu():
    welcome_admin = (
        "````````````````````````````````````````````````````````````````````````````````````````````````\n"
        "                                             Admin Menu\n"
        "````````````````````````````````````````````````````````````````````````````````````````````````"
    )
    print(welcome_admin)

    while True:
        print("\n1. Verify New Customer")
        print("2. Check Customer Order Status (Purchase Order)")
        print("3. Repair/Service Order")
        print("4. Purchase order (SUPPLIER)")
        print("5. Reports")
        print("6. Logout")

        choice = input("Enter choice: ")

        if choice == "1":
            verify_new_customer()
        elif choice == "2":
            CUSpurchase_order()
        elif choice == "3":
            repair_service()
        elif choice == "4":
            SUPpurchase_order()
        elif choice == "5":
            reports("2")
        elif choice == "6":
            break
        else:
            print("Invalid choice!")

#Super user menu
def superuser_menu():
    welcome_superuser = (
        "````````````````````````````````````````````````````````````````````````````````````````````````\n"
        "                                   SUPER USER MENU\n"
        "````````````````````````````````````````````````````````````````````````````````````````````````"
    )
    print(welcome_superuser)

    while True:
        print("\n1. Add Users")
        print("2. Modify User Personal Details")
        print("3. Disable User Access")
        print("4. Inquiry of User’s System Usage")
        print("5. Check Customer Order Status (Purchase Order)")
        print("6. Repair/Service Order")
        print("7. Purchase Order (SUPPLIER)")
        print("8. Reports")
        print("9. Logout")

        choice = input("Enter choice: ")

        if choice == "1":
            add_users()
        elif choice == "2":
            modify_user_personal_details()
        elif choice == "3":
            disable_user_access()
        elif choice == "4":
            inquiry_of_user_system_usage()
        elif choice == "5":
            CUSpurchase_order()
        elif choice == "6":
            repair_service()
        elif choice == "7":
            SUPpurchase_order()
        elif choice == "8":
            reports("superuser")
        elif choice == "9":
            break
        else:
            print("Invalid choice!")

def reports(user_type):
    print("Reports Menu")
    
    if user_type == "superuser":
        print("1. Invoice")
        print("2. Financial Reports")
        print("3. Inventory Reports")
        print("4. Attendance Reports")
        print("5. Log of Activity Report")
        
    elif user_type == "2":  # Admin
        print("1. Invoice")
        print("2. Financial Reports")
        print("3. Inventory Reports")
        
    elif user_type == "3":  # Inventory Staff
        print("1. Invoice")
        print("2. Inventory Reports")
        
    elif user_type == "1":  # Customer
        print("1. Invoice")
    
    choice = input("Enter the number of the report you want to view: ").strip()
    
    if choice == "1":
        invoice_report()
    elif choice == "2" and user_type in ["superuser", "2"]:
        financial_report()
    elif choice == "3" and user_type in ["superuser", "2", "3"]:
        inventory_report()
    elif choice == "4" and user_type == "superuser":
        attendance_report()
    elif choice == "5" and user_type == "superuser":
        log_activity_report() 
    else:
        print("Invalid choice or unauthorized report.")


def load_inventory(filename):
    inventory_list = []
    try:
        with open(filename, "r") as file:
            for line in file:
                data = line.strip().split(", ")
                inventory_list.append(data)
    except FileNotFoundError:
        print("Inventory file not found, starting with an empty list.")
    
    return inventory_list

def get_next_item_id(existing_item_ids):
    if not existing_item_ids:
        return "101"  # Start with "101" if no items exist

    # Convert item IDs to integers and find the highest one
    max_id = max(int(item_id) for item_id in existing_item_ids)
    return str(max_id + 1)

def get_next_sku(item_id):
    return f"SKU{item_id}"

def get_valid_int(prompt):
    while True:
        try:
            value = int(input(prompt).strip())
            return value
        except ValueError:
            print("Incorrect data type, please enter an integer.")

def get_valid_float(prompt):
    while True:
        try:
            value = float(input(prompt).strip())
            return value
        except ValueError:
            print("Incorrect data type, please enter a number.")

def add_inventory_item(filename, inventory_list):
    # Read existing ItemIDs
    existing_item_ids = set(item[0] for item in inventory_list)

    # Generate the next ItemID
    item_id = get_next_item_id(existing_item_ids)
    sku = get_next_sku(item_id)

    # Ask for the other required attributes
    item_name = input("Enter Item Name: ").strip()
    brand = input("Enter Brand: ").strip()
    category = input("Enter Category: ").strip()
    model_number = input("Enter Model Number: ").strip()
    description = input("Enter Description: ").strip()
    specification = input("Enter Specification: ").strip()
    warranty = get_valid_int("Enter Warranty (Year): ")
    price_per_unit = get_valid_float("Enter Price/Unit (RM): ")
    quantity_in_stock = get_valid_int("Enter Quantity In Stock: ")
    
    # Create a new item list
    new_item = [
        item_id, item_name, brand, category, model_number, 
        description, specification, warranty, sku, 
        price_per_unit, quantity_in_stock
    ]
    
    # Append the new item to the in-memory list
    inventory_list.append(new_item)
    
    # Write the new item to the file (Append mode)
    with open(filename, "a") as file:
        file.write(", ".join(map(str, new_item)) + "\n")

    print(f"Item added successfully with Item ID: {item_id} and SKU: {sku}")

def generate_invoice(order):
    """Generates an invoice and writes it to the invoices_data.txt file."""
    invoice_id = f"INV-{order['order_id']}"
    customer_name = order['username']
    date = datetime.datetime.now().strftime("%Y-%m-%d")
    amount = order['total_amount']

    # Write invoice details to the invoice file
    with open("invoices_data.txt", "a") as file:
        file.write(f"{invoice_id},{customer_name},{date},{amount}\n")

    print(f"Invoice generated for Order ID {order['order_id']} with Invoice ID {invoice_id}.")

def remove_inventory_item(filename, inventory_list):
    item_id = input("Enter the Item ID of the item you want to remove: ").strip()
    
    # Find the item in the inventory
    item_to_remove = None
    for item in inventory_list:
        if item[0] == item_id:
            item_to_remove = item
            break
    
    if item_to_remove:
        print(f"Item found: {item_to_remove}")
        confirmation = input("Are you sure you want to remove this item? (yes/no): ").strip().lower()
        
        if confirmation == 'yes':
            inventory_list.remove(item_to_remove)
            
            # Rewrite the entire inventory to the file (excluding the removed item)
            with open(filename, "w") as file:
                for item in inventory_list:
                    file.write(", ".join(map(str, item)) + "\n")
            
            print(f"Item with ID {item_id} has been removed from the inventory.")
        else:
            print("No changes were made.")
    else:
        print(f"Item with ID {item_id} not found in the inventory.")

def update_inventory_item(filename, inventory_list):
    item_id = input("Enter the Item ID of the item you want to modify: ").strip()
    
    # Search for the item in the inventory
    item_to_update = None
    for item in inventory_list:
        if item[0] == item_id:
            item_to_update = item
            break
    
    if item_to_update:
        print(f"Item found: {item_to_update}")
        
        # List out the attributes for the user to choose from (excluding Item ID and SKU)
        attributes = [
            "Item Name", "Brand", "Category", "Model Number",
            "Description", "Specification", "Warranty (Years)",
            "Price/Unit (RM)", "Quantity In Stock"
        ]
        print("Which attribute do you want to update?")
        for idx, attribute in enumerate(attributes, start=1):
            print(f"{idx}. {attribute}")
        
        # Get the user's choice
        choice = get_valid_int("Enter the number corresponding to the attribute: ")
        
        if 1 <= choice <= len(attributes):
            attribute_name = attributes[choice - 1]
            # Mapping user's choice to the correct index in item_to_update
            mapping = [1, 2, 3, 4, 5, 6, 7, 9, 10]  # Corrected mapping
            correct_index = mapping[choice - 1]
            current_value = item_to_update[correct_index]
            print(f"Current {attribute_name}: {current_value}")
            
            # Get new value from the user
            if choice in [7, 9]:  # If updating Warranty or Quantity In Stock (integer fields)
                new_value = get_valid_int(f"Enter new {attribute_name}: ")
            elif choice == 8:  # If updating Price/Unit (float field)
                new_value = get_valid_float(f"Enter new {attribute_name}: ")
            else:  # For all other fields (strings)
                new_value = input(f"Enter new {attribute_name}: ").strip()
            
            # Ask for confirmation
            confirmation = input(f"Are you sure you want to update {attribute_name} to '{new_value}'? (yes/no): ").strip().lower()
            
            if confirmation == 'yes':
                item_to_update[correct_index] = str(new_value)
                # Rewrite the entire inventory to the file
                with open(filename, "w") as file:
                    for item in inventory_list:
                        file.write(", ".join(map(str, item)) + "\n")
                print(f"{attribute_name} has been updated successfully for Item ID {item_id}.")
            else:
                print("No changes were made.")
        else:
            print("Invalid choice. No changes were made.")
    else:
        print(f"Item with ID {item_id} not found in the inventory.")


# Function to load the inventory from the file
inventory = load_inventory("inventory_item.txt")

def greet_user(username):
    print("Welcome,inv_", username)
    
##define manage inventory menu
def manage_inventory():
    inventory_header = (
    "````````````````````````````````````````````````````````````````````````````````````````````````\n"
    "                                   MANAGE INVENTORY ITEM\n"
    "````````````````````````````````````````````````````````````````````````````````````````````````"
    )
    greet_user(username)
    print(inventory_header)
    
    while True:
        print(
        reminder_msg,
        "\n(Example: enter '1' to view inventory item.)"
        )
        print(
        "\nPlease select your action:\n"
        "1. View Inventory Item\n"
        "2. Add Inventory Item\n"
        "3. Remove Inventory Item\n"
        "4. Update Inventory Item\n"
        "5. Return to Inventory Main Menu\n"
        )
        
        try:

            choice = int(input("Your input: "))
            
            if choice == 1:
                view_inventory("inventory_item.txt")
            elif choice == 2:
                add_inventory_item("inventory_item.txt",inventory)
            elif choice == 3:
                remove_inventory_item("inventory_item.txt",inventory)
            elif choice == 4:
                update_inventory_item("inventory_item.txt", inventory)
            elif choice == 5:
                break
            elif choice not in range(1,6):
                print("Enter selections displayed only.")
                print("------------------------------------------------------------------------------------------------\n")

        except ValueError:
            print("Enter option NUMBER only.")
            print("------------------------------------------------------------------------------------------------\n")

def display_options_with_exit(options):
    for key, value in options.items():
        print(f"{key}. {value}")
    print("x. Exit")

def display_options_with_exit_and_return(options):
    for key, value in options.items():
        print(f"{key}. {value}")
    print("r. Return to previous menu")
    print("x. Exit")

def repair_service_information():
    service_options = display_service_options()
    repair_options = display_repair_options()

    while True:
        print("\nService/Repair Information Menu")
        print("1. Service")
        print("2. Repair")
        print("x. Exit")
        choice = input("Choose an option (1 for Service, 2 for Repair, x to Exit): ")

        if choice == 'x':
            print("Exiting menu.")
            break

        if choice == '1':
            while True:
                print("Available Service Options:")
                for key, value in service_options.items():
                    print(f"{key}. {value['name']}")
                print("r. Return to previous menu")
                print("x. Exit")
                service_choice = input("Select a service option (1-4), 'r' to return, or 'x' to exit: ")

                if service_choice == 'x':
                    print("Exiting menu.")
                    return
                elif service_choice == 'r':
                    break

                if service_choice in service_options:
                    while True:
                        print(f"\n--- {service_options[service_choice]['name']} ---")
                        display_options_with_exit_and_return(service_options[service_choice]['options'])
                        specific_choice = input("Select'r' to return, or 'x' to exit: ")

                        if specific_choice == 'x':
                            print("Exiting menu.")
                            return
                        elif specific_choice == 'r':
                            break

                        else:
                            print("Invalid choice. Returning to previous menu.")
                else:
                    print("Invalid choice. Returning to previous menu.")

        elif choice == '2':
            while True:
                print("Available Repair Options:")
                for key, value in repair_options.items():
                    print(f"{key}. {value['name']}")
                print("r. Return to previous menu")
                print("x. Exit")
                repair_choice = input("Select a repair option (1-2), 'r' to return, or 'x' to exit: ")

                if repair_choice == 'x':
                    print("Exiting menu.")
                    return
                elif repair_choice == 'r':
                    break

                if repair_choice in repair_options:
                    while True:
                        print(f"\n--- {repair_options[repair_choice]['name']} ---")
                        display_options_with_exit_and_return(repair_options[repair_choice]['options'])
                        specific_choice = input("Select 'r' to return, or 'x' to exit: ")

                        if specific_choice == 'x':
                            print("Exiting menu.")
                            return
                        elif specific_choice == 'r':
                            break

                        else:
                            print("Invalid choice. Returning to previous menu.")
                else:
                    print("Invalid choice. Returning to previous menu.")

        else:
            print("Invalid choice. Returning to previous menu.")



##define greet user message
def greet_user(username):
    print("Welcome,inv_", username)
    ##define manage manage customer orders
def manage_customer_orders():
    CO_header = (
    "````````````````````````````````````````````````````````````````````````````````````````````````\n"
    "                                   MANAGE CUSTOMER ORDERS\n"
    "````````````````````````````````````````````````````````````````````````````````````````````````"
    )
    greet_user(username)
    print(CO_header)
    
    while True:
        print(
        reminder_msg,
        "\n(Example: enter '1' to view customer purchase order.)"
        )
        print(
        "\nPlease select your action:\n"
        "1. View Customer Purchase Order\n"
        "2. View Repair/Service Order\n"
        "3. Repair/Service Information\n"
        "4. Return to Inventory Main Menu\n"
        )
        
        try:

            choice = int(input("Your input: "))
            
            if choice == 1:
                CUSpurchase_order()
            elif choice == 2:
                repair_service() 
            elif choice == 3:
                repair_service_information()
            elif choice == 4:
                break      
            elif choice not in range(1,5):
                print("Enter selections displayed only.")
                print("------------------------------------------------------------------------------------------------\n")

        except ValueError:
            print("Enter option NUMBER only.")
            print("------------------------------------------------------------------------------------------------\n")

def append_to_file(file_path, data):
    with open(file_path, "a") as file:
        file.write(",".join(data) + "\n")

# Function to update the check_SUPpurchase_order to include Payment_Status & Delivery_Status
def check_SUPpurchase_order(file_path):
    supplier_order_data = read_file(file_path)
    print("Purchase Order (SUPPLIER)")
    
    # Display all supplier orders and their statuses
    for order in supplier_order_data:
        print(f"Order ID: {order[0]}, Payment Status: {order[4]}, Delivery Status: {order[3]}")
    
    # Check status of a specific supplier order
    print("\n**Example Order ID: order001 \nEnter Order ID to check status: ")
    order_id = input().strip()
    
    # Search for the specified order ID
    for order in supplier_order_data:
        if order[0] == order_id:
            print(f"Order ID: {order[0]}, Payment Status: {order[4]}, Delivery Status: {order[3]}")
            break
    else:
        print("Order ID not found.")

def load_sup_purchase_order(filename):
    S_order_list = []
    try:
        with open(filename, "r") as file:
            for line in file:
                data = line.strip().split(",")  # Correct split without space
                S_order_list.append(data)
    except FileNotFoundError:
        print(f"Order file not found: {filename}")
    
    return S_order_list

def get_next_order_id(existing_order_ids):
    if not existing_order_ids:
        return "order001"  # Start with "order001" if no orders exist

    # Convert order IDs to integers and find the highest one
    max_id = max(int(order_id[5:]) for order_id in existing_order_ids)
    return f"order{max_id + 1:03d}"

# Function to generate a purchase order
def generate_purchase_order(file_path):
    # Load existing orders from file
    existing_orders = read_file(file_path)
    
    # Get next Order ID
    order_ids = [order[0] for order in existing_orders]
    order_id = get_next_order_id(order_ids)
    
    # Initialize the order
    order = [order_id, "1"]  # Only one item per order
    
    # Initialize total price
    total_price = 0
    
    # Get item details
    while True:
        item_id = input("Enter Item ID: ").strip()
        if any(item[0] == item_id for item in inventory):
            break
        else:
            print("Invalid input. Item ID not found in inventory.")
    
    quantity_ordered = int(input("Enter Quantity Ordered: "))
    
    # Find the item in inventory and get its unit price
    item = next(item for item in inventory if item[0] == item_id)
    unit_price = item[9]
    price_per_item = unit_price * quantity_ordered
    total_price += price_per_item
    
    # Append item details to the order
    order.extend([item_id, "Pending", "Unpaid", str(quantity_ordered), str(unit_price), str(price_per_item)])
    
    # Get the current date and time
    now = datetime.datetime.now()
    order_date = now.strftime("%Y-%m-%d")
    order_time = now.strftime("%H:%M:%S")
    
    # Calculate expected delivery date (30 days after order date)
    expected_delivery_date = (now + datetime.timedelta(days=30)).strftime("%Y-%m-%d")
    
    # Add the remaining order details
    order.extend([order_date, order_time, str(total_price), expected_delivery_date])
    
    # Get remark from the user
    remark = input("Enter any remarks: ").strip()
    order.append(remark)
    
    # Write the order to the file
    append_to_file(file_path, order)

# Function to view purchase order
def view_SUPpurchase_order(file_path):
    # Read the orders from the file
    orders = read_file(file_path)

    # Ask the user to input an Order ID
    order_id = input("Enter the Order ID: ").strip()

    # Search for the specified order ID
    for order in orders:
        if order[0] == order_id:
            # If the order is found, display its details
            print(f"\nOrder ID: {order[0]}")
            print(f"Item ID: {order[2]}")
            print(f"Delivery Status: {order[3]}")
            print(f"Payment Status: {order[4]}")
            print(f"Order Date: {order[8]}")
            print(f"Order Time: {order[9]}")
            print(f"Quantity Ordered: {order[5]}")
            print(f"Unit Price: {order[6]}")
            print(f"Price Per Item: {order[7]}")
            print(f"Total Price: {order[10]}")
            print(f"Expected Delivery Date: {order[11]}")
            print(f"Remarks: {order[12]}")
            return
    
    # If the order ID is not found, print a message
    print("Order ID not found.")
    
# Function to cancel a purchase order
def cancel_SUPpurchase_order(file_path):
    # Read the orders from the file
    orders = read_file(file_path)

    # Ask the user to input an Order ID to cancel
    order_id = input("Enter the Order ID to cancel: ").strip()

    # Search for the specified order ID
    for order in orders:
        if order[0] == order_id:
            # If the order is found, display its details
            print(f"\nOrder ID: {order[0]}")
            print(f"Item ID: {order[2]}")
            print(f"Delivery Status: {order[3]}")
            print(f"Payment Status: {order[4]}")
            print(f"Order Date: {order[8]}")
            print(f"Order Time: {order[9]}")
            print(f"Quantity Ordered: {order[5]}")
            print(f"Total Price: {order[10]}")
            print(f"Expected Delivery Date: {order[11]}")
            print(f"Remarks: {order[12]}")

            # Confirm if the user wants to cancel the order
            confirm = input("Do you want to cancel this order? (yes/no): ").strip().lower()
            if confirm == "yes":
                # Remove the order from the list
                orders.remove(order)
                # Update the file with the remaining orders
                write_file(file_path, orders)
                print(f"Order {order_id} has been canceled.")
            else:
                print("Order cancellation aborted.")
            return
    
    # If the order ID is not found, print a message
    print("Order ID not found.")

# Function to modify a purchase order
def modify_SUPpurchase_order(file_path):
    # Read the orders from the file
    orders = read_file(file_path)

    # Ask the user to input an Order ID to modify
    order_id = input("Enter the Order ID to modify: ").strip()

    # Search for the specified order ID
    for order in orders:
        if order[0] == order_id:
            # If the order is found, display its current details
            print(f"\nOrder ID: {order[0]}")
            print(f"Item ID: {order[2]}")
            print(f"Delivery Status: {order[3]}")
            print(f"Payment Status: {order[4]}")
            print(f"Order Date: {order[8]}")
            print(f"Order Time: {order[9]}")
            print(f"Quantity Ordered: {order[5]}")
            print(f"Unit Price: {order[6]}")
            print(f"Price Per Item: {order[7]}")
            print(f"Total Price: {order[10]}")
            print(f"Expected Delivery Date: {order[11]}")
            print(f"Remarks: {order[12]}")

            # Ask the user what attribute they want to modify
            attribute_to_modify = input("\nWhich attribute do you want to modify? (Item ID, Delivery Status, Payment Status, Quantity Ordered, Remarks): ").strip().lower()

            # Validate input and modify the attribute
            if attribute_to_modify == "item id":
                new_item_id = input("Enter new Item ID: ").strip()
                if any(item[0] == new_item_id for item in inventory):
                    order[2] = new_item_id
                    # Update the unit price based on the new item ID
                    item = next(item for item in inventory if item[0] == new_item_id)
                    unit_price = float(item[9])
                    order[6] = str(unit_price)  # Update unit price

                    # Recalculate the price per item and total price based on the current quantity
                    quantity_ordered = int(order[5])
                    price_per_item = unit_price * quantity_ordered
                    order[7] = str(price_per_item)  # Update price per item
                    order[10] = str(price_per_item)  # Update total price (single item order)
                else:
                    print("Invalid Item ID. Modification aborted.")
                    return
            elif attribute_to_modify == "quantity ordered":
                new_quantity_ordered = input("Enter new Quantity Ordered: ").strip()
                if new_quantity_ordered.isdigit() and int(new_quantity_ordered) > 0:
                    order[5] = new_quantity_ordered
                    # Recalculate the price per item and total price based on the new quantity
                    unit_price = float(order[6])
                    price_per_item = unit_price * int(new_quantity_ordered)
                    order[7] = str(price_per_item)  # Update price per item
                    order[10] = str(price_per_item)  # Update total price (single item order)
                else:
                    print("Invalid Quantity. Modification aborted.")
                    return
            
            # Other modifications (Delivery Status, Payment Status, Remarks) don't affect pricing
            elif attribute_to_modify == "delivery status":
                new_delivery_status = input("Enter new Delivery Status (pending/shipping/delivered): ").strip().lower()
                if new_delivery_status in ["pending", "shipping", "delivered"]:
                    order[3] = new_delivery_status
                else:
                    print("Invalid Delivery Status. Modification aborted.")
                    return
            elif attribute_to_modify == "payment status":
                new_payment_status = input("Enter new Payment Status (paid/unpaid): ").strip().lower()
                if new_payment_status in ["paid", "unpaid"]:
                    order[4] = new_payment_status
                else:
                    print("Invalid Payment Status. Modification aborted.")
                    return
            elif attribute_to_modify == "remarks":
                new_remarks = input("Enter new Remarks: ").strip()
                order[12] = new_remarks
            else:
                print("Invalid attribute. Modification aborted.")
                return
            
            # Recalculate the Expected Delivery Date based on logic (e.g., add 7 days to current date)
            now = datetime.datetime.now()
            order[8] = now.strftime("%Y-%m-%d")  # Update order date
            order[9] = now.strftime("%H:%M:%S")  # Update order time
            expected_delivery_date = now + datetime.timedelta(days=7)  # Add 7 days for delivery
            order[11] = expected_delivery_date.strftime("%Y-%m-%d")
            
            # Update the file with the modified order
            write_file(file_path, orders)
            print(f"Order {order_id} has been modified.")
            return
    
    # If the order ID is not found, print a message
    print("Order ID not found.")

##define manage purchase order
def manage_purchase_orders():
    PO_header= (
    "````````````````````````````````````````````````````````````````````````````````````````````````\n"
    "                                   MANAGE PURCHASE ORDER\n"
    "````````````````````````````````````````````````````````````````````````````````````````````````"
    )
    greet_user(username)
    print(PO_header)
    
    while True:
        print(
        reminder_msg,
        "\n(Example: enter '1' to generate purchase order.)"
        )
        print(
        "\nPlease select your action:\n"
        "1. Generate Purchase Order\n"
        "2. Check Supplier Purchase Order Status\n"
        "3. Modify Purchase Order\n"
        "4. Cancel Supplier Purchase Order\n"
        "5. View Supplier Purchase Order\n"
        "6. Return to Inventory Main Menu\n"
        )
        
        try:

            choice = int(input("Your input: "))
            
            if choice == 1:
                generate_purchase_order("SUP_purchase_orders.txt")
            elif choice == 2:
                check_SUPpurchase_order("SUP_purchase_orders.txt")
            elif choice == 3:
                modify_SUPpurchase_order("SUP_purchase_orders.txt")
            elif choice == 4:
                cancel_SUPpurchase_order("SUP_purchase_orders.txt")
            elif choice == 5:
                view_SUPpurchase_order("SUP_purchase_orders.txt")
            elif choice == 6:
                break
            elif choice not in range(1,7):
                print("Enter selections displayed only.")
                print("------------------------------------------------------------------------------------------------\n")

        except ValueError:
            print("Enter option NUMBER only.")
            print("------------------------------------------------------------------------------------------------\n")

def invoice_report():
    print("Generating Invoice Report...")

    invoice_data = read_file("invoices_data.txt")

    if not invoice_data:
        print("No invoices found.")
        return

    print("\nInvoice Report")
    print("---------------------------")
    total_amount = 0  # To calculate the total amount

    for record in invoice_data:
        invoice_id = record[0]
        customer_name = record[1]
        date = record[2]
        amount = float(record[3])  # Convert the amount to a floating-point number

        print(f"Invoice ID: {invoice_id}, Customer: {customer_name}, Date: {date}, Amount: RM {amount:.2f}")
        total_amount += amount  # Add the amount to the total

    print("---------------------------")
    print(f"Total Amount: RM {total_amount:.2f}")
    print("---------------------------\n")


def inventory_report():
    # Load inventory list from the inventory file
    inventory_list = load_inventory("inventory_item.txt")
    
    # Create an empty list for the inventory report
    inventory_report_list = []
    
    # Iterate through each item in the inventory and calculate total value
    for item in inventory_list:
        
        quantity_in_stock = int(item[-1])
        unit_price = float(item[-2])
        
        # Calculate total value
        total_value = quantity_in_stock * unit_price
        
        # Add total value as a new column to the item data
        item.append(f"{total_value:.2f}")
        
        # Add the updated item to the inventory report list
        inventory_report_list.append(item)
    
    # Write the inventory report list to the "inventory_report.txt" file
    with open("inventory_report.txt", "w") as file:
        for item in inventory_report_list:
            file.write(", ".join(item) + "\n")
    
    # Read and print the final result from the "inventory_report.txt" file
    print("\nFinal Inventory Report:")
    with open("inventory_report.txt", "r") as file:
        print(file.read())
        
        
##define greet user message
def greet_user(username):
    print("Welcome,inv_", username)
    
##define view_report
def view_report():
    view_report_header= (
    "````````````````````````````````````````````````````````````````````````````````````````````````\n"
    "                                   VIEW REPORTS\n"
    "````````````````````````````````````````````````````````````````````````````````````````````````"
    )
    greet_user(username)
    print(view_report_header)
    
    while True:
        print(
        reminder_msg,
        "\n(Example: enter '1' to view invoice.)"
        )
        print(
        "\nPlease select your action:\n"
        "1. View invoice\n"
        "2. Inventory Reports\n"
        "3. Return to Inventory Main Menu\n"
        )
        
        try:

            choice = int(input("Your input: "))
            
            if choice == 1:
                invoice_report()
            elif choice == 2:
                inventory_report()
            elif choice == 3:
                break
            elif choice not in range(1,4):
                print("Enter selections displayed only.")
                print("------------------------------------------------------------------------------------------------\n")

        except ValueError:
            print("Enter option NUMBER only.")
            print("------------------------------------------------------------------------------------------------\n")

reminder_msg = "**Select action by entering option number only."
username = "Felix Diu"

##define inventory main menu    
def inventory_menu():

    welcome_inventory = (
    "````````````````````````````````````````````````````````````````````````````````````````````````\n"
    "                                   INVENTORY MAIN MENU\n"
    "````````````````````````````````````````````````````````````````````````````````````````````````"
    )
        
    greet_user(username)
    print(welcome_inventory)
     
    while True:
        print(
        reminder_msg,
        "\n(Example: enter '1' to manage inventory item.)"
        )
        print(
        "\nPlease select your action:\n"
        "1. Manage Inventory Item\n"
        "2. Manage Customer Orders\n"
        "3. Manage Purchase Orders\n"
        "4. View Report\n"
        "5. Logout\n"
        )
        
        try:

            choice = int(input("Your input: "))
            
            if choice == 1:
                manage_inventory()
            elif choice == 2:
                manage_customer_orders()
            elif choice == 3:
                manage_purchase_orders()
            elif choice == 4:
                view_report()
            elif choice == 5:
                break
            elif choice not in range(1,6):
                print("Enter selections displayed only.")
                print("------------------------------------------------------------------------------------------------\n")

        except ValueError:
            print("Enter option NUMBER only.")
            print("------------------------------------------------------------------------------------------------\n")

#Functions for superuser and admin
def add_users():
    print("Add users")
    login_data = read_file(login_data_file)
    user_type = input("Enter user type (1 for Customer | 2 for Admin | 3 for Inventory Staff): ").strip()

    if user_type == "2":
        # Generate a username for Admin
        username = get_next_admin_username(login_data)
        print(f"Generated admin username: {username}")
    else:
        username = input("Enter username: ").strip()

    password = input("Enter password: ").strip()

    if user_type == "1":  # Customer
        if not (len(password) >= 8 and any(c.isupper() for c in password) and sum(c.isdigit() for c in password) >= 3):
            print("Customer password must be at least 8 characters long, including 1 UPPER CASE and 3 NUMBERS.")
            return
    elif user_type == "2":  # Admin
        if not (len(password) >= 10 and password.startswith("ADMIN@")):
            print("Admin password must be at least 10 characters long and start with 'ADMIN@'.")
            return
    elif user_type == "3":  # Inventory Staff
        if not (len(password) >= 8 and password.startswith("INV@") and sum(c.isdigit() for c in password) == 4):
            print("Inventory staff password must be at least 8 characters long, start with 'INV@' and followed by 4 numbers.")
            return

    # Automatically approve users added by superuser
    login_data.append([username, password, "Approved", user_type])
    write_file(login_data_file, login_data)
    print("User added successfully.")


def modify_user_personal_details():
    print("Modify User Personal Details")
    login_data = read_file(login_data_file)
    username = input("Enter the username of the user to modify: ").strip()
    
    for user in login_data:
        if user[0] == username:
            print("Current details:", user)
            
            while True:
                print("\nWhat do you want to change?")
                print("1. Username")
                print("2. Password")
                print("3. Approval Status")
                print("4. User Type")
                print("5. Nationality (Customers only)")
                print("6. IC/Passport Number (Customers only)")
                print("7. Phone Number (Customers only)")
                print("8. Registration Date")
                print("9. Exit")
                
                choice = input("Enter your choice: ").strip()
                
                if choice == "1":
                    new_username = input("Enter new username: ").strip()
                    user[0] = new_username if new_username else user[0]
                elif choice == "2":
                    new_password = input("Enter new password: ").strip()
                    user[1] = new_password if new_password else user[1]
                elif choice == "3":
                    new_status = input("Enter new approval status (Approved/Pending): ").strip()
                    user[2] = new_status if new_status else user[2]
                elif choice == "4":
                    new_user_type = input("Enter new user type (1 for Customer, 2 for Admin, 3 for Inventory Staff): ").strip()
                    user[3] = new_user_type if new_user_type else user[3]
                elif choice == "5" and user[3] == "1":
                    new_nationality = input("Enter new nationality: ").strip()
                    user[4] = new_nationality if new_nationality else user[4]
                elif choice == "6" and user[3] == "1":
                    new_ic_passport = input("Enter new IC/Passport Number: ").strip()
                    user[5] = new_ic_passport if new_ic_passport else user[5]
                elif choice == "7" and user[3] == "1":
                    new_phone_number = input("Enter new phone number: ").strip()
                    user[6] = new_phone_number if new_phone_number else user[6]
                elif choice == "8":
                    new_registration_date = input("Enter new registration date: ").strip()
                    user[7] = new_registration_date if new_registration_date else user[7]
                elif choice == "9":
                    break
                else:
                    print("Invalid choice or not applicable to this user type, please try again.")
            
            write_file(login_data_file, login_data)
            print("User details updated successfully.")
            return
    
    print("User not found.")

def disable_user_access():
    print("Disable User Access")
    login_data = read_file(login_data_file)
    username = input("Enter the username of the user to disable: ").strip()
    
    user_found = False
    updated_login_data = []

    for user in login_data:
        if user[0] == username:
            user_found = True
            print(f"Disabling user: {user[0]}")
        else:
            updated_login_data.append(user)

    if user_found:
        write_file(login_data_file, updated_login_data)
        print("User access disabled and user removed from the file successfully.")
    else:
        print("User not found.")

def inquiry_of_user_system_usage():
    print("Inquiry of User’s System Usage")
    user_activity_log = read_file(user_activity_log_file)
    username = input("Enter the username to inquire about: ").strip()
    
    found = False
    for log in user_activity_log:
        if log[0] == username:
            print("Activity:", log[1:])
            found = True
    
    if not found:
        print("No activity found for this user.")
    else:
        print("Inquiry completed.")

def verify_new_customer():
    print("Verify New Customer")
    login_data = read_file(login_data_file)
    
    # Filter and display only pending customers
    pending_customers = [user for user in login_data if user[3] == "1" and user[2] == "Pending"]
    
    if not pending_customers:
        print("No pending customers to verify.")
        return
    
    print("Pending Customers:")
    for user in pending_customers:
        print(f"Username: {user[0]}")
    
    # Ask for the username to verify
    username_to_verify = input("Enter the username of the customer to approve: ").strip()
    
    for user in login_data:
        if user[0] == username_to_verify and user[3] == "1" and user[2] == "Pending":
            user[2] = "Approved"  # Update status to "Approved"
            write_file(login_data_file, login_data)
            print(f"Customer '{username_to_verify}' has been approved.")
            return
    
    print("Customer not found or already approved.")


def CUSpurchase_order():
    print("Check customer order status")
    customer_data = read_file(customer_data_file)
    
    # Display all orders and their statuses
    for order in customer_data:
        print(f"Order ID: {order[0]}, Status: {order[4]}")
    
    # Check status of a specific order
    order_id = input("Enter Order ID to check status: ").strip()
    
    # Search for the specified order
    for order in customer_data:
        if order[0] == order_id:
            print(f"Order ID: {order[0]}, Status: {order[4]}")
            break
    else:
        print("Order ID not found.")

def repair_service():
    print("Repair/Service Order")
    repair_data = read_file(repair_data_file)
    
    # Display all repair/service orders and their statuses
    for repair in repair_data:
        print(f"Repair ID: {repair[0]}, Status: {repair[5]}")
    
    # Check status of a specific repair/service order
    repair_id = input("Enter Repair ID to check status: ").strip()
    
    # Search for the specified repair ID
    for repair in repair_data:
        if repair[0] == repair_id:
            print(f"Repair ID: {repair[0]}, Status: {repair[5]}")
            break
    else:
        print("Repair ID not found.")

def SUPpurchase_order():
    print("Purchase Order (SUPPLIER)")
    supplier_order_data = read_file(supplier_order_data_file) 
    
    # Display all supplier orders and their statuses
    for order in supplier_order_data:
        print(f"Order ID: {order[0]}, Status: {order[2]}")
    
    # Check status of a specific supplier order
    order_id = input("Enter Order ID to check status: ").strip()
    
    # Search for the specified order ID
    for order in supplier_order_data:
        if order[0] == order_id:
            print(f"Order ID: {order[0]}, Status: {order[2]}")
            break
    else:
        print("Order ID not found.")


def financial_report():
    print("Generating Financial Report...")
    
    # Sample financial data
    financial_data = {
        "Total Revenue": "RM10,000.00",
        "Total Expenses": "RM7,500.00",
        "Net Profit": "RM2,500.00"
    }
    
    print("\nFinancial Report")
    print("----------------")
    for key, value in financial_data.items():
        print(f"{key}: {value}")
    print("----------------\n")

def invoice_report():
    print("Generating Invoice Report...")

    invoice_data = read_file("invoices_data.txt")

    if not invoice_data:
        print("No invoices found.")
        return

    print("\nInvoice Report")
    print("---------------------------")
    total_amount = 0  # To calculate the total amount

    for record in invoice_data:
        invoice_id = record[0]
        customer_name = record[1]
        date = record[2]
        amount = float(record[3])  # Convert the amount to a floating-point number

        print(f"Invoice ID: {invoice_id}, Customer: {customer_name}, Date: {date}, Amount: RM {amount:.2f}")
        total_amount += amount  # Add the amount to the total

    print("---------------------------")
    print(f"Total Amount: RM {total_amount:.2f}")
    print("---------------------------\n")

def attendance_report():
    print("Generating Attendance Report...")

    log_data = read_file(user_activity_log_file)
    
    # Group logs by date and user
    attendance_data = {}
    for log in log_data:
        username, activity, timestamp = log
        date = timestamp.split(" ")[0]
        month_year = "-".join(date.split("-")[:2])
        
        if month_year not in attendance_data:
            attendance_data[month_year] = {}
        
        if username not in attendance_data[month_year]:
            attendance_data[month_year][username] = timestamp
    
    # Display attendance report by month and year
    for month_year, users in attendance_data.items():
        print(f"\nAttendance Report for {month_year}")
        print("-----------------")
        for username, first_login in users.items():
            print(f"Employee: {username}, Date: {first_login.split(' ')[0]}, Initial Login Time: {first_login.split(' ')[1]}")
        print("-----------------\n")


log_activity_file = "log_activity.txt"

def log_activity_report():
    """
    Displays the log of activity report.
    
    This function reads the log file and displays the content, which contains
    all logged activities in the system.
    """
    print("\nDisplaying the Log of Activity Report...\n")

    try:
        # Read and display the log entries
        with open(log_activity_file, "r") as file:
            log_entries = file.readlines()

        if log_entries:
            for entry in log_entries:
                print(entry.strip())
        else:
            print("No activities logged yet.")
    except FileNotFoundError:
        print("Log file not found. No activities have been logged yet.")

def log_activity(username, activity):
    """
    Logs the activity of a user.
    
    Parameters:
    - username: The username of the user performing the activity.
    - activity: A description of the activity performed.
    """
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"{timestamp} - {username} - {activity}\n"

    # Append the log entry to the log file
    with open(log_activity_file, "a") as file:
        file.write(log_entry)

    print(f"Activity logged: {log_entry.strip()}")

def financial_report():
    print("Generating Financial Report...")
    
    # Sample financial data
    financial_data = {
        "Total Revenue": "RM10,000.00",
        "Total Expenses": "RM7,500.00",
        "Net Profit": "RM2,500.00"
    }
    
    print("\nFinancial Report")
    print("----------------")
    for key, value in financial_data.items():
        print(f"{key}: {value}")
    print("----------------\n")


def attendance_report():
    print("Generating Attendance Report...")
    
    # Read the user activity log
    log_data = read_file(user_activity_log_file)
    
    # Process attendance data
    attendance_data = {}
    for log in log_data:
        if len(log) == 3:  # Ensure log entry has 3 elements
            username, activity, timestamp = log
            date = timestamp.split(" ")[0]  # Extract date part from the timestamp
            
            if activity == "Logged in":
                # Record the first login of the day
                if username not in attendance_data or date < attendance_data[username]["Date"]:
                    attendance_data[username] = {"Date": date, "Time": timestamp.split(" ")[1]}
    
    # Display the attendance report by month and year
    report_month = input("Enter the month (MM): ")
    report_year = input("Enter the year (YYYY): ")
    
    print(f"\nAttendance Report for {report_month}-{report_year}")
    print("-----------------")
    for username, info in attendance_data.items():
        if info["Date"].startswith(f"{report_year}-{report_month}"):
            print(f"Employee: {username}, Date: {info['Date']}, Initial Login Time: {info['Time']}")
    print("-----------------\n")

def main():
    # Welcome message
    welcome = """`````````````````````````````````````````````````````````````````````````````````````````````````
                                     Welcome to Main Menu
````````````````````````````````````````````````````````````````````````````````````````````````"""
    print(welcome)

    while True:
        print("\n1. Login")
        print("2. Sign Up")
        print("3. Exit")
        
        choice = input("Enter choice: ").strip()
        
        if choice == "1":
            login()
        elif choice == "2":
            sign_up()
        elif choice == "3":
            break
        else:
            print("Invalid choice!")

if __name__ == "__main__":
    main()



        




