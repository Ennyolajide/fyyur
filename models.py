#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
from sqlalchemy import null

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db = SQLAlchemy(app)
migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    website_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.Text)
    
    shows = db.relationship('Show', back_populates='venue', viewonly=True)
    
    artists = db.relationship('Artist', secondary='show', back_populates='venues', cascade='all, delete')

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, unique=True)
    city = db.Column(db.String(120), nullable=False)
    state = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(120))
    website_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.Text)
    
    shows = db.relationship('Show', back_populates='artist',viewonly=True )
    
    venues = db.relationship('Venue', secondary='show', back_populates='artists', cascade='all, delete')
    
    albums = db.relationship('Album')
    

class Show(db.Model):
    __tablename__ = 'show'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    start_time = db.Column(db.DateTime)
    
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id', ondelete='CASCADE'), primary_key = True)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id', ondelete='CASCADE'), primary_key = True)
    
    venue = db.relationship('Venue', back_populates = 'shows', viewonly=True)
    artist = db.relationship('Artist', back_populates= 'shows', viewonly=True)
    
    # venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), primary_key = True)
    # artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), primary_key = True)
    
class Album(db.Model):
    __tablename__ = 'album'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    
    songs = db.relationship('Song')
    
class Song(db.Model):
    __tablename__ = 'song'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    
    album_id = db.Column(db.Integer, db.ForeignKey('album.id'))
    
class Availability(db.Model):
    __tablename__ = 'availability'
    
    id = db.Column(db.Integer, primary_key=True)
    form_date = db.Column(db.DateTime, nullable=False)
    to_date = db.Column(db.DateTime, nullable=False)
    
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'))
    
    