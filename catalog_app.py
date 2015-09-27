from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

#The following global variables are intended as constants
QUERY_ITEM_ONE = "SELECT name FROM items WHERE name=%s"
QUERY_ITEM_DESC = "SELECT description FROM items WHERE name=%s;"
QUERY_ITEM_CAT = "SELECT category FROM category_items WHERE item=%s;"
QUERY_ALL_CAT = "SELECT name FROM categories ORDER BY name;"

app = Flask(__name__)
# IMPLEMENT BREAD CRUMBS AS A GLOBAL STACK
# BEWARE OF MANUALLY TYPED URLS
@app.route('/')
@app.route('/catalog/')
def categories():
    categories = getDBvalues(QUERY_ALL_CAT)
    return render_template('catalog_page.html', categories=categories)

@app.route('/catalog/<string:category_name>/items')
def categoryItems(category_name):
    querystring = "SELECT item FROM category_items WHERE category = %s;"
    items = getDBvalues(querystring, category_name)

    return render_template(
        'category_page.html', category=category_name, items=items)

@app.route('/catalog/items')
def itemAll():
    """Displays all items and their associated categories"""
    querystring = "SELECT name FROM items;"
    allitems = getDBvalues(querystring)

    itemcatlist = [] # list of list of categories for each item
    for i in allitems:
        itemcatlist.append(getDBvalues(QUERY_ITEM_CAT, i)) # even if i is an empty

    itemcatpairs = zip(allitems, itemcatlist)

    return render_template('item_all.html', itemcatpairs=itemcatpairs)

@app.route('/catalog/<string:item_name>')
def itemDetails(item_name):
    description = getDBvalues(QUERY_ITEM_DESC, item_name, True)
    itemcategories = getDBvalues(QUERY_ITEM_CAT, item_name)
    cat_table = htmlTable(itemcategories, min(5, len(itemcategories)))

    return render_template(
        'item_page.html', item=item_name, description=description,
        itemcattable=cat_table)

@app.route('/catalog/new', methods=['GET', 'POST'])
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

        # check if item name is unique
        if getDBvalues(QUERY_ITEM_ONE, name):
            flash("Error. An item with that name already exists.")
            return redirect(url_for('itemNew'))

        # only reach here if all form fields filled in and name unique
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
        categories = getDBvalues(QUERY_ALL_CAT)
        cat_table = htmlTable(categories, min(5, len(categories)))
        return render_template('item_new.html', categorytable=cat_table)

@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def itemEdit(item_name):
    if request.method == 'POST':
        # check if at least one category checked or else try again
        if not request.form.getlist('categories'):
            flash("Error. At least one category must be checked.")
            return redirect(url_for('itemEdit', item_name=item_name))

        # gather other form elements and check for unique item name
        item_update = request.form['name']
        desc_update = request.form['description']
        if item_update: # only check if the form was not blank
            if getDBvalues(QUERY_ITEM_ONE, item_update):
                flash("Error. An item with that name already exists.")
                return redirect(url_for('itemEdit', item_name=item_name))
        # else the value is blank or otherwise fine

        # only reach here if the form and values entered are error-free
        # update item name last or else you could lose the way to look up the
        #   item before you can update everything else
        DB, dbcursor = connect()

        # update categories if necessary
        formcategories = request.form.getlist('categories')
        itemcategories = getDBvalues(QUERY_ITEM_CAT, item_name)

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
        if desc_update:
            querystring = "UPDATE items SET description=%s WHERE name=%s;"
            params = (desc_update, item_name)
            dbcursor.execute(querystring, params)

        # update item name if form field is filled in; cascades dependent table
        if item_update:
            querystring = "UPDATE items SET name=%s WHERE name=%s;"
            params = (item_update, item_name)
            dbcursor.execute(querystring, params)

        DB.commit()
        DB.close()

        # Provide a message upon next page load indicating success
        flash("Item has been updated.")
        return redirect(url_for('categories'))
    else: # the request method is GET
        # fetch the item description and associated categories
        description = getDBvalues(QUERY_ITEM_DESC, item_name, True)
        itemcategories = getDBvalues(QUERY_ITEM_CAT, item_name)

        # fetch the categories as a table to display as checkboxes
        categories = getDBvalues(QUERY_ALL_CAT)
        cat_table = htmlTable(categories, min(5, len(categories)))

        return render_template(
            'item_edit.html', item=item_name, description=description,
            categorytable=cat_table, itemcategories=itemcategories)

