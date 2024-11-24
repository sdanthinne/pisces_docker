from threading import Thread
import subprocess

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
