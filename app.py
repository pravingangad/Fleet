# importing libraries
from flask import Flask, request, Response, jsonify
from flask_sqlalchemy import  SQLAlchemy
import json
from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

# creating an instance of the flask app
app = Flask(__name__)

# Configure our Database
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///movie.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.secret_key = "ASDXSSDDFXXXSSSS"
Bootstrap(app)
# Initializing our database
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class User(UserMixin, db.Model):
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(15), unique =True)
	email = db.Column(db.String(50),unique=True)
	password = db.Column(db.String(80), unique=True)

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(int(user_id))

class LoginForm(FlaskForm):
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
	remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
	email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
	username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
	password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80), EqualTo('confirm', message='Passwords must match')])
	confirm  = PasswordField('confirm password', validators=[InputRequired(), Length(min=8, max=80)])


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET','POST'])
def login():
	form = LoginForm()

	if form.validate_on_submit():
		user = User.query.filter_by(username=form.username.data).first()
		if user:
			if check_password_hash(user.password,form.password.data):
				login_user(user, remember=form.remember.data)
				return redirect(url_for('dashboard'))

		return '<h1> Invalid username or password</h1>'

	return render_template('login.html', form=form)

@app.route('/signup', methods=['GET','POST'])
def signup():
	form = RegisterForm()

	if form.validate_on_submit():
		hashed_password = generate_password_hash( form.password.data, method='sha256')
		new_user = User(username=form.username.data, email = form.email.data, password = hashed_password)
		db.session.add(new_user)
		db.session.commit()

		return '<h1> New user created successfully </h1>'

	return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    pagination=db.session.query(Movie.id,Movie.title,Movie.genre,Movie.year,Movie.release_date,Movie.votes,Movie.reviews).all()
    return render_template('dash.html',name=current_user.username,pagination=pagination)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('index'))


# the class Movie will inherit the db.Model of SQLAlchemy
class Movie(db.Model):
    __tablename__ = 'movie'  # creating a table name
    id = db.Column(db.Integer, primary_key=True)  # this is the primary key
    title = db.Column(db.String(80), nullable=False)
    year = db.Column(db.Integer, nullable=False)
    votes = db.Column(db.String(80), nullable=False)
    genre = db.Column(db.String(80), nullable=False)
    release_date = db.Column(db.String(80), nullable=False)
    reviews = db.Column(db.String(80), nullable=False)
    
    def json(self):
        return {'id': self.id, 'title': self.title,
                'year': self.year,'votes':self.votes,
                'genre': self.genre,'release_date':self.release_date,
                'reviews':self.reviews}
        
        
    def add_movie(_title, _year, _votes, _genre, _release_date, _reviews):
            '''function to add movie to database using _title, _year, _genre,_release_date,_reviews
            as parameters'''
            # creating an instance of our Movie constructor
            new_movie = Movie(title=_title, year=_year,votes=_votes, genre=_genre,release_date=_release_date,reviews=_reviews)
            db.session.add(new_movie)  # add new movie to database session
            db.session.commit()  # commit changes to session
        
        
    def get_all_movies():
        '''function to get all movies in our database'''
        return [Movie.json(movie) for movie in Movie.query.all()]

    def get_movie(_id):
        '''function to get movie using the id of the movie as parameter'''
        return [Movie.json(Movie.query.filter_by(id=_id).first())]

    def update_movie(_id, _title, _year,_votes, _genre,_release_date,_reviews):
        '''function to update the details of a movie using the id, title,
        year,votes ,release date , review and genre as parameters'''
        movie_to_update = Movie.query.filter_by(id=_id).first()
        movie_to_update.title = _title
        movie_to_update.year = _year
        movie_to_update.votes = _votes
        movie_to_update.genre = _genre   
        movie_to_update.release_date = _release_date
        movie_to_update.reviews = _reviews
        
        db.session.commit()
        

    def delete_movie(_id):
        '''function to delete a movie from our database using
            the id of the movie as a parameter'''
        Movie.query.filter_by(id=_id).delete()
        # filter movie by id and delete
        db.session.commit()  # commiting the new change to our database
        
        
# route to get all movies
@app.route('/movies', methods=['GET'])
def get_movies():
    '''Function to get all the movies in the database'''
    return jsonify({'Movies': Movie.get_all_movies()})

# route to get movie by id
@app.route('/movies/<int:id>', methods=['GET'])
def get_movie_by_id(id):
    return_value = Movie.get_movie(id)
    return jsonify(return_value)


# route to add new movie
@app.route('/movies', methods=['POST'])
def add_movie():
    '''Function to add new movie to our database'''
    request_data = request.get_json()  # getting data from client
    Movie.add_movie(request_data["title"], request_data["year"],request_data["votes"],
                    request_data["genre"],request_data["release_date"],request_data["reviews"])
    response = Response("Movie added", 201, mimetype='application/json')
    return response

# route to update movie with PUT method
@app.route('/movies/<int:id>', methods=['PUT'])
def update_movie(id):
    '''Function to edit movie in our database using movie id'''
    request_data = request.get_json()
    Movie.update_movie(id, request_data["title"], request_data["year"], request_data["votes"], request_data["genre"], request_data["release_date"], request_data["reviews"]) 
    response = Response("Movie Updated", status=200, mimetype='application/json')
    return response


# route to delete movie using the DELETE method
@app.route('/movies/<int:id>', methods=['DELETE'])
def remove_movie(id):
    '''Function to delete movie from our database'''
    Movie.delete_movie(id)
    response = Response("Movie Deleted", status=200, mimetype='application/json')
    return response


if __name__ == "__main__":
    app.run(port=5000, debug=True)
