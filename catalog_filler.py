# this file populates the catalog database with sample entries

import psycopg2


def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    DB = psycopg2.connect("dbname=catalog")
    dbcursor = DB.cursor()
    return DB, dbcursor

# define sample values for categories, item, descriptions
categories = ["Electronics", "Kitchen", "Video games", "Luggage", "Camera",
    "Software title"]
items = [
    "Sony PlayStation 4",
    "Logitech UE Megaboom",
    "KitchenAid stand mixer",
    "ScoopTHAT! II Ice Cream Scoop",
    "The Witcher III The Wild Hunt",
    "Case Logic Griffith Park backpack",
    "Case Logic Reflexion cross-body bag",
    "Sony RX100 MK IV",
    "Turbo Tax 2016 Federal",
    "Microsoft Windows 10 OEM Installation"]
descriptions = [
    "The latest video game system from Sony.",
    "Incredible sound booms via bluetooth connections of up to 100 ft away.",
    "A must for every baker's kitchen.",
    "Non-electric, heat-conductive design cuts through ice cream like butter.",
    "Journey far and wide as a mutated monster hunter in search of his star-crossed adopted daughter",
    "Black and green accents with compartments for laptop, tablet, and power supply.",
    "Adjustable storage walls and a tablet pocket keep you organized and stylish.",
    "This fourth iteration introduces 4k video recording with the same great superior optics and rotating view screen to make the best handheld camera.",
    "Your tax accountant in a box.",
    "All the power of the latest Microsoft operating system, none of the packaging"]
item_desc = zip(items, descriptions) # combine for later easy DB writes

# define category/item pairs. One item may belong to multiple categories.
category_pairing = [0, 0, 0, 0, 1, 1, 2, 2, 3, 3, 4, 4, 5, 5, 5]
item_pairing =     [0, 1, 2, 7, 2, 3, 0, 4, 5, 6, 6, 7, 4, 8, 9]

category_items = []
for i in zip(category_pairing, item_pairing):
    category_items.append((categories[i[0]], items[i[1]]))

# populate DB
DB, dbcursor = connect()

# clear the database in case it already containes values
dbcursor.execute("DELETE FROM category_items;")
dbcursor.execute("DELETE FROM categories;")
dbcursor.execute("DELETE FROM items;")
DB.commit()

querystring = "INSERT INTO categories VALUES (%s);"
for i in categories:
    i = (i,) # data to insert must be a tuple
    dbcursor.execute(querystring, i)

querystring = "INSERT INTO items VALUES (%s, %s);"
for i in item_desc:
    dbcursor.execute(querystring, i)

querystring = "INSERT INTO category_items VALUES (%s, %s);"
for i in category_items:
    dbcursor.execute(querystring, i)

DB.commit()
DB.close()
