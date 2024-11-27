
from flask import Flask,render_template, send_from_directory, url_for, redirect, session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from pathlib import Path
from flask_basicauth import BasicAuth
from time import sleep

from wtforms import StringField, TextAreaField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired
import subprocess
from threading import Thread

from utils import has_files
from processing import PiscesThread, generate_form

form = None # global form object

def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = 'this is the way the world started. In chaos'
    app.config["BASIC_AUTH_USERNAME"] = 'od260'
    app.config["BASIC_AUTH_PASSWORD"] = 'od260ONLY'

    AUTH_HASH='pbkdf2:sha256:260000$AAwUgjbKNucc80Sj$6e15d7de7a0010800f87bfd208b62ae0182b8d9c8a02b76c1b6720fd7a38ff00'
    app.secret_key = AUTH_HASH
    return app

app = create_app()
basic_auth = BasicAuth(app)

class PiscesForm(FlaskForm):
    jobname = StringField("Job Name", validators=[DataRequired()])
    files = MultipleFileField(validators=[has_files], render_kw={'multiple': True})
    submit = SubmitField("Submit Job",render_kw={"onclick":"loading();"})

@app.route("/download/<path:path>")
def send_results(path):
    app.logger.info(f"Sending from path {path}")
    return send_from_directory('tmp',path)

@app.route("/s/<path:path>")
def send_static(path):
    return send_from_directory('static',path)

@app.route("/tmp/<string:jobname>")
def display_results(jobname):
    try:
        open(f"tmp/{jobname}/done")
    except FileNotFoundError:
        app.logger.info(f"File not found, must not be done with processing")
        return render_template("job_results.html",output_message="",jobname=jobname,done=False)

    commands = open(f'tmp/{jobname}/commands_used.txt').readlines()
    commands = "<br/>".join(commands)
    output_message=f"Processing completed, please click link below to download. These results will be saved for 1 day online at this URL. The commands used were:\n <br/> {commands}"
    return render_template("job_results.html",output_message=output_message,jobname=jobname,done=True)

@app.route("/",methods=['GET','POST'])
@basic_auth.required
def contact():
    form = PiscesForm()
    if form.validate_on_submit():
        jobname = form.jobname.data
        app.logger.info(f"Form is valid, dispatching processing for name \"{jobname}\"")
        t = PiscesThread(jobname=jobname)
        t.start()
        return redirect(url_for(f"display_results",jobname=jobname))
    app.logger.info(f"Form is invalid, redirect to home")
    return render_template("start.html",form=form)

if __name__=="__main__":
    form = generate_form()
    app.run(debug=True)
