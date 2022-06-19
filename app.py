#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import collections
from platform import platform
from pprint import pp, pprint
import queue
import sys
import json
from urllib import response
from wsgiref.simple_server import sys_version
import dateutil.parser
import babel
import logging
from logging import Formatter, FileHandler

from flask import jsonify
from forms import *
from models import *
from datetime import datetime




#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

#This is important as python version 3.10 have issues with collections
# I'm using 3.10.4 so i have to conditionally set this 
# see https://stackoverflow.com/questions/69515086/beautifulsoup-attributeerror-collections-has-no-attribute-callable
# and https://docs.python.org/3/whatsnew/3.10.html#removed
if sys.version_info.minor == 10:
  collections.Callable = collections.abc.Callable


#----------------------------------------------------------------------------#
# Functions.
#----------------------------------------------------------------------------#

#This format the errors so as to display the error in a readbale format in the view
def format_errors(form):
  for f,i in form.errors.items():
    form.form_errors.append(f.replace('_', ' ').capitalize() + ' : ' + ' '.join(map(str,i)))

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
  # get the recently listed venues and artists
  venues = Venue.query.order_by(Venue.id.desc()).limit(5).all()
  artists = Artist.query.order_by(Artist.id.desc()).limit(5).all()
  
  return render_template('pages/home.html', artists=artists, venues=venues)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.✅
  # num_upcoming_shows should be aggregated based on number of upcoming shows per venue.✅
  data = list()
  groups = Venue.query.with_entities(Venue.city, Venue.state).group_by(Venue.city, Venue.state).all()
  if not groups: 
    flash('no venues exists') 
    return render_template('pages/venues.html')
  for group in groups:
    venues_list = []
    venues = Venue.query.filter_by(city=group[0], state=group[1]).all()
    for venue in venues:
      venues_list.append({
        "id": venue.id,
        "name": venue.name,
        "num_upcoming_shows": len(Show.query.filter(Show.venue_id == venue.id, Show.start_time > datetime.now()).all())
      })
    data.append({
      "city":group[0],
      "state":group[1],
      "venues":venues_list,
    })
  
  return render_template('pages/venues.html', areas=data)



@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.✅
  # seach for Hop should return "The Musical Hop".✅
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee✅
  data = list()
  s = request.form.get('search_term', '')
  results = Venue.query.filter(Venue.name.ilike(f'%{s}%')| Venue.city.ilike(f'%{s}%')| Venue.state.ilike(f'%{s}%')).all()
  # for each result append the neccesarry data
  for result in results:
    data.append({
      "id": result.id,
      "name": result.name,
      "num_upcoming_shows": len(Show.query.filter(Show.venue_id == result.id, Show.start_time > datetime.now()).all()),
    })
  response = { 'count': len(results), 'data': data }
  
  return render_template('pages/search_venues.html', results=response, search_term=s)



