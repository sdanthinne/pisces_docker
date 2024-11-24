from werkzeug.utils import secure_filename
from pathlib import Path
from wtforms.validators import Email, ValidationError

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