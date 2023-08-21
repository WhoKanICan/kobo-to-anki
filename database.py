import sqlite3
from pathlib import Path
from typing import Tuple
from collections.abc import Iterable
import string

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


def is_created(db_path: Path):
    """
    Used to check if the anki database exists.
    If path and/ or sqlite does not exist then these are created

    Parameters
    ----------
    db_path : str
        the path where the anki database should reside
    """
    if not db_path.exists():
        db_path.parent.mkdir(exist_ok=True)
        db_path.touch(exist_ok=True)


def open(db_path: Path) -> sqlite3.Connection:
    """
    Helper function to open sqlite database

    Parameters
    ----------
    db_path : str
        path to the database to be opened

    Returns
    -------
    sqlite3.Connection
        database connection object
    """
    if db_path.exists():
        return sqlite3.connect(db_path)
    raise FileNotFoundError(db_path)


def close(db_connection: sqlite3.Connection):
    """
    Helper function to close sqlite database

    Parameters
    ----------
    db_connection : sqlite3.Connection
        database connection object
    Returns
    -------
    sqlite3.Connection
        database connection object
    """
    db_connection.close()


def create_table(db_connection: sqlite3.Connection, schema: str):
    """
    Create the table schema if they do not exists

    Parameters
    ----------
    db_connection : sqlite3.Connection
        database connection object

    schema : str
        the schema that should be created
    """
    try:
        db_connection.execute(schema)
        db_connection.commit()
    except sqlite3.OperationalError:
        pass


def query_world_list(
    db_connection: sqlite3.Connection,
) -> Iterable[Tuple[str, str, str, str]]:
    """
    Used to grab the words from the KoboReader.sqlite

    Parameters
    ----------
    db_connection : sqlite3.Connection
        database to copy. KoboReader.sqlite will reside in /home/username/.kobo-to-anki/

    Returns
    -------
    tuple
        a tuple containing all the words from the WordList table
    """
    queried_words = db_connection.execute("SELECT * FROM WordList").fetchall()

    for idx, (word, book, _, date_added) in enumerate(queried_words):
        word = word.lower().strip(string.punctuation)
        book = book.replace("file:///mnt/onboard/", "")
        queried_words[idx] = word, book, _, date_added
    # if word list is not enabled or no words are present an empty list will be returned
    if not queried_words:
        raise Exception("No words can be found in My Words")
    return queried_words


def word_exist(db_connection: sqlite3.Connection, word: str) -> tuple:
    """
    Check if the word exists before making a query to merriam webster

    Parameters
    ----------
    db_connection : sqlite3.Connection
        database connection object
    word : str
        The headword

    Returns
    -------
    tuple
        if nothing is return then word does not exists to a query will be made
    """
    return db_connection.execute(
        """
        SELECT Notes.Id
        FROM Words LEFT JOIN Notes ON Words.HeadWord = Notes.Word
        WHERE Words.Stem = (?) AND Notes.Id IS NOT NULL
        """,
        (word,),
    ).fetchone()


def update_notes(
    db_connection: sqlite3.Connection,
    word: str,
    note_id: str,
    book: str,
    date_added: str,
):
    """
    Updates the Notes table within the Anki.sqlite database

    Parameters
    ----------
    db_connection : sqlite3.Connection
        database connection object
    word : str
        the head word to add
    note_id : str
        the note id provided because of the creation within anki
    book : str
        the book in which the word was added
    date_added : str
        the date in which that word was added
    """
    db_connection.execute(
        """
        INSERT INTO Notes (Id, Word, Book, DateAdded) VALUES (?,?,?,?)
        """,
        (note_id, word, book, date_added),
    )
    db_connection.commit()


def update_words(db_connection: sqlite3.Connection, word: str, stems_set: set):
    """
    Updates the word table within the Anki.sqlite database

    Parameters
    ----------
    db_connection : sqlite3.Connection
        database connection object
    word : str
        the head word
    stems_set : set
        the head word stems
    """
    for stem in stems_set:
        db_connection.execute(
            """
            INSERT INTO Words (HeadWord, Stem) VALUES (?,?)
            """,
            (word, stem),
        )
    db_connection.commit()