@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id✅
  venue = Venue.query.get(venue_id)
  data = {
    "id": venue.id,
    "name": venue.name,
    "genres": venue.genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website_link": venue.website_link,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  
  #get all Venue Past Shows
  all_past_shows = Show.query.join(Venue).filter(Show.venue_id == venue_id, Show.start_time < datetime.now()).all()
  #pprint(datetime.now().strftime('%Y-%m-%dT%H:%M:%S.%f%z'))
  #get all Venue Upcoming Shows
  all_upcoming_shows = Show.query.join(Venue).filter(Show.venue_id == venue_id, Show.start_time > datetime.now()).all()
  
  #Past shows
  past_shows_list = list()
  for past_show in all_past_shows:
    past_shows_list.append({
      "artist_id": past_show.artist_id,
      "artist_name": past_show.artist.name,
      "artist_image_link": past_show.artist.image_link,
      "start_time": past_show.start_time.isoformat()#strftime('%Y-%m-%dT%H:%M:%S.%f%z')
    })
    
  #Upcoming shows
  upcoming_shows_list = list()
  for upcoming_show in all_upcoming_shows:
    upcoming_shows_list.append({
      "artist_id": upcoming_show.artist_id,
      "artist_name": upcoming_show.artist.name,
      "artist_image_link": upcoming_show.artist.image_link,
      "start_time": upcoming_show.start_time.isoformat()
    })
  
  #for past shows
  data['past_shows'] = past_shows_list
  data['past_shows_count'] = len(past_shows_list)
  #for upcoming shows
  data['upcoming_shows'] = upcoming_shows_list
  data['upcoming_shows_count'] = len(upcoming_shows_list)

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead✅
  # TODO: modify data to be the data object returned from db insertion✅
  form = VenueForm()
  
  if form.validate_on_submit():
    try: 
      new_venue = Venue()
      form.populate_obj(new_venue)
      db.session.add(new_venue)
      db.session.commit()
      flash('Venue ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Venue ' + form.name + ' could not be listed.')
    finally:
      db.session.close()
      return redirect(url_for('index'))
  else:
    format_errors(form)
    return render_template('forms/new_venue.html', form=form)
  


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using✅
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.✅
  error = False
  try:
    db.session.delete(Venue.query.get(venue_id))
    db.session.commit()
  except:
    error = True
    db.session.rollback()
  finally :
    db.session.close()
  return jsonify({'success' : not error })
  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that✅
  # clicking that button delete it from the db then redirect the user to the homepage✅


#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database✅
  artists = Artist.query.with_entities(Artist.id, Artist.name).all()
  if not artists:
    flash('no artists exists') 
  return render_template('pages/artists.html', artists=artists)


@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.✅
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".✅
  # search for "band" should return "The Wild Sax Band".'✅
  
  data = list()
  s = request.form.get('search_term', '')
  results = Artist.query.filter(Artist.name.ilike(f'%{s}%')| Artist.city.ilike(f'%{s}%')| Artist.state.ilike(f'%{s}%')).all()
  for result in results:
    data.append({
      'id': result.id,
      "name": result.name,
      "num_upcoming_shows": len(Show.query.filter(Show.venue_id == result.id, Show.start_time > datetime.now()).all()),
    })
  response = { 'count': len(results), 'data': data }
  
  return render_template('pages/search_artists.html', results=response, search_term=s)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id✅
  artist = Artist.query.get(artist_id)
  
  data = {
    'id': artist.id,
    'name': artist.name,
    'genres': artist.genres,
    'city': artist.city,
    'state': artist.state,
    'phone': artist.phone,
    'website_link': artist.website_link,
    'facebook_link': artist.facebook_link,
    'seeking_venue': artist.seeking_venue,
    'seeking_description': artist.seeking_description,
    'image_link': artist.image_link,
    "past_shows": [],
    "upcoming_shows": [],
    "past_shows_count": 0,
    "upcoming_shows_count": 0,
  }
  
  #get all Venue Past Shows
  all_past_shows = Show.query.join(Artist).filter(Show.artist_id == artist_id, Show.start_time < datetime.now()).all()
  #get all Venue Upcoming Shows
  all_upcoming_shows = Show.query.join(Artist).filter(Show.artist_id == artist_id, Show.start_time > datetime.now()).all()
  
  #Past shows
  past_shows_list = list()
  for past_show in all_past_shows:
    past_shows_list.append({
      'venue_id': past_show.venue_id,
      'venue_name': past_show.venue.name,
      'venue_image_link': past_show.venue.image_link,
      'start_time': past_show.start_time.isoformat()
    })
    
  #Upcoming shows
  upcoming_shows_list = list()
  for upcoming_show in all_upcoming_shows:
    upcoming_shows_list.append({
      'venue_id': upcoming_show.venue_id,
      'venue_name': upcoming_show.venue.name,
      'venue_image_link': upcoming_show.venue.image_link,
      'start_time': upcoming_show.start_time.isoformat()
    })
  
  
  data['past_shows'] = past_shows_list
  data['past_shows_count'] = len(past_shows_list)
  
  data['upcoming_shows'] = upcoming_shows_list
  data['upcoming_shows_count'] = len(upcoming_shows_list)
  
  return render_template('pages/show_artist.html', artist=data)


#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  artist = Artist.query.get(artist_id)
  if artist:
    form = ArtistForm(obj=artist)   
  else:
    form = ArtistForm()
    flash('Artist not found')
  # TODO: populate form with fields from artist with ID <artist_id>✅
  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing✅
  # artist record with ID <artist_id> using the new attributes
  artist = Artist.query.get(artist_id)
  
  form = ArtistForm(obj=artist)
  if form.validate_on_submit():
    try:
      form.populate_obj(artist)
      db.session.add(artist)
      db.session.commit()
      flash('Artist information edited successfully!')
    except:
      db.session.rollback()
      flash('An error occurred while editing the artist information')
    finally:
      db.session.close()
  else:
    format_errors(form)
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  
  return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  venue = Venue.query.get(venue_id)
  if venue:
    form = VenueForm(obj=venue)  
  else:
    form = VenueForm()
    flash('Venue not found')
    return redirect(url_for('venues'))
  # TODO: populate form with values from venue with ID <venue_id>✅
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing✅
  # venue record with ID <venue_id> using the new attributes
  venue = Venue.query.get(venue_id)
  
  form = VenueForm(obj=venue)
  if form.validate_on_submit():
    try:
      form.populate_obj(venue)
      pprint(venue.__dict__)
      db.session.add(venue)
      db.session.commit()
      flash('Venue updated successfully!')
    except:
      db.session.rollback()
      flash('An error occurred while updating venue')
    finally:
      db.session.close() 
  else:
    format_errors(form)
    return render_template('forms/edit_venue.html', form=form, venue=venue)
  
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
  form = ArtistForm()
  if form.validate_on_submit():
    try: 
      new_artist = Artist()
      form.populate_obj(new_artist)
      db.session.add(new_artist)
      db.session.commit()
      flash('Artist ' + request.form['name'] + ' was successfully listed!')
    except:
      db.session.rollback()
      flash('An error occurred. Artist ' + form.name + ' could not be listed.')
    finally:
      db.session.close()
  else:
    format_errors(form)
    return render_template('forms/new_artist.html', form=form)
  
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.✅
  
  shows = Show.query.all()
  if not shows:
    flash('No show exists')
    render_template('pages/shows.html', shows=[])
  else:
    data = list()
    for show in Show.query.all():
      data.append({
        'venue_id': show.venue.id,
        'venue_name': show.venue.name,
        'artist_id': show.artist.id,
        'artist_name': show.artist.name,
        'artist_image_link': show.artist.image_link,
        'start_time': show.start_time.isoformat()
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
  form = ShowForm()
  #pprint(form.venue_id.__dict__)
  if form.validate_on_submit():
    try:
      venue_id = form.venue_id.data
      artist_id = form.artist_id.data
      if not Artist.query.get(artist_id):
        flash('Artist ID does not exist')
      elif not Venue.query.get(venue_id):
        flash('Venue ID does not exist')
      else:
        new_show = Show()
        form.populate_obj(new_show)
        pprint(new_show)
        db.session.add(new_show)
        db.session.commit()
        flash('Show was successfully listed!')  
    except:
      db.session.rollback()
      flash('Show could not be listed.')
    finally:
      db.session.close()
  else:
    format_errors(form)
    return render_template('forms/new_show.html', form=form)
  
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
