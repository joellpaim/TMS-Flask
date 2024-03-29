import profile
from email.mime import image

from flask import Blueprint, flash, render_template, request, url_for
from flask_login import (LoginManager, current_user, login_required,
                         login_user, logout_user)
from PIL import Image
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import redirect

from ..admin.forms import (AddItemForm, AdminRegisterForm, CadastroCategoria,
                           CadastroDispositivo, CadastroFerramenta,
                           CadastroInserto, CadastroMaquina)
from ..db_models import (Categoria, Dispositivo, Ferramenta, Inserto, Item,
                         Maquina, User, db, maq_disp, maq_ferr, maq_item)
from ..funcs import admin_only

admin = Blueprint("admin", __name__, url_prefix="/admin",
                  static_folder="static", template_folder="templates")
                  


@admin.route('/')
@admin_only
def dashboard():
    maquinas = Maquina.query.all()
    items = Item.query.all()
    ferramentas = Ferramenta.query.all()
    return render_template("admin/dashboard.html", maquinas=maquinas)


@admin.route('/items')
@admin_only
def items():
    items = Item.query.all()
    return render_template("admin/items.html", items=items)

@admin.route('/categorias')
@admin_only
def categorias():
    categorias = Categoria.query.all()
    return render_template("admin/categorias.html", categorias=categorias)

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
        code = form.code.data
        name = form.name.data        
        category = form.category.data
        details = form.details.data
        image = ("Sem imagem")
        item = Item(code=code, name=name, category=category,
                    details=details, image=image)
        db.session.add(item)
        db.session.commit()
        flash(f'{name} adicionado com sucesso!', 'success')
        return redirect(url_for('admin.items'))
    return render_template("admin/add.html", form=form)

@admin.route('/add_categoria', methods=['POST', 'GET'])
@admin_only
def add_categoria():
    form = CadastroCategoria()

    if form.validate_on_submit():
        name = form.name.data
        details = form.details.data
        form.image.data.save('app/static/uploads/categorias/' + form.image.data.filename)
        image = url_for(
            'static', filename=f'uploads/categorias/{form.image.data.filename}')
        
        categoria = Categoria(name=name, details=details, image=image)

        lista = form.maquinas.data
        for v in lista:
            maquina = Maquina.query.get(v)
        
            categoria.maquinas.append(maquina)
            
            db.session.add(categoria)
            db.session.commit() 
        
        flash(f'{name} adicionado com sucesso!', 'success')
        return redirect(url_for('admin.categorias'))
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
        form.image.data.save('app/static/uploads/maquinas/' + form.image.data.filename)
        image = url_for(
            'static', filename=f'uploads/maquinas/{form.image.data.filename}')
        
        if category_id:
            maquina = Maquina(code=code, name=name, category_id=category_id,
                    details=details, image=image)
        else:
            maquina = Maquina(code=code, name=name, details=details, image=image)        
        
        
        for id in form.dispositivos.data:
                maquina.dispositivos.append(Dispositivo.query.get(id))

        for id in form.items.data:
            maquina.itens.append(Item.query.get(id))

        for id in form.ferramentas.data:
            maquina.ferramentas.append(Ferramenta.query.get(id))

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
        form.image.data.save('app/static/uploads/dispositivos/' + form.image.data.filename)
        image = url_for(
            'static', filename=f'uploads/dispositivos/{form.image.data.filename}')
        
        
        dispositivo = Dispositivo(code=code, name=name, category=category,
                    details=details, image=image)
        lista = form.maquinas.data
        if lista:
            for v in lista:
                maquina = Maquina.query.get(v)
            
                dispositivo.maquinas.append(maquina)
                
                db.session.add(dispositivo)
                db.session.commit()  
        else:
            db.session.add(dispositivo)
            db.session.commit() 

        flash(f'{name} adicionado com sucesso!', 'success')
        return redirect(url_for('admin.dispositivos'))
    return render_template("admin/add.html", form=form)

@admin.route('/add_ferramenta', methods=['POST', 'GET'])
@admin_only
def add_ferramenta():
    form = CadastroFerramenta()

    if form.validate_on_submit():
        code = form.code.data
        name = form.name.data 
        price = form.price.data       
        category = form.category.data
        details = form.details.data
        form.image.data.save('app/static/uploads/ferramentas/' + form.image.data.filename)
        image = url_for(
            'static', filename=f'uploads/ferramentas/{form.image.data.filename}')
        
        
        ferramenta = Ferramenta(code=code, name=name, price=price, category=category,
                    details=details, image=image)

        lista = form.insertos.data

        if lista:
            for v in lista:
                inserto = Inserto.query.get(v)
            
                ferramenta.insertos.append(inserto)
                
                db.session.add(ferramenta)
                db.session.commit()
        else:
            db.session.add(ferramenta)
            db.session.commit()
         

        flash(f'{name} adicionado com sucesso!', 'success')
        return redirect(url_for('admin.ferramentas'))
    return render_template("admin/add.html", form=form)


@admin.route('/edit/<string:type>/<int:id>', methods=['POST', 'GET'])
@admin_only
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
            return redirect(url_for(f'admin.{type}s'))
    
    elif type == "user":
        user = User.query.get(id)
        #profile = Profile.query.get(user.id)
        form = AdminRegisterForm(
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
            return redirect(url_for(f'admin.{type}s'))

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
            return redirect(url_for(f'admin.{type}s'))

    elif type == "maquina":
        maquina = Maquina.query.get(id)
        
        form = CadastroMaquina(
            code=maquina.code,
            name=maquina.name,
            image=maquina.image,
            details=maquina.details,
            category_id=maquina.category_id,
            dispositivos=maquina.dispositivos,
            items=maquina.itens,
            ferramentas=maquina.ferramentas
        )

        print(maquina.dispositivos)
                
        if form.validate_on_submit():
            maquina.code = form.code.data
            maquina.name = form.name.data
            maquina.image = form.image.data
            maquina.details = form.details.data
            maquina.category_id = form.category_id.data

            for id in form.dispositivos.data:
                maquina.dispositivos.append(Dispositivo.query.get(id))

            for id in form.items.data:
                maquina.itens.append(Item.query.get(id))

            for id in form.ferramentas.data:
                maquina.ferramentas.append(Ferramenta.query.get(id))

            db.session.commit()
            flash(f'{maquina.code} alterado com sucesso!', 'success')
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

    return render_template('admin/edit.html', form=form, maquina=maquina)

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

@admin.route('/search/<string:type>')
def search(type):
    query = request.args['query']
    search = "%{}%".format(query)

    if type == 'items':      
        items = Item.query.filter(Item.code.like(search)).all()
        return render_template('admin/items.html', items=items, search=True, query=query)

    else:
        pass
