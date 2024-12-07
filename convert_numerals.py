geez_arabic_map = {
    "፩": 1,
    "፪": 2,
    "፫": 3,
    "፬": 4,
    "፭": 5,
    "፮": 6,
    "፯": 7,
    "፰": 8,
    "፱": 9,
    "፲": 10,
    "፳": 20,
    "፴": 30,
    "፵": 40,
    "፶": 50,
    "፷": 60,
    "፸": 70,
    "፹": 80,
    "፺": 90,
    "፻": 100,
    "፼": 10000,
}

arabic_geez_map = {value: key for key, value in geez_arabic_map.items()}


def split_arabic_num(arabic_num):
    arabic_num = str(arabic_num)
    chunk_length = 2
    if len(arabic_num) % 2 == 1:
        arabic_num = "0" + arabic_num

    return [
        arabic_num[i : i + chunk_length]
        for i in range(0, len(arabic_num), chunk_length)
    ]


def arabic_to_geez_chunk(arabic_chunk, chunk_index):
    if int(arabic_chunk) == 0:
        return ""

    geez_chunk = arabic_geez_map.get(int(arabic_chunk))
    if not geez_chunk:
        geez_chunk = (
            arabic_geez_map[int(arabic_chunk[0]) * 10]
            + arabic_geez_map[int(arabic_chunk[1])]
        )

    if chunk_index % 2 == 1:
        geez_chunk = "፻" if geez_chunk == "፩" else geez_chunk + "፻"
    elif chunk_index != 0:
        geez_chunk = "፼" if geez_chunk == "፩" else geez_chunk + "፼"

    return geez_chunk


def convert_arabic_to_geez(arabic_num):
    arabic_chunks = split_arabic_num(arabic_num)

    geez_num = ""
    for i in range(len(arabic_chunks)):
        geez_num += arabic_to_geez_chunk(arabic_chunks[i], len(arabic_chunks) - 1 - i)

    return geez_num


def geez_to_arabic_chunk(geez_num):
    if len(geez_num) == 0:
        return 1

    arabic_num = geez_arabic_map.get(geez_num)
    if not arabic_num:
        arabic_num = geez_arabic_map[geez_num[0]] + geez_arabic_map[geez_num[1]]
    return arabic_num


def split_geez_num(geez_num):
    arabic_chunks = []
    geez_num_len = len(geez_num)
    slice_end_index = geez_num_len
    for i in range(geez_num_len):
        if geez_num[-i - 1] == "፻":
            arabic_chunks.insert(0, geez_to_arabic_chunk(geez_num[-i:slice_end_index]))
            slice_end_index = -i - 1
            if len(arabic_chunks) % 2 == 0:
                arabic_chunks.insert(0, 0)
        elif geez_num[-i - 1] == "፼":
            arabic_chunks.insert(0, geez_to_arabic_chunk(geez_num[-i:slice_end_index]))
            slice_end_index = -i - 1
            if len(arabic_chunks) % 2 == 1:
                arabic_chunks.insert(0, 0)

    slice_end_index = geez_num.index("፻" if len(arabic_chunks) % 2 == 1 else "፼")
    arabic_chunks.insert(0, geez_to_arabic_chunk(geez_num[0:slice_end_index]))

    return arabic_chunks


def convert_geez_to_arabic(geez_num):
    arabic_chunks = split_geez_num(geez_num)
    arabic_num = 0
    for i in range(len(arabic_chunks)):
        arabic_num += arabic_chunks[-i - 1] * pow(10, i * 2)

    return arabic_num


def convert_numeral(num, from_numeral, to_numeral):
    # 'gz' - ge'ez
    # 'ha' - hindu-arabic
    if [from_numeral, to_numeral] != [
        "gz",
        "ha",
    ] and [from_numeral, to_numeral] != [
        "ha",
        "gz",
    ]:
        raise ValueError("Invalid numeral systems provided")

    if from_numeral == "gz":
        return convert_geez_to_arabic(num)
    if from_numeral == "ha":
        return convert_arabic_to_geez(num)

