# Item Catalog
## Locally hosted website representing a catalog of items
As described here: https://storage.googleapis.com/supplemental_media/udacityu/3487760229/P3ItemCatalog-GettingStarted.pdf

This goal of this project is to build a locally hosted website representing a
catalog of items by category. It features item DB CRUD operations protected
behind ~~Google account logins.~~ _this feature requires a Google token via paid
subscription, which is expired for the time being._

## Also found in this repository
`README.txt` The previous readme provided with the original submission of this project

`README_webhost.md` The readme provided for the following project, which was to transfer the site to a webhosted environment, including server configuration

## To run this program:

### Assumes postgres installed
### Assumes Python dependencies are installed for these library import statements
```python
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
import psycopg2
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError, OAuth2Credentials
import httplib2
import json
from flask import make_response
import requests
from io import BytesIO
import base64
import xml.etree.ElementTree as ET
```

### Lines to execute in command line _with commentary_
_Start postgres server_
`> sudo service postgresql start`

_Create the database_
`> psql -f catalog_items.sql`

_Populate sample data_
`> python catalog_filler.py`

_Begin hosting the website_
`> python catalog_app.py`

### Open a browser and nagivate to
`localhost:8000`

## Site Map
Site Map:
Featured on the left of every page is the fictional name and logo of the company
hosting the catalog, CATaLOG.  The logo is a link back to the home page.  A link
is featured for user login.  The link changes for logged in users to log out.

`http://localhost:8000/`

`http://localhost:8000/catalog/`
- Home page
- Features links to different available categories
- Link at bottom offers an all items view
- Link at the bottom for categories edit for logged in users

`http://localhost:8000/catalog/<category>/items`
(The name of the category clicked replaces `<category>` in the above URL)
- Features links to different items belonging to the category
- Items may appear under more than one category
- Link at the end directs the user back to the home page

`http://localhost:8000/catalog/<item>`
(The name of the item clicked replaces `<item>` in the above URL)
- Features a table of links for every category to which the item belongs
- Links for editing and deleting the item will appear for a logged in user if the user created the item
- Link at the end directs the user back to the home page

`http://localhost:8000/catalog/<item>/edit`
(The name of the item clicked replaces `<item>` in the above URL)
- Requires login
- A field for item name, item description
    - If either field is left blank, values will not change
- A table of checkboxes for every category
    - Values that are checked will be associated with the item (or are already associated with the item)
    - Values that are unchecked will be removed from being associated with the item
- A short form for adding an image will appear differently according to whether the item already has an image
- Clicking the submit button will record changes in fields and checkboxes
- Links at the bottom will cancel changes and return to the item details

`http://localhost:8000/catalog/<item>/delete`
(The name of the item clicked replaces `<item>` in the above URL)
- Clicking the submit button will remove the item from the catalog
- Links at the bottom will cancel changes and return to the item details

`http://localhost:8000/catalog/items`
- Table of links for categories and items belonging to each category
- Link for JSON endpoint
- Link for XML endpoint
- Link at the end directs the user back to the home page

`http://localhost:8000/catalog.json`
- JSON endpoint

`http://localhost:8000/catalog.xml`
- XML endpoint

`http://localhost:8000/catalog/categoriesEdit`
- Allows for changing the available categories on the home page
- Table of checkboxes features current categories
    - Unchecking checkboxes will remove categories upon clicking submit button
    - Removing a category with items that do not belong to any other category will result in those items only appearing on the all items page.  The user can then edit and add categories for those items.
- A text field where new category names can be entered
- Submit button records changes in checkboxes or text field
- Link at the bottom cancels changes and directs user to home page
