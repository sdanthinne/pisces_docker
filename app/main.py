from flask import Flask,flash,request,redirect,url_for,send_from_directory
from werkzeug.utils import secure_filename

import os

app = Flask(__name__)


##envs
UPLOAD_FOLDER="/temp/"
ALLOWED_EXTENSIONS={'.bam','.bai','.fa'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
##

def allowed_filename(fname):
    return '.' in fname and filename.rsplit('.',1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/uploads/<name>')
def download_file(name):
    return send_from_directory(app.config["UPLOAD_FOLDER"], name)

@app.route('/',methods=['GET','POST'])
def main_upload():
    if request.method == 'POST':
        print("POST rcvd")
        if 'file' not in request.files:
            flash('no file part')
            return redirect(request.url)
        files = request.files['file']
        filename = ''
        for f in files:
            if f.filename == '':
                flash("No selected file")
                return redirect(request.url)
            if f and allowed_filename(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(app.config['UPLOAD_FOLDER'],f))
        return redirect(url_for('download file', name=filename))
    return '<!doctype html><h1>Welcome to Pisces Online.</h1>\
        <form method=post enctype=multipart/form-data>\
        <input type="file" name="file" multiple="multiple">\
        <input type="submit" value="Upload"\
        </form>\
        '

@app.route('/process')
def process():
    return 'processing... <a href="output.vcf">download here</a>'
