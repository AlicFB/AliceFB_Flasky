from flask import render_template, session, redirect, url_for, current_app, flash, request
from .. import db
from ..models import User, Role
from ..email import send_simple_message, unique_recipients, PROFESSOR_EMAIL
from . import main
from .forms import NameForm, EditUserForm, DeleteForm


@main.route('/', methods=['GET', 'POST'])
def index():
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data.strip()
        user = User.query.filter_by(username=name).first()
        if user is None:
            Role.insert_roles()
            user = User(username=name,
                        role=Role.query.filter_by(name='User').first())
            db.session.add(user)
            db.session.commit()
            session['known'] = False

            recipients = unique_recipients(
                PROFESSOR_EMAIL,
                current_app.config.get('FLASKY_ADMIN'),
                form.email.data,
            )
            send_simple_message(recipients, 'Novo usuário', name)
        else:
            session['known'] = True

        session['name'] = name
        return redirect(url_for('.index'))

    users = User.query.order_by(User.id).all()

    edit_id = request.args.get('edit', type=int)
    edit_form = None
    if edit_id is not None:
        user_to_edit = db.session.get(User, edit_id)
        if user_to_edit is not None:
            edit_form = EditUserForm(user=user_to_edit)
            edit_form.name.data = user_to_edit.username
        else:
            edit_id = None

    return render_template('index.html',
                           form=form,
                           delete_form=DeleteForm(),
                           edit_form=edit_form,
                           edit_id=edit_id,
                           name=session.get('name'),
                           known=session.get('known', False),
                           users=users)


@main.route('/edit/<int:id>', methods=['POST'])
def edit_user(id):
    user = db.get_or_404(User, id)
    form = EditUserForm(user=user)
    if form.validate_on_submit():
        user.username = form.name.data.strip()
        db.session.commit()
        flash('Usuário atualizado com sucesso.')
        return redirect(url_for('.index'))
    for errors in form.errors.values():
        for error in errors:
            flash(error)
    return redirect(url_for('.index', edit=id))


@main.route('/delete/<int:id>', methods=['POST'])
def delete_user(id):
    form = DeleteForm()
    if not form.validate_on_submit():      # valida o token CSRF
        flash('Requisição inválida.')
        return redirect(url_for('.index'))
    user = db.get_or_404(User, id)
    username = user.username
    db.session.delete(user)
    db.session.commit()
    if session.get('name') == username:
        session.pop('name', None)
    flash(f'Usuário "{username}" excluído.')
    return redirect(url_for('.index'))