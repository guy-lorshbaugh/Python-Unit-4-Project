from collections import OrderedDict
import csv
import re
import os
import datetime

from peewee import *

inventory = SqliteDatabase('inventory.db')
stars1 = "*" * 40
trim = re.compile(r'[^\d]+')


def clear():
    """Clears the screen."""
    os.system("cls" if os.name == "nt" else "clear")


class Product(Model):
    product_id = AutoField(primary_key=True)
    product_name = CharField(unique=True)
    product_quantity = IntegerField(default=0, unique=False)
    product_price = IntegerField(default=0, unique=False)
    date_updated = DateField(null=True)

    class Meta:
        database = inventory


def initialize():
    """Create the database and the table if they don't already exist."""
    inventory.connect()
    inventory.create_tables([Product], safe=True)


def process_data():
    """Cleans CSV data and enters it into the database."""
    with open('inventory.csv', newline='') as inventory:
        inv_list = []
        reader = csv.reader(inventory)
        columns = next(reader)
        for row in reader:
            trim = re.compile(r'[^\d]+')
            date = datetime.datetime.strptime(row[3], "%m/%d/%Y")
            inv_list.append(row)
        return inv_list

def populate(table):
    for row in table:
        trim = re.compile(r'[^\d]+')
        date = datetime.datetime.strptime(row[3], "%m/%d/%Y")
        try:
            Product.create(
                    product_name=row[0],
                    product_price=trim.sub('',row[1]),
                    product_quantity=int(row[2]),
                    date_updated=date
            )
        except IntegrityError:
            prev_date = Product.select().where(Product.product_name == row[0]).get()
            if prev_date.date_updated <= date.date():
                prev_date.product_price = trim.sub('', row[1])
                prev_date.product_quantity = int(row[2])
                prev_date.date_updated = date.date()
                prev_date.save()
            else: pass

def main_menu():
    """Show the menu"""
    choice = None
    # clear()

    while choice != 'q':
        clear()
        print(f"""
    {stars1}
    Inventory for The Storensons' Store!
    {stars1}
        """)        
        print("""
Please make a selection from the menu below:""")
        
        for key, value in menu.items():
            print("""
    {}) {}""".format(key, value.__doc__))
        print()
        choice = input("Your Selection:  ").lower().strip()
        try:
            if choice not in menu:
                raise ValueError
        except ValueError:
            print("\nThe only options available are v/b/a/q, please enter one of these.")
        else:
            if choice in menu:
                # clear()
                menu[choice]()
                break



def view_product():
    """View information on a product"""
    clear()
    choice = 0
    again = None
    range = Product.select().order_by(Product.product_id.desc()).get()
    print(f"""
    {stars1}
            View Product Details
    {stars1}""")
    while again != "n":
        
        choice = input("""
Please enter the Product ID:  """).lower().strip()
        try:
            id = Product.select().where(Product.product_id == choice).get()
        except:
            print(f"\nSelection out of range.  There are {range} items in inventory.\nPlease enter only numeral values.\n")
            choice = 0
        else:
            print(f"""
            Name:  {id.product_name}
            Price:  {id.product_price}
            {id.product_quantity} in Stock
            Entry Date: {id.date_updated}
            """)
        again = input("View another Product? (y/n)  ").lower().strip()
    main_menu()


def add_product():
    """Add a product to the inventory"""
    clear()
    again = None
    print(f"""
    {stars1}
                 Add a Product
    {stars1}
    """)
    while again != "n":
        name = input("Enter the product name:  ")
        quantity = input("Enter the number of available units:  ")
        try:
            quantity == int(quantity)
        except:
            print("\nPlease enter only numeral values for quantity.\n")
            continue
        price = input("Enter the price in cents.  (e.g., $12.99 = 1299):  ")
        try:
            price == int(price)
        except:
            print("\nPlease enter only numeral values for price.\n")
            continue
        date = datetime.datetime.now().date().strftime('%m/%d/%Y')
        inv_list.append([name, price, quantity, date])
        populate(inv_list)
        again = input("\n--- Inventory Updated ---\n\nAdd another item? (y/n)  ")
        print()
    main_menu()


def full_view():
    """View the full store inventory"""
    clear()
    print(f"""

    {stars1}
                Current Inventory
    {stars1}
    """)
    for item in Product.select():
        print(f"- {item.product_name}, {item.product_quantity}, {item.product_price}, {item.date_updated}")
    back = input("\nWould you like to return to the main menu? (y/n)  ")
    if back != "n":
        main_menu()
    else:
        quit()

def make_backup():
    """Make a backup of the inventory database"""
    clear()
    back = None
    with open('backup.csv', 'w', newline='\n') as backup:
        wr = csv.writer(backup)
        wr.writerow(["product_name","product_price","product_quantity","date_updated"])
        for row in inv_list:
            wr.writerow(row)
    print(f"""
    {stars1}
                Backup Successful!
    {stars1}
    """)
    back = input("Would you like to return to the main menu? (y/n)  ")
    if back != "n":
        main_menu()
    else:
        quit()


def quit():
    """Quit"""
    print(f"""
    {stars1}
         You are an Inventory Wizard!!
               Have a great day!
    {stars1}
    """)
    exit()

menu = OrderedDict([
        ('v', view_product),
        ("e", full_view),
        ('a', add_product),
        ('b', make_backup),
        ('q', quit)
    ])

if __name__ == "__main__":
    print(f"""

    {stars1}
                  Loading ...
    {stars1}
    """)
    initialize()
    inv_list = process_data()
    populate(inv_list)
    main_menu()
