import json

filename = "SERA_transliteration.json"
with open(filename, "r", encoding="utf-8") as file:
    global latin_ethiopic_map, ethiopic_latin_map
    ethiopic_latin_map = json.load(file)
    latin_ethiopic_map = {value: key for key, value in ethiopic_latin_map.items()}


def transliterate(word, direction):
    """
    direction:
        fwd - Transliteration of words written in Ethiopic script using Latin alphabet.
        bwd - Converts transliterated words back to their original form.
    """

    if direction not in ["fwd", "bwd"]:
        raise ValueError("Invalid direction provided")

    if direction == "fwd":
        if not all(char in ethiopic_latin_map.keys() for char in word):
            raise ValueError(f"Found non-Ethiopic during transliteration")
        return "".join([ethiopic_latin_map[letter] for letter in word])
    elif direction == "bwd":
        ethiopic_word = ""
        i = min(4, len(word))
        while i > 0:
            if fidel := latin_ethiopic_map.get(word[:i]):
                ethiopic_word += fidel
                word = word[i:]
                i = min(4, len(word))
            else:
                i -= 1

        return ethiopic_word
