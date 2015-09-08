from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
# IMPLEMENT BREAD CRUMBS AS A GLOBAL STACK
# BEWARE OF MANUALLY TYPED URLS
@app.route('/')
@app.route('/catalog/')
def categories():
    categories = getCategoriesList()
    return render_template('catalog_page.html', categories=categories)

@app.route('/catalog/<string:category_name>/items')
def categoryItems(category_name):
    DB, dbcursor = connect()
    querystring = "SELECT item FROM category_items WHERE category = %s;"
    dbcursor.execute(querystring, (category_name,))
    items = [i[0] for i in dbcursor.fetchall()] # list of tuples into a list

    DB.close()
    return render_template(
        'category_page.html', category=category_name, items=items)

@app.route('/catalog/<string:item_name>')
def itemDetails(item_name):
    description = getItemDescription(item_name)

    itemcategories = getItemCategories(item_name)
    cat_table = htmlTable(itemcategories, min(5, len(itemcategories)))

    return render_template(
        'item_page.html', item=item_name, description=description,
        itemcattable=cat_table)

@app.route('/catalog/newitem', methods=['GET', 'POST'])
def itemNew():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        categories = request.form.getlist('categories')

        # check if all form elements filled and if not redirect

        DB, dbcursor = connect()
        querystring = "INSERT INTO items VALUES (%s, %s);"
        params = (name, description)
        dbcursor.execute(querystring, params)

        querystring = "INSERT INTO category_items VALUES (%s, %s);"
        for i in categories:
            params = (i, name)
            dbcursor.execute(querystring, params)

        DB.commit()
        DB.close()
        return 'Under construction! <a href='+url_for('categories')+'>Home</a>'
    else: # the request method is GET
        categories = getCategoriesList()
        cat_table = htmlTable(categories, min(5, len(categories)))
        return render_template('item_new.html', categorytable=cat_table)

@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def itemEdit(item_name):

    if request.method == 'POST':
        DB, dbcursor = connect()
        # update item name last or else you could lose the way to look up the
        # item before you can update everything else
        if request.form['description']:
            desc_update = request.form['description']
            # update the description
            querystring = "UPDATE items SET description=%s WHERE name=%s;"
            dbcursor.execute(querystring, (desc_update, item_name))

        if request.form['categories']:
            formcategories = request.form.getlist('categories')
            itemcategories = getItemCategories(item_name)

            toadd = [i for i in formcategories if i not in itemcategories]
            toremove = [i for i in itemcategories if i not in formcategories]

            querystring = "INSERT INTO category_items VALUES (%s, %s);"
            for i in toadd:
                params = (i, item_name)
                dbcursor.execute(querystring, params)

            querystring = "DELETE FROM category_items WHERE category=%s AND item=%s;"
            for i in toremove:
                params = (i, item_name)
                dbcursor.execute(querystring, params)

        if request.form['name']:
            item_update = request.form['name']
            # update the item; this cascades to dependent table
            querystring = "UPDATE items SET name=%s WHERE name=%s;"
            dbcursor.execute(querystring, (item_update, item_name))

        DB.commit()
        DB.close()
        return 'Under construction! <a href='+url_for('categories')+'>Home</a>'
    else: # the request method is GET
        # fetch the item description and associated categories
        description = getItemDescription(item_name)
        itemcategories = getItemCategories(item_name)

        # fetch the categories as a table to display as checkboxes
        categories = getCategoriesList()
        cat_table = htmlTable(categories, min(5, len(categories)))

        return render_template(
            'item_edit.html', item=item_name, description=description,
            categorytable=cat_table, itemcategories=itemcategories)

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    DB = psycopg2.connect("dbname=catalog")
    dbcursor = DB.cursor()
    return DB, dbcursor

def getItemDescription(item_name):
    """Returns the item description and the categories it belongs to."""
    DB, dbcursor = connect()
    # fetch the description
    querystring = "SELECT description FROM items WHERE name = %s;"
    dbcursor.execute(querystring, (item_name,))
    description = dbcursor.fetchone()[0]

    DB.close()
    return description

def getItemCategories(item_name):
    """Returns the categories that this item blongs to in a list."""
    DB, dbcursor = connect()
    querystring  = "SELECT category FROM category_items WHERE item=%s;"
    dbcursor.execute(querystring, (item_name,))
    itemcategories = [i[0] for i in dbcursor.fetchall()] # flatten list of tuple

    DB.close()
    return itemcategories

def getCategoriesList():
    """Retrieves a list of all available categories."""
    DB, dbcursor = connect()
    querystring = "SELECT name FROM categories ORDER BY name;"
    dbcursor.execute(querystring)
    categories = [i[0] for i in dbcursor.fetchall()] # flatten list of tuple

    DB.close()
    return categories

def htmlTable(flatlist, numrows):
    """Converts a flat list into list of sublists ordered for an HTML table."""
    return [flatlist[i::numrows] for i in range(0, numrows)]

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
