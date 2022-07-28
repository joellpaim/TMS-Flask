from flask import Blueprint, render_template, url_for, flash
from werkzeug.utils import redirect
from werkzeug.security import generate_password_hash, check_password_hash
from ..db_models import Item, db, User, Categoria, Dispositivo, Ferramenta, Inserto, Maquina, maq_disp, maq_ferr, maq_item
from ..admin.forms import AddItemForm, AdminRegisterForm, CadastroCategoria, CadastroDispositivo, CadastroFerramenta, CadastroInserto, CadastroMaquina
from ..funcs import admin_only
from flask_login import LoginManager, login_user, current_user, login_required, logout_user
from PIL import Image


admin = Blueprint("admin", __name__, url_prefix="/admin",
                  static_folder="static", template_folder="templates")


@admin.route('/')
@admin_only
def dashboard():
    return render_template("admin/home.html")


@admin.route('/items')
@admin_only
def items():
    items = Item.query.all()
    return render_template("admin/items.html", items=items)

@admin.route('/maquinas')
@admin_only
def maquinas():
    maquinas = Maquina.query.all()
    return render_template("admin/maquinas.html", maquinas=maquinas)

@admin.route('/dispositivos')
@admin_only
def dispositivos():
    dispositivos = Dispositivo.query.all()
    return render_template("admin/dispositivos.html", dispositivos=dispositivos)

@admin.route('/ferramentas')
@admin_only
def ferramentas():
    ferramentas = Ferramenta.query.all()
    return render_template("admin/ferramentas.html", ferramentas=ferramentas)

@admin.route('/insertos')
@admin_only
def insertos():
    insertos = Inserto.query.all()
    return render_template("admin/insertos.html", insertos=insertos)


@admin.route('/users')
@admin_only
def users():
    users = User.query.all()
    return render_template("admin/users.html", users=users)


@admin.route('/add', methods=['POST', 'GET'])
@admin_only
def add():
    form = AddItemForm()

    if form.validate_on_submit():
        name = form.name.data
        price = form.price.data
        category = form.category.data
        details = form.details.data
        form.image.data.save('app/static/uploads/' + form.image.data.filename)
        image = url_for(
            'static', filename=f'uploads/{form.image.data.filename}')
        price_id = form.price_id.data
        item = Item(name=name, price=price, category=category,
                    details=details, image=image, price_id=price_id)
        db.session.add(item)
        db.session.commit()
        flash(f'{name} adicionado com sucesso!', 'success')
        return redirect(url_for('admin.items'))
    return render_template("admin/add.html", form=form)

@admin.route('/addmaq', methods=['POST', 'GET'])
@admin_only
def addmaq():
    form = CadastroMaquina()

    if form.validate_on_submit():
        code = form.code.data
        name = form.name.data        
        category_id = form.category_id.data
        details = form.details.data
        form.image.data.save('app/static/uploads/' + form.image.data.filename)
        image = url_for(
            'static', filename=f'uploads/{form.image.data.filename}')
        
        maquina = Maquina(code=code, name=name, category_id=category_id,
                    details=details, image=image)
        
        lista = form.dispositivos.data
        for v in lista:
            dispositivo = Dispositivo.query.get(v)
        
            maquina.dispositivos.append(dispositivo)
            
            db.session.add(maquina)
            db.session.commit()  

        lista = form.items.data
        for v in lista:
            item = Item.query.get(v)
        
            maquina.itens.append(item)
            
            db.session.add(maquina)
            db.session.commit() 

        lista = form.ferramentas.data
        for v in lista:
            ferramenta = Ferramenta.query.get(v)
        
            maquina.ferramentas.append(ferramenta)
            
            db.session.add(maquina)
            db.session.commit() 

        flash(f'{name} adicionado com sucesso!', 'success')
        return redirect(url_for('admin.maquinas'))
    return render_template("admin/add.html", form=form)

@admin.route('/add_dispositivo', methods=['POST', 'GET'])
@admin_only
def add_dispositivo():
    form = CadastroDispositivo()

    if form.validate_on_submit():
        code = form.code.data
        name = form.name.data        
        category = form.category.data
        details = form.details.data
        #maquinas = form.maquinas.data
        form.image.data.save('app/static/uploads/' + form.image.data.filename)
        image = url_for(
            'static', filename=f'uploads/{form.image.data.filename}')
        
        
        dispositivo = Dispositivo(code=code, name=name, category=category,
                    details=details, image=image)
        lista = form.maquinas.data
        for v in lista:
            maquina = Maquina.query.get(v)
        
            dispositivo.maquinas.append(maquina)

            
            db.session.add(dispositivo)
            db.session.commit()        

        flash(f'{name} adicionado com sucesso!', 'success')
        return redirect(url_for('admin.dispositivos'))
    return render_template("admin/add.html", form=form)


@admin.route('/edit/<string:type>/<int:id>', methods=['POST', 'GET'])
@admin_only
def edit(type, id):
    if type == "item":
        item = Item.query.get(id)
        form = AddItemForm(
            name=item.name,
            price=item.price,
            category=item.category,
            details=item.details,
            image=item.image,
            price_id=item.price_id,
        )
        if form.validate_on_submit():
            item.name = form.name.data
            item.price = form.price.data
            item.category = form.category.data
            item.details = form.details.data
            item.price_id = form.price_id.data
            form.image.data.save('app/static/uploads/' +
                                 form.image.data.filename)
            item.image = url_for(
                'static', filename=f'uploads/{form.image.data.filename}')
            db.session.commit()
            return redirect(url_for(f'admin.{type}s'))
    
    elif type == "user":
        user = User.query.get(id)
        form = AdminRegisterForm(
            name=user.name,
            email=user.email,
            phone=user.phone,
            password=user.password,
            admin=user.admin,
        )
        if form.validate_on_submit():
            user.name = form.name.data
            user.email = form.email.data
            user.phone = form.phone.data
            user.password = form.password.data
            user.admin = form.admin.data

            db.session.commit()
            return redirect(url_for(f'admin.{type}s'))

    elif type == "maquina":
        maquina = Maquina.query.get(id)
        form = CadastroMaquina(
            code=maquina.code,
            name=maquina.name,
            image=maquina.image,
            details=maquina.details,
        )
        if form.validate_on_submit():
            maquina.code = form.code.data
            maquina.name = form.name.data
            maquina.image = form.image.data
            maquina.details = form.details.data

            db.session.commit()
            return redirect(url_for(f'admin.{type}s'))

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
            return redirect(url_for(f'admin.{type}s'))

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
            return redirect(url_for(f'admin.{type}s'))
    
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
            return redirect(url_for(f'admin.{type}s'))

    return render_template('admin/add.html', form=form)


@admin.route('/delete/<string:type>/<int:id>', methods=['POST', 'GET'])
@admin_only
def delete(type, id):
    if type == "item":
        to_delete = Item.query.get(id)
        db.session.delete(to_delete)
        db.session.commit()
        flash(f'{to_delete.name} deletado com sucesso!', 'error')
        return redirect(url_for('admin.items'))

    elif type == "user":
        to_delete = User.query.get(id)
        db.session.delete(to_delete)
        db.session.commit()
        flash(f'{to_delete.name} deletado com sucesso!', 'error')
        return redirect(url_for('admin.users')) 
    
    elif type == "maquinas":
        to_delete = Maquina.query.get(id)
        db.session.delete(to_delete)
        db.session.commit()
        flash(f'{to_delete.name} deletado com sucesso!', 'error')
        return redirect(url_for(f'admin.{type}'))

    elif type == "dispositivos":
        to_delete = Dispositivo.query.get(id)
        db.session.delete(to_delete)
        db.session.commit()
        flash(f'{to_delete.name} deletado com sucesso!', 'error')
        return redirect(url_for(f'admin.{type}'))

    elif type == "ferramentas":
        to_delete = Ferramenta.query.get(id)
        db.session.delete(to_delete)
        db.session.commit()
        flash(f'{to_delete.name} deletado com sucesso!', 'error')
        return redirect(url_for(f'admin.{type}'))

    elif type == "insertos":
        to_delete = Inserto.query.get(id)
        db.session.delete(to_delete)
        db.session.commit()
        flash(f'{to_delete.name} deletado com sucesso!', 'error')
        return redirect(url_for(f'admin.{type}'))

    return render_template('admin/home.html')


@admin.route('/cleartable/<string:type>', methods=['POST', 'GET'])
@admin_only
def cleartable(type):
    if type:
        db.session.execute(f"delete from {type}")
        db.session.commit()
        flash('deletado com sucesso!', 'error')
        return redirect(url_for(f'admin.{type}'))    
    return render_template('admin/home.html')


@admin.route("/adminregister", methods=['POST', 'GET'])
@admin_only
def adminregister():
    if not current_user.is_authenticated:
        return redirect(url_for('home'))
    form = AdminRegisterForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            flash(
                f"O Usuário com email {user.email} já existe!!<br> <a href={url_for('login')}>Entrar agora</a>", "error")
            return redirect(url_for('adminregister'))
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
        flash('Administrador registrado com sucesso! Você deve logar agora.', 'success')
        return redirect(url_for('login'))
    return render_template("admin/register.html", form=form)
