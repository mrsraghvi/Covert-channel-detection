import subprocess
import time
import sys

def launch(cmd, title):
    print(f"[+] Starting {title}")
    return subprocess.Popen(cmd, shell=True)

processes = []

try:
    processes.append(
        launch("python live/live_logger.py", "Live Logger")
    )
    time.sleep(2)

    processes.append(
        launch("python -m live.realtime_detector", "Realtime Detector")
    )
    time.sleep(2)

    processes.append(
        launch("streamlit run dashboard/app.py", "Dashboard")
    )

    print("\n🚀 Covert Channel IDS is running")
    print("Press CTRL+C to stop all services\n")

    while True:
        time.sleep(5)

except KeyboardInterrupt:
    print("\n[!] Shutting down system...")
    for p in processes:
        p.terminate()
    sys.exit(0)
