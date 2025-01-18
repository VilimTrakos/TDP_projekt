import subprocess
import sys
import os

def launch_script(script_name, *args):
    python_executable = sys.executable
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    subprocess.Popen([python_executable, script_path] + [str(arg) for arg in args])
