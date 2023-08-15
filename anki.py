import subprocess
import time

def start() -> None:
    """starts anki
    """
    subprocess.Popen(
        "ps -C anki >/dev/null || anki >/dev/null",
        shell=True
    )

def close() -> None:
    """kills anki
    """
    subprocess.run(
        "kill $(ps -C anki -o pid=)",
        shell=True
    )