from flask import Flask, render_template, request, redirect, url_for, flash
import psycopg2

app = Flask(__name__)

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
    print '***'
    print items
    print '***'

    DB.close()
    return render_template(
        'category_page.html', category=category_name, items=items)

@app.route('/catalog/<string:item_name>')
def itemDescription(item_name):
    # project guide indicates category name is not part of URL but keeping for now
    # because it could help to create a back button
    # need to return an error page when manually typed URL contains an unknown
    # catalog, item, or catalog/item pair
    # tbd
    # assuming catalog/item pair exists
    DB, dbcursor = connect()
    querystring = "SELECT * FROM items WHERE name = %s;"
    dbcursor.execute(querystring, (item_name,))
    item, description = dbcursor.fetchone()
    DB.close()
    return render_template(
        'item_page.html', item=item, description=description)

@app.route('/catalog/<string:item_name>/edit', methods=['GET', 'POST'])
def itemEdit(item_name):
    # need to return an error page when manually typed URL contains an unknown
    # catalog, item, or catalog/item pair
    # tbd
    # assuming catalog/item pair exists...

    # fetch the item in question
    DB, dbcursor = connect()
    if request.method == 'POST':
        # update the description before the item name or else you could lose the
        # way to look up the item before you can update the description
        if request.form['description']:
            desc_update = request.form['description']
            # update the description
            querystring = "UPDATE items SET description=%s WHERE name=%s"
            dbcursor.execute(querystring, (desc_update, item_name))

        if request.form['name']:
            item_update = request.form['name']
            # update the item; this cascades to dependent table
            querystring = "UPDATE items SET name=%s WHERE name=%s"
            dbcursor.execute(querystring, (item_update, item_name))

        DB.commit()
        DB.close()
        return 'Under construction! <a href='+url_for('categories')+'>Home</a>'
    else:
        # fetch the description to display as form placeholder
        querystring = "SELECT * FROM items WHERE name = %s;"
        dbcursor.execute(querystring, (item_name,))
        item, description = dbcursor.fetchone()
        DB.close()
        return render_template(
            'item_edit.html', item=item, description=description)


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
