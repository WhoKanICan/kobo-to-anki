import subprocess


def start():
    """
    starts anki
    """
    subprocess.Popen(
        "pgrep anki > /dev/null || anki > /dev/null",
        shell=True,
    )
