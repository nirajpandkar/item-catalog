from flask import Flask, render_template, request, redirect, url_for, \
    jsonify, flash
from database import Base, Category, Item, User
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
import random
import string
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

@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
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

    # check if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    print login_session['username']
    print login_session['picture']
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += '" style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    print 'In gdisconnect access token is %s', access_token
    username = login_session.get('username')
    if username is not None:
        print 'User name is: '
        print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % login_session['access_token']
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        del login_session['access_token']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for '
                                            'given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# Facebook login

@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    print "access token received %s " % access_token

    app_id = json.loads(open('fb_client_secrets.json', 'r').read())[
        'web']['app_id']
    app_secret = json.loads(
        open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token&client_id=%s&client_secret=%s&fb_exchange_token=%s' % (
        app_id, app_secret, access_token)
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]

    # Use token to get user info from API
    userinfo_url = "https://graph.facebook.com/v2.4/me"
    # strip expire tag from access token
    token = result.split("&")[0]


    url = 'https://graph.facebook.com/v2.4/me?%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    # print "url sent for API access:%s"% url
    # print "API JSON result: %s" % result
    data = json.loads(result)
    login_session['provider'] = 'facebook'
    login_session['username'] = data["name"]
    login_session['email'] = data["email"]
    login_session['facebook_id'] = data["id"]

    # The token must be stored in the login_session in order to properly logout, let's strip out the information before the equals sign in our token
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

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']

    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '

    flash("Now logged in as %s" % login_session['username'])
    return output


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    # The access token must me included to successfully logout
    access_token = login_session['access_token']
    url = 'https://graph.facebook.com/%s/permissions?access_token=%s' % (facebook_id,access_token)
    h = httplib2.Http()
    result = h.request(url, 'DELETE')
    print "Result" + result[0]['status']
    if result[0]['status'] == '200':
        del login_session['access_token']
        del login_session['facebook_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for '
                                            'given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


engine = create_engine('sqlite:///categories.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template("login.html", state=state)


@app.route('/')
@app.route('/categories')
def show_categories():
    categories = session.query(Category).all()
    username = login_session.get('username')

    user_id = login_session.get('user_id')
    if username is not None:
        username = login_session.get('username')
    else:
        username = "Guest"
    return render_template("categories.html", categories=categories,
                           username=username, user_id=user_id)


@app.route('/category/new', methods=['GET', 'POST'])
def new_category():
    '''
        Creates a new category
    '''
    if 'username' not in login_session:
        return redirect("/login")
    if request.method == 'POST':
        genre = Category(name=request.form['new_category'],
                         user_id=login_session['user_id'])
        session.add(genre)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template("newcategory.html")


@app.route('/category/<string:category_name>/edit', methods=['GET', 'POST'])
def edit_category(category_name):
    '''
        Arguments: Name of the category which is to be edited

        Edits an existing category name.
    '''
    if 'username' not in login_session:
        return redirect("/login")
    edited_genre = session.query(Category).filter_by(name=category_name)\
        .first()
    if request.method == 'POST':
        if request.form['edit_category']:
            edited_genre.name = request.form['edit_category']
        session.add(edited_genre)
        edited_genre_item = session.query(Item).filter_by(
            category_name=category_name)
        for i in edited_genre_item:
            i.category_name = request.form['edit_category']
            session.add(i)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template("editcategory.html", genre=edited_genre.name)


@app.route('/category/<string:category_name>/delete', methods=['GET', 'POST'])
def delete_category(category_name):
    '''
        Arguments: Name of the category which is to be edited

        Deletes an existing category name.
    '''
    if 'username' not in login_session:
        return redirect("/login")
    deleted_genre = session.query(Category).filter_by(
        name=category_name).one()
    if request.method == 'POST':
        # deleted_genre.delete(synchronize_session=False)
        session.delete(deleted_genre)
        session.commit()
        return redirect(url_for('show_categories'))
    else:
        return render_template("deletecategory.html",
                               genre=deleted_genre.name)


@app.route('/category/<string:name>/items')
@app.route('/category/<string:name>/')
def show_items(name):
    books = session.query(Item).filter_by(category_name=name)
    return render_template("items.html", books=books, genre=name)


@app.route('/category/<string:category_name>/<string:item_name>/')
def show_particular_item(category_name, item_name):
    genre = session.query(Category).filter_by(name=category_name).first()
    book = session.query(Item).filter_by(name=item_name).first()
    logged_user_id = login_session.get('user_id')
    return render_template("item.html", book=book, genre=genre,
                           logged_user_id=logged_user_id)


@app.route('/category/<string:category_name>/new', methods=['GET', 'POST'])
def new_item(category_name):
    if 'username' not in login_session:
        return redirect("/login")
    category = session.query(Category).filter_by(name=category_name).one()
    if request.method == 'POST':
        book = Item(name=request.form['name'],
                    description=request.form['description'],
                    category_name=category_name,
                    user_id=category.user_id)
        session.add(book)
        session.commit()
        return redirect(url_for('show_items', name=category_name))
    else:
        return render_template("newitem.html", category_name=category_name)


@app.route('/category/<string:category_name>/<string:item_name>/edit',
           methods=['GET', 'POST'])
def edit_item(category_name, item_name):
    if 'username' not in login_session:
        return redirect("/login")
    edited_item = session.query(Item).filter_by(name=item_name).one()
    if request.method == 'POST':
        edited_item.name = request.form['item_name']
        edited_item.description = request.form['item_description']
        session.add(edited_item)
        session.commit()
        return redirect(url_for('show_particular_item',
                                category_name=category_name,
                                item_name=edited_item.name))
    else:
        return render_template("edititem.html", item=edited_item,
                               genre=category_name)


@app.route('/category/<string:category_name>/<string:item_name>/delete',
           methods=['GET', 'POST'])
def delete_item(category_name, item_name):
    if 'username' not in login_session:
        return redirect("/login")
    deleted_item = session.query(Item).filter_by(
        name=item_name)
    if request.method == 'POST':
        deleted_item.delete(synchronize_session=False)
        session.commit()
        return redirect(url_for('show_items', name=category_name))
    else:
        return render_template("deleteitem.html", genre=category_name,
                               item=item_name)


@app.route('/category/<string:category_name>/item/JSON')
def itemsJSON(category_name):
    # category = session.query(Category).filter_by(name=category_name).one()
    items = session.query(Item).filter_by(
        category_name=category_name).all()
    return jsonify(Items=[i.serialize for i in items])


@app.route('/category/<string:category_name>/<string:item_name>/JSON')
def itemJSON(category_name, item_name):
    # category = session.query(Category).filter_by(name=category_name).one()
    item = session.query(Item).filter_by(
        category_name=category_name, name=item_name).one()
    return jsonify(Item=[item.serialize])


@app.route('/categories/JSON')
def categoriesJSON():
    categories = session.query(Category).all()
    return jsonify(Categories=[i.serialize for i in categories])

# User functions


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

if __name__ == '__main__':
    app.secret_key = "super secret key"
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
