#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
from itertools import count
from ntpath import join
import os
import sys
import json
from sre_parse import State
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for, jsonify
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form as BaseForm
from flask_migrate import Migrate

from forms import *
from config import *
from flask_wtf.csrf import CSRFProtect
from sqlalchemy_utils import PhoneNumberType
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

db = SQLAlchemy(app)
migrate = Migrate(app, db)


#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(20), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    website_link = db.Column(db.String(120), nullable=False)
    seeking_talent = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(500), nullable=False)
    shows = db.relationship('Show', cascade="all, delete-orphan", backref=('venue'))
    # artist = db.relationship('Artist', secondary = 'Show', backref=db.backref('artist', lazy=True))
    

    def __repr__(self):
       return f'<Venue {self.name} {self.city} {self.state} >'

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.Unicode(20), nullable=False)
    image_link = db.Column(db.String(500), nullable=False)
    facebook_link = db.Column(db.String(120), nullable=False)
    
    # TODO: implement any missing fields, as a database migration using Flask-Migrate
    genres = db.Column(db.ARRAY(db.String(120)), nullable=False)
    website_link = db.Column(db.String(120), nullable=False)
    seeking_venue = db.Column(db.Boolean, nullable=False)
    seeking_description = db.Column(db.String(500), nullable=False)

    def __repr__(self):
        return f'<Artist {self.name} {self.city} {self.state}>'

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Show(db.Model):
    __tablename__ = 'Show'
    
    id = db.Column(db.Integer, primary_key=True)
    artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), nullable=False)
    venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Show {self.venue_id} {self.artist_id} {self.start_time}>'
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def total_num_of_upcoming_shows(id):
    # return Show.query.filter(Show.start_time > datetime.now(), Show.venue_id==id).count()
    return Venue.query.join(Venue.shows).filter(Show.start_time > datetime.now()).count()

def total_num_of_past_shows(id):
  # return Show.query.filter(Show.start_time < datetime.now(), Show.venue_id==id).count()
  return Venue.query.join(Venue.shows).filter(Show.start_time < datetime.now()).count()

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

  # TODO: replace with real venues data.
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  
  VenuesList=[]

  city_venue = Venue.query.with_entities(Venue.city, Venue.state).distinct().order_by(Venue.city).order_by(Venue.state).all()

  allVenuesList = [] 
  for city, state in city_venue:
    groupedVenues = Venue.query.filter(Venue.city == city, Venue.state == state).all()
    venuesLocation = [city, state, groupedVenues]
    allVenuesList.append(venuesLocation)

  def ResponseObject(responseList):
    for x in responseList:
      object= {
        "city": x[0],
        "state": x[1],
        "venues": []
      }
      
      venues = x[2]
      for y in venues:
        sub_object={
          "id": y.id,
          "name": y.name,
          "num_upcoming_shows": total_num_of_upcoming_shows(y.id)
        }

        object["venues"].append(sub_object)

      VenuesList.append(object)

  ResponseObject(allVenuesList)

  return render_template('pages/venues.html', areas=VenuesList)
  # return render_template('pages/venues.html', areas=data);


@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  # search_term=request.form['search_term']

  # search_result = Venue.query.filter(Venue.name.ilike(f'%{search_term}%')).all()
  # search_count = search_result.count(Venue.name.ilike(f'%{search_term}%')).count()
  # response = searchResponseBody(search_count, search_result)

  search_term=request.form['search_term']
 
  if search_term == "":
         flash('Please specify the name of the venue in your search phrase.')
         return redirect(url_for('venues'))
 
  search_result = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).order_by(Venue.id).all()
  search_count = len(search_result)

