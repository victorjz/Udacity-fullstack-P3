from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import psycopg2

#The following global variables are intended as constants
QUERY_ITEM_ONE = "SELECT * FROM items WHERE name=%s;"
QUERY_ITEM_DESC = "SELECT description FROM items WHERE name=%s;"
QUERY_ITEM_CAT = "SELECT category FROM category_items WHERE item=%s;"
QUERY_ALL_CAT = "SELECT name FROM categories ORDER BY name;"
ITEM_FIELDS = ('name', 'description')
CLIENT_ID = "635118461401-b9i2jr946sit8rlh0qfd6vbbbq8hr04o.apps.googleusercontent.com"

# imports for logging in and anti forgery
from flask import session as login_session
import random
import string

# imports for logging in callback
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError, OAuth2Credentials
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)
@app.route('/')
@app.route('/catalog/')
def categories():
    """Function associated with home page. Displays category links to items"""
    categories = getDBvalues(QUERY_ALL_CAT)
    return render_template('catalog_page.html', categories=categories)

@app.route('/catalog.json')
def catalogJSON():
    """Present page of all items in JSON format"""
    # get all items, descriptions, and categories into a dictionary
    itemdictlist = getItemCategoriesDict()
    return jsonify(Items=itemdictlist)

# DEBUG function
@app.route('/check')
def check():
    return 'hello'

# Create anti-forgery state token
# borrowed from Udacity
@app.route('/login')
def showLogin():
    """Creates a cross-site anti-forgery key and presents the login page.

    This code borrowed directly from the Udacity course.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html')

@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Checks authentication of login and updates the login state

    This code borrowed directly from Udacity course."""
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials.to_json() # added to_json
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("You are now logged in as %s" % login_session['username'])
    print "done!"
    return output

@app.route('/gdisconnect')
def gdisconnect():
    """Properly disconnects from Google login service; redirects to home page.

    This code borrowed directly from Udacity course.
    """
    # Only disconnect a connected user.
    credentials = login_session.get('credentials')
    if credentials is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    credentials = OAuth2Credentials.from_json(credentials) # convert
    access_token = credentials.access_token
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print result
    if result['status'] == '200':
        # Reset the user's sesson.
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']

        # Changed the following lines. Instead of displaying a new page,
        # redirect the user back to the home page with a message
        flash("Log out successful.  See you next time.")
        response = make_response(redirect(url_for('categories')))
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        # For whatever reason, the given token was invalid.
        # Changed the following lines. Instead of displaying a new page,
        # redirect the user back to the home page with a message
        flash("Failed to revoke token for given user.")
        response = make_response(redirect(url_for('categories')))
        response.headers['Content-Type'] = 'application/json'
        return response

@app.route('/catalog/<string:category_name>/items')
def categoryItems(category_name):
    """Presents a list of items for the associated category.

    Args:
      category_name: String. Name of the category previously clicked.
    """
    querystring = "SELECT item FROM category_items WHERE category = %s;"
    items = getDBvalues(querystring, category_name)

    return render_template(
        'category_page.html', category=category_name, items=items)

@app.route('/catalog/items')
def itemAll():
    """Displays all items and their associated categories as a table of links"""
    # get all items, descriptions, and categories into a dictionary
    itemdictlist = getItemCategoriesDict()

    return render_template('item_all.html', items=itemdictlist)

@app.route('/catalog/<string:item_name>')
def itemDetails(item_name):
    """Displays the information relating to all the item detail fields

    Args:
      item_name: String. The name of the item clicked on the previous page.
    """
    itemresult = getDBvalues(QUERY_ITEM_ONE, item_name, True)
    if not itemresult:
        flash("The item for which you're trying to view details doesn't exist.")
        return redirect(url_for('categories'))
    itemcategories = getDBvalues(QUERY_ITEM_CAT, item_name)
    cat_table = htmlTable(itemcategories, min(5, len(itemcategories)))

    # create the dictionary
    itemdict = dict(zip(ITEM_FIELDS, itemresult))

    return render_template(
        'item_page.html', item=itemdict, itemcattable=cat_table)

