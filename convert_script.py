import json

filename = "SERA_transliteration.json"
with open(filename, "r", encoding="utf-8") as file:
    global transcription_table, transliteration_table
    transliteration_table = json.load(file)
    transcription_table = {value: key for key, value in transliteration_table.items()}


def transliterate(word: str) -> str:
    """
    Transliteration of words written in Ethiopic script using Latin alphabet.
    """
    if not all(char in transliteration_table.keys() for char in word):
        raise Exception(f"Found non-Ethiopic during transliteration")
        return
    return "".join([transliteration_table[letter] for letter in word])


def transcribe(word: str) -> str:
    """
    Converts transliterated words back to their original form.
    """
    transcription = ""
    i = min(4, len(word))
    while i > 0:
        if fidel := transcription_table.get(word[:i]):
            transcription += fidel
            word = word[i:]
            i = min(4, len(word))
        else:
            i -= 1

    return transcription
