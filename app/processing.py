from threading import Thread
import subprocess
import re
import logging

DOTNET = "dotnet"

CMD_PISCES_BASE = "Pisces/Pisces.dll"
CMD_CREATEGENOMESIZEFILE_BASE = "CreateGenomeSizeFile/CreateGenomeSizeFile.dll"

CMD_CREATEGENOMESIZEFILE=" ".join([DOTNET, CMD_CREATEGENOMESIZEFILE_BASE, "-g {FILE_DIR}/ -o {FILE_DIR}/ -s \"Not Valid (not valid)\""])
CMD_PISCES=" ".join([DOTNET, CMD_PISCES_BASE, "-Bam {FILE_DIR}/{jobname}.bam -G {FILE_DIR}/ -OutFolder {FILE_DIR}/ -CallMNVs false -gVCF false -RMxNFilter 5,9,0.35 -MinimumFrequency 0.01 -threadbychr true"])

def process_files(jobname):
    FILE_DIR=f"tmp/{jobname}"
    genome_size_cmd = CMD_CREATEGENOMESIZEFILE.format(kwargs={"FILE_DIR":FILE_DIR})
    pisces_cmd = CMD_PISCES.format(kwargs={"FILE_DIR":FILE_DIR,"jobname":jobname})
    with open(f"{FILE_DIR}/commands_used.txt","w+") as f:
        f.writelines([genome_size_cmd, f"\n{pisces_cmd}"])
        f.close()
    subcmd_creategenomesizefile = subprocess.run(genome_size_cmd, shell=True, text=True)
    if subcmd_creategenomesizefile.returncode !=0:
        return False
    cmd = subprocess.run(pisces_cmd, shell=True,text=True)
    return f"{cmd.stdout}\n{cmd.stderr}",True if cmd.returncode == 0 else False

class PiscesThread(Thread):
    def __init__(self,jobname,*args,**kwargs):
        Thread.__init__(self,*args,**kwargs)
        self.jobname = jobname
        self.output = ()
        self.done = False

    def run(self):
        logging.info(f"Starting processing for {self.jobname}")
        self.output = process_files(self.jobname)
        logging.info(f"Finished processing for {self.jobname}")
        self.done = True
        path = f"tmp/{self.jobname}"
        with open(f"{path}/done", "w+") as df:
            df.close()

def generate_form(example_command: str) -> dict:
    out = subprocess.run(" ".join(DOTNET, example_command), text=True, shell=True)
    command_help: str = out.stdout
    # this regex does not match everything...
    matches = re.findall(r"(?P<command>[-]+[a-z_]+).* (?:<(?P<type>[A-Z]+)>)*\s+(?P<description>[A-Za-z\.,\+\-':=% 0-9\n\(\)]+)(?:      )|(?:\n)", command_help)
    cmd = {}
    for match in matches:
        if not match[0]:
            continue
        else:
            cmd[match[0]] = {"description": match[2], "type": match[1]}

    return cmd

def generate_forms() -> dict:
    return generate_form(CMD_PISCES_BASE) | generate_form(CMD_CREATEGENOMESIZEFILE_BASE)