def searchResponseBody(search_count, search_result):
  response={
    'count': search_count,
    'data': []
  }
  # prtString = json.dumps(search_count, search_result)
  # print('Error message: ', prtString)

  for result in search_result:
    venue ={
      'id': result.id,
      'name': result.name,
      'num_upcoming_shows': total_num_of_upcoming_shows(result.id)
    }

    response['data'].append(venue)
    return response
  return render_template('pages/search_venues.html', results=response, search_term=request.form('search_term', ''))

  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 2,
  #     "name": "The Dueling Pianos Bar",
  #     "num_upcoming_shows": 0,
  #   }]
  # }
  
  # return render_template('pages/search_venues.html', results=response, search_term=request.form('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  showVenue = Venue.query.get(venue_id)
  print(showVenue)

  def past_shows(venue_id):
    return db.session.query(Show.venue_id, Show.artist_id, Artist.name, Artist.image_link, Show.start_time).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time < datetime.now()).all()

  def upcoming_shows(venue_id):
    return db.session.query(Show.venue_id, Show.artist_id, Artist.name, Artist.image_link, Show.start_time).join(Artist).filter(Show.venue_id == venue_id).filter(Show.start_time > datetime.now()).all()

  VenueData={
  "id": showVenue.id,
  "name": showVenue.name,
  "genres": showVenue.genres,
  "address": showVenue.address,
  "city": showVenue.city,
  "state": showVenue.state,
  "phone": showVenue.phone,
  "website": showVenue.website_link,
  "facebook_link": showVenue.facebook_link ,
  "seeking_talent": showVenue.seeking_talent,
  "seeking_description": showVenue.seeking_description,
  "image_link": showVenue.image_link,
  "past_shows": [],
  "upcoming_shows": [],
  "past_shows_count": total_num_of_past_shows(venue_id),
  "upcoming_shows_count": total_num_of_upcoming_shows(venue_id),
  
  }

  past_shows = past_shows(venue_id)
  for show in past_shows:
    pastShows={
      "artist_id": show.artist_id,
      "artist_name": show.name,
      "artist_image_link": show.image_link,
      "start_time": show.start_time
    }

    VenueData["past_shows"].append(pastShows)

  upcoming_shows = upcoming_shows(venue_id)
  for show in upcoming_shows:
    upcomingShows={
      "artist_id": show.artist_id,
      "artist_name": show.name,
      "artist_image_link": show.image_link,
      "start_time": show.start_time
    }

    VenueData["past_shows"].append(upcomingShows)
    
  return render_template('pages/show_venue.html', venue=VenueData)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route("/venues/create", methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  try:
    form = VenueForm(request.form)
    venue = Venue(
      name = form.name.data,
      city =  form.city.data,
      state = form.state.data,
      address = form.address.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website_link = form.website_link.data,
      seeking_talent = form.seeking_talent.data,
      seeking_description = form.seeking_description.data
      )
    db.session.add(venue)
    db.session.commit()

  # on successful db insert, flash success
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  except:
    db.session.rollback()
    print("MY ERROR MESSAGE: ", sys.exc_info())
    flash('An error occurred. Venue could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html', venue=Venue)

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.
  #deleteVenue = Venue.query.get(venue_id)
  Venue.query.filter_by(id=venue_id).delete()
  try:
    
    db.session.commit()
    flash('Venue was successfully deleted.')
  
  except:
    db.session.rollback()
    print("MY ERROR MESSAGE: ", sys.exc_info())
    flash('An error occurred. Venue could not be deleted.')
  finally:
    db.session.close()

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  return redirect(url_for('home.html'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database
  artists_data = db.session.query(Artist.id, Artist.name).all()

  return render_template('pages/artists.html', artists=artists_data)
  # return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

  # search_term=request.form('search_term', '')
  # search_result = Artist.query.filter(Artist.name.ilike(f'%{search_term}%')).all()
  # search_count = Artist.query.count(Artist.name.ilike(f'%{search_term}%')).count()
  # response = searchResponseBody(search_count, search_result)


  search_term=request.form['search_term']
 
  if search_term == "":
         flash('Please specify the name of the artist in your search phrase.')
         return redirect(url_for('artists'))
 #case sensitive search result
  search_result = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).order_by(Venue.id).all()
  search_count = len(search_result)

def searchResponseBody(search_count, search_result):
  response={
    'count': search_count,
    'data': []
  }

  for result in search_result:
    venue ={
      'id': result.id,
      'name': result.name,
      'num_upcoming_shows': total_num_of_upcoming_shows(result.id)
    }

    response['data'].append(venue)
    return response
  return render_template('pages/search_artists.html', results=response, search_term=request.form('search_term', ''))


  # response={
  #   "count": 1,
  #   "data": [{
  #     "id": 4,
  #     "name": "Guns N Petals",
  #     "num_upcoming_shows": 0,
  #   }]
  # }

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

  showArtist = Artist.query.get(artist_id)
  print(showArtist)

  def past_shows(artist_id):
      return db.session.query(Show.venue_id, Show.artist_id, Artist.name, Artist.image_link, Show.start_time).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time < datetime.now()).all()

  def upcoming_shows(artist_id):
      return db.session.query(Show.venue_id, Show.artist_id, Artist.name, Artist.image_link, Show.start_time).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()

  ArtistData={
  "id": showArtist.id,
  "name": showArtist.name,
  "genres": showArtist.genres,
  "address": showArtist.address,
  "city": showArtist.city,
  "state": showArtist.state,
  "phone": showArtist.phone,
  "website": showArtist.website_link,
  "facebook_link": showArtist.facebook_link ,
  "seeking_talent": showArtist.seeking_talent,
  "seeking_description": showArtist.seeking_description,
  "image_link": showArtist.image_link,
  "past_shows": [],
  "upcoming_shows": [],
  "past_shows_count": total_num_of_past_shows(artist_id),
  "upcoming_shows_count": total_num_of_upcoming_shows(artist_id),
  
  }

  past_shows = past_shows(artist_id)
  for show in past_shows:
    pastShows={
      "artist_id": show.artist_id,
      "artist_name": show.name,
      "artist_image_link": show.image_link,
      "start_time": show.start_time
    }

    ArtistData["past_shows"].append(pastShows)

  upcoming_shows = upcoming_shows(artist_id)
  for show in upcoming_shows:
    upcomingShows={
      "artist_id": show.artist_id,
      "artist_name": show.name,
      "artist_image_link": show.image_link,
      "start_time": show.start_time
    }

    ArtistData["past_shows"].append(upcomingShows)
  return render_template('pages/show_artist.html', artist=ArtistData)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  # TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.get(artist_id)

  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  form = ArtistForm(request.form)
  try:
    edit_artist = Artist.query.get(artist_id)   

    edit_artist.name = form.name.data
    edit_artist.city = form.city.data 
    edit_artist.state = form.state.data
    edit_artist.phone = form.phone.data
    edit_artist.genres = form.genres.data
    edit_artist.facebook_link = form.facebook_link.data
    edit_artist.image_link = form.image_link.data
    edit_artist.website_link = form.website_link.data
    edit_artist.seeking_venue = form.seeking_venue.data
    edit_artist.seeking_description = form.seeking_description.data
    db.session.add(edit_artist)
    db.session.commit()

    flash('Artist ' + form.name.data + ' was successfully updated!')
  
  except:
    db.session.rollback()
    flash('An error occurred. Artist ' + form.name.data + ' could not be updated.')

  finally: 
    db.session.close()

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  
  #populate form with values from venue with ID <venue_id>
  venue = Venue.query.get(venue_id)

  return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  form = VenueForm(request.form)
  try:
    edit_venue = Venue.query.get(venue_id)   

    edit_venue.name = form.name.data
    edit_venue.city = form.city.data 
    edit_venue.state = form.state.data
    edit_venue.address = form.address.data
    edit_venue.phone = form.phone.data
    edit_venue.genres = form.genres.data
    edit_venue.facebook_link = form.facebook_link.data
    edit_venue.image_link = form.image_link.data
    edit_venue.website_link = form.website_link.data
    edit_venue.seeking_talent = form.seeking_talent.data
    edit_venue.seeking_description = form.seeking_description.data
    db.session.add(edit_venue)
    db.session.commit()

    flash('Venue ' + form.name.data + ' was successfully updated!')
  
  except:
    db.session.rollback()
    flash('An error occurred. Venue ' + form.name.data + ' could not be updated.')

  finally: 
    db.session.close()

  return redirect(url_for('show_venue', venue_id=venue_id))


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  
  try:
    form = ArtistForm(request.form)
    artists = Artist(
      name = form.name.data,
      city =  form.city.data,
      state = form.state.data,
      phone = form.phone.data,
      genres = form.genres.data,
      facebook_link = form.facebook_link.data,
      image_link = form.image_link.data,
      website_link = form.website_link.data,
      seeking_venue = form.seeking_venue.data,
      seeking_description = form.seeking_description.data
      )
    db.session.add(artists)
    db.session.commit()
    # form = ArtistForm(request.form)
    # artist = Artist(
    #   name = request.form['name'],
    #   city =  request.form['city'],
    #   State = request.form['state'],
    #   address = request.form['address'],
    #   phone = request.form['phone'],
    #   genres = request.form['genres'],
    #   facebook_link = request.form['facebook_link'],
    #   image_link = request.form['image_link'],
    #   website_link = request.form['website_link'],
    #   seeking_venue = request.form['seeking_venue'],
    #   seeking_description = request.form['description ']
    #   )
    # db.session.add(artist)
    # db.session.commit()

  # on successful db insert, flash success
    flash('Artist ' + form.name.data + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.'
  except:
    db.session.rollback()
    print(sys.exc_info())
    flash('An error occurred. Artist ' + form.name.data + ' could not be listed.')
  finally:
    db.session.close()

  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  
  # displays list of shows at /shows
  # TODO: replace with real venues data.

  shows = db.session.query(Show.venue_id, Venue.name, Show.artist_id, Artist.name, Artist.image_link, Show.start_time).join(Venue).join(Artist).filter(Show.venue_id == Venue.id, Show.artist_id == Artist.id).all()
  print(shows)
  ListOfShows=[]
  for show in shows:
    object={
      "venue_id": show[0],
      "venue_name": show[1],
      "artist_id": show[2],
      "artist_name": show[3],
      "artist_image_link": show[4],
      "start_time": show[5]
    }
    ListOfShows.append(object)
  return render_template('pages/shows.html', shows=ListOfShows)

  
  # data=[{
  #   "venue_id": 1,
  #   "venue_name": "The Musical Hop",
  #   "artist_id": 4,
  #   "artist_name": "Guns N Petals",
  #   "artist_image_link": "https://images.unsplash.com/photo-1549213783-8284d0336c4f?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=300&q=80",
  #   "start_time": "2019-05-21T21:30:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 5,
  #   "artist_name": "Matt Quevedo",
  #   "artist_image_link": "https://images.unsplash.com/photo-1495223153807-b916f75de8c5?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=334&q=80",
  #   "start_time": "2019-06-15T23:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-01T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-08T20:00:00.000Z"
  # }, {
  #   "venue_id": 3,
  #   "venue_name": "Park Square Live Music & Coffee",
  #   "artist_id": 6,
  #   "artist_name": "The Wild Sax Band",
  #   "artist_image_link": "https://images.unsplash.com/photo-1558369981-f9ca78462e61?ixlib=rb-1.2.1&ixid=eyJhcHBfaWQiOjEyMDd9&auto=format&fit=crop&w=794&q=80",
  #   "start_time": "2035-04-15T20:00:00.000Z"
  # }]
  

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  # form = ShowForm()
  try:
    form = ShowForm(request.form)
    show = Show(
        artist_id = form.artist_id.data,
        venue_id = form.venue_id.data,
        start_time = form.start_time.data
    )

    db.session.add(show)
    db.session.commit()

  # on successful db insert, flash success
    flash('Show was successfully listed!')
  except:
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
    db.session.rollback()
    flash('An error occured! Show could not be listed!')

  return render_template('pages/home.html')
  # return render_template('pages/shows.html', shows=Show)

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
    port = int(os.environ[]PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
