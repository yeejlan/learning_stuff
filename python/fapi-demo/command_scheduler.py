import os
import subprocess
import sys
import schedule
import time

working_path = os.getcwd()
python = sys.executable

def job():
    print("I'm working...")


def run_command(command):
    _ = subprocess.Popen(command, shell=True, cwd=working_path)

def run_python_script(command):
    _ = subprocess.Popen(f"{python} {command}", shell=True, cwd=working_path)    
    

schedule.every(1).minutes.do(job)


if __name__ == "__main__":
    job()
    run_python_script(f'commands/echo.py Python = {python}')

    while True:
        schedule.run_pending()
        time.sleep(1)

