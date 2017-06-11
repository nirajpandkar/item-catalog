from flask import Flask, render_template, request, redirect, url_for, \
    jsonify, flash
from database import Base, Category, Item, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from functools import wraps
import random
import string
import time
from flask import session as login_session


# Authorization
from oauth2client.client import flow_from_clientsecrets, AccessTokenCredentials
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(open('client_secret.json', 'r').read())['web'][
        'client_id']

app = Flask(__name__)

# Connect to database
engine = create_engine('postgresql://catalog:superman1$@localhost/catalog')
Base.metadata.bind = engine

# Create database session
DBSession = sessionmaker(bind=engine)
session = DBSession()


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'username' not in login_session:
            return redirect(url_for('showLogin'))
        return f(*args, **kwargs)
    return decorated_function

# User helper functions


def createUser(login_session):
    new_user = User(name=login_session['username'],
                    email=login_session['email'],
                    picture=login_session['picture'])
    session.add(new_user)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


@app.route('/logout')
def logout():
    if login_session['provider'] == 'facebook':
        fbdisconnect()
        del login_session['facebook_id']
        del login_session['access_token']

    if login_session['provider'] == 'google':
        gdisconnect()
        del login_session['gplus_id']
        del login_session['access_token']

    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['provider']

    flash("Logout Successful!")
    return redirect(url_for('show_categories'))


@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate anti-forgery state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Obtain authorization code
    code = request.data     # One time code

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secret.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)   # Exchanges
        # authorization code for credential object
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
        return response

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

    stored_credentials = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')

    if stored_credentials is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    login_session['provider'] = 'google'

    # check if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    return 'Login Successful!</br>Redirecting...'


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')

    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % \
          login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]

    if result['status'] != '200':
        response = make_response(json.dumps('Failed to revoke token for '
                                            'given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        flash("Failed to revoke token for given user")
        return redirect(url_for("show_categories"))


# Facebook login

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    # Validate anti-forgery state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Get access token
    access_token = request.data

    # Gets info from fb clients secrets
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web'][
        'app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']

    url = 'https://graph.facebook.com/v2.9/oauth/access_token?grant_type' \
          '=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
          app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    data = json.loads(result)
    token = 'access_token=' + data['access_token']

    url = 'https://graph.facebook.com/v2.9/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)

    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly
    # logout, strip out the information before the equals sign in our token
    stored_token = token.split("=")[1]
    login_session['access_token'] = stored_token

    # Get user picture
    url = 'https://graph.facebook.com/v2.4/me/picture?%s&redirect=0&height=200&width=200' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)

    login_session['picture'] = data["data"]["url"]

    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    return 'Login Successful!</br>Redirecting...'


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    access_token = login_session['access_token']

    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')

    if result[0]['status'] != '200':
        flash("Failed to revoke token for given user")
        return redirect(url_for("show_categories"))


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    """
        Renders the login page.
    """
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template("login.html", state=state)


@app.route('/')
@app.route('/categories')
def show_categories():
    """
        Returns all the category names.
    """
    categories = session.query(Category).all()
    username = login_session.get('username')
    user_id = login_session.get('user_id')
    provider = login_session.get('provider')
    if username is not None:
        username = login_session.get('username')
    return render_template("categories.html", categories=categories,
                           username=username, user_id=user_id,
                           provider=provider)


@app.route('/category/new', methods=['GET', 'POST'])
@login_required
def new_category():
    """
        Creates a new category
    """
    if request.method == 'POST':
        genre = Category(name=request.form['new_category'],
                         user_id=login_session['user_id'])
        session.add(genre)
        try:
            session.commit()
        except:
            session.rollback()
            flash("Error: Cannot have two categories with the same name!")
        return redirect(url_for('show_categories'))
    else:
        return render_template("newcategory.html")


