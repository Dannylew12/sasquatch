from flask_app import app, bcrypt
from flask import render_template,redirect,request,session,flash,url_for

from flask_app.models import user_model as u
from flask_app.models import sighting_model as s



@app.route("/dashboard")
def dashboard():
	if(not session['user'] if 'user' in session else False):
		print("Dashboard no user in session ",session)
		return redirect(url_for('index'))
	else:
		print("Dashboard user in session ",session)
		users = u.User.get_all_sightings_user()
		print("USERS PRINTOUT:   ",users.email)
		if users:
			print("SIGHTINGS: ",users)
		skeptics = u.User.skeptical_users()
		believers = u.User.believing_users()
		# user = u.User.get_one_by_id({'id':id})
		return render_template("dashboard.html",users=users, page='Dashboard', skeptics=skeptics,believers=believers)



@app.route("/login", methods=["POST"])
def login():
	if(session['user'] if 'user' in session else False):
		print("Login user in session ",session)
		return redirect(url_for('index'))
	else:
		print('No session')
		redirect(url_for('index'))
	data = {**request.form}
	user = u.User.get_by_email(data)
	if not user:
		return redirect(url_for('index'))

	if not u.User.validate_user(user,data):
		return redirect(url_for('index'))
	
	print(bcrypt.check_password_hash(user.password, data['password']))
	if bcrypt.check_password_hash(user.password, data['password']):
		session['user'] = user.email
		session['id'] = user.id
		print("Session info",session,session['id'])

	return redirect(url_for('index'))



@app.route("/logout")
def logout():
	session.clear()
	session["__invalidate__"] = True
	print("session destroyed")
	return redirect(url_for('index'))

@app.after_request
def remove_if_invalid(response):
	if "__invalidate__" in session:
		response.delete_cookie(app.session_cookie_name)
		print("Cookie deleted.")
	return response


@app.route("/create", methods=["POST"])
def create_user():
	data = {**request.form}

	if not u.User.validate_create(data):
		print("not valid", data)
		return redirect(url_for('index'))
	else:
		data['password'] = bcrypt.generate_password_hash(data['password'])
		u.User.create(data)
		return redirect(url_for('index'))
