import ankiconnect
import database
import ereader
import merriam
import anki
from pathlib import Path

ANKI_DB_PATH = Path.home().joinpath(".kobo-to-anki/Anki.sqlite")


def main():
    # query wordList table in KoboReader.sqlite
    ereader_db_path = ereader.get_db_path()
    ereader_db_connection = database.open(ereader_db_path)
    ereader_saved_words = database.query_world_list(ereader_db_connection)
    database.close(ereader_db_connection)
    # create Anki.sqlite db if it does not exists
    database.is_created(ANKI_DB_PATH)
    # start and check services
    anki.start()  # have this start then
    ankiconnect.status()  # this can start. needs to be sync
    ankiconnect.setup()
    # open db
    anki_db = database.open(ANKI_DB_PATH)
    database.create_table(anki_db, database.NOTES_TABLE_SCHEMA)
    database.create_table(anki_db, database.WORDS_TABLE_SCHEMA)

    # database setup
    for word, book, _, date_added in ereader_saved_words:
        if not database.word_exist(anki_db, word):
            # api call
            data = merriam.get_word(word)
            parsed_data = merriam.parse(data)
            # unpack dict
            word = parsed_data["word"]
            stem_set = parsed_data["stem_set"]
            # create notes
            template = ankiconnect.create_note(parsed_data)
            note_id = ankiconnect.invoke("addNote", **template)
            # update notes and words table
            database.update_notes(anki_db, word, note_id, book, date_added)
            database.update_words(anki_db, word, stem_set)
    # close db
    database.close(anki_db)
    database.close(ereader_db_connection)
    # sync
    ankiconnect.invoke("sync")


if __name__ == "__main__":
    main()
