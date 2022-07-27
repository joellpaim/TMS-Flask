import os, json
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, abort
from flask_bootstrap import Bootstrap
from .forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from .db_models import Maquina, db, User, Item
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
from .admin.routes import admin, maquinas
from math import ceil


load_dotenv()
app = Flask(__name__)
app.register_blueprint(admin)

app.config["SECRET_KEY"] = os.environ["SECRET_KEY"]
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ["DB_URI"]
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['MAIL_USERNAME'] = os.environ["EMAIL"]
app.config['MAIL_PASSWORD'] = os.environ["PASSWORD"]
app.config['MAIL_SERVER'] = "smtp.googlemail.com"
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_PORT'] = 587

Bootstrap(app)
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)

with app.app_context():
	db.create_all()

@app.context_processor
def inject_now():
	""" sends datetime to templates as 'now' """
	return {'now': datetime.utcnow()}

@login_manager.user_loader
def load_user(user_id):
	return User.query.get(user_id)

@app.route("/")
def home():
	items = Item.query.all()
	maquinas = Maquina.query.all()
	return render_template("home.html", items=items, maquinas=maquinas)

@app.route("/login", methods=['POST', 'GET'])
def login():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = LoginForm()
	if form.validate_on_submit():
		email = form.email.data
		user = User.query.filter_by(email=email).first()
		if user == None:
			flash(f'Não existe usuário com email: {email} <br> <a href={url_for("register")}>Cadastrar agora</a>', 'error')
			return redirect(url_for('login'))
		elif check_password_hash(user.password, form.password.data):
			login_user(user)
			return redirect(url_for('home'))
		else:
			flash("Email e senha incorretos!!", "error")
			return redirect(url_for('login'))
	return render_template("login.html", form=form)

@app.route("/register", methods=['POST', 'GET'])
def register():
	if current_user.is_authenticated:
		return redirect(url_for('home'))
	form = RegisterForm()
	if form.validate_on_submit():
		user = User.query.filter_by(email=form.email.data).first()
		if user:
			flash(f"Usuário com email {user.email} já existe!!<br> <a href={url_for('login')}>Entrar agora</a>", "error")
			return redirect(url_for('register'))
		new_user = User(name=form.name.data,
						email=form.email.data,
						password=generate_password_hash(
									form.password.data,
									method='pbkdf2:sha256',
									salt_length=8),
						phone=form.phone.data,
						admin=form.admin.data)
						
		db.session.add(new_user)
		db.session.commit()
		# send_confirmation_email(new_user.email)
		flash('Obrigado por seu cadastro! Você deve logar agora.', 'success')
		return redirect(url_for('login'))
	return render_template("register.html", form=form)

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('login'))

@app.route('/item/<int:id>')
def item(id):
	item = Item.query.get(id)
	return render_template('item.html', item=item)

@app.route('/search')
def search():
	query = request.args['query']
	search = "%{}%".format(query)
	items = Item.query.filter(Item.name.like(search)).all()
	return render_template('home.html', items=items, search=True, query=query)
