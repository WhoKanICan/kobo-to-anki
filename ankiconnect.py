import json
import os
import requests

ANKICONNECT_URL = "http://localhost:8765"
DECK_NAME = "Kobo_to_anki"
MODEL_NAME = "Word"

create_deck_params = {
    'deck': DECK_NAME
}

create_model_params = {
    "modelName": MODEL_NAME,
    "inOrderFields": ["Front", "Back"],
    "css": ".card {\nfont-family: arial;\nfont-size: 20px;\ntext-align: center;\ncolor: black;\nbackground-color: white; }\n.back {  text-align: left;\n}",
    "isCloze": False,
    "cardTemplates": [
        {
            "Name": "Card 1",
            "Front": "{{Front}}",
            "Back": "{{FrontSide}}  <hr id=answer>  <div class=back> {{Back}} </div>"
        }
    ]
}

add_note_params = {
    "note": {
        "deckName": DECK_NAME,
        "modelName": MODEL_NAME,
        "fields": {
            "Front": "",
            "Back": ""
        },
        "options": {
            "allowDuplicate": False,
            "duplicateScope": "deck",
            "duplicateScopeOptions": {
                "deckName": DECK_NAME,
                "checkChildren": False,
                "checkAllModels": False
            }
        },
        "tags": [
            "word"
        ],
        "audio": [
        ]
    }
}

model_names_params = {
    "action": "modelNames",
    "version": 6
}

def status() -> bool:
    """Attempts to see if anki-connect is installed on the host machine

    Returns
    -------
    bool
        Depending on the status of anki-connect a boolean will be returned
    """
    try:
        requests.get(ANKICONNECT_URL, timeout=3)
        return True
    except requests.exceptions.ConnectionError:
        return False


def invoke(action: str, **params: dict) -> dict:
    """Invokes actions currently supported by anki-connect. More details about the supported actions can be found on the anki-connect project

    Parameters
    ----------
    action : str
        specify the actions you would like to invoke supported by anki-connect

    Returns
    -------
    dict
        key value will depend on action invoked

    Raises
    ------
    Exception
        response has an unexpected number of fields
    Exception
        response is missing required error field
    Exception
        response is missing required result field
    Exception
        error not listed
    """
    payload = {'action': action, 'params': params, 'version': 6}
    requestJson = json.dumps(payload).encode('utf-8')
    response = requests.get(ANKICONNECT_URL, data=requestJson).json()
    if len(response) != 2:
        raise Exception('response has an unexpected number of fields')
    if 'error' not in response:
        raise Exception('response is missing required error field')
    if 'result' not in response:
        raise Exception('response is missing required result field')
    if response['error'] is not None:
        raise Exception(response['error'])
    return response['result']


def create_note(data: dict) -> dict:
    """Creates note template that is used with the addNote action supported by anki-connect

    Parameters
    ----------
    data : dict
        the parsed data when a query was made to merriam webster

    Returns
    -------
    dict
        structured dict to match the sample request format for the addNote action supported by anki-connect
    """
    template = add_note_params
    front = data["word"]
    word_data = data["word_data"]
    stem_set = data["stem_set"]

    back = ""
    audio = []
    for v in word_data.values():
        functional_label = v["functional_label"]
        definition_list = v["definition"]
        audio_url = v['audio_url']
        if audio_url:
            file_name = os.path.basename(audio_url)
            audio.append(
                {
                    "url": audio_url,
                    "filename": file_name,
                    "fields": "Back"
                }
            )
            back += f"<p><strong>{functional_label} [sound:{file_name}]</strong></p>"
        else:
            back += f"<p><strong>{functional_label}</strong></p>"
        for definition in definition_list:
            back += f"<p style='margin-left:5%'>{definition.capitalize()}</p>"

        back += f"<p><strong>stems:&nbsp</strong><em>{', '.join(stem_set)}</em></p>"

    template["note"]["fields"]["Front"] = front
    template["note"]["fields"]["back"] = back
    template["note"]["audio"] = audio

    return template


def setup() -> bool:
    """Ensures that anki has the correct deck and model available. If not, this will be created

    Returns
    -------
    bool
        True value is returned once check has been performed
    """
    deck_names = invoke('deckNames')
    model_names = invoke('modelNames')

    if MODEL_NAME in model_names:
        pass
    else:
        invoke('createModel', **create_model_params)

    if DECK_NAME in deck_names:
        pass
    else:
        invoke('createDeck', **create_deck_params)

    return True