@app.route('/catalog/new', methods=['GET', 'POST'])
def itemNew():
    """Displays a form for a new item or updates the database with a new item.

    Behavior varies according to http method:
      GET: presents a form that a user can fill out to define a new item
      POST:  inserts the item defined by the form into the database
    """
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
    """Displays a form to update an item or updates the item in the database

    Behavior varies according to http method
      GET: Presents the form that can be used to update item details
      POST: Takes values from the form and updates the item in the database

    Args:
      item_name: String. The name of the item on the page before clicking edit.
    """
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
        itemresult = getDBvalues(QUERY_ITEM_ONE, item_name, True)
        # check if the item exists
        if not itemresult:
            flash("The item you tried to edit doesn't exist.")
            return redirect(url_for('categories'))

        # create the dictionary and add associated categories
        itemdict = dict(zip(ITEM_FIELDS, itemresult))
        itemdict['categories'] = getDBvalues(QUERY_ITEM_CAT, item_name)

        # fetch the categories as a table to display as checkboxes
        categories = getDBvalues(QUERY_ALL_CAT)
        cat_table = htmlTable(categories, min(5, len(categories)))

        return render_template(
            'item_edit.html', item=itemdict, categorytable=cat_table)

@app.route('/catalog/<string:item_name>/delete', methods=['GET', 'POST'])
def itemDelete(item_name):
    """Presents confirmation page to delete an item or deletes the item in the
    database

    Behavior varies according to http method
      GET: Displays a page with the option to confirm deletion of the item
      POST: Deletes the item in the database and redirects to home

    Args:
      item_name: String. The name of the item on the page before clicking edit.
    """
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
            return render_template('item_delete.html', item=item_name)

@app.route('/catalog/categoriesEdit', methods=['GET', 'POST'])
def categoriesEdit():
    """Presents a form to add or remove categories or performs those functions
    in the database

    Behavior varies according to http method
      GET: Shows a form to remove categories via checkbox or manually type in
        names of new categories
      POST: Performs adding or removing categories in the database according
        to the form
    """
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
    """Connect to database, run query, return values as list. Options available

    Args:
      querystring: A string representing an SQL query
      params: Optional. May be a tuple or a singular value. If provided, runs
        the query with parameters
      returnOne: Optional. If not provided or False, provides results in a
      list. If True, provides the first result as a singular value.

    Returns:
      The results of running the query which may be altered by the value of
      returnOne, see above.
    """

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
    """Take a value of any of several types and return that value as a tuple

    Args:
      value: A value of any type.

    Returns:
      The same value contained in a tuple. No change if the value is already a
      tuple.
    """
    # values of these types fail a direct conversion to tuple.
    if isinstance(value, (int, basestring)):
        atuple = (value,)
    else: # any other kind of value can be converted
        atuple = tuple(value)
    return atuple

def getItemCategoriesDict():
    """Returns a dictionary of items and their fields for easy function argument
    passing
    """

    # get all items and descriptions into a dictionary
    querystring = "SELECT * FROM items;"
    allitems = getDBvalues(querystring)
    itemdictlist = [dict(zip(ITEM_FIELDS, i)) for i in allitems]

    # list of tuples of category then item, in that order
    catitempairs = getDBvalues("SELECT * FROM category_items;")

    # insert into dictionary list of categories for each item
    # c[0] is the category and c[1] is the item name
    for i in itemdictlist:
        i['categories'] = [c[0] for c in catitempairs if i['name']==c[1]]

    return itemdictlist

def htmlTable(flatlist, numrows):
    """Converts a flat list into list of sublists ordered for an HTML table.

    This is used particularly for passing a list of categories to a page that
    will display them in a table. This arranges the values into the right order
    for an HTML table.

    Args:
      flatlist: a list of values containing singular values"""
    return [flatlist[i::numrows] for i in range(0, numrows)]

if __name__ == '__main__':
    app.secret_key = 'r5Sb35U-kE24aNrF55ee9MK0'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
