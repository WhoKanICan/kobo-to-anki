import ankiconnect
import database
import ereader
import merriam
import sys
import string
import anki

def main():
    # create kobo-to-anki db if it does not exist
    if database.exist(database.ANKI_DB_PATH):
        pass
    else:
        database.create_table(database.ANKI_DB_PATH, database.NOTES_TABLE_SCHEMA)
        database.create_table(database.ANKI_DB_PATH, database.WORDS_TABLE_SCHEMA)

    if ankiconnect.status():
        pass
    else:
        anki.start()

    # get the sqlite db from ereader
    ereader.get_db()
    # create deck and card model if not created
    ankiconnect.setup()

    # database setup
    kobo_query = database.query(ereader.EREADER_DB_PATH)
    for entry in kobo_query:
        word = entry[0].lower().strip(string.punctuation)  # Text column
        book = entry[1]  # VolumeId column
        date_added = entry[3]  # DateCreated column
        exist = database.word_exist(database.ANKI_DB_PATH, word)
        if exist:
            pass
        else:
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
            database.update_notes(database.ANKI_DB_PATH, word, note_id, book, date_added)
            database.update_words(database.ANKI_DB_PATH, word, stem_set)
    # sync
    ankiconnect.invoke('sync')
    # close
    anki.close()

if __name__ == '__main__':
    main()