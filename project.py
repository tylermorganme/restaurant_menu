import random
import string
from flask import (Flask, render_template, request,
                   redirect, url_for, flash, jsonify, make_response)
from flask import session as login_session

from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Restaurant, Base, MenuItem, User

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Restaurant Menu Application"

engine = create_engine('sqlite:///restaurantmenuwithusers.db')
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


def createUser(login_session):
    """Create a new user"""
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    """Get the inforation for a user. Take a user ID as an argument."""
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    """Get the ID for a user. Takes an email address as an arugment."""
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.context_processor
def utilities():
    """Provide utility context processors."""
    def user_logged_in():
        """Return if a user is logged in."""
        return True if 'username' in login_session else False
    return dict(user_logged_in=user_logged_in)


@app.route('/')
@app.route('/restaurants/')
def restaurants():
    """Render a view of all restaurants"""
    restaurants = session.query(Restaurant).order_by(Restaurant.name.asc())
    if 'username' not in login_session:
        return render_template('publicrestaurants.html',
                               restaurants=restaurants)
    else:
        user = login_session['user_id']
        return render_template('restaurants.html',
                               restaurants=restaurants,
                               user_id=user)


@app.route('/restaurant/<int:restaurant_id>/')
#  TODO: Breakout by course
def restaurantMenu(restaurant_id):
    """Render a view of the menu of a single restaurant"""
    restaurant = session.query(Restaurant).filter_by(
        id=restaurant_id).one()
    creator = getUserInfo(restaurant.user_id)
    apps = session.query(MenuItem).filter_by(
        restaurant_id=restaurant.id, course="Appetizer")
    entrees = session.query(MenuItem).filter_by(
        restaurant_id=restaurant.id, course="Entree")
    desserts = session.query(MenuItem).filter_by(
        restaurant_id=restaurant.id, course="Dessert")
    beverages = session.query(MenuItem).filter_by(
        restaurant_id=restaurant.id, course="Beverages")
    if ('username' not in login_session or
            creator.id != login_session['user_id']):
        return render_template('publicmenu.html',
                               restaurant=restaurant,
                               apps=apps,
                               entrees=entrees,
                               desserts=desserts,
                               beverages=beverages,
                               creator=creator)
    else:
        return render_template('menu.html',
                               restaurant=restaurant,
                               apps=apps,
                               entrees=entrees,
                               desserts=desserts,
                               beverages=beverages,
                               creator=creator)


@app.route('/restaurant/new/', methods=['GET', 'POST'])
def newRestaurant():
    """Render a view for creating new restaurants"""
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        restaurant = Restaurant(name=request.form['name'],
                                user_id=login_session['user_id'])
        session.add(restaurant)
        session.commit()
        return redirect(url_for('restaurants'))
    else:
        return render_template('newrestaurant.html')


@app.route('/restaurant/<int:restaurant_id>/edit/', methods=['GET', 'POST'])
def editRestaurant(restaurant_id):
    """Render a view for editing an existing restaurant"""
    if 'username' not in login_session:
        return redirect('/login')
    restaurantToEdit = session.query(Restaurant).filter_by(
        id=restaurant_id).one()
    if restaurantToEdit.user_id != login_session['user_id']:
        return ('You are not authorized to edit this restaurant. '
                'Please create your own restaurant in order to edit.')
    if request.method == 'POST':
        restaurantToEdit.name = request.form['name']
        session.add(restaurantToEdit)
        session.commit()
        return redirect(url_for('restaurants'))
    else:
        return render_template('editrestaurant.html',
                               restaurant=restaurantToEdit)


@app.route('/restaurant/<int:restaurant_id>/delete/', methods=['GET', 'POST'])
def deleteRestaurant(restaurant_id):
    """Render a view for deleting an existing restaurant"""
    if 'username' not in login_session:
        return redirect('/login')
    restaurantToDelete = session.query(Restaurant).filter_by(
        id=restaurant_id).one()
    if restaurantToDelete.user_id != login_session['user_id']:
        return ('You are not authorized to delete this restaurant. '
                'Please create your own restaurant in order to delete.')
    if request.method == 'POST':
        menuItems = session.query(MenuItem).filter_by(
            restaurant_id=restaurantToDelete.id)
        for item in menuItems:
            session.delete(item)
        session.delete(restaurantToDelete)
        session.commit()
        return redirect(url_for('restaurants'))
    else:
        return render_template('deleterestaurant.html',
                               restaurant=restaurantToDelete)


@app.route('/restaurant/<int:restaurant_id>/menu/new/',
           methods=['GET', 'POST'])
def newMenuItem(restaurant_id):
    """Render a view for creating a new menu item"""
    restaurant = session.query(Restaurant).filter_by(
        id=restaurant_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if restaurant.user_id != login_session['user_id']:
        return ('Your are not authorized to add items to this restaurant. '
                'Please create your own restaurant to add menu items.')
    if request.method == 'POST':
        newItem = MenuItem(name=request.form['name'],
                           course=request.form['course'],
                           description=request.form['description'],
                           price=request.form['price'],
                           restaurant_id=restaurant_id,
                           user_id=restaurant.user_id)
        session.add(newItem)
        session.commit()
        flash("new menu item create!")
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('newmenuitem.html', restaurant_id=restaurant_id)


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/edit/',
           methods=['GET', 'POST'])
