from flask_app import app, bcrypt
from flask_app.controllers import dashboard_controller # Import controllers for routing
from flask_app.controllers import sighting_controller

from flask import render_template,redirect,request,session,flash,url_for

from flask_app.models import user_model as u

@app.route("/")
def index():
	if(session['user'] if 'user' in session else False):
		print("Index ",session,"\nRedirecting to dashboard.")
		return redirect(url_for('dashboard'))
	else:
		print('No session @ Index')
	users=u.User.get_all()
	
	return render_template("index.html",data={},users=users, page='Index')


if __name__ == "__main__":
    app.run(debug=True, port=5001)