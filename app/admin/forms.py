from email.mime import image
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, FileField, PasswordField, BooleanField, SelectField, SelectMultipleField
from wtforms_alchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp
from app.db_models import Maquina, Dispositivo, Ferramenta,Inserto

class AddItemForm(FlaskForm):
	name = StringField("Nome:", validators=[DataRequired(), Length(max=50)])
	price = FloatField("Preço:", validators=[DataRequired()])
	category = StringField("Categoria:", validators=[DataRequired(), Length(max=50)])
	image = FileField("Imagem:", validators=[DataRequired()])
	details = StringField("Detalhes:", validators=[DataRequired()])
	price_id = StringField("Stripe id:", validators=[DataRequired()])
	submit = SubmitField("Adicionar")

class AdminRegisterForm(FlaskForm):
	name = StringField("Nome:", validators=[DataRequired(), Length(max=50)])
	phone = StringField("Telefone:", validators=[DataRequired(), Length(max=30)])
	email = StringField("Email:", validators=[DataRequired(), Email()])
	password = PasswordField("Senha:", validators=[DataRequired(), Regexp("^[a-zA-Z0-9_\-&$@#!%^*+.]{8,30}$", message='Password must be 8 characters long and should contain letters, numbers and symbols.')])
	confirm = PasswordField("Confirmar Senha:",validators=[EqualTo('password', message='Passwords must match')])
	admin = BooleanField("Admin")
	submit = SubmitField("Cadastrar")

class CadastroCategoria(FlaskForm):
	name = StringField("Nome:", validators=[DataRequired(), Length(max=50)])	
	image = FileField("Imagem:", validators=[DataRequired()])
	details = StringField("Detalhes:", validators=[DataRequired()])
	submit = SubmitField("Adicionar")

class CadastroMaquina(FlaskForm):
	code = StringField("Código:", validators=[DataRequired(), Length(max=100)])
	name = StringField("Nome:", validators=[DataRequired(), Length(max=50)])
	image = FileField("Imagem:", validators=[DataRequired()])
	details = StringField("Detalhes:", validators=[DataRequired()])
	submit = SubmitField("Adicionar")

class CadastroDispositivo(FlaskForm):
	code = StringField("Código:", validators=[DataRequired(), Length(max=100)])
	name = StringField("Nome:", validators=[DataRequired(), Length(max=50)])
	category = StringField("Categoria:", validators=[DataRequired(), Length(max=50)])
	image = FileField("Imagem:", validators=[DataRequired()])
	details = StringField("Detalhes:", validators=[DataRequired()])
	maquinas = SelectMultipleField("Máquinas", coerce=int)	
	submit = SubmitField("Adicionar")

	def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			self.maquinas.choices = [ 
            (maquinas.id, maquinas.code) for maquinas in Maquina.query.all()
        ]

class CadastroFerramenta(FlaskForm):
	code = StringField("Código:", validators=[DataRequired(), Length(max=100)])
	name = StringField("Nome:", validators=[DataRequired(), Length(max=50)])
	category = StringField("Categoria:", validators=[DataRequired(), Length(max=50)])
	image = FileField("Imagem:", validators=[DataRequired()])
	details = StringField("Detalhes:", validators=[DataRequired()])
	submit = SubmitField("Adicionar")

class CadastroInserto(FlaskForm):
	code = StringField("Código:", validators=[DataRequired(), Length(max=100)])
	name = StringField("Nome:", validators=[DataRequired(), Length(max=50)])
	category = StringField("Categoria:", validators=[DataRequired(), Length(max=50)])
	image = FileField("Imagem:", validators=[DataRequired()])
	details = StringField("Detalhes:", validators=[DataRequired()])
	submit = SubmitField("Adicionar")