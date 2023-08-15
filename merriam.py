import os
import string
import requests

API_KEY = os.environ.get("MERRIAM_WEBSTER_KEY")

def get_word(word: str) -> dict[str, list]:
    """query to merriam webster api service with the word in question

    Parameters
    ----------
    word : str
        the word to which information about is to be gained

    Returns
    -------
    dict[str, list]
        key is the word and the value is a list that is the json response

    Raises
    ------
    SystemExit
        If the api key is invalid
    SystemExit
        Other errors to do with the query
    """
    merriam_url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}"
    try:
        response = requests.get(merriam_url, params={"key": API_KEY})        
        if response.text == "Invalid API key. Not subscribed for this reference.":
           raise SystemExit(response.text)
        else:
            word_data = {
                "word" : word,
                "response": response.json()
            }
            return _validate(word_data)
    except requests.exceptions.HTTPError as err:
        raise SystemExit(err)


def _validate(word_data: dict[str, list]) -> dict[str, list]:
    """Checks to see if the word is a stem or head word

    Parameters
    ----------
    word_data : dict[str, list]
        The returned value from the get_word() function

    Returns
    -------
    dict[str, list]
        returns the same structure as the get_word() function. Key value where the key is the word and the value is the response from merriam webster
    """
    word = word_data['word']
    headword = word_data['response'][0]['hwi']['hw'].translate(str.maketrans('', '', string.punctuation))
    if word == headword:
        return word_data
    else:
        return get_word(headword)


def parse(word_data: dict[str, list]) -> dict[str, list, list]:
    """Extracts the relevant information to compose the notes in anki

    Parameters
    ----------
    word_data : dict[str, list]
        the returned dict from the get_word() function

    Returns
    -------
    dict[str, list, list]
        head word, the information needed to compose the notes in anki, list of stem words related to the head word
    """
    word = word_data["word"]
    response = word_data["response"]
    # get all the other data
    stem_set = set()
    word_data = {}
    for idx, entry in enumerate(response):
        stems_list = entry["meta"]["stems"]
        if word in stems_list:
            functional_label = entry.get("fl")
            if functional_label:
                stem_set.update(stems_list)
                short_def = entry.get("shortdef")
                word_data[idx] = {
                    "functional_label": functional_label,
                    "definition": short_def,
                    "audio_url": _audio(entry)
                }
    # package up data to be returned
    parsed_data = {
        "word": word,
        "word_data": word_data,
        "stem_set": stem_set
    }
    return parsed_data


def _audio(entry: list) -> None | str:
    """grabs the audio file link if available 

    Parameters
    ----------
    entry : list
        the list that is parsed from the parse() function

    Returns
    -------
    None | str
        returns audio url if available otherwise returns None if not found
    """
    prs = entry['hwi'].get('prs')
    if prs:
        file_name = prs[0]['sound']['audio']
        # set the correct subdirectory based on audio name
        subdirectory = ""
        if file_name.startswith("bix"):
            subdirectory = "bix"
        elif file_name.startswith("gg"):
            subdirectory = "gg"
        elif file_name.startswith(string.punctuation) or file_name[0].isdigit():
            subdirectory = "number"
        else:
            subdirectory = file_name[0]

        audio_url = f"https://media.merriam-webster.com/audio/prons/en/us/mp3/{subdirectory}/{file_name}.mp3"
        return audio_url
    return None