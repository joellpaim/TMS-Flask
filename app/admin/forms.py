from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, FileField, PasswordField, BooleanField, SelectField, SelectMultipleField, MultipleFileField
from wtforms_alchemy.fields import QuerySelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, Regexp
from app.db_models import Categoria, Item, Maquina, Dispositivo, Ferramenta,Inserto

class AddItemForm(FlaskForm):
	name = StringField("Nome:", validators=[DataRequired(), Length(max=50)])
	price = FloatField("Preço:", validators=[DataRequired()])
	category = StringField("Categoria:", validators=[DataRequired(), Length(max=50)])
	image = FileField("Imagem:", validators=[DataRequired()], id="img-input")
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
	image = FileField("Imagem:", validators=[DataRequired()], id="img-input")
	details = StringField("Detalhes:", validators=[DataRequired()])
	maquinas = SelectMultipleField("Maquinas", coerce=int)
	submit = SubmitField("Salvar")

	def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			self.maquinas.choices = [(maquinas.id, maquinas.code) for maquinas in Maquina.query.all()]

class CadastroMaquina(FlaskForm):	
	code = StringField("Código:", validators=[DataRequired(), Length(max=100)])
	name = StringField("Nome:", validators=[DataRequired(), Length(max=50)])
	image = FileField("Imagem:", validators=[DataRequired()], id="img-input")
	details = StringField("Detalhes:", validators=[DataRequired()])
	category_id = SelectField("Categoria", coerce=int, validate_choice=False)
	dispositivos = SelectMultipleField("Dispositivos", coerce=int)
	items = SelectMultipleField("Produtos", coerce=int)
	ferramentas = SelectMultipleField("Ferramentas", coerce=int)
	submit = SubmitField("Salvar")

	def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			self.category_id.choices = [(category_id.id, category_id.code) for category_id in Categoria.query.all()]
			self.dispositivos.choices = [(dispositivos.id, dispositivos.code) for dispositivos in Dispositivo.query.all()]
			self.items.choices = [(items.id, items.code) for items in Item.query.all()]
			self.ferramentas.choices = [(ferramentas.id, ferramentas.code) for ferramentas in Ferramenta.query.all()]

class CadastroDispositivo(FlaskForm):
	code = StringField("Código:", validators=[DataRequired(), Length(max=100)])
	name = StringField("Nome:", validators=[DataRequired(), Length(max=50)])
	category = StringField("Categoria:", validators=[DataRequired(), Length(max=50)])
	image = FileField("Imagem:", validators=[DataRequired()], id="img-input")
	details = StringField("Detalhes:", validators=[DataRequired()])
	maquinas = SelectMultipleField("Máquinas", coerce=int)	
	submit = SubmitField("Salvar")

	def __init__(self, *args, **kwargs):
			super().__init__(*args, **kwargs)
			self.maquinas.choices = [(maquinas.id, maquinas.code) for maquinas in Maquina.query.all()]

class CadastroFerramenta(FlaskForm):
	code = StringField("Código:", validators=[DataRequired(), Length(max=100)])
	name = StringField("Nome:", validators=[DataRequired(), Length(max=50)])
	category = StringField("Categoria:", validators=[DataRequired(), Length(max=50)])
	image = FileField("Imagem:", validators=[DataRequired()], id="img-input")
	details = StringField("Detalhes:", validators=[DataRequired()])
	submit = SubmitField("Salvar")

class CadastroInserto(FlaskForm):
	code = StringField("Código:", validators=[DataRequired(), Length(max=100)])
	name = StringField("Nome:", validators=[DataRequired(), Length(max=50)])
	category = StringField("Categoria:", validators=[DataRequired(), Length(max=50)])
	image = FileField("Imagem:", validators=[DataRequired()], id="img-input")
	details = StringField("Detalhes:", validators=[DataRequired()])
	submit = SubmitField("Salvar")