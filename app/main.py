
from flask import Flask,render_template, send_from_directory, url_for, redirect, session
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from werkzeug.utils import secure_filename
from pathlib import Path
from flask_basicauth import BasicAuth
from time import sleep

from wtforms import StringField, TextAreaField, SubmitField, MultipleFileField
from wtforms.validators import DataRequired,Email, ValidationError
import subprocess
from threading import Thread

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

def has_files(form, files):
    name_types = [".bam",".bam.bai",".fa"]
    for file in form.files.data:
        matched = False
        for name in name_types:
            secure_fname = secure_filename(file.filename)
            if name in secure_fname:
                name_types.remove(name)
                new_fname = secure_filename(form.jobname.data)
                Path(f"tmp/{new_fname}").mkdir(parents=True, exist_ok=True)
                file.save(f'''tmp/{new_fname}/{new_fname}{name}''')
                matched = True
        if not matched:
            raise ValidationError



class PiscesForm(FlaskForm):
    jobname = StringField("Job Name", validators=[DataRequired()])
    files = MultipleFileField(validators=[has_files], render_kw={'multiple': True})
    submit = SubmitField("Submit Job",render_kw={"onclick":"loading();"})

@app.route("/download/<path:path>")
def send_results(path):
    return send_from_directory('tmp',path)

def process_files(jobname):
    FILE_DIR=f"tmp/{jobname}"
    CMD_CREATEGENOMESIZEFILE=f"dotnet CreateGenomeSizeFile/CreateGenomeSizeFile.dll -g {FILE_DIR}/ -o {FILE_DIR}/ -s \"Not Valid (not valid)\""
    CMD_PISCES=f"dotnet Pisces/Pisces.dll -Bam {FILE_DIR}/{jobname}.bam -G {FILE_DIR}/ -OutFolder {FILE_DIR}/ -CallMNVs false -gVCF false -RMxNFilter 5,9,0.35 -MinimumFrequency 0.01 -threadbychr true"
    with open(f"{FILE_DIR}/commands_used.txt","w+") as f:
        f.writelines([CMD_CREATEGENOMESIZEFILE, f"\n{CMD_PISCES}"])
        f.close()
    subcmd_creategenomesizefile = subprocess.run(CMD_CREATEGENOMESIZEFILE, shell=True, text=True)
    if subcmd_creategenomesizefile.returncode !=0:
        return False
    cmd = subprocess.run(CMD_PISCES, shell=True,text=True)
    return f"{cmd.stdout}\n{cmd.stderr}",True if cmd.returncode == 0 else False

@app.route("/tmp/<string:jobname>")
def display_results(jobname):
    try:
        open(f"tmp/{jobname}/done")
    except FileNotFoundError:
        return render_template("job_results.html",output_message="",jobname=jobname,done=False)
    
    commands = open(f'tmp/{jobname}/commands_used.txt').readlines()
    commands = "<br/>".join(commands)
    output_message=f"Processing completed, please click link below to download. These results will be saved for 1 day online at this URL. The commands used were:\n <br/> {commands}"
    return render_template("job_results.html",output_message=output_message,jobname=jobname,done=True)

class PiscesThread(Thread):
    def __init__(self,jobname,*args,**kwargs):
        Thread.__init__(self,*args,**kwargs)
        self.jobname = jobname
        self.output = ()
        self.done = False
    def run(self):
        self.output = process_files(self.jobname)
        self.done = True
        path = f"tmp/{self.jobname}"
        with open(f"{path}/done", "w+") as df:
            df.close()
        


@app.route("/",methods=['GET','POST'])
@basic_auth.required
def contact():
    form = PiscesForm()
    if form.validate_on_submit():
        jobname = form.jobname.data
        t = PiscesThread(target=process_files,jobname=jobname)
        t.start()
        return redirect(url_for(f"display_results",jobname=jobname))

    return render_template("start.html",form=form)

if __name__=="__main__":
    app.run(debug=True)
