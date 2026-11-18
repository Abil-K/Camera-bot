#!/usr/bin/env python3
"""Install this classroom project in the Ubuntu guest; never run as root."""
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import sys
import urllib.request

SOURCE = Path(__file__).resolve().parent
ROOT = Path.home() / 'ros_camera_robot'

def make_writable(path):
    """Files copied from an optical disk must remain editable by their owner."""
    if not path.exists() or path.is_symlink():
        return
    paths = [path]
    if path.is_dir():
        paths.extend(path.rglob('*'))
    for item in paths:
        if not item.is_symlink():
            mode = item.stat().st_mode | stat.S_IWUSR
            if item.is_dir():
                mode |= stat.S_IXUSR
            item.chmod(mode)

def run(args, **kw):
    print('\nRUN:', ' '.join(map(str, args)), flush=True)
    subprocess.run(list(map(str, args)), check=True, **kw)

def main():
    if os.geteuid() == 0:
        raise SystemExit('Run python3 setup.py as your normal Ubuntu user.')
    if ROOT.exists() and SOURCE != ROOT and not (ROOT / '.ros_camera_project').exists():
        raise SystemExit(f'{ROOT} already exists without our marker. Nothing overwritten.')
    ROOT.mkdir(exist_ok=True)
    (ROOT / '.ros_camera_project').write_text('Classroom ROS2 camera project\n')
    if SOURCE != ROOT:
        for name in ['install_system.sh', 'run_demo.sh', 'run_demo.py', 'src', 'tests', 'README_RU.md', 'VALIDATION.md', 'DEMO_RU.md']:
            origin = SOURCE / name
            destination = ROOT / name
            make_writable(destination)
            if origin.is_dir():
                shutil.copytree(origin, destination, dirs_exist_ok=True)
            elif origin.exists():
                shutil.copy2(origin, destination)
            make_writable(destination)
        make_writable(ROOT / 'setup.py')
        shutil.copy2(__file__, ROOT / 'setup.py')
        make_writable(ROOT / 'setup.py')
    (ROOT / 'logs').mkdir(exist_ok=True)
    print('Project folder:', ROOT, flush=True)
    print('Ubuntu system packages require your sudo password ONCE. It is not stored.', flush=True)
    run(['sudo', 'bash', ROOT / 'install_system.sh'])
    sim = ROOT / 'simulation_ws/src/turtlebot3_simulations'
    if not sim.exists():
        sim.parent.mkdir(parents=True, exist_ok=True)
        run(['git', 'clone', '--depth', '1', '--branch', 'jazzy',
             'https://github.com/ROBOTIS-GIT/turtlebot3_simulations.git', sim])
    run(['bash', '-c', 'source /opt/ros/jazzy/setup.bash && colcon build --symlink-install --parallel-workers 2'], cwd=sim.parent.parent)
    venv = ROOT / '.venv'
    run([sys.executable, '-m', 'venv', '--system-site-packages', venv])
    python = venv / 'bin/python'
    run([python, '-m', 'pip', 'install', 'numpy==1.26.4', 'opencv-contrib-python==4.11.0.86', 'mediapipe==0.10.21'])
    models = ROOT / 'models'
    models.mkdir(exist_ok=True)
    model = models / 'gesture_recognizer.task'
    if not model.exists():
        url = 'https://storage.googleapis.com/mediapipe-models/gesture_recognizer/gesture_recognizer/float16/1/gesture_recognizer.task'
        print('Downloading the official MediaPipe gesture model...', flush=True)
        with urllib.request.urlopen(url, timeout=120) as response:
            model.write_bytes(response.read())
    run([python, '-m', 'unittest', 'discover', '-s', str(ROOT / 'tests'), '-v'], cwd=ROOT)
    env = os.environ.copy()
    env['PYTHONPATH'] = str(ROOT / 'src')
    run(['bash', '-c', 'source /opt/ros/jazzy/setup.bash && .venv/bin/python -c "import rclpy, cv2, mediapipe; from sensor_msgs.msg import Image; from geometry_msgs.msg import TwistStamped; print(\'ROS_AND_VISION_IMPORTS_OK\')"'], cwd=ROOT, env=env)
    (ROOT / 'run_demo.sh').chmod(0o755)
    desktop = Path.home() / 'Desktop'
    desktop.mkdir(exist_ok=True)
    launcher = desktop / 'ROS2_Camera_TurtleBot.desktop'
    launcher.write_text('[Desktop Entry]\nType=Application\nName=ROS2 Camera TurtleBot\nComment=Webcam gesture control in Gazebo\nExec=bash ' + str(ROOT / 'run_demo.sh') + '\nIcon=camera-web\nTerminal=true\n', encoding='utf-8')
    launcher.chmod(0o755)
    subprocess.run(['gio', 'set', str(launcher), 'metadata::trusted', 'true'], check=False)
    subprocess.run(['VBoxClient', '--clipboard'], check=False)
    (ROOT / 'logs/setup_status.json').write_text(json.dumps({'status':'installed', 'python':platform.python_version(), 'ros':'jazzy', 'simulation_commit':subprocess.check_output(['git','rev-parse','HEAD'],cwd=sim,text=True).strip()},indent=2))
    print('\nSETUP COMPLETE. Starting the demo, motion initially DISABLED.\n', flush=True)
    os.execv('/bin/bash', ['bash', str(ROOT / 'run_demo.sh')])

if __name__ == '__main__':
    try:
        main()
    except Exception as error:
        print('\nSETUP STOPPED:', error, flush=True)
        raise
