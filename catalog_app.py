from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)
# IMPLEMENT BREAD CRUMBS AS A GLOBAL STACK
# BEWARE OF MANUALLY TYPED URLS
def connect():
    """Connect to the PostgreSQL database.  Returns a database connection."""
    DB = psycopg2.connect("dbname=catalog")
    dbcursor = DB.cursor()
    return DB, dbcursor

@app.route('/')
@app.route('/catalog/')
def categories():
    DB, dbcursor = connect()
    querystring = "SELECT * FROM categories;"
    dbcursor.execute(querystring)
    categories = [i[0] for i in dbcursor.fetchall()]

    DB.close()
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
def itemDescription(item_name):
    DB, dbcursor = connect()
    querystring = "SELECT * FROM items WHERE name = %s;"
    dbcursor.execute(querystring, (item_name,))
    item, description = dbcursor.fetchone()
    DB.close()
    return render_template(
        'item_page.html', item=item, description=description)

@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def itemEdit(item_name):

    if request.method == 'POST':
        DB, dbcursor = connect()
        # update item name last or else you could lose the way to look up the
        # item before you can update everything else
        if request.form['description']:
            desc_update = request.form['description']
            # update the description
            querystring = "UPDATE items SET description=%s WHERE name=%s"
            dbcursor.execute(querystring, (desc_update, item_name))

        # if request.form['categories']
        # will likely have to check which categories are already valid for the
        # item and remove any missing from the form and add any missing that are
        # on the form

        if request.form['name']:
            item_update = request.form['name']
            # update the item; this cascades to dependent table
            querystring = "UPDATE items SET name=%s WHERE name=%s"
            dbcursor.execute(querystring, (item_update, item_name))

        DB.commit()
        DB.close()
        return 'Under construction! <a href='+url_for('categories')+'>Home</a>'
    else:
        DB, dbcursor = connect()
        # fetch the description to display as form placeholder
        querystring = "SELECT * FROM items WHERE name = %s;"
        dbcursor.execute(querystring, (item_name,))
        item, description = dbcursor.fetchone()

        # fetch the categories to display as checkboxes
        querystring = "SELECT name FROM categories ORDER BY name;"
        dbcursor.execute(querystring)
        categories = dbcursor.fetchall() # list of tuples
        categories = list(zip(*categories)[0]) # make a flat list
        cat_table = htmlRowsList(categories, min(5, len(categories)))

        # fetch the categories that this item belongs to
        querystring  = "SELECT category FROM category_items WHERE item=%s;"
        dbcursor.execute(querystring, (item_name,))
        itemcategories = dbcursor.fetchall() # list of tuples
        itemcategories = list(zip(*itemcategories)[0]) # make a flat list
        DB.close()
        return render_template(
            'item_edit.html', item=item, description=description,
            categorytable=cat_table, itemcategories=itemcategories)

def htmlRowsList(flatlist, numrows):
    """Converts a flat list into list of sublists ordered for an HTML table."""
    return [flatlist[i::numrows] for i in range(0, numrows)]


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
