from email.policy import default
import json
import os
from datetime import datetime

import stripe
from dotenv import load_dotenv
from flask import (Flask, abort, flash, jsonify, redirect, render_template,
                   request, url_for)
from flask_bootstrap import Bootstrap
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from itsdangerous import URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from .admin.routes import admin, maquinas
from .db_models import (Dispositivo, Ferramenta, Inserto, Item, Maquina, User, db, Categoria)
from .forms import LoginForm, RegisterForm, AddItemForm, CadastroCategoria, CadastroDispositivo, CadastroFerramenta, CadastroInserto, CadastroMaquina

# https://testdriven.io/blog/flask-stripe-tutorial/


load_dotenv()
app = Flask(__name__)
app.register_blueprint(admin)

stripe_keys = {
    "secret_key": os.environ["STRIPE_SECRET_KEY"],
    "publishable_key": os.environ["STRIPE_PUBLISHABLE_KEY"],
	"endpoint_secret": os.environ["STRIPE_ENDPOINT_SECRET"],
}

stripe.api_key = stripe_keys["secret_key"]

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

# Stripe

@app.route("/config")
def get_publishable_key():
    stripe_config = {"publicKey": stripe_keys["publishable_key"]}
    return jsonify(stripe_config)

@app.route("/create-checkout-session")
def create_checkout_session():
    domain_url = "http://127.0.0.1:5000/"
    stripe.api_key = stripe_keys["secret_key"]

    try:
        # Create new Checkout Session for the order
        # Other optional params include:
        # [billing_address_collection] - to display billing address details on the page
        # [customer] - if you have an existing Stripe Customer ID
        # [payment_intent_data] - capture the payment later
        # [customer_email] - prefill the email input in the form
        # For full details see https://stripe.com/docs/api/checkout/sessions/create

        # ?session_id={CHECKOUT_SESSION_ID} means the redirect will have the session ID set as a query param
        checkout_session = stripe.checkout.Session.create(
			client_reference_id=current_user.id if current_user.is_authenticated else None,
            success_url=domain_url + "success?session_id={CHECKOUT_SESSION_ID}",
            cancel_url=domain_url + "cancelled",
            payment_method_types=["card"],
            mode="payment",
            line_items=[
                {
                    "name": "Plano Premium",
                    "quantity": 1,
                    "currency": "brl",
                    "amount": "22990",
                }
            ]
        )
        return jsonify({"sessionId": checkout_session["id"]})
    except Exception as e:
        return jsonify(error=str(e)), 403

@app.route("/success")
def success():
    return render_template("success.html")

@app.route("/cancelled")
def cancelled():
    return render_template("cancelled.html")

@app.route("/webhook", methods=["POST"])
def stripe_webhook():
    payload = request.get_data(as_text=True)
    sig_header = request.headers.get("Stripe-Signature")

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, stripe_keys["endpoint_secret"]
        )

    except ValueError as e:
        # Invalid payload
        return "Invalid payload", 400
    except stripe.error.SignatureVerificationError as e:
        # Invalid signature
        return "Invalid signature", 400

    # Handle the checkout.session.completed event
    if event["type"] == "checkout.session.completed":
        print("Payment was successful.")
        # TODO: run some custom code here

    return "Success", 200

# Home page in dev
@app.route("/inicio")
def inicio():
		
	return render_template("index.html")

@app.route("/")
def home():
	if current_user.is_authenticated:

		ROWS_PER_PAGE = 10
		page = request.args.get('page', 1, type=int)
		items = Item.query.all()
		maquinas = Maquina.query.paginate(page=page, per_page=ROWS_PER_PAGE)
		return render_template("home.html", items=items, maquinas=maquinas)
	else:
		return redirect(url_for('login'))

@app.route("/profile")
def profile():
	if current_user.is_authenticated:
		return render_template("profile.html")
	else:
		return redirect(url_for('login'))

@app.route("/plans")
def plans():
	if current_user.is_authenticated:
		return render_template("plans.html")
	else:
		return redirect(url_for('login'))

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
		new_user = User(first_name=form.first_name.data,
						last_name=form.last_name.data,
						email=form.email.data,
						password=generate_password_hash(
									form.password.data,
									method='pbkdf2:sha256',
									salt_length=8),
						phone=form.phone.data,
						admin=0)
						
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

@app.route('/maquina/<int:id>')
def maquina(id):
	maquina = Maquina.query.get(id)
	return render_template('maquina.html', maquina=maquina)

@app.route('/dispositivo/<int:id>')
def dispositivo(id):
	dispositivo = Dispositivo.query.get(id)
	return render_template('dispositivo.html', dispositivo=dispositivo)

@app.route('/ferramenta/<int:id>')
def ferramenta(id):
	ferramenta = Ferramenta.query.get(id)
	return render_template('ferramenta.html', ferramenta=ferramenta)

@app.route('/inserto/<int:id>')
def inserto(id):
	inserto = Inserto.query.get(id)
	return render_template('inserto.html', inserto=inserto)

@app.route('/search')
def search():
	query = request.args['query']
	search = "%{}%".format(query)
	maquinas = Maquina.query.filter(Maquina.code.like(search)).all()
	return render_template('home.html', maquinas=maquinas, search=True, query=query)

@app.route('/edit/<string:type>/<int:id>', methods=['POST', 'GET'])
def edit(type, id):
	if type == "item":
		item = Item.query.get(id)
		form = AddItemForm(
			code=item.code,
			name=item.name,
			category=item.category,
			details=item.details,
			image=item.image,
			ferramentas=item.ferramentas,
		)
		if form.validate_on_submit():
			item.name = form.name.data
			item.price = form.price.data
			item.category = form.category.data
			item.details = form.details.data
			item.ferramentas = form.ferramentas.data
			form.image.data.save('app/static/uploads/itens/' +
									form.image.data.filename)
			item.image = url_for(
				'static', filename=f'uploads/itens/{form.image.data.filename}')
			db.session.commit()
			return redirect(url_for(f'{type}s'))

	elif type == "user":
		user = User.query.get(id)
		#profile = Profile.query.get(user.id)
		form = RegisterForm(
			name=user.name,
			email=user.email,
			phone=user.phone,
			password=user.password,
			admin=user.admin,
			image = "sem imagem",
		)        
		if form.validate_on_submit():
			user.name = form.name.data
			user.email = form.email.data
			user.phone = form.phone.data
			user.password = form.password.data
			user.admin = form.admin.data

			db.session.commit()
			return redirect(url_for(f'{type}s'))

	elif type == "categoria":
		categoria = Categoria.query.get(id)

		form = CadastroCategoria(            
			name=categoria.name,
			image=categoria.image,
			details=categoria.details,
			maquinas=categoria.maquinas
		)
				
		if form.validate_on_submit():
			categoria.name = form.name.data
			categoria.image = form.image.data
			categoria.details = form.details.data
			categoria.maquinas = form.maquinas.data

			db.session.commit()
			return redirect(url_for(f'{type}s'))

	elif type == "maquina":
		maquina = Maquina.query.get(id)
		pecas = [(items.id, items.code) for items in Item.query.all()]

		form = CadastroMaquina(
			code=maquina.code,
			name=maquina.name,
			image=maquina.image,
			details=maquina.details,
			category_id=maquina.category_id,
			dispositivos=[maquina.dispositivos],
			ferramentas=[maquina.ferramentas]
		)
		
		form.all_items.choices = [(items.id, items.code) for items in Item.query.all()]
		form.items.choices = [(items.id, items.code) for items in maquina.itens]
		
				
		if request.method == "POST" and form.validate_on_submit():
			maquina.code = form.code.data
			maquina.name = form.name.data
			maquina.details = form.details.data
			maquina.category_id = form.category_id.data
			# Novo método
			maquina.dispositivos = Dispositivo.query.filter(Dispositivo.id.in_(form.dispositivos.data)).all()
			#maquina.itens = Item.query.filter(Item.id.in_(request.form.getlist('to[]'))).all()
			maquina.ferramentas = Ferramenta.query.filter(Ferramenta.id.in_(form.ferramentas.data)).all()
			
			produtos = request.form.getlist('to[]')
			
			

			#for id in form.dispositivos.data:
				#maquina.dispositivos.append(Dispositivo.query.get(id))

			if produtos:
				maquina.itens = []
				for id in produtos:
					maquina.itens.append(Item.query.get(id))
			else:
				maquina.itens = []

			#maquina.itens = [elemento for elemento in maquina.itens if elemento in selectValue]

			print(maquina.itens)

			#for id in form.ferramentas.data:
				#maquina.ferramentas.append(Ferramenta.query.get(id))

			try:
				db.session.commit()
			except Exception as e:
				print(f"Erro: {e}")
			flash(f'{maquina.code} alterado com sucesso!', 'success')
			return redirect(url_for('maquina', id=maquina.id))

	elif type == "dispositivo":
		dispositivo = Dispositivo.query.get(id)
		print(dispositivo.image)
		form = CadastroDispositivo(
			code=dispositivo.code,
			name=dispositivo.name,
			category=dispositivo.category,
			image=dispositivo.image,
			details=dispositivo.details,
			maquinas=dispositivo.maquinas
		)
		if form.validate_on_submit():
			dispositivo.code = form.code.data
			dispositivo.name = form.name.data
			dispositivo.category = form.category.data
			dispositivo.image = form.image.data
			dispositivo.details = form.detail.data
			dispositivo.maquinas = form.maquinas.data

			db.session.commit()
			return redirect(url_for(f'{type}s'))

	elif type == "ferramenta":
		ferramenta = Ferramenta.query.get(id)
		form = CadastroFerramenta(
			code=ferramenta.code,
			name=ferramenta.name,
			category=ferramenta.category,
			image=ferramenta.image,
			details=ferramenta.details,
		)
		if form.validate_on_submit():
			ferramenta.code = form.code.data
			ferramenta.name = form.name.data
			ferramenta.category = form.category.data
			ferramenta.image = form.image.data
			ferramenta.details = form.detail.data

			db.session.commit()
			return redirect(url_for(f'{type}s'))

	elif type == "inserto":
		inserto = Inserto.query.get(id)
		form = CadastroInserto(
			code=inserto.code,
			name=inserto.name,
			category=inserto.category,
			image=inserto.image,
			details=inserto.details,
		)
		if form.validate_on_submit():
			inserto.code = form.code.data
			inserto.name = form.name.data
			inserto.category = form.category.data
			inserto.image = form.image.data
			inserto.details = form.detail.data

			db.session.commit()
			return redirect(url_for(f'{type}s'))

	return render_template('edit.html', form=form, maquina=maquina, pecas=pecas)
