from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
app = Flask(__name__)

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem

engine = create_engine('sqlite:///restaurantmenu.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

@app.route('/')
@app.route('/restaurants/')
def restaurants():
	restaurants = session.query(Restaurant).order_by(Restaurant.name.asc())
	return render_template('restaurants.html', restaurants=restaurants)

@app.route('/restaurant/<int:restaurant_id>/')
#  TODO: Breakout by course
def restaurantMenu(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(
		id=restaurant_id).one()
	apps = session.query(MenuItem).filter_by(
		restaurant_id=restaurant.id, course="Appetizer")
	entrees = session.query(MenuItem).filter_by(
		restaurant_id=restaurant.id, course="Entree")
	desserts = session.query(MenuItem).filter_by(
		restaurant_id=restaurant.id, course="Dessert")
	beverages = session.query(MenuItem).filter_by(
		restaurant_id=restaurant.id, course="Beverages")
	return render_template('menu.html',
	 restaurant=restaurant,
	 apps=apps,
	 entrees=entrees,
	 desserts=desserts,
	 beverages=beverages)

@app.route('/restaurant/new/', methods=['GET', 'POST'])
def newRestaurant():
	if request.method == 'POST':
		restaurant = Restaurant(name=request.form['name'])
		session.add(restaurant)
		session.commit()
		return redirect(url_for('restaurants'))
	else:
		return render_template('newrestaurant.html')

@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
	restaurantToEdit = session.query(Restaurant).filter_by(id=restaurant_id).one()
	if request.method == 'POST':
		restaurantToEdit.name = request.form['name']
		session.add(restaurantToEdit)
		session.commit()
		return redirect(url_for('restaurants'))
	else:
		return render_template('editrestaurant.html', restaurant=restaurantToEdit)

@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
	itemToDelete = session.query(Restaurant).filter_by(id = restaurant_id).one()
	if request.method == 'POST':
		menuItems = session.query(MenuItem).filter_by(restaurant_id = itemToDelete.id)
		for item in menuItems:
			session.delete(item)
		session.delete(itemToDelete)
		session.commit()
		return redirect(url_for('restaurants'))
	else:
		return render_template('deleterestaurant.html', restaurant=itemToDelete)

@app.route('/restaurant/<int:restaurant_id>/menu/new/', methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
	if request.method == 'POST':
		newItem = MenuItem(name = request.form['name'], restaurant_id = restaurant_id)
		session.add(newItem)
		session.commit()
		flash("new menu item create!")
		return redirect(url_for('restaurantMenu', restaurant_id = restaurant_id))
	else:
		return redirect(url_for('newmenuitem.html', restaurant_id = restaurant_id))

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/', methods = ['GET', 'POST'])
#  TODO: Add edit inputs for the other fields in MenuItem
def editMenuItem(restaurant_id, menu_id):
	editedItem = session.query(MenuItem).filter_by(id = menu_id).one()
	previousName = editedItem.name
	if request.method == 'POST':
		editedItem.name = request.form['name']
		session.add(editedItem)
		session.commit()
		flash("Changed name form " + previousName + " to " + editedItem.name)
		return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
	else:
		return render_template('editmenuitem.html', restaurant_id = restaurant_id, menu_id = menu_id, item = editedItem)

@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/', methods = ['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
	deleteItem = session.query(MenuItem).filter_by(id = menu_id).one()
	deletedItemName = deleteItem.name
	if request.method =='POST':
		session.delete(deleteItem)
		session.commit()
		flash("Deleted " + deletedItemName)
		return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
	else:
		return render_template('deletemenuitem.html', restaurant_id = restaurant_id, menu_id = menu_id, item = deleteItem)

#Making an API Endpoint (GET Request)
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
	return jsonify(MenuItems=[i.serialize for i in items])

@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
	restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
	item = session.query(MenuItem).filter_by(id=menu_id).one()
	return jsonify(MenuItems=item.serialize)


if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	app.debug = True
	app.run(host='0.0.0.0', port=5000)
