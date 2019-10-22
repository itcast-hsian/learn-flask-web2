from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp

class PostForm(FlaskForm):
	body = TextAreaField("What's on your mind?", validators=[DataRequired()])
	submit = SubmitField('Submit')