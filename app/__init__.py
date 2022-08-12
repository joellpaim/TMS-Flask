import os, json
from datetime import datetime
from flask import Flask, render_template, redirect, url_for, flash, request, abort, jsonify
from flask_bootstrap import Bootstrap
from .forms import LoginForm, RegisterForm
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from .db_models import Maquina, db, User, Item, Dispositivo, Ferramenta, Inserto
from itsdangerous import URLSafeTimedSerializer
from dotenv import load_dotenv
from .admin.routes import admin, maquinas
import stripe

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
		items = Item.query.all()
		maquinas = Maquina.query.all()
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
