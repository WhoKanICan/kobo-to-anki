import sqlite3
from pathlib import Path

ANKI_DB_PATH = Path.home().joinpath(".kobo-to-anki/anki.sqlite")

NOTES_TABLE_SCHEMA = """
CREATE TABLE "Notes" (
"IdNotes" INTEGER,
"Id" INTEGER,
"Word" TEXT UNIQUE,
"Book" TEXT,
"DateAdded" TEXT,
PRIMARY KEY("IdNotes" AUTOINCREMENT)
);
"""

WORDS_TABLE_SCHEMA = """
CREATE TABLE "Words" (
"IdWords"   INTEGER,
"HeadWord"  TEXT,
"Stem"  TEXT,
PRIMARY KEY("IdWords" AUTOINCREMENT)
);
"""


def exist(db_path: str) -> str:
    """Is used to check if the anki database exists

    Parameters
    ----------
    db_path : str
        the path where the anki database should reside

    Returns
    -------
    str
        boolean depending on if the database can be found
    """
    if db_path.exists():
        return True
    else:
        db_path.parent.mkdir(exist_ok=True)
        db_path.touch(exist_ok=True)
        return False


def create_table(db_path: str, schema: str) -> None:
    """create the table schema

    Parameters
    ----------
    db_path : str
        path to the database
    schema : str
        the schema that should be created

    Returns
    -------
    _type_
        return None
    """
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(schema)
    con.commit()
    con.close()
    return None


def query(db_path: str) -> tuple:
    """used to grab the words from the KoboReader.sqlite

    Parameters
    ----------
    db_path : str
        path to copied KoboReader.sqlite which will reside in /home/username/.kobo-to-anki

    Returns
    -------
    tuple
        a tuple containing all the words from the WordList table within KoboReader.sqlite
    """
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    results = cur.execute("SELECT * FROM WordList").fetchall()
    con.close()
    return results


def word_exist(db_path: str, word: str) -> tuple:
    """Check if the word exists before making a query to merriam webster

    Parameters
    ----------
    db_path : str
        path to Anki.sqlite database
    word : str
        The headword

    Returns
    -------
    tuple
        if nothing is return then word does not exists to a query will be made
    """    
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    result = cur.execute("""
        SELECT Notes.Id
        FROM Words LEFT JOIN Notes ON Words.HeadWord = Notes.Word
        WHERE Words.Stem = (?) AND Notes.Id IS NOT NULL""", (word,)).fetchone()
    con.close()
    return result


def update_notes(db_path: str, word: str, note_id: str, book: str, date_added: str) -> None:
    """Updates the Notes table within the Anki.sqlite database

    Parameters
    ----------
    db_path : str
        path to the anki.sqlite database
    word : str
        the head word to add
    note_id : str
        the note id provided because of the creation within anki
    book : str
        the book in which the word was added
    date_added : str
        the date in which that word was added

    Returns
    -------
    _type_
        return nothing
    """    
    book = book.replace("file:///mnt/onboard/", "")
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO Notes (Id, Word, Book, DateAdded) VALUES (?,?,?,?)
        """, (
            note_id, word, book, date_added
        )
    )
    con.commit()
    con.close()
    return None


def update_words(db_path: str, word: str, stems_set: set) -> None:
    """Updates the word table within the Anki.sqlite database

    Parameters
    ----------
    db_path : str
        path to the anki.sqlite database
    word : str
        the head word
    stems_set : set
        the head word stems

    Returns
    -------
    _type_
        Return nothing
    """ 
    con = sqlite3.connect(db_path)
    cur = con.cursor()
    for stem in stems_set:
        cur.execute(
            """
            INSERT INTO Words (HeadWord, Stem) VALUES (?,?)
            """, (
                word,
                stem
            )
        )
    con.commit()
    con.close()
    return None
