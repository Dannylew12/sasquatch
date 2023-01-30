from .. import app, bcrypt  # .. in place of flask_app folder
from flask import render_template,redirect,request,session,flash,url_for

from ..models import user_model as u
from ..models import sighting_model as s



@app.route("/add_sighting")
def add_sighting():
	if(not session['user'] if 'user' in session else False):
		return redirect(url_for('index'))
	return render_template("add_sighting.html", page='Add')



@app.route("/create_sighting", methods=["POST"])
def create_sighting():
	data = {**request.form}
	print(data)
	if not s.Sighting.validate_sighting(data):
		print("not valid", data)
		return redirect(url_for('add_sighting'))
	else:
		s.Sighting.create_sighting(data)
		return redirect(url_for('dashboard'))



@app.route("/view_sighting/<int:id>")
def view_sighting(id):
	skeptics=u.User.skeptical_users()
	# print("Skeptics Vars   \n",vars(skeptics[0]))
	sighting = s.Sighting.get_one_by_id({'id':id})
	user = u.User.get_one_by_id({'id':sighting.user_id})
	print(user)
	return render_template("view_sighting.html", sighting=sighting, page='View', skeptics=skeptics,user=user)



@app.route('/believe', methods=['POST'])
def make_believe():
	print("REQUEST  ",request.form)
	data={
		'user_id': request.form['user_id'],
		'sighting_id':request.form['sighting_id']
	}
	u.User.create_believer(data)
	return redirect(url_for("view_sighting", id=data['sighting_id']))



@app.route("/edit_sighting/<int:id>")
def edit_sighting(id):
	sighting = s.Sighting.get_one_by_id({'id':id})
	return render_template("edit_sighting.html",sighting=sighting, page='Edit')



@app.route("/update_sighting/<int:id>", methods=["POST"])
def update_sighting(id):
	data = {**request.form}
	print("************\n",data,"\n***************")
	if not s.Sighting.validate_sighting(data):
		print("not valid save info ", data)
		return redirect(url_for('edit_sighting',id=id))
	else:
		s.Sighting.update(data)
		return redirect(url_for('dashboard'))



@app.route("/delete_sighting/<int:id>", methods=["GET","POST"])
def delete_sighting(id):
	s.Sighting.delete({'id':id})
	return redirect(url_for('dashboard'))