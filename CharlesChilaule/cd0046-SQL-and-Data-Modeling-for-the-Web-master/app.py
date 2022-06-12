#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
from urllib import response
from flask_migrate import Migrate
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
import psycopg2.extras, psycopg2
from logging import Formatter, FileHandler
from flask_wtf import Form
from sqlalchemy import ForeignKey
from forms import *
import sys
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

# dabname="flyyur"
# user1="postgres"
# passwor="Mchingis123"
# hostn="localhost"
app = Flask(__name__)
moment = Moment(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Mchingis123@localhost:5432/flyyurtest'

#conn = psycopg2.connect(dbname=dabname, user=user1, password=passwor, host=hostn)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
#app.config.from_object('config')
app.secret_key = 'super secret key'
app.config['SESSION_TYPE'] = 'filesystem'
db = SQLAlchemy(app)


# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

migrate = Migrate(app, db)

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    genres = db.Column(db.ARRAY(db.String))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(100))
    seekingTalent = db.Column(db.Boolean(), default=False)
    seekingDescription = db.Column(db.String(200))
    aritistShows = db.relationship('Show', backref="venue")
    createdAt = db.Column(db.DateTime())
    

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    website = db.Column(db.String(100))
    seekingVenue = db.Column(db.Boolean(), default=False)
    seekingDescription = db.Column(db.String(200))
    shows = db.relationship('Show', backref="artist")
    createdAt = db.Column(db.DateTime())

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

class Show(db.Model):
  __tablename__ = 'shows'
  id = db.Column(db.Integer, primary_key=True)
  artistId = db.Column(db.Integer, ForeignKey(Artist.id), nullable=False)
  venueId = db.Column(db.Integer, ForeignKey(Venue.id), nullable=False)
  showDateTime = db.Column(db.DateTime())

# create tables
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
@app.route('/venues')
def venues():

        #get city names
        cities = Venue.query.with_entities(Venue.city, Venue.state).distinct().all()
        data = []
        for temp in cities:
            venues_list = []
            #get venue names
            venues_query = Venue.query.filter_by(city=temp.city).filter_by(state=temp.state).all()
            for venue in venues_query:
                venues_list.append({
                    "id": venue.id,
                    "name": venue.name,
                    "num_upcoming_shows": len([])
                })
                
            data.append({
                "city": temp.city,
                "state": temp.state,
                "venues": venues_list
            })

        return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
        temp = request.form.get('search_term')
        temp = "%{}%".format(temp)

        query = Venue.query.filter(Venue.name.ilike(temp) | Venue.city.ilike(temp) |Venue.address.ilike(temp) | Venue.state.ilike(temp)).all()
        data = []
        for value in query:
            data.append({
                "id": value.id,
                "name": value.name,
              
                "num_upcoming_shows": "non"
            })
        response={
            "count": len(query),
            "data": data
        }
        print(response)
        return render_template('pages/search_venues.html',
                               results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id

        venue = Venue.query.filter_by(id=venue_id).first()
        pastShows = []
        upcomingShows = []
        for show in venue.aritistShows:
            show_data = {
                "artist_id": show.artistId,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.showDateTime.strftime('%Y-%m-%d %H:%M:%S'),
            }
            if datetime.now() > show.showDateTime:
                pastShows.append(show_data)
            else:
                upcomingShows.append(show_data)

        data = {
            "id": venue.id,
            "name": venue.name,
            "genres": venue.genres,
            "city": venue.city,
            "state": venue.state,
            "address": venue.address,
            "phone": venue.phone,
            "website": venue.website,
            "seeking_talent": venue.seekingTalent,
            "image_link": venue.image_link,
            "facebook_link": venue.facebook_link,
            "seeking_description": venue.seekingDescription,
            "past_shows": pastShows,
            "past_shows_count": len(pastShows),
            "upcoming_shows": upcomingShows,
            "upcoming_shows_count": len(upcomingShows)
        }

        return render_template('pages/show_venue.html', venue=data)
#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

        error = False
        try:

            venue = Venue(name=request.form['name'], city=request.form['city'], state=request.form['state'], address=request.form['address'], phone=request.form['phone'],
                        genres=request.form.getlist('genres'),website=request.form['website'],facebook_link=request.form['image_link'], image_link=request.form['image_link'],
                         seekingTalent=bool(request.form['seeking_talent']), seekingDescription=request.form['seeking_description'],
                        createdAt=datetime.now())

            db.session.add(venue)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            
        finally:
            db.session.close()
        
        if error:
            flash('An error occurred.')
        if not error:
            flash('The Venue ' + request.form['name'] + ' is successfully listed!')
        
        return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
        error=False
        try:
            venue = Venue.query.get(venue_id)
           
            db.session.delete(venue)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            
        finally:
            db.session.close()

        if error:
            flash(f'An error occurre.')
        if not error:
            flash('Venue was successfully removed.')

        return redirect(url_for('home.index'))
#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

#get artist information
        query = Artist.query.all()
        data = []
        #assigning id and name 
        for item in query:
            data.append({
              "id": item.id,
              "name": item.name,
            })

        return render_template('pages/artists.html', artists=data)



@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".

        temp = request.form.get('search_term')
        temp = "%{}%".format(temp)
        #search by name,genre and city
        query = Artist.query.filter(Artist.name.ilike(temp)| Artist.genres.ilike(temp)|Artist.city.ilike(temp)|Artist.state.ilike(temp)).all()
        data = []
        for item in query:
            data.append({
              "id": item.id,
              "name": item.name,
              "num_upcoming_shows": 0
            })
        response={
          "count": len(query),
          "data": data
        }
        return render_template('pages/search_artists.html',
                                results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id

        artist = Artist.query.filter_by(id=artist_id).first()
        pastShows = []
        upcomingShows = []
        for show in artist.shows:
            show_data = {
                "artist_id": show.artistId,
                "artist_name": show.artist.name,
                "artist_image_link": show.artist.image_link,
                "start_time": show.showDateTime.strftime('%Y-%m-%d %H:%M:%S'),
            }
            if datetime.now() > show.showDateTime:
                pastShows.append(show_data)
            else:
                upcomingShows.append(show_data)

        data = {
            "id": artist.id,
            "name": artist.name,
            "genres": artist.genres,
            "city": artist.city,
            "state": artist.state,
            "phone": artist.phone,
            "website": artist.website,
            "image_link": artist.image_link,
            "facebook_link": artist.facebook_link,
            "seeking_venue": artist.seekingVenue,
            "seeking_description": artist.seekingDescription,
            "past_shows": pastShows,
            "past_shows_count": len(pastShows),
            "upcoming_shows": upcomingShows,
            "upcoming_shows_count": len(upcomingShows)
        }

        return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
# TODO: populate form with fields from artist with ID <artist_id>
  artist = Artist.query.filter_by(id=artist_id).first()

  form.name.data = artist.name
  form.city.data = artist.city
  form.state.data = artist.state
  form.genres.data = artist.genres
  form.phone.data = artist.phone
  form.facebook_link.data = artist.facebook_link
  form.image_link.data = artist.image_link

  return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):

        artist = Artist.query.get(artist_id)
        error = False
        try:
            artist.name = request.form['name']
            artist.city = request.form['city']
            artist.state = request.form['state']
            artist.genres = request.form.getlist('genres')
            artist.phone = request.form['phone']
            artist.image_link = request.form['image_link']
            artist.facebook_link = request.form['facebook_link']
        
            db.session.commit()
        except:
          
            db.session.rollback()
            
        finally:
            db.session.close()


        return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
        form = VenueForm()
        form = VenueForm()
        venue = Venue.query.filter_by(id=venue_id).first()

        form.seeking_talent.default = venue.seekingTalent
        form.process()

        form.name.data = venue.name
        form.city.data = venue.city
        form.state.data = venue.state
        form.genres.data = venue.genres
        form.address.data = venue.address
        form.phone.data = venue.phone
        form.website_link.data = venue.website
        form.facebook_link.data = venue.facebook_link
        form.image_link.data = venue.image_link
        form.seeking_description.data = venue.seekingDescription

        return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
        venue = Venue.query.get(venue_id)
        error = False
        try:
            venue.name = request.form['name']
            venue.city = request.form['city']
            venue.state = request.form['state']
            venue.address = request.form['address']
            venue.genres = request.form.getlist('genres')
            venue.phone = request.form['phone']
            venue.image_link = request.form['image_link']
            venue.facebook_link = request.form['facebook_link']
            venue.website = request.form['website']
            venue.seekingTalent = json.loads(request.form['seeking_talent'].lower())
            venue.seekingDescription = request.form['seeking_description']

            db.session.commit()
        except:
            error = True
            db.session.rollback()
           
        finally:
            db.session.close()
      
        if error:
            flash('An error occurred.')
        if not error:
            flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('venues.show_venue', venue_id=venue_id))

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
  # on successful db insert, flash success

        error= False
       
        try:
            name = request.form['name']
            city = request.form['city']
            state = request.form['state']
            genres = request.form.getlist('genres')
            phone = request.form['phone']
            image_link = request.form['image_link']
            facebook_link = request.form['facebook_link']
            website = request.form['website']
            seeking_venue = json.loads(request.form['seeking_venue'].lower())
            seeking_description = request.form['seeking_description']
            created_at = datetime.now()
            artist = Artist(name=name, city=city, state=state, phone=phone,
                        genres=genres,facebook_link=facebook_link, image_link=image_link,
                        website=website, seekingVenue=seeking_venue, seekingDescription=seeking_description,
                        createdAt=created_at)
            db.session.add(artist)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            print(sys.exc_info())
        finally:
            db.session.close()

        if error:
            
            flash('An error occurred.')
        if not error:
           
            flash('Artist ' + request.form['name'] + ' was successfully listed!')
      
        return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
       
        query_data = Show.query.all()
        data = []
        for item in query_data:
            data.append({
              "venue_id": item.venueId,
              "venue_name": item.venue.name,
              "artist_id": item.artistId,
              "artist_name": item.artist.name,
              "artist_image_link": item.artist.image_link,
              "start_time": item.showDateTime.strftime('%Y-%m-%d %H:%M:%S')
            })
        return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
        error = False
       
        try:
            artistId = request.form['artist_id']
            venueId = request.form['venue_id']
            startTime = request.form['start_time']
            show = Show(artist_id=artistId, venue_id=venueId, start_time=startTime)
            db.session.add(show)
            db.session.commit()
        except:
            error = True
            db.session.rollback()
            
        finally:
            db.session.close()

        if error:
           
            flash('An error occurred.')
        if not error:
            
            flash('Show was successfully listed!')
        
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
