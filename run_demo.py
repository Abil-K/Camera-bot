"""Start simulation and two project nodes; keep logs for the report."""
import fcntl
import glob
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

root = Path(__file__).resolve().parent
children, handles = [], []
lock_file = (root / 'logs/demo.lock').open('w')

def launch(name, args):
    log = (root / 'logs' / f'{name}.log').open('w', buffering=1)
    handles.append(log)
    p = subprocess.Popen(args, cwd=root, stdout=log, stderr=subprocess.STDOUT, start_new_session=True)
    children.append(p)
    return p

def main():
    try:
        fcntl.flock(lock_file,fcntl.LOCK_EX|fcntl.LOCK_NB)
    except BlockingIOError:
        raise SystemExit('The project demo is already running.')
    print('Starting TurtleBot3 Gazebo. Logs:', root/'logs', flush=True)
    sim = launch('gazebo', ['ros2','launch','turtlebot3_gazebo','empty_world.launch.py'])
    topic_type = ''
    for _ in range(90):
        if sim.poll() is not None:
            raise RuntimeError('Gazebo exited; see logs/gazebo.log')
        try:
            response = subprocess.run(['ros2','topic','type','/cmd_vel'],capture_output=True,text=True,timeout=3)
            topic_type = response.stdout.strip()
        except subprocess.TimeoutExpired:
            topic_type = ''
        if topic_type in ('geometry_msgs/msg/Twist','geometry_msgs/msg/TwistStamped'):
            break
        time.sleep(1)
    if not topic_type:
        raise RuntimeError('No /cmd_vel topic from simulator; see logs/gazebo.log')
    print('Simulator command type:',topic_type,flush=True)
    python = str(root/'.venv/bin/python')
    devices = sorted(glob.glob('/dev/video*'))
    if not devices:
        raise RuntimeError('No /dev/video*: attach camera under VirtualBox Devices > Webcams')
    # Verify a capture endpoint: a webcam can expose a second metadata-only node.
    import cv2
    device = None
    for candidate in devices:
        cap = cv2.VideoCapture(candidate,cv2.CAP_V4L2)
        ok,_ = cap.read() if cap.isOpened() else (False,None)
        cap.release()
        if ok:
            device = candidate
            break
    if device is None:
        raise RuntimeError('Camera is attached but no frames can be read. Close other camera apps.')
    camera = launch('camera',[python,'-m','gesture_control.camera_node','--ros-args','-p',f'device:={device}'])
    stamped = 'true' if topic_type.endswith('TwistStamped') else 'false'
    robot = launch('robot',[python,'-m','gesture_control.robot_node','--ros-args','-p',f'stamped:={stamped}'])
    print('Click ENABLE in the camera window. Click STOP to disable. Ctrl+C closes the demo.',flush=True)
    while all(p.poll() is None for p in children):
        time.sleep(.5)
    failed = [(name,p.returncode) for name,p in zip(['gazebo','camera','robot'],children) if p.poll() is not None]
    print('Process ended:',failed,flush=True)

def stop_all():
    for p in reversed(children):
        if p.poll() is None:
            try: os.killpg(p.pid,signal.SIGINT)
            except ProcessLookupError: pass
    deadline=time.monotonic()+8
    for p in children:
        try: p.wait(timeout=max(.1,deadline-time.monotonic()))
        except subprocess.TimeoutExpired:
            try: os.killpg(p.pid,signal.SIGTERM)
            except ProcessLookupError: pass
    for h in handles: h.close()

if __name__=='__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
    except Exception as exc:
        print('DEMO STOPPED:',exc,flush=True)
    finally:
        stop_all()
