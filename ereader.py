from pathlib import Path
import subprocess


def get_db_path() -> Path:
    """
    Return the KoboReader.sqlite path from the mount path

    Returns
    -------
    Path
        to the KoboReader.sqlite db path

    Raises
    ------
    Exception
        if Kobo reader can not be found
    """
    db_path = subprocess.getoutput(
        "df -h --output=target | grep -P '.*KOBOeReader'",
    )
    if not db_path:
        raise Exception(
            "Kobo Reader can not be found. Ensure device is plugged in and mounted"
        )
    return Path(db_path).joinpath(".kobo/KoboReader.sqlite")
