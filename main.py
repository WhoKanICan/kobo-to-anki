import ankiconnect
import database
import ereader
import merriam
import sys
import string
import anki

def main():
    # create Anki.sqlite db if it does not exists
    database.is_created(database.ANKI_DB_PATH)

    # open db
    anki_db = database.open(database.ANKI_DB_PATH)
    ereader_db = database.open(ereader.EREADER_DB_PATH)
        
    # create schema to Anki.sqlite db if it does not exists
    database.create_table(anki_db, database.NOTES_TABLE_SCHEMA)
    database.create_table(anki_db, database.WORDS_TABLE_SCHEMA)

    if not ankiconnect.status():
        anki.start()
        
    # get the sqlite db from ereader
    ereader.get_db()

    # create deck and card model if not created
    ankiconnect.setup()

    # database setup
    for word, book, _, date_added in database.query(ereader_db):
        word = word.lower().strip(string.punctuation)
        exist = database.word_exist(anki_db, word)
        if not exist:
            # api call
            data = merriam.get_word(word)
            parsed_data = merriam.parse(data)
            # unpack dict
            word = parsed_data['word']
            stem_set = parsed_data['stem_set']
            # create notes
            template = ankiconnect.create_note(parsed_data)
            note_id = ankiconnect.invoke('addNote', **template)
            # update notes and words table
            database.update_notes(anki_db, word, note_id, book, date_added)
            database.update_words(anki_db, word, stem_set)
    # close db
    database.close(anki_db)
    database.close(ereader_db)
    # sync
    ankiconnect.invoke('sync')

if __name__ == '__main__':
    main()