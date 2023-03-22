
from flask import Flask,render_template
from flask_wtf import FlaskForm

from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired,Email

app = Flask(__name__)
app.config["SECRET_KEY"] = 'this is the way the world started. In chaos'


class PiscesForm(FlaskForm):
    name = StringField("Name:", validators=[DataRequired()])
    submit = SubmitField("Submit Job")

@app.route("/",methods=['GET','POST'])
def contact():
    form = ContactForm()
    if form.validate_on_submit():
        name = form.name.data
        return f"thanks! {name}"
    return render_template("start.html")

if __name_=="__main__":
    app.run(debug=True)
