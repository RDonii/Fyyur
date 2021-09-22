#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import re
from warnings import showwarning
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from flask_wtf.recaptcha import fields
from sqlalchemy.sql.functions import count
from sqlalchemy.sql.schema import Column
from werkzeug.wrappers import response
from wtforms.validators import Length
from forms import *
from flask_migrate import Migrate
import datetime
from sqlalchemy import func
from sqlalchemy.orm import load_only
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)

# TODO: connect to a local postgresql database+
app.config['SQLALCHEMY_DATABASE_URI']='postgresql://postgres:12814@localhost:5432/fyyur'
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120), nullable=True)
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500), nullable=True)
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('show', backref='Venue', lazy=True)

    def __repr__(self):
        return '<Venue {}>'.format(self.name)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate+

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False, nullable=False)
    seeking_description = db.Column(db.String(500))
    shows = db.relationship('show', backref='Artist', lazy=True)

    def __repr__(self):
        return '<Artist {}>'.format(self.name)


class show(db.Model):
    __tablename__ = 'show'

    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return '<Show {}{}>'.format(self.artist_id, self.venue_id)

    # TODO: implement any missing fields, as a database migration using Flask-Migrate+

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.+
db.session.commit()
db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')

#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.+
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.+

  today = datetime.datetime.now()
  areas = []
  area = Venue.query.with_entities(func.count(Venue.id), Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  for i in area:
    state = i[2]
    city = i[1]
    data_dict = {'city': city,
                 'state': state,
                 'venues': []
    }
    venues = db.session.query(Venue).filter_by(city=city, state=state).all()
    for v in venues:
      v_nmae = v.name
      v_id = v.id
      upcoming_shows = db.session.query(show.id).filter_by(venue_id=v_id).filter(show.start_time>today).all()
      ven_dict = {
        'id': v_id,
        'name': v_nmae,
        'num_upcoming_shows': len(upcoming_shows)
      }
      data_dict["venues"].append(ven_dict)
    areas.append(data_dict)

  data=[{
    "city": "San Francisco",
    "state": "CA",
    "venues": [{
      "id": 1,
      "name": "The Musical Hop",
      "num_upcoming_shows": 0,
    }, {
      "id": 3,
      "name": "Park Square Live Music & Coffee",
      "num_upcoming_shows": 1,
    }]
  }, {
    "city": "New York",
    "state": "NY",
    "venues": [{
      "id": 2,
      "name": "The Dueling Pianos Bar",
      "num_upcoming_shows": 0,
    }]
  }]

  return render_template('pages/venues.html', areas=areas);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.+
  # seach for Hop should return "The Musical Hop".+
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"+

  search_request = request.form.get('search_term', '')

  cols = ['id', 'name']
  resoult = db.session.query(Venue).filter(Venue.name.ilike(f'%{search_request}%')
    ).options(load_only(*cols)).all()

  response={
    "count": len(resoult),
    "data": resoult
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  data ={}
  
  current_venue = Venue.query.get(venue_id)

  today = datetime.datetime.now()
  all_shows = show.query.filter_by(venue_id=venue_id)

  past_shows_dics = all_shows.filter(show.start_time < today).all()
  past_shows = []
  for current_show in past_shows_dics:
    current_artist = Artist.query.get(current_show.artist_id)
    show_dic = {
      'artist_id': current_show.artist_id,
      'artist_name': current_artist.name,
      'artist_image_link': current_artist.image_link,
      'start_time': str(current_show.start_time)
    }
    past_shows.append(show_dic)

  upcoming_shows_dics = all_shows.filter(show.start_time>=today).all()
  upcoming_shows = []
  for single_show in upcoming_shows_dics:
    current_artist = Artist.query.get(single_show.artist_id)
    show_dic = {
      'artist_id': single_show.artist_id,
      'artist_name': current_artist.name,
      'artist_image_link': current_artist.image_link,
      'start_time': str(single_show.start_time)
    }
    upcoming_shows.append(show_dic)

  data = {
    'id': current_venue.id,
    'name': current_venue.name,
    'genres': current_venue.genres,
    'address': current_venue.address,
    'city': current_venue.city,
    'state': current_venue.state,
    'phone': current_venue.phone,
    'website_link': current_venue.website_link,
    'facebook_link': current_venue.facebook_link,
    'seeking_talent': current_venue.seeking_talent,
    'seeking_description': current_venue.seeking_description,
    'image_link': current_venue.image_link,
    'past_shows': past_shows,
    'upcoming_shows': upcoming_shows,
    'past_shows_count': len(past_shows),
    'upcoming_shows_count': len(upcoming_shows)
  }


  data1={
    "id": 1,
    "name": "The Musical Hop",
    "genres": ["Jazz", "Reggae", "Swing", "Classical", "Folk"],
    "address": "1015 Folsom Street",
    "city": "San Francisco",
    "state": "CA",
    "phone": "123-123-1234",
    "website": "https://www.themusicalhop.com",
    "facebook_link": "https://www.facebook.com/TheMusicalHop",
    "seeking_talent": True,
    "seeking_description": "We are on the lookout for a local artist to play every two weeks. Please call us.",
    "image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
    "past_shows": [{
      "artist_id": 4,
      "artist_name": "Guns N Petals",
      "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 2,
    "name": "The Dueling Pianos Bar",
    "genres": ["Classical", "R&B", "Hip-Hop"],
    "address": "335 Delancey Street",
    "city": "New York",
    "state": "NY",
    "phone": "914-003-1132",
    "website": "https://www.theduelingpianos.com",
    "facebook_link": "https://www.facebook.com/theduelingpianos",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1497032205916-ac775f0649ae?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=750&q=80",
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 3,
    "name": "Park Square Live Music & Coffee",
    "genres": ["Rock n Roll", "Jazz", "Classical", "Folk"],
    "address": "34 Whiskey Moore Ave",
    "city": "San Francisco",
    "state": "CA",
    "phone": "415-000-1234",
    "website": "https://www.parksquarelivemusicandcoffee.com",
    "facebook_link": "https://www.facebook.com/ParkSquareLiveMusicAndCoffee",
    "seeking_talent": False,
    "image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
    "past_shows": [{
      "artist_id": 5,
      "artist_name": "Matt Quevedo",
      "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [{
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "artist_id": 6,
      "artist_name": "The Wild Sax Band",
      "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 1,
    "upcoming_shows_count": 1,
  }
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  try:
    name = request.form.get('name')
    city = request.form.get('city')
    state = request.form.get('state')
    address = request.form.get('address')
    phone = request.form.get('phone')
    image_link = request.form.get('image_link')
    genres = request.form.getlist('genres')
    facebook_link = request.form.get('facebook_link')
    website_link = request.form.get('website_link')
    seeking_talent = request.form.get('seeking_talent')
    seeking_description = request.form.get('seeking_description')

    if seeking_talent=='y':
      seeking_talent=True
    else:
      seeking_talent=False

    new_venue = Venue(
      name=name,
      city=city,
      state=state,
      address=address,
      phone=phone,
      image_link=image_link,
      genres=genres,
      facebook_link=facebook_link,
      website_link=website_link,
      seeking_talent=seeking_talent,
      seeking_description=seeking_description
    )

    db.session.add(new_venue)
    db.session.commit()

    db.session.refresh(new_venue)
  # TODO: insert form data as a new Venue record in the db, instead+
  # TODO: modify data to be the data object returned from db insertion+

  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occured. Venue ' + request.form.get('name') + ' could not be listed.')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  finally:
    db.session.close()
    return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  name = Venue.query.get(venue_id).name

  try:
    venue_to_delete = db.session.query(Venue).filter_by(id=venue_id)
    venue_to_delete.delete()
    db.session.commit()
    flash('Venue ' + name + 'was successfully delete.')

  except:
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    return redirect(url_for('index'))
  # TODO: Complete this endpoint for taking a venue_id, and using+
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.+

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database+
  
  cols = ['id', 'name']

  data = db.session.query(Artist).options(load_only(*cols)).all()
  
#  data=[{
#    "id": 4,
#    "name": "Guns N Petals",
#  }, {
#    "id": 5,
#    "name": "Matt Quevedo",
#  }, {
#    "id": 6,
#    "name": "The Wild Sax Band",
#  }]
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.+
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  searched_item = request.form.get('search_term','')
  response = {'count': 0,
              'data': []
  }
  cols = ['id', 'name']
  searched_artist = db.session.query(Artist).filter(Artist.name.ilike(f'%{searched_item}%')).options(load_only(*cols)).all()
  num_upcoming_shows = 0
  response["count"] = len(searched_artist)

  for r in searched_artist:
    i = {
      'id': r.name,
      'name': r.name,
      'num_upcoming_shows': num_upcoming_shows
    }
    response["data"].append(i)

  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id+

  
  data = {}
  today = datetime.datetime.now()
  requested_artist = Artist.query.get(artist_id)
  

  shows = show.query.filter_by(artist_id=artist_id)

  raw_past_shows = shows.filter(show.start_time < today).all()
  past_shows = []
  for single_p_show in raw_past_shows:
      venue = Venue.query.get(single_p_show.venue_id)
      show_data = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(single_p_show.start_time),
      }
      past_shows.append(show_data)

  raw_upcoming_shows = shows.filter(show.start_time >= today).all()
  upcoming_shows = []
  for single_u_show in raw_upcoming_shows:
      venue = Venue.query.get(single_u_show.venue_id)
      show_data = {
                "venue_id": venue.id,
                "venue_name": venue.name,
                "venue_image_link": venue.image_link,
                "start_time": str(single_u_show.start_time),
      }
      upcoming_shows.append(show_data)

  data = {
            "id": requested_artist.id,
            "name": requested_artist.name,
            "genres": requested_artist.genres,
            "city": requested_artist.city,
            "state": requested_artist.state,
            "phone": requested_artist.phone,
            "seeking_venue": False,
            "facebook_link": requested_artist.facebook_link,
            "image_link": requested_artist.image_link,
            "past_shows": past_shows,
            "upcoming_shows": upcoming_shows,
            "past_shows_count": len(past_shows),
            "upcoming_shows_count": len(upcoming_shows),
        }

  data1={
    "id": 4,
    "name": "Guns N Petals",
    "genres": ["Rock n Roll"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "326-123-5000",
    "website": "https://www.gunsnpetalsband.com",
    "facebook_link": "https://www.facebook.com/GunsNPetals",
    "seeking_venue": True,
    "seeking_description": "Looking for shows to perform at in the San Francisco Bay Area!",
    "image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
    "past_shows": [{
      "venue_id": 1,
      "venue_name": "The Musical Hop",
      "venue_image_link": "https://images.unsplash.com/photo-1543900694-133f37abaaa5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=400&q=60",
      "start_time": "2019-05-21T21:30:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data2={
    "id": 5,
    "name": "Matt Quevedo",
    "genres": ["Jazz"],
    "city": "New York",
    "state": "NY",
    "phone": "300-400-5000",
    "facebook_link": "https://www.facebook.com/mattquevedo923251523",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
    "past_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2019-06-15T23:00:00.000Z"
    }],
    "upcoming_shows": [],
    "past_shows_count": 1,
    "upcoming_shows_count": 0,
  }
  data3={
    "id": 6,
    "name": "The Wild Sax Band",
    "genres": ["Jazz", "Classical"],
    "city": "San Francisco",
    "state": "CA",
    "phone": "432-325-5432",
    "seeking_venue": False,
    "image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
    "past_shows": [],
    "upcoming_shows": [{
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-01T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-08T20:00:00.000Z"
    }, {
      "venue_id": 3,
      "venue_name": "Park Square Live Music & Coffee",
      "venue_image_link": "https://images.unsplash.com/photo-1485686531765-ba63b07845a7?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=747&q=80",
      "start_time": "2035-04-15T20:00:00.000Z"
    }],
    "past_shows_count": 0,
    "upcoming_shows_count": 3,
  }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()

  requested = Artist.query.get(artist_id)
  
  artist = {
    'id': requested.id,
    'name': requested.name,
    'city': requested.city,
    'state': requested.state,
    'phone': requested.phone,
    'genres': requested.genres,
    'facebook_link': requested.facebook_link,
    'seeking_venue': requested.seeking_venue,
    'seeking_description': requested.seeking_description,
    'image_link': requested.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>+
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

  try:
        to_update = Artist.query.get(artist_id)
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        facebook_link = request.form.get("facebook_link")
        image_link = request.form.get('image_link')

        to_update.name = name
        to_update.city = city
        to_update.state = state
        to_update.phone = phone
        to_update.facebook_link = facebook_link
        to_update.image_link = image_link
        to_update.genres = genres

        db.session.add(to_update)
        db.session.commit()

        db.session.refresh(to_update)
        flash("The Venue was successfully updated!")

  except:
        db.session.rollback()
        print(sys.exc_info())
        flash(
            "An error occurred. Venue "
            + request.form.get("name")
            + " could not be updated."
        )

  finally:
        db.session.close()

  return redirect(url_for("show_artist", artist_id=artist_id))

  # TODO: take values from the form submitted, and update existing+
  # artist record with ID <artist_id> using the new attributes

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  data = {}

  try:
        requested_venue = Venue.query.get(venue_id)

        data = {
            "id": requested_venue.id,
            "name": requested_venue.name,
            "city": requested_venue.city,
            "state": requested_venue.state,
            "address": requested_venue.address,
            "phone": requested_venue.phone,
            "genres": requested_venue.genres,
            "facebook_link": requested_venue.facebook_link,
            "seeking_talent": requested_venue.seeking_talent,
            "seeking_description": requested_venue.seeking_description,
            "image_link": requested_venue.image_link,
        }

  except:
        print(sys.exc_info())
        flash("Something went wrong. Please try again.")
        return redirect(url_for("index"))

  finally:
        db.session.close()

  # TODO: populate form with values from venue with ID <venue_id>+
  return render_template('forms/edit_venue.html', form=form, venue=data)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):

    try:
        name = request.form.get("name")
        city = request.form.get("city")
        state = request.form.get("state")
        address = request.form.get("address")
        phone = request.form.get("phone")
        genres = request.form.getlist("genres")
        facebook_link = request.form.get("facebook_link")

        venue_to_be_updated = Venue.query.get(venue_id)

        venue_to_be_updated.name = name
        venue_to_be_updated.city = city
        venue_to_be_updated.state = state
        venue_to_be_updated.address = address
        venue_to_be_updated.phone = phone
        venue_to_be_updated.facebook_link = facebook_link
        venue_to_be_updated.genres = genres

        db.session.add(venue_to_be_updated)
        db.session.commit()

        db.session.refresh(venue_to_be_updated)
        flash("This venue was successfully updated!")

    except:
        db.session.rollback()
        print(sys.exc_info())
        flash(
            "An error occurred. Venue "
            + request.form.get("name")
            + " could not be updated."
        )

    finally:
        db.session.close()

    return redirect(url_for("show_venue", venue_id=venue_id))
  # TODO: take values from the form submitted, and update existing+
  # venue record with ID <venue_id> using the new attributes

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    try:
        name = request.form.get('name')
        city = request.form.get('city')
        state = request.form.get('state')
        phone = request.form.get('phone')
        genres = request.form.getlist('genres'),
        facebook_link = request.form.get('facebook_link')
        image_link = request.form.get('image_link')
        seeking_venue=request.form.get('seeking_venue')
        website_link = request.form.get('website_link')
        seeking_description = request.form.get('seeking_description')
        seeking_venue = True if 'seeking_venue' in request.form else False

        new_artist = Artist(name=name, city=city, state=state, phone=phone, genres=genres, facebook_link=facebook_link, image_link=image_link, website_link=website_link, seeking_venue=seeking_venue, seeking_description=seeking_description)
        db.session.add(new_artist)
        db.session.commit()

        flash("Artist " + new_artist.name + " was successfully listed!")

    except:
        db.session.rollback()
        print(sys.exc_info())
        flash(
            "An error occurred. Venue "
            + request.form.get("name")
            + " could not be listed."
        )

    finally:
        db.session.close()
        return render_template("pages/home.html")
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  #flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  #return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  data = []
  all_shows = db.session.query(show).join(Artist).join(Venue).all()

  data = []
  for single_show in all_shows: 
    data.append({
      "venue_id": single_show.venue_id,
      "venue_name": single_show.Venue.name,
      "artist_id": single_show.artist_id,
      "artist_name": single_show.Artist.name, 
      "artist_image_link": single_show.Artist.image_link,
      "start_time": single_show.start_time.strftime('%Y-%m-%d %H:%M:%S')
    })
  
  return render_template('pages/shows.html', shows=data)
  
@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success
    errors = {"invalid_artist_id": False, "invalid_venue_id": False}

    try:
        artist_id = request.form.get("artist_id")
        venue_id = request.form.get("venue_id")
        start_time = request.form.get("start_time")

        # TODO-STEP1: Check if artist is present in the db
        found_artist = Artist.query.get(artist_id)
        if found_artist is None:
            errors["invalid_artist_id"] = True

        # TODO-STEP2: Check if venue is present in the db
        found_venue = Venue.query.get(venue_id)
        if found_venue is None:
            errors["invalid_venue_id"] = True

        # TODO-STEP3: If the above tests pass, add the record to the DB as usual. Else, set the errors above.
        if (errors["invalid_artist_id"] or errors["invalid_venue_id"]):
            print(sys.exc_info())
            db.session.rollback()
        else:
            new_show = show(
                artist_id=found_artist.id,
                venue_id=found_venue.id,
                start_time=start_time,
            )
            db.session.add(new_show)
            db.session.commit()
            flash(
                "The show by "
                + found_artist.name
                + " has been successfully scheduled at the following venue: "
                + found_venue.name
            )

    except:
        print(sys.exc_info())
        db.session.rollback()
        flash("Something went wrong and the show was not created. Please try again.")

    finally:
        db.session.close()

    if errors["invalid_artist_id"] is True:
        flash(
            "There is no artist with id "
            + request.form.get("artist_id")
            + " in our records"
        )
    if errors["invalid_venue_id"] is True:
        flash(
            "There is no venue with id "
            + request.form.get("venue_id")
            + " in our records"
        )

  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