#  TODO: Add edit inputs for the other fields in MenuItem
def editMenuItem(restaurant_id, menu_id):
    """Render a view of for editing an existing menu item"""
    if 'username' not in login_session:
        return redirect('/login')
    editedItem = session.query(MenuItem).filter_by(id=menu_id).one()
    previousName = editedItem.name
    if editedItem.user_id != login_session['user_id']:
        return ('Your are not authorized to edit this restaurant\'s menu '
                'items. Please create your own restaurant in order to delete.')
    if request.method == 'POST':
        editedItem.name = request.form['name']
        session.add(editedItem)
        session.commit()
        flash("Changed name form " + previousName + " to " + editedItem.name)
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('editmenuitem.html',
                               restaurant_id=restaurant_id,
                               menu_id=menu_id,
                               item=editedItem)


@app.route('/restaurant/<int:restaurant_id>/<int:menu_id>/delete/',
           methods=['GET', 'POST'])
def deleteMenuItem(restaurant_id, menu_id):
    """Render a view to delete an existing menu item"""
    if 'username' not in login_session:
        return redirect('/login')
    deleteItem = session.query(MenuItem).filter_by(id=menu_id).one()
    deletedItemName = deleteItem.name
    if deleteItem.user_id != login_session['user_id']:
        return ('Your are not authorized to delete this restaurant\'s menu '
                'items. Please create your own restaurant in order to delete.')
    if request.method == 'POST':
        session.delete(deleteItem)
        session.commit()
        flash("Deleted " + deletedItemName)
        return redirect(url_for('restaurantMenu', restaurant_id=restaurant_id))
    else:
        return render_template('deletemenuitem.html',
                               restaurant_id=restaurant_id,
                               menu_id=menu_id,
                               item=deleteItem)


# Create a state token to prevent request forgery
# Store it in the session for later validation
@app.route('/login')
def showLogin():
    """Render a view for user login"""
    state = ''.join(
        random.choice(string.ascii_uppercase + string.digits)
        for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """Authorize a user through Google OAuth2"""
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
        response = make_response(json.dumps(
            "Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(json.dumps(
            "Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_credentials = login_session.get('credentials')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps(
            'Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['credentials'] = credentials
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()
    print data

    login_session['provider'] = 'google'
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style="width: 300px; height: 300px; border-radius: 150px; '
               '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> ')
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    """Authorize a user through Facebook OAuth2"""
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = ('https://graph.facebook.com/oauth/access_token?'
           'grant_type=fb_exchange_token&client_id=%s&'
           'client_secret=%s&fb_exchange_token=%s') % (
            app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.2/me"
    # strip expire tag from access token
    token = result.split("&")[0]

    url = 'https://graph.facebook.com/v2.2/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # Token must be stored in the login_session in order to properly logout.
    # Strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = ('https://graph.facebook.com/v2.2/me/picture?'
           '%s&redirect=0&height=200&width=200') % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += (' " style = "width: 300px; height: 300px;border-radius: 150px; '
               '-webkit-border-radius: 150px;-moz-border-radius: 150px;"> ')

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/disconnect')
def disconnect():
    """Disconnect a user from either Facebook or Google"""
    if login_session['provider'] == 'facebook':
        facebook_id = login_session['facebook_id']
        # The access token must me included to successfully logout
        access_token = login_session['access_token']
        url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (
            facebook_id, access_token)
        h = httplib2.Http()
        result = h.request(url, 'DELETE')[1]
        flash("You have been logged out")
        del login_session['facebook_id']
    else:
        # Only disconnect a connected user.
        credentials = login_session.get('credentials')
        if credentials is None:
            response = make_response(
                json.dumps('Current user not connected'), 401)
            response.headers['Content-type'] = 'application/json'
        # Execute HTTP GET request to revoke current token.
        access_token = credentials.access_token
        url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % (
            access_token)
        h = httplib2.Http()
        result = h.request(url, 'GET')[0]

        if result['status'] == '200':
            # Result the user's session.
            del login_session['gplus_id']
            del login_session['credentials']

            response = make_response(
                json.dumps('Sucessfully disconencted.'), 200)
            response.headers['Content-Type'] = 'application/json'
            flash("You have been logged out")
        else:
            # For whatever reason, the given token was invalid.
            flash('Failed to revoke token for given use.')
            response = make_response(
                json.dumps('Failed to revoke token for given use.', 400)
            )
            response.headers['Content-Type'] = 'application/json'

    del login_session['username']
    del login_session['email']
    del login_session['picture']
    return redirect(url_for('restaurants'))


# API Endpoints
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    """API endpoint for a restaurant menu"""
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id=restaurant.id)
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    """API endpoint for a restaurant menu item"""
    restaurant = session.query(Restaurant).filter_by(id=restaurant_id).one()
    item = session.query(MenuItem).filter_by(id=menu_id).one()
    return jsonify(MenuItems=item.serialize)

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
