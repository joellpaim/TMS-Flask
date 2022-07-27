import os, datetime
from flask import render_template, url_for
from itsdangerous import URLSafeTimedSerializer
from flask_login import current_user
from flask_mail import Mail, Message
from dotenv import load_dotenv
from .db_models import db, User


load_dotenv()
mail = Mail()

def admin_only(func):
	""" Decorator for giving access to authorized users only """
	def wrapper(*args, **kwargs):
		if current_user.is_authenticated and current_user.admin == 1:
			return func(*args, **kwargs)
		else:
			return "Você não está autorizado a acessar esta URL."
	wrapper.__name__ = func.__name__
	return wrapper
		