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
        formgood = name and description and categories
        if not formgood:
            flash("Error. All form fields should have a value.")
            return redirect(url_for('itemNew'))

        # only reach here if all form fields filled in
        DB, dbcursor = connect()

        # create item
        querystring = "INSERT INTO items VALUES (%s, %s);"
        params = (name, description)
        dbcursor.execute(querystring, params)

        # associate item with selected categories
        querystring = "INSERT INTO category_items VALUES (%s, %s);"
        for i in categories:
            params = (i, name)
            dbcursor.execute(querystring, params)

        DB.commit()
        DB.close()
        flash("Item has been created.")
        return redirect(url_for('categories'))
    else: # the request method is GET
        # get all possible categories for the checkboxes stored as a table
        categories = getCategoriesList()
        cat_table = htmlTable(categories, min(5, len(categories)))
        return render_template('item_new.html', categorytable=cat_table)

@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def itemEdit(item_name):

    if request.method == 'POST':
        # check if at least one category checked or else try again
        if not request.form.getlist('categories'):
            flash("Error. At least one category must be checked.")
            return redirect(url_for('itemEdit', item_name=item_name))

        # only reach here if at least one category checked
        # update item name last or else you could lose the way to look up the
        #   item before you can update everything else
        DB, dbcursor = connect()

        # update categories if necessary
        formcategories = request.form.getlist('categories')
        itemcategories = getItemCategories(item_name)

        # compare the two lists and find what needs to be added or removed
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

        # update item description if form field is filled in
        desc_update = request.form['description']
        if desc_update:
            querystring = "UPDATE items SET description=%s WHERE name=%s;"
            params = (desc_update, item_name)
            dbcursor.execute(querystring, params)

        # update item name if form field is filled in; cascades dependent table
        item_update = request.form['name']
        if item_update:
            querystring = "UPDATE items SET name=%s WHERE name=%s;"
            params = (item_update, item_name)
            dbcursor.execute(querystring, params)

        DB.commit()
        DB.close()
        flash("Item has been updated.")
        return redirect(url_for('categories'))
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
