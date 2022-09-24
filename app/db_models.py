import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

"""
INSERT INTO tabela_novo (id, code, name, image, details)
SELECT id, code, name, image, details FROM tabela;

ALTER TABLE tabela RENAME TO tabela_old;

ALTER TABLE tabela_novo RENAME TO tabela;

PRAGMA foreign_keys = 0;
DROP TABLE tabela_old;
PRAGMA foreign_keys = 1;

"""


db = SQLAlchemy()

class Plano(db.Model):
	__tablename__ = "planos"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(50), nullable=False)
	nro_maquinas = db.Column(db.Integer, nullable=False)
	nro_dispositivos = db.Column(db.Integer, nullable=False)
	nro_pecas = db.Column(db.Integer, nullable=False)
	nro_ferramentas = db.Column(db.Integer, nullable=False)
	preco = db.Column(db.String(50), nullable=False)
	#user = db.relationship('User', backref='planos', lazy=True, uselist=False, cascade='all,delete')


class Profile(db.Model):
	__tablename__ = "profiles"
	id = db.Column(db.Integer, primary_key=True)
	image = db.Column(db.String(250), nullable=True)
	user = db.relationship('User', backref='profiles', lazy=True, uselist=False, cascade='all,delete')
	
class User(UserMixin, db.Model):
	__tablename__ = "users"
	id = db.Column(db.Integer, primary_key=True)
	first_name = db.Column(db.String(50), nullable=False)
	last_name = db.Column(db.String(50), nullable=False)
	email = db.Column(db.String(50), nullable=False)
	phone = db.Column(db.String(50), nullable=False)
	password = db.Column(db.String(250), nullable=False)	
	admin = db.Column(db.Boolean, nullable=True, default=False)
	profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id'), nullable=True)
	#plano_id = db.Column(db.Integer, db.ForeignKey('planos.id'), nullable=True)
	
class Categoria(db.Model):
	__tablename__ = "categorias"
	id = db.Column(db.Integer, primary_key=True)
	name = db.Column(db.String(100), nullable=False)
	image = db.Column(db.String(250), nullable=False)
	details = db.Column(db.String(250), nullable=False)
	maquinas = db.relationship('Maquina', backref='categorias', lazy=True)


maq_disp = db.Table('maq_disp',
    db.Column('disp_id', db.Integer, db.ForeignKey('dispositivos.id'), primary_key=True),
    db.Column('maq_id', db.Integer, db.ForeignKey('maquinas.id'), primary_key=True)
)

maq_item = db.Table('maq_item',
    db.Column('item_id', db.Integer, db.ForeignKey('items.id'), primary_key=True),
    db.Column('maq_id', db.Integer, db.ForeignKey('maquinas.id'), primary_key=True)
)

maq_ferr = db.Table('maq_ferr',
    db.Column('ferr_id', db.Integer, db.ForeignKey('ferramentas.id'), primary_key=True),
    db.Column('maq_id', db.Integer, db.ForeignKey('maquinas.id'), primary_key=True)
)

class Maquina(db.Model):
	__tablename__ = "maquinas"
	id = db.Column(db.Integer, primary_key=True)
	code = db.Column(db.String(100), nullable=False)
	name = db.Column(db.String(100), nullable=False)
	image = db.Column(db.String(250), nullable=True)
	details = db.Column(db.String(250), nullable=True)
	data_aquisicao = db.Column(db.DateTime, default=datetime.datetime.utcnow)
	cone = db.Column(db.String(20), nullable=True)
	velocidade = db.Column(db.String(20), nullable=True)
	avanco_rapido = db.Column(db.String(20), nullable=True)
	mesa = db.Column(db.String(20), nullable=True)
	luneta = db.Column(db.String(20), nullable=True)
	potencia = db.Column(db.String(10), nullable=True)
	capacidade_magazine = db.Column(db.String(10), nullable=True)
	category_id = db.Column(db.Integer, db.ForeignKey('categorias.id'),
        nullable=True)
	dispositivos = db.relationship('Dispositivo', secondary=maq_disp, lazy='subquery',
        backref=db.backref('maquinas', lazy=True))
	itens = db.relationship('Item', secondary=maq_item, lazy='subquery',
        backref=db.backref('maquinas', lazy=True))
	ferramentas = db.relationship('Ferramenta', secondary=maq_ferr, lazy='subquery',
		backref=db.backref('maquinas', lazy=True))

	def __repr__(self):
		return self.code

class Dispositivo(db.Model):
	__tablename__ = "dispositivos"
	id = db.Column(db.Integer, primary_key=True)
	code = db.Column(db.String(100), nullable=False)
	name = db.Column(db.String(100), nullable=False)
	category = db.Column(db.Text, nullable=False)
	image = db.Column(db.String(250), nullable=False)
	details = db.Column(db.String(250), nullable=False)

	def __repr__(self):
		return self.code

item_ferr = db.Table('item_ferr',
    db.Column('ferr_id', db.Integer, db.ForeignKey('ferramentas.id'), primary_key=True),
    db.Column('item_id', db.Integer, db.ForeignKey('items.id'), primary_key=True)
)

class Item(db.Model):
	__tablename__ = "items"
	id = db.Column(db.Integer, primary_key=True)
	code = db.Column(db.String(100), nullable=False)
	name = db.Column(db.String(100), nullable=False)
	category = db.Column(db.Text, nullable=False)
	image = db.Column(db.String(250), nullable=False)
	details = db.Column(db.String(250), nullable=False)
	ferramentas = db.relationship('Ferramenta', secondary=item_ferr, lazy='subquery',
		backref=db.backref('items', lazy=True))	

	def __repr__(self):
		return self.code

ferr_ins = db.Table('ferr_ins',
    db.Column('ins_id', db.Integer, db.ForeignKey('insertos.id'), primary_key=True),
    db.Column('ferr_id', db.Integer, db.ForeignKey('ferramentas.id'), primary_key=True)
)

class Ferramenta(db.Model):
	__tablename__ = "ferramentas"
	id = db.Column(db.Integer, primary_key=True)
	code = db.Column(db.String(100), nullable=False)
	name = db.Column(db.String(100), nullable=False)
	price = db.Column(db.Float, nullable=False)
	category = db.Column(db.Text, nullable=False)
	image = db.Column(db.String(250), nullable=False)
	details = db.Column(db.String(250), nullable=False)
	insertos = db.relationship('Inserto', secondary=ferr_ins, lazy='subquery',
		backref=db.backref('ferramentas', lazy=True))

	def __repr__(self):
		return self.code

class Inserto(db.Model):
	__tablename__ = "insertos"
	id = db.Column(db.Integer, primary_key=True)
	code = db.Column(db.String(100), nullable=False)
	name = db.Column(db.String(100), nullable=False)
	price = db.Column(db.Float, nullable=False)
	category = db.Column(db.Text, nullable=False)
	image = db.Column(db.String(250), nullable=False)
	details = db.Column(db.String(250), nullable=False)

	def __repr__(self):
		return self.code
