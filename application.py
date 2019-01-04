#!/usr/bin/env python3
from flask import (
    Flask,
    render_template,
    request,
    redirect,
    jsonify,
    url_for,
    flash

    )
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, User, Manufacturer, Candy
from flask import session as login_session
import random
import string
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests
import os

app = Flask(__name__)

CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Candy-Mania"

UPLOAD_FOLDER = os.path.basename('static')
app.config['UPLOAD FOLDER'] = UPLOAD_FOLDER

engine = create_engine('sqlite:///candymanufacturers.db',
                       connect_args={'check_same_thread': False})
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
    print ("Namaste")
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'appplication/json'
        return response
    code = request.data

    try:
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
        print ("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is\
         already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    print (login_session['access_token'])
    print (login_session['gplus_id'])

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    data = answer.json()
    print (data)

    name = data['email'].split("@")
    login_session['username'] = name[0]
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id
    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ' " style = "width: 200px; height: 200px;border-radius: \
    150px;-webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print ("done!")
    return output


def createUser(login_session):
    newUser = User(name=login_session['username'],
                   email=login_session['email'],
                   picture=login_session['picture'])
    session.add(newUser)
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# To get user Information
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# To get users information
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        session.commit()
        return user.id
    except:
        return None


# DISCONNECT - Revoke a current user's token and reset their login_session
# To disconnect from google login
@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for \
        given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
            del login_session['username']
            del login_session['email']
            del login_session['picture']
            del login_session['user_id']
            flash("You have successfully been logged out.")
            return redirect(url_for('Home'))
    else:
        flash("You were not logged in")
        return redirect(url_for('Home'))


# route to home page, add button visible only on login
@app.route('/')
@app.route('/candymanufacturers/')
def Home():
    manufacturers = session.query(Manufacturer). \
        order_by(asc(Manufacturer.name))
    candies = session.query(Candy).all()
    if 'username' not in login_session:
        return render_template('publicindex.html',
                               manufacturers=manufacturers, candies=candies)
    else:
        return render_template('index.html',
                               manufacturers=manufacturers, candies=candies)


# route to add new candy manufacturers
@app.route('/candymanufacturers/new/', methods=['GET', 'POST'])
def newManufacturer():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        Manufacturer_create = Manufacturer(
            name=request.form['name'], user_id=login_session['user_id'])
        session.add(Manufacturer_create)
        flash('New Manufacturer %s Successfully Created'
              % Manufacturer_create.name)
        session.commit()
        return redirect(url_for('Home'))
    else:
        return render_template('newManufacturer.html')


# route to edit the name of an existing manufacturers
@app.route('/candymanufacturers/<int:manufacturer_id>/edit/',
           methods=['GET', 'POST'])
def editManufacturer(manufacturer_id):
    Manufacturer_alt = session.query(Manufacturer). \
        filter_by(id=manufacturer_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if Manufacturer_alt.user_id != login_session['user_id']:
        return flash("You are not authorised to edit this Manufacturer.Please \
        create your own manufacturer in order to edit")
    if request.method == 'POST':
        if request.form['name']:
            Manufacturer_alt.name = request.form['name']
            flash('Manufacturer Successfully Edited %s'
                  % Manufacturer_alt.name)
            return redirect(url_for('Home'))
    else:
        return render_template('editManufacturer.html',
                               manufacturer=Manufacturer_alt)


# route to delete manufacturers
@app.route('/candymanufacturers/<int:manufacturer_id>/delete/',
           methods=['GET', 'POST'])
def deleteManufacturer(manufacturer_id):
    manufacturerToDelete = session.query(Manufacturer). \
        filter_by(id=manufacturer_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if manufacturerToDelete.user_id != login_session['user_id']:
        return flash("You are not authorised to delete this Manufacturer.Please \
        create your own manufacturer in order to delete")
    if request.method == 'POST':
        session.delete(manufacturerToDelete)
        flash('%s Successfully Deleted'
              % manufacturerToDelete.name)
        session.commit()
        return redirect(url_for('Home',
                                manufacturer_id=manufacturer_id))
    else:
        return render_template('deleteManufacturer.html',
                               manufacturer=manufacturerToDelete)


# route to display list of candies for a particualr manufacturer
@app.route('/candymanufacturers/<int:manufacturer_id>/')
@app.route('/candymanufacturers/<int:manufacturer_id>/candies/')
def showCandies(manufacturer_id):
    manufacturer = session.query(Manufacturer). \
        filter_by(id=manufacturer_id).one()
    creator = getUserInfo(manufacturer.user_id)
    candies = session.query(Candy). \
        filter_by(manufacturer_id=manufacturer_id).all()
    if ('username' not in login_session or
            creator.id != login_session['user_id']):
        return render_template('publiccandies.html',
                               candies=candies,
                               manufacturer=manufacturer,
                               creator=creator)
    else:
        return render_template('candies.html',
                               candies=candies,
                               manufacturer=manufacturer,
                               creator=creator)


# route to add new candy to a manufacturer, take details provided by user
@app.route('/candymanufacturers/<int:manufacturer_id>/candies/new/',
           methods=['GET', 'POST'])
def newCandy(manufacturer_id):
    if 'username' not in login_session:
        return redirect('/login')
    manufacturer = session.query(Manufacturer). \
        filter_by(id=manufacturer_id).one()
    if login_session['user_id'] != manufacturer.user_id:
        return flash("You are not authorised to add candies this Manufacturer.Please \
        create your own manufacturer in order to add candies")
    if request.method == 'POST':

        candy = session.query(Candy). \
                    filter_by(name=request.form['name']).first()
        newCandy = Candy(name=request.form['name'],
                         description=request.form['description'],
                         price=request.form['price'],
                         manufacturedat=request.form['manufacturedat'],
                         manufacturer_id=manufacturer_id,
                         user_id=manufacturer.user_id)
        session.add(newCandy)
        session.commit()
        flash('New Candy %s Successfully Created' % (newCandy.name))
        return redirect(url_for('showCandies',
                                manufacturer_id=manufacturer_id))
    else:
        return render_template('newcandy.html',
                               manufacturer_id=manufacturer_id)


# route to edit candy of a manufacturer, take details provided by user
@app.route('/<int:manufacturer_id>/candies/<int:candy_id>/edit',
           methods=['GET', 'POST'])
def editCandy(manufacturer_id, candy_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedCandy = session.query(Candy).filter_by(id=candy_id).one()
    manufacturer = session.query(Manufacturer). \
        filter_by(id=manufacturer_id).one()
    if login_session['user_id'] != manufacturer.user_id:
        return flash("You are not authorised to edit candies of this Manufacturer.Please \
        create your own manufacturer in order to edit candies")
    if request.method == 'POST':
        if request.form['name']:
            editedCandy.name = request.form['name']
        if request.form['description']:
            editedCandy.description = request.form['description']
        if request.form['price']:
            editedCandy.price = request.form['price']
        if request.form['manufacturedat']:
            editedCandy.course = request.form['manufacturedat']
        session.add(editedCandy)
        session.commit()
        flash('Candy Successfully Edited')
        return redirect(url_for('showCandies',
                                manufacturer_id=manufacturer_id))
    else:
        return render_template('editCandies.html',
                               manufacturer_id=manufacturer_id,
                               candy_id=candy_id,
                               candy=editedCandy)


# route to delete candy from a particular manufacturer
@app.route('/<int:manufacturer_id>/candies/<int:candy_id>/delete',
           methods=['GET', 'POST'])
def deleteCandy(manufacturer_id, candy_id):
    if 'username' not in login_session:
        return redirect('/login')
    manufacturer = session.query(Manufacturer). \
        filter_by(id=manufacturer_id).one()
    candyToDelete = session.query(Candy).filter_by(id=candy_id).one()
    if login_session['user_id'] != manufacturer.user_id:
        return flash("You are not authorised to delete candies of this Manufacturer.Please \
        create your own manufacturer in order to delete candies")
    if request.method == 'POST':
        session.delete(candyToDelete)
        session.commit()
        flash('Candy Successfully Deleted')
        return redirect(url_for('showCandies',
                                manufacturer_id=manufacturer_id))
    else:
        return render_template('deleteCandy.html',
                               candy=candyToDelete)


# details of a candy are displayed
@app.route('/candymanufacturers/candy/<int:candy_id>/')
def showCandyDetails(candy_id):

    candy = session.query(Candy).filter_by(id=candy_id).one()
    if candy is not None:

        manufacturer = session.query(Manufacturer). \
            filter_by(id=candy.manufacturer_id).one()
        creator = session.query(User).filter_by(id=candy.user_id).one()

        return render_template("showCandyDetails.html",
                               candy=candy,
                               creator=creator)

    else:
        flash('Candy does not exist.')
        return redirect(url_for('Home'))

if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5059)