@app.route('/category/<string:category_name>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(category_name):
    """
        Arguments: Name of the category which is to be edited

        Edits an existing category name.
    """
    edited_genre = session.query(Category).filter_by(name=category_name)\
        .one()

    if edited_genre.user_id == login_session['user_id']:
        if request.method == 'POST':
            if request.form['edit_category']:
                edited_genre.name = request.form['edit_category']
            session.add(edited_genre)
            edited_genre_item = session.query(Item).filter_by(
                category_id=edited_genre.id)
            for i in edited_genre_item:
                i.category_id = edited_genre.id
                session.add(i)
            try:
                session.commit()
            except:
                session.rollback()
                flash("Error: Cannot have two categories with the same name!")
            return redirect(url_for('show_categories'))
        else:
            return render_template("editcategory.html", genre=edited_genre.name)
    else:
        flash("Not authorized to edit category: " + str(category_name))
        return redirect(url_for('show_items', name=category_name))


@app.route('/category/<string:category_name>/delete', methods=['GET', 'POST'])
@login_required
def delete_category(category_name):
    """
        Arguments: Name of the category which is to be edited

        Deletes an existing category name.
    """
    deleted_genre = session.query(Category).filter_by(
        name=category_name).one()

    if deleted_genre.user_id == login_session['user_id']:
        if request.method == 'POST':
            # deleted_genre.delete(synchronize_session=False)
            session.delete(deleted_genre)
            try:
                session.commit()
            except:
                session.rollback()
                flash("Error in deleting the category" + str(category_name))

            return redirect(url_for('show_categories'))
        else:
            return render_template("deletecategory.html",
                                   genre=deleted_genre.name)
    else:
        flash("Not authorized to delete category: " + str(category_name))
        return redirect(url_for('show_items', name=category_name))


@app.route('/category/<string:name>/items')
@app.route('/category/<string:name>/')
def show_items(name):
    """
    Arguments: Name of the category

    Gives the information about the items contained in that particular
    category
    """
    categories = session.query(Category).all()
    genre = session.query(Category).filter_by(name=name).one()
    books = session.query(Item).filter_by(category_id=genre.id)
    username = login_session.get('username')
    logged_user_id = login_session.get('user_id')
    genre_user_id = session.query(Category).filter_by(name=name).one().user_id
    return render_template("items.html", books=books, genre=name,
                           categories=categories, username=username,
                           logged_user_id=logged_user_id,
                           genre_user_id=genre_user_id)


@app.route('/category/<string:category_name>/<string:item_name>/')
def show_particular_item(category_name, item_name):
    """
    Arguments: Name of the category
               Name of the item

    Used to return information about a particular item.
    """
    genre = session.query(Category).filter_by(name=category_name).first()
    book = session.query(Item).filter_by(name=item_name).first()
    logged_user_id = login_session.get('user_id')
    username = login_session.get('username')
    categories = session.query(Category).all()
    return render_template("item.html", book=book, genre=genre,
                           logged_user_id=logged_user_id,
                           categories=categories, username=username)


@app.route('/category/<string:category_name>/new', methods=['GET', 'POST'])
@login_required
def new_item(category_name):
    """
    Arguments: Name of the category

    Adds a new item to the given category.
    """
    category = session.query(Category).filter_by(name=category_name).one()
    if request.method == 'POST':
        book = Item(name=request.form['name'],
                    description=request.form['description'],
                    category_id=category.id,
                    user_id=login_session['user_id'])
        session.add(book)
        try:
            session.commit()
        except:
            session.rollback()
            flash("Error while adding new item!")

        return redirect(url_for('show_items', name=category_name))
    else:
        return render_template("newitem.html", category_name=category_name)


@app.route('/category/<string:category_name>/<string:item_name>/edit',
           methods=['GET', 'POST'])
@login_required
def edit_item(category_name, item_name):
    """
    Arguments: Name of the category
               Name of the item

    Edit a particular item from a particular category.
    """
    edited_item = session.query(Item).filter_by(name=item_name).one()

    if edited_item.user_id == login_session['user_id']:
        if request.method == 'POST':
            edited_item.name = request.form['item_name']
            edited_item.description = request.form['item_description']
            session.add(edited_item)
            try:
                session.commit()
            except:
                session.rollback()
                flash("Error while editing existing item!")
            return redirect(url_for('show_particular_item',
                                    category_name=category_name,
                                    item_name=edited_item.name))
        else:
            return render_template("edititem.html", item=edited_item,
                                   genre=category_name)
    else:
        flash("Not authorized to edit item: " + str(item_name))
        return redirect(url_for('show_particular_item',
                                category_name=category_name,
                                item_name=item_name))


@app.route('/category/<string:category_name>/<string:item_name>/delete',
           methods=['GET', 'POST'])
@login_required
def delete_item(category_name, item_name):
    """
    Arguments: Name of the category
               Name of the item

    Deletes a particular item from a particular category.
    """
    deleted_item = session.query(Item).filter_by(
        name=item_name).one()

    if deleted_item.user_id == login_session['user_id']:
        if request.method == 'POST':
            # deleted_item.delete(synchronize_session=False)
            session.delete(deleted_item)
            try:
                session.commit()
            except:
                session.rollback()
                flash("Error while deleting the item" + item_name)
            return redirect(url_for('show_items', name=category_name))
    else:
        flash("Not authorized to delete item: " + str(item_name))
        return redirect(url_for('show_particular_item',
                                category_name=category_name,
                                item_name=item_name))


# JSON API endpoints

@app.route('/category/<string:category_name>/items/JSON')
def itemsJSON(category_name):
    category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(
        category_id=category.id).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/category/<string:category_name>/<string:item_name>/JSON')
def itemJSON(category_name, item_name):
    category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(
        category_id=category.id, name=item_name).one()
    return jsonify(Item=[item.serialize])


@app.route('/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])


@app.route('/users/JSON')
def usersJSON():
    users = session.query(User).all()
    return jsonify(User=[i.serialize for i in users])

if __name__ == '__main__':
    app.secret_key = "super secret key"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
