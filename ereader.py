import ftplib
from pathlib import Path
import os


IP_ADDRESS = os.environ.get("EREADER_IP_ADDRESS")
EREADER_DB_PATH = Path.home().joinpath(".kobo-to-anki/KoboReader.sqlite")

def get_db() -> bool:
    """copy the KoboReader.sqlite database from the reader

    Returns
    -------
    bool
        boolean returned depends on success of copying the KoboReader.sqlite database
    """
    ereader = ftplib.FTP()
    try:
        ereader.connect(IP_ADDRESS)
        ereader.login("root","")
        with open(EREADER_DB_PATH, 'wb') as fp:
            ereader.retrbinary("RETR KoboReader.sqlite", fp.write)
        ereader.quit()
        return True
    except ftplib.all_errors as e:
        print(e)
        return False
    
if __name__ == "__main__":
    get_db()