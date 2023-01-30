# import the function that will return an instance of a connection
from flask_app.config.mysqlconnection import connectToMySQL
# from flask_app.models import user_model as u
from flask_app import DATABASE
from flask_app import bcrypt
from flask_app.models import sighting_model as s
# model the class after the user table from our database
from flask import flash #Flash for validations
import re	# the regex module
# create a regular expression object that we'll use later   
EMAIL_REGX = re.compile(r'^[a-zA-Z0-9.+_-]+@[a-zA-Z0-9._-]+\.[a-zA-Z]+$') 
USERNAME_REGX = re.compile(r'[a-zA-Z]{2,}')
PASSWORD_REGX = re.compile(r'^[A-Z]{1,}[a-z]{2,}[0-9]{1,}$')

class User:
	def __init__(self, data):
		self.id = data['id']
		self.fname = data['fname']
		self.lname = data['lname']
		self.email = data['email']
		self.password = data['password']
		self.created_at = data['created_at']
		self.updated_at = data['updated_at']
		self.sightings = []


	# This method will retrieve the burger with all the toppings that are associated with the burger.
	@classmethod
	def get_user_with_sightings( cls , data ):
		query = """SELECT * FROM users
		LEFT JOIN skeptics ON skeptics.user_id = users.id 
		LEFT JOIN sightings ON skeptics.sighting_id = sightings.id
		WHERE users.id = %(id)s;"""
		results = connectToMySQL(DATABASE).query_db( query , data )
		# results will be a list of topping objects with the burger attached to each row. 
		user = cls( results[0] )
		for row_from_db in results:
			# Now we parse the topping data to make instances of toppings and add them into our list.
			sighting_data = {
				"id" : row_from_db["sightings.id"],
				# "sighting_name" : row_from_db["sighting_name"], handling conflicts
				"location" : row_from_db["location"],
				"content" : row_from_db["content"],
				"num_seen" : row_from_db["num_seen"],
				"date_seen" : row_from_db["date_seen"],
				"created_at" : row_from_db["sightings.created_at"],
				"updated_at" : row_from_db["sightings.updated_at"]
			}
			user.sightings.append( s.Sighting( sighting_data ) )
		return user


	@staticmethod
	def validate_create(data):
		is_valid = True # we assume this is true
		if len(data['fname']) < 2:
			flash("First Name must be at least 3 letters.", "err_user_fname_count")
			is_valid = False
		if not USERNAME_REGX.match(data['fname']):
			flash("First Name, only letters allowed.", "err_user_fname_complexity")
			is_valid = False
		if len(data['lname']) < 2:
			flash("Last Name must be at least 3 characters.", "err_user_lname_count")
			is_valid = False
		if not USERNAME_REGX.match(data['lname']):
			flash("Last Name, only letters allowed.", "err_user_lname_complexity")
			is_valid = False
		if len(data['email']) < 2 or not EMAIL_REGX.match(data['email']):
			flash("Email invalid.", "err_user_email")
			is_valid = False
		else:
			potential_user = User.get_by_email({'email' :data['email']})
			print("User Not Found: ",potential_user )
			if potential_user:
				flash("Email in use.", "err_user_email_exists")
				is_valid = False
		if len(data['password']) < 8:
			flash("Password must be at least 8 characters.", "err_user_password")
			is_valid = False
		if not PASSWORD_REGX.match(data['password']):
			flash("Password is not complex enough.", "err_user_password_complexity")
			is_valid = False
		if data['password-confirm'] != data['password'] :
			flash("Password confirmation does not match.", "err_user_password-confirm")
			is_valid = False
		return is_valid
	
	@staticmethod
	def validate_user(user,data):
		is_valid = True
		if not EMAIL_REGX.match(data['email']): 
			flash("Invalid email address!", "err_user_login_email")
			is_valid = False
		if len(data['password']) < 3:
			flash("Password must be at least 3 characters.", "err_user_login_password")
			is_valid = False
		if not bcrypt.check_password_hash(user.password, data['password']):
			flash("Password does not match.", "err_user_login_password")
			is_valid = False
		return is_valid


	
	# ========== READ ALL ===============
	@classmethod
	def get_all(cls):
		query = "SELECT * FROM users;"
		all_users = [] # Create an empty list to append our instances of users
		results = connectToMySQL(DATABASE).query_db(query) # make sure to call the connectToMySQL function with the schema you are targeting.
		[all_users.append(cls(users)) for users in results] # Iterate over the db results and create instances of users with cls.
				
		return all_users
	
	# ========== READ ONE ===============
	@classmethod
	def get_by_email(cls, data):
		query = """
			SELECT *
			FROM users
			WHERE email = %(email)s;
		"""
		results = connectToMySQL(DATABASE).query_db(query, data)
		print(f"The results: {results}")
		if results:
			return cls(results[0])
		return []
	
	# ========== READ ONE ===============
	@classmethod
	def get_by_password(cls, data):
		query = """
			SELECT *
			FROM users
			WHERE password = %(password)s;
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
			FROM users
			WHERE id = %(id)s;
		"""
		results = connectToMySQL(DATABASE).query_db(query, data)
		print(f"The results: {results}")
		if results:
			return cls(results[0])
		return []

	# ========== READ ALL ===============
	# @classmethod
	# Pair Programmed with Renan
	# def get_x_by_y_id(cls,data):
	# 	query = """
	# 		SELECT * 
	# 		FROM users
	# 		LEFT JOIN ninjas on dojos.id = ninjas.dojo_id 
	# 		WHERE dojos.id = %(id)s;
	# 	"""
	# 	results = connectToMySQL(DATABASE).query_db(query,data)
	# 	print(results if results else 'Empty results')
	# 	if results:
	# 		dojo_one = cls(results[0])
	# 	# Create an empty list to append our instances of users
	# 	all_ninjas = []
	# 	for row in results:
	# 		ninja_row = {
	# 		'id': row['id'],
	# 		'first_name': row['first_name'],
	# 		'last_name': row['last_name'],
	# 		'age': row['age'],
	# 		'updated_at': row['updated_at'],
	# 		'created_at': row['created_at'],
	# 		'dojo_id': row['dojo_id']
	# 		}
	# 		all_ninjas.append(n.Ninja(ninja_row))
	# 	dojo_one.ninjas = all_ninjas
	# 	return dojo_one


	# ========== READ all ===============
	@classmethod
	def get_all_sightings_user(cls):
		query = """
		SELECT * 
		FROM users
		LEFT JOIN sightings ON user_id=users.id
		ORDER BY sightings.id asc;
		"""

		results = connectToMySQL(DATABASE).query_db(query)
		print("Results--\n",results)
		sighting_reporter = cls( results[0] )
		if results[0]['user_id'] != None:
			for result in results:
				sighting_data = {
					"id" : result["sightings.id"],
					"location" : result["location"],
					"email" : result["email"],
					"content" : result["content"],
					"date_seen" : result["date_seen"],
					"num_seen" : result["num_seen"], #Hashed
					"created_at" : result["sightings.created_at"],
					"updated_at" : result["sightings.updated_at"],
					"user_id" : result["user_id"],
				}
				sighting_reporter.sightings.append(s.Sighting( sighting_data ))
		return sighting_reporter
	
	# ---------------READ Many to Many-----------------
	@classmethod
	def skeptical_users(cls):
		query = """
		SELECT *
		FROM users
		WHERE users.id NOT IN (SELECT user_id FROM skeptics);
		"""
		users=[]
		results = connectToMySQL(DATABASE).query_db(query)
		if results:
			for row in results:
				users.append(cls(row))
		return users
	
	@classmethod
	def believing_users(cls):
		query = """
		SELECT *
		FROM users
		WHERE users.id IN (SELECT user_id FROM skeptics);
		"""
		users=[]
		results = connectToMySQL(DATABASE).query_db(query)
		if results:
			for row in results:
				users.append(cls(row))
		return users


	@classmethod
	def create_believer(cls,data):
		query = """
		INSERT INTO skeptics (user_id,sighting_id)
		VALUES (%(user_id)s,%(sighting_id)s)
		"""
		return connectToMySQL(DATABASE).query_db(query, data)


	# ============ CREATE ==============
	@classmethod
	def create(cls, data):
		query = """
			INSERT INTO users (fname,lname,email,password)
			VALUES (%(fname)s,%(lname)s,%(email)s,%(password)s);
		"""
		return connectToMySQL(DATABASE).query_db(query, data)
	
	# ============ UPDATE ==============
	@classmethod
	def update(cls, data):
		query = """
			UPDATE dojos SET name=%(name)s
			WHERE id=%(id)s
		"""
		return connectToMySQL(DATABASE).query_db(query, data)
	
	# ============ DELETE ==============
	@classmethod
	def delete(cls, data):
		query = """
			DELETE FROM dojos
			WHERE id=%(id)s
		"""
		return connectToMySQL(DATABASE).query_db(query, data)