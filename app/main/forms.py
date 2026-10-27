from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length, ValidationError
from ..models import User


class NameForm(FlaskForm):
    name = StringField('Qual é o seu nome?', validators=[DataRequired()])
    email = StringField('Qual é o seu email (Envio de notificação do novo usuário)?', validators=[Optional(), Email()])
    submit = SubmitField('Submit')


class EditUserForm(FlaskForm):
    name = StringField('Nome do usuário', validators=[DataRequired(), Length(max=64)])
    submit = SubmitField('Salvar')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def validate_name(self, field):
        name = field.data.strip()
        other = User.query.filter_by(username=name).first()
        if other is not None and other.id != self.user.id:
            raise ValidationError('Já existe um usuário com esse nome.')


class DeleteForm(FlaskForm):
    pass