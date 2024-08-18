import subprocess
import psutil
while True:
    for proc in psutil.process_iter():
        name = proc.name()
        print(name)
        if name == "main.py":
            continue
        else:
            subprocess.call("python main.py", shell=True)