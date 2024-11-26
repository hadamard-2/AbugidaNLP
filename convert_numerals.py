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
    split_length = 2
    if len(arabic_num) % 2 == 1:
        arabic_num = "0" + arabic_num

    return [
        arabic_num[i : i + split_length]
        for i in range(len(arabic_num) - split_length, -1, -split_length)
    ][::-1]


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
    split_num = split_arabic_num(arabic_num)

    geez_num = ""
    for i in range(len(split_num)):
        geez_num += arabic_to_geez_chunk(split_num[i], len(split_num) - 1 - i)

    return geez_num


# print(split_arabic_num("13802"))
# print(split_arabic_num("7654321"))

# convert_arabic_to_geez("7654321")
print(convert_arabic_to_geez("7654321"))  # ፯፻ ፷፭፼ ፵፫፻ ፳፩
print(convert_arabic_to_geez("7650021"))  # ፯፻ ፷፭፼ ፳፩
print(convert_arabic_to_geez("7650121"))  # ፯፻ ፷፭፼ ፻ ፳፩
print(convert_arabic_to_geez("20242"))  # ፪፼ ፪፻ ፵፪


def split_geez_num(geez_num):
    # ፯፻ ፷፭፼ ፵፫፻ ፳፩ --> [7, 65, 43, 21] --> 7,000,000 + 650,000 + 4300 + 21
    # ፯፻ ፷፭፼ ፳፩ --> [7, 65, 0, 21] --> 7,000,000 + 650,000 + 0 + 21
    # ፯፻ ፷፭፼ ፻ ፳፩ --> [7, 65, 1, 21] --> 7,000,000 + 650,000 + 100 + 21
    # ፪፼ ፪፻ ፵፪ --> [2, 2, 42] --> 20,000 + 200 + 42
    pass


def convert_geez_to_arabic(geez_num):
    pass