@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
def itemDelete(item_name):
    if request.method == 'POST':
        # check that the item exists
        if not getDBvalues(QUERY_ITEM_ONE, item_name):
            flash("The item you tried to delete doesn't exist.")
            return redirect(url_for('categories'))
        else: # the item exists. delete it
            DB, dbcursor = connect()
            querystring = "DELETE FROM items WHERE name=%s;"
            params = (item_name,)
            dbcursor.execute(querystring, params)
            DB.commit()
            DB.close()

        flash(item_name + " was deleted.")
        return redirect(url_for('categories'))
    else: # the request method is GET
        if not getDBvalues(QUERY_ITEM_ONE, item_name):
            flash("The item you tried to delete doesn't exist.")
            return redirect(url_for('categories'))
        else:
            flash("You are about to delete the following item.")
        return render_template('item_delete.html', item=item_name)

@app.route('/catalog/categoriesEdit', methods=['GET', 'POST'])
def categoriesEdit():
    if request.method == 'POST':
        all_cat = getDBvalues(QUERY_ALL_CAT) # all categories
        keep_cat = request.form.getlist('categories') # categories to keep
        remove_cat = [i for i in all_cat if i not in keep_cat]

        add_cat = request.form['add_categories'] # manually typed categories
        add_cat = add_cat.split('\n') # make new lines into a list
        add_cat = [i.strip() for i in add_cat] # trailing/leading whitespace
        add_cat = set(add_cat) # unique entries only
        if '' in add_cat: add_cat.remove('') # remove empty string

        # Check that categories to be added don't already exist
        for i in add_cat:
            if i in all_cat:
                flash("One or more of the categories to add already exists.")
                return redirect(url_for('categoriesEdit'))

        # Only reach this point if typed categories are unique (or empty)
        DB, dbcursor = connect()
        querystring = "DELETE FROM categories WHERE name=%s;"
        for i in remove_cat:
            params = (i,)
            dbcursor.execute(querystring, params)

        querystring = "INSERT INTO categories VALUES (%s);"
        for i in add_cat:
            params = (i,)
            dbcursor.execute(querystring, params)

        DB.commit()
        DB.close()
        flash("Categories removed or added accordingly.")
        return redirect(url_for('categories'))
    else: # request method is GET
        categories = getDBvalues(QUERY_ALL_CAT)
        cat_table = htmlTable(categories, min(5, len(categories)))
        return render_template('category_edit.html', categorytable=cat_table)

def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    DB = psycopg2.connect("dbname=catalog")
    dbcursor = DB.cursor()
    return DB, dbcursor

def getDBvalues(querystring, params=None, returnOne=False):
    """Connect to database, run query, return values as list. Options available"""
    DB, dbcursor = connect()
    if params:
        params = makeTuple(params)
        dbcursor.execute(querystring, params)
    else:
        dbcursor.execute(querystring)

    if returnOne: # a non-list expected
        result = dbcursor.fetchone()
        # if the result is a tuple with just 1 value, flatten
        if type(result) is tuple and len(result) == 1:
            result = result[0]
    else: # flat list expected if results are len==1 tuples
        result = dbcursor.fetchall()
        # check if results are tuples with just 1 value
        if len(result) > 0 and len(result[0]) <= 1:
            result = [i[0] for i in result] # flatten the list
    DB.close()
    return result

def makeTuple(value):
    """Take a value of any of several types and return that value as a tuple"""
    if isinstance(value, (int, basestring)):
        atuple = (value,)
    else:
        atuple = tuple(value)
    return atuple

def htmlTable(flatlist, numrows):
    """Converts a flat list into list of sublists ordered for an HTML table."""
    return [flatlist[i::numrows] for i in range(0, numrows)]

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
