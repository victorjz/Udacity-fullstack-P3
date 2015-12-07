Udacity Full Stack Web Developer Nanodegree
P3: Item Catalog
As described here: https://storage.googleapis.com/supplemental_media/udacityu/3487760229/P3ItemCatalog-GettingStarted.pdf

Prepared by: Victor Zaragoza vjzara@gmail.com

This goal of this project is to build a locally hosted website representing a
catalog of items by category. It features item DB CRUD operations protected
behind Google account logins.

Of special note for the implementation of this project is that neither
SQLAlchemy nor any other ORM were used for database operations.  The Python
postgres API was used throughout.  As a result, custom functions were written to
reduce repeating code, all commented appropriately.

To run this program:
Execute:
> psql -f catalog_items.sql
> python catalog_app.py
And if you would like sample data pre-populated, execute:
> python catalog_filler.py
Open the browser and navigate to localhost:8000
Read on further for the links and functions available

The following information should help the reviewer identify where the functions
that are required for the assignment are located, as well as where additional
features "exceeding specifications" are located, marked by a *.

Site Map:
Featured on the left of every page is the fictional name and logo of the company
hosting the catalog, CATaLOG.  The logo is a link back to the home page.  A link
is featured for user login.  The link changes for logged in users to log out.

http://localhost:8000/
http://localhost:8000/catalog/
-Home page
-Features links to different available categories
*Link at bottom offer all items view
*Link at the bottom for categories edit for logged in users

http://localhost:8000/catalog/<category>/items
(The name of the category clicked replaces <category> in the above URL)
-Features links to different items belonging to the category
-Items may appear under more than one category
-Link at the end directs the user back to the home page

http://localhost:8000/catalog/<item>
(The name of the item clicked replaces <item> in the above URL)
-Features a table of links for every category to which the item belongs
-Links for editing and deleting the item will appear for a logged in user if the
 user created the item
-Link at the end directs the user back to the home page

http://localhost:8000/catalog/<item>/edit
(The name of the item clicked replaces <item> in the above URL)
-A field for item name, item description
--If either field is left blank, values will not change
*A table of checkboxes for every category with checks for categories to which
 the item belongs
--Values that are checked will be associated with the item
--Values that are unchecked will be removed from being associated with the item
*A short form for adding an image will appear differently according to whether
 the item already has an item
-Clicking the submit button will record changes in fields and checkboxes
-Links at the bottom will cancel changes are return to the item details, link to
  return to the homepage

http://localhost:8000/catalog/<item>/delete
(The name of the item clicked replaces <item> in the above URL)
-Clicking the submit button will remove the item from the catalog
-Links at the bottom will cancel changes are return to the item details, link to
  return to the homepage

http://localhost:8000/catalog/items
*This page provides an extra view not specified in requirements
-Table of links for categories and items belonging to each category
-Link for JSON endpoint
*Link for XML endpoint
-Link at the end directs the user back to the home page

http://localhost:8000/catalog.json
-JSON endpoint

http://localhost:8000/catalog.xml
*XML endpoint

http://localhost:8000/catalog/categoriesEdit
*This page provides extra functions not specified in requirements
-Allows for changing the available categories on the home page
-Table of checkboxes features current categories
--Unchecking checkboxes will remove categories upon clicking submit button
--Removing a category with items that do not belong to any other category will
 result in those items only appearing on the all items page for the user to edit
 and add categories
-A text field where new category names can be entered
-Submit button records changes in checkboxes or text field
-Link at the bottom cancels changes and directs user to home page
