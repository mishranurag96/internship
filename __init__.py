from flask import Flask, url_for, redirect, request, render_template, session
from flask_sqlalchemy import SQLAlchemy
import re

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///studentdata.db'
db = SQLAlchemy(app)

# Data Tables
class Users(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	name = db.Column(db.String(20), nullable = False)
	email = db.Column(db.String(50), nullable = False, unique = True)
	contact_number = db.Column(db.String(20), nullable= False)
	password = db.Column(db.String(25), nullable = False)
	check = db.Column(db.String(10), nullable = False)
	student = db.relationship('Students', backref = 'stu', lazy= True)
	company = db.relationship('Company', backref = 'com', lazy= True)

class Students(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	alternate_contact = db.Column(db.String(13))
	internship_pref = db.Column(db.String(200), default= 'No')
	availability = db.Column(db.String(20))
	location = db.Column(db.String(150))
	resume = db.Column(db.String(100))
	pref = db.Column(db.String(50))
	hide = db.Column(db.String(20), default = 'no')
	changes = db.Column(db.String(20), default = 'no')
	user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)

class Status(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	stu_id = db.Column(db.Integer, db.ForeignKey('students.id'), nullable = False)
	com_id = db.Column(db.String(20))
	action = db.Column(db.String(10), default = 'Pending')

class Company(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	address = db.Column(db.String(300))
	alter_con = db.Column(db.String(25))
	role = db.Column(db.String(25))
	stipend = db.Column(db.String(10))
	duration = db.Column(db.String(25))
	skills = db.Column(db.String(100))
	intern_role = db.Column(db.String(200))
	ppo  = db.Column(db.String(10))
	doj  = db.Column(db.String(20))
	when = db.Column(db.String(25))
	num  = db.Column(db.String(15))
	user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable = False)

class Sign(db.Model):
	id = db.Column(db.Integer, primary_key = True)
	disable = db.Column(db.String(25), default = 'No')

db.create_all()
u = Users.query.filter_by(check= 'students').all()
lst = Students.query.all()

@app.route('/',methods= ['POST','GET'])
def index():
	hello =''
	if 'username' in session:
		hello = Users.query.filter_by(email = session['username']).first()
		return render_template('index.html',display=session['username'],hello=hello)
	return render_template('index.html',display='index',hello=hello)

@app.route('/logsign/',methods=['POST','GET'])
def logsign():
	s = Sign.query.first()
	try:
		if 'username' in session:
			hello = Users.query.filter_by(name = session['username']).first()
	except:
		return render_template('500.html')
	if request.method == 'POST':
		if request.form['test'] == 'signup':
			try:
				user = Users.query.filter_by(email = request.form['email']).first()
				if request.form['email'] == 'Anur@g7':
					return render_template('logsign.html',error = 'Account already exists with email'+ request.form['email'])
				elif user:
					return render_template('logsign.html',error = 'Account already exists with email'+ request.form['email'])
				else:
					sign = Users(name = request.form['firstname']+" "+request.form['midname']+" "+
					request.form['lastname'], email=request.form['email'], contact_number = request.form['mob'],
					password = request.form['password'], check = request.form['role'])
					db.session.add(sign)
					db.session.commit()
					return render_template('logsign.html', msg='Acccount Created Successfully', s=s)
			except:
				return render_template('logsign.html',msg = 'There was something wrong!',s=s)
		else:
			try:
				data = Users.query.filter_by(email=request.form['username']).first()
				if data:
					username = data.email
					ps = data.password
					ch = data.check
					if username == request.form['username'] and ps == request.form['password'] and ch == request.form['role']:
						display = data.email
						session['username'] = display
						if request.form['role'] == 'students':
							return redirect(url_for('dashboard', display=display))
						else:
							return redirect(url_for('comdash',display=display))
					else:
						return render_template('logsign.html', error='Invalid Credentials',s=s)
				else:
					return render_template('logsign.html',s=s, error='No Account exists with '+ request.form['username'])
			except:
				return render_template('logsign.html',s=s, error = 'There was something wrong')
	return render_template('logsign.html',s=s)

@app.route('/student/dashboard/<display>', methods=['POST','GET'])
def dashboard(display):
	if 'username' in session:
		var = 'new'
		try:
			st = ''
			u = Users.query.filter_by(email = display).first()
			st = Status.query.filter_by(stu_id = u.id).all()
			return render_template('dashboard.html', st=st, var=var, display=display)
		except:
			return render_template('500.html',display=display)
	return redirect(url_for('index'))

@app.route('/student/details/<display>', methods=['POST','GET'])
def details(display):
	msg = ''
	if 'username' in session:
		var = 'new'
		try:
			uc = Users.query.filter_by(email = session['username']).first()
			sc = Students.query.filter_by(user = uc.id).first()
		except:
			return render_template('500.html')
		if request.method == 'POST':
			u = Users.query.filter_by(email = display).first()
			s = Students.query.filter_by(user = u.id).first()
			try:
				if s is None:
					data = Students(alternate_contact = request.form['alter'],internship_pref= request.form['internships'],
					availability = request.form['when'],pref = request.form['pref'], location = request.form['loc'], resume = request.form['resume'],
					user = u.id)
					db.session.add(data)
					db.session.commit()
				else:
					d = Students.query.filter_by(user = u.id).update({Students.alternate_contact:request.form['alter'],
						Students.internship_pref:request.form['internships'], Students.availability:request.form['when'],
						Students.location:request.form['loc'],Students.resume:request.form['resume'],Students.changes:'no'})
					db.session.commit()
				return render_template('details.html',sc=sc, msg = 'Added Successfully!', var=var,display=display)
			except:
				return render_template('details.html',sc=sc, msg = 'There was something wrong', var=var,display=display)
		return render_template('details.html',sc=sc, var=var,display=display)
	return redirect(url_for('index'))

@app.route('/company/dashboard/<display>', methods=['POST','GET'])
def comdash(display):
	msg = ''
	var = 'new'
	if 'username' in session:
		if request.method == 'POST':
			c = Users.query.filter_by(email = display).first()
			try:
				a = Company(address= request.form['address'], alter_con=request.form['alter'] ,role= request.form['role'], 
					stipend= request.form['stipend'],duration= request.form['intern'], skills= request.form['skill'],
					intern_role= request.form['internrole'], ppo= request.form['ppo'],doj= request.form['doj'],
					when= request.form['when'],num= request.form['num'],user = c.id)
				db.session.add(a)
				db.session.commit()
				return render_template('students.html', msg = "Added Successfully", var=var, display=display)
			except:
				return render_template('students.html', msg = "There was something wrong!",var=var,display=display)
		return render_template('students.html',var=var,display=display)
	return redirect(url_for('index'))

@app.route('/company/students/<display>', methods=['POST','GET'])
def allstudents(display):
	if 'username' in session:
		var = 'new'
		try:
			lst = Status.query.filter_by(com_id = display, action= 'Selected').all()
			u = []
			l = []
			for items in lst:
				a = Users.query.filter_by(id = items.stu_id).first()
				b = Students.query.filter_by(user=a.id).first()
				u.append(a)
				l.append(b)
			return render_template('com.html', u=u, lst=lst, l=l, var=var,display=display)
		except:
			return render_template('500.html')
	return redirect('index')

@app.route('/profile/<display>')
def profile(display):
	if 'username' in session:
		var = 'new'
		u = Users.query.filter_by(email = display).first()
		try:
			if u.check == 'students':
				c = Students.query.filter_by(user = u.id).first()
			else:
				c = Company.query.filter_by(user = u.id).first()
			return render_template('profile.html', c=c, u=u,display=display)
		except:
			return render_template('profile.html', msg= 'There was something wrong!', var=var,display=display)
	return redirect(url_for('index'))

@app.route('/log', methods = ['POST','GET'])
def log():
	if request.method == 'POST':
		try:
			if request.form['username'] == 'Anur@g7' and request.form['password'] == '@!nterns#!p$':
				session['username'] = None
				session['username'] = 'Anur@g7'
				display = session['username']
				return redirect(url_for('admins', display = display))
		except:
			return render_template('500.html')
	return render_template('log.html')

@app.route('/admins/<display>',methods=['POST','GET'])
def admins(display):
	msg = ''
	var = 'new'
	if session['username'] == 'Anur@g7':
		try:
			u = Users.query.filter_by(check= 'students').all()
			lst = Students.query.all()
			com = Users.query.filter_by(check= 'company').all()
			if request.method == 'POST':
				for items in u:
					try:
						if request.form[items.email] == '0':
							continue
						new = Status.query.filter_by(stu_id = items.id, com_id = request.form['comp']).first()
						if new:
							ad = Status.query.filter_by(stu_id = items.id).update({Status.action:request.form[items.email]})
							# if request.form[items.email == 'Selected'] or request.form[items.email == 'Rejected']:
							bc = Students.query.filter_by(user= items.id).update({Students.changes:'yes'})
							db.session.commit()
						else:
							st = Status(stu_id = items.id, com_id = request.form['comp'], action =str(request.form[items.email]))
							# if request.form[items.email == 'Selected'] or request.form[items.email == 'Rejected']:
							bc = Students.query.filter_by(user= items.id).update({Students.changes:'yes'})
							db.session.add(st)
							db.session.commit()
					except:
						new = None
				return render_template('admin1.html',lst=lst,u=u,var=var,com=com,display = display,msg='Added Successfully!')
			return render_template('admin1.html',lst=lst,u=u,var=var,com=com, display=display)
		except:
			return render_template('500.html')
	return redirect(url_for('logsign'))

@app.route('/adminc/<display>', methods=['POST','GET'])
def adminc(display):
	if session['username'] == 'Anur@g7':
		var = 'new'
		try:
			u = Users.query.filter_by(check= 'company').all()
			lst = Company.query.all()
			return render_template('search.html',lst=lst,u=u,var=var,display=display)
		except:
			return render_template('500.html')
	return redirect('logout')

@app.route('/settings/<display>',methods=['POST','GET'])
def settings(display):
	msg = ''
	if session['username'] == 'Anur@g7':
		try:
			u = Users.query.filter_by(check= 'students').all()
			s = Students.query.all()
			d = Sign.query.first()
		except:
			return render_template('500.html')
		if request.method == 'POST':
			for i in u:
				try:
					a = Students.query.filter_by(user=i.id).update({Students.hide:request.form[i.email]})
					db.session.commit()
				except:
					a = None
			if d:
				v = Sign.query.filter_by(id=1).update({Sign.disable:request.form['regis']})
				db.session.commit()
			else:
				v = Sign(disable = request.form['regis'])
				db.session.add(v)
				db.session.commit()
			return render_template('settings.html',display=display,u=u,s=s,d=d,msg='Setting Changed')
		return render_template('settings.html',display=display, u=u,s=s,d=d)
	return redirect('logout')

@app.route('/about/<display>')
def about(display):
	k = 'test'
	hello = ''
	if 'username' in session:
		hello = Users.query.filter_by(email = display).first()
		return render_template('about.html',hello=hello,k=k)
	return render_template('about.html',hello=hello,k=k)

@app.route('/logout')
def logout():
	if 'username' in session:
		session['username'] = None
		return redirect(url_for('index'))
	return redirect(url_for('index'))

@app.errorhandler(404)
def page_not_found(e):
	return render_template('404.html')

@app.errorhandler(500)
def not_found(e):
	return render_template('500.html')

if __name__ == '__main__':
	app.run(debug=True,port=8000)