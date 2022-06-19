from datetime import datetime
from flask_wtf import FlaskForm as Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, ValidationError
from wtforms.validators import DataRequired, AnyOf, URL, StopValidation
import re
from models import Artist, Venue
from enums import Genre, State

genres_choices = Genre.choices()
state_choices = State.choices()


# validate artist id and venue id to ensure it is a an int and it also exist in the db  
def validate_model_id(field, model):
    if not re.search(r"[0-9]", field.data):
        raise ValidationError('must be an integer')
    if not model.query.get(field.data):
         raise ValidationError('does not exist.')

#enums validator for both single and multiple select fields
def validate_enums(enum_choices, field):
    field_data = list()
    enum_values = [choice[1] for choice in enum_choices]
    field_data = field.data if  isinstance(field.data, list) else [field.data]
    for value in field_data:
        if value not in enum_values:
            raise ValidationError()


#phone number validator for VenueForm and ArtistForm
def validate_phone(form, field):
    if not re.search(r"^[0-9]{3}-[0-9]{3}-[0-9]{4}$", field.data):
        raise ValidationError('Invalid phone number.')

#Artist ID validator for ShowForm
def validate_artist_id(form,field):
    validate_model_id(field, Artist)

#Venue ID validator for ShowForm
def validate_artist_id(form,field):
    validate_model_id(field, Artist)
    
def validate_show_start_date(form,field):
    if field.data < datetime.today():
        raise ValidationError('Time cannot be a date/time in the past')
 
# state fields validator (non multiple select field) for VenueForm and ArtistForm
def validate_state(form, field):           
    validate_enums(state_choices, field)

# genres fields validator (multiple select field)  for VenueForm and ArtistForm
def validate_genres(form, field):
    validate_enums(genres_choices, field)    

class ShowForm(Form):
    artist_id = StringField(
        'artist_id',
        validators=[DataRequired(), validate_artist_id]
    )
    venue_id = StringField(
        'venue_id',
        validators=[DataRequired(), validate_artist_id]
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired(), validate_show_start_date],
        default= datetime.today()
    )

class VenueForm(Form):         
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        # TODO implement enum restriction✅
        'state', validators=[DataRequired(), validate_state],
        choices = state_choices
    )
    address = StringField(
        'address', validators=[DataRequired()]
    )
    phone = StringField(
        # TODO implement validation for phone number✅
        'phone', validators= [validate_phone]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction✅
        'genres', validators=[DataRequired(), validate_genres],
        choices = genres_choices,
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    website_link = StringField(
        'website_link'
    )

    seeking_talent = BooleanField( 'seeking_talent' )

    seeking_description = StringField(
        'seeking_description'
    )



class ArtistForm(Form):      
    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired()]
    )
    state = SelectField(
        # TODO implement enum restriction✅
        'state', validators=[DataRequired(), validate_state],
        choices = state_choices
    )
    phone = StringField(
        # TODO implement validation for phone number✅
        'phone', validators=[DataRequired(), validate_phone]
    )
    image_link = StringField(
        'image_link'
    )
    genres = SelectMultipleField(
        # TODO implement enum restriction✅
        'genres', validators=[DataRequired(), validate_genres],
        choices = genres_choices 
     )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
     )

    website_link = StringField(
        'website_link'
     )

    seeking_venue = BooleanField( 'seeking_venue' )

    seeking_description = StringField(
            'seeking_description'
     )

