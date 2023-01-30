# import the function that will return an instance of a connection
from flask_app.config.mysqlconnection import connectToMySQL
from flask_app.models import user_model as u
from flask_app import DATABASE
from flask_app import bcrypt
# model the class after the user table from our database
from flask import flash #Flash for validations
import re	# the regex module
DATE_SEEN_REGX = re.compile(r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$')

class Sighting:
	def __init__(self, data):
		self.id = data['id']
		self.location = data['location']
		self.content = data['content']
		self.num_seen = data['num_seen']
		self.date_seen = data['date_seen']
		self.user_id = data['user_id']
		self.users = []
		self.created_at = data['created_at']
		self.updated_at = data['updated_at']	

	
	# This method will retrieve the specific topping along with all the burgers associated with it.
	@classmethod
	def get_sighting_with_skeptics( cls , data ):
		query = """SELECT * FROM sightings 
		LEFT JOIN skeptics ON skeptics.sighting_id = sightings.id 
		LEFT JOIN users ON skeptics.user_id = users.id
		WHERE sightings.id = %(id)s;"""
		results = connectToMySQL(DATABASE).query_db( query , data )
		# results will be a list of topping objects with the burger attached to each row. 
		skeptic = cls( results[0] )
		if results[0]['users.id'] != None:
			for row_from_db in results:
				print("row_db",row_from_db)
				# Now we parse the topping data to make instances of toppings ="keyword from-rainbow">and add them into our list.
				user_data = {
					"id" : row_from_db["users.id"],
					"fname" : row_from_db["fname"],
					"lname" : row_from_db["lname"],
					"email" : row_from_db["email"],
					"password" : row_from_db["password"], #Hashed
					"created_at" : row_from_db["users.created_at"],
					"updated_at" : row_from_db["users.updated_at"]
				}
				skeptic.users.append( u.User( user_data ) )
		return skeptic



	@staticmethod
	def validate_sighting(data):
		is_valid = True # we assume this is true
		if len(data['location']) < 3:
			flash("Location must be at least 3 letters.", "err_sighting_location_count")
			is_valid = False
		else:
			potential_sighting = Sighting.get_by_location({'location' :data['location']}) # Match by location
			if potential_sighting:
				if str(potential_sighting.id) != data['id']:# Is edit sighting id different from potential sighting id?
					flash("Location exists and must be unique.", "err_sighting_location_exists")
					is_valid = False
		if len(data['content']) < 20:
			flash("Content must be at least 20 characters.", "err_sighting_content_count")
			is_valid = False
		if len(data['date_seen']) < 4 or not DATE_SEEN_REGX.match(data['date_seen']):
			flash("Invalid date.", "err_sighting_date_syntax")
			is_valid = False
		if len(data['num_seen']) < 1 or data['num_seen'] == '0':
			flash("Only sasquatch sightings may be posted.", "err_sighting_num_seen_zero")
			is_valid = False

		return is_valid
	
	
	# ========== READ ALL ===============
	@classmethod
	def get_all(cls):
		query = "SELECT * FROM sightings;"

		results = connectToMySQL(DATABASE).query_db(query)
		all_users = []
		[all_users.append(cls(users)) for users in results]
				
		return all_users
	
	# ========== READ one to one ===============
	@classmethod
	def get_one_sightings_users(cls, data ):
		query = """SELECT * 
		FROM sightings
		LEFT JOIN users ON user_id=users.id
		WHERE sightings.id = %(id)s;"""

		results = connectToMySQL(DATABASE).query_db(query,data)
		print("Resuls----&&&&&&&&&&&&&&&&&&&&&\n",results)
		sighting_reporter = cls( results[0] )
		if results[0]['users.id'] != None:
			for row_from_db in results:

				user_data = {
					"id" : row_from_db["users.id"],
					"fname" : row_from_db["fname"],
					"lname" : row_from_db["lname"],
					"email" : row_from_db["email"],
					"password" : row_from_db["password"], #Hashed
					"created_at" : row_from_db["users.created_at"],
					"updated_at" : row_from_db["users.updated_at"]
				}
				sighting_reporter.users.append( u.User( user_data ) )
		return sighting_reporter
	

	# ========== READ all ===============
	@classmethod
	def get_all_sightings_users(cls):
		query = """SELECT * 
		FROM sightings
		LEFT JOIN users ON user_id=users.id
		;"""

		results = connectToMySQL(DATABASE).query_db(query)
		print("Resuls----&&&&&&&&&&&&&&&&&&&&&\n",results)
		sighting_reporter = cls( results[0] )
		if results[0]['users.id'] != None:
			for row_from_db in results:
				# print("row_db",row_from_db)
				# Now we parse the topping data to make instances of toppings ="keyword from-rainbow">and add them into our list.
				user_data = {
					"id" : row_from_db["users.id"],
					"fname" : row_from_db["fname"],
					"lname" : row_from_db["lname"],
					"email" : row_from_db["email"],
					"password" : row_from_db["password"], #Hashed
					"created_at" : row_from_db["users.created_at"],
					"updated_at" : row_from_db["users.updated_at"]
				}
				sighting_reporter.users.append( u.User( user_data ) )
		return sighting_reporter
	
	
	# ========== READ ONE ===============
	@classmethod
	def get_by_location(cls, data):
		query = """
			SELECT *
			FROM sightings
			WHERE location = %(location)s;
		"""
		results = connectToMySQL(DATABASE).query_db(query, data)
		print(f"The results: {results}")
		if results:
			return cls(results[0])
		return []
	
	# ========== READ ONE ===============
	@classmethod
	def get_one_by_id(cls, data):
		query = """
			SELECT *
			FROM sightings
			WHERE sightings.id = %(id)s;
		"""
		results = connectToMySQL(DATABASE).query_db(query, data)
		print(f"The results: {results}")
		if results:
			return cls(results[0])
		return []


	# ============ CREATE ==============
	@classmethod
	def create_sighting(cls, data):
		query = """
			INSERT INTO sightings (location,content,num_seen,date_seen,user_id)
			VALUES (%(location)s,%(content)s,%(num_seen)s,%(date_seen)s,%(user_id)s);
		"""
		return connectToMySQL(DATABASE).query_db(query, data)
	
	# ============ UPDATE ==============
	@classmethod
	def update(cls, data):
		query = """
			UPDATE sightings
			SET id=%(id)s,location=%(location)s,content= %(content)s,num_seen=%(num_seen)s,date_seen=%(date_seen)s
			WHERE id=%(id)s
		"""
		return connectToMySQL(DATABASE).query_db(query, data)
	
	# ============ DELETE ==============
	@classmethod
	def delete(cls, data):
		query = """
			DELETE FROM sightings
			WHERE id=%(id)s
		"""
		return connectToMySQL(DATABASE).query_db(query, data)