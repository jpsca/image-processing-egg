import os

import pyvips
from PIL import Image


def fixture_image(name):
    return f"tests/fixtures/{name}"


SIMILAR_TRESHOLD = 4


def assert_similar(filename1, filename2):
    diff = difference(filename1, filename2)
    print("DIFFERENCE:", diff)
    assert SIMILAR_TRESHOLD > diff


def assert_different(filename1, filename2):
    diff = difference(filename1, filename2)
    print("DIFFERENCE:", diff)
    assert SIMILAR_TRESHOLD <= diff


def difference(filename1, filename2):
    f1 = fingerprint(filename1)
    f2 = fingerprint(filename2)
    count = 0
    for a, b in zip(f1, f2):
        if a != b:
            count += 1
    return count


def fingerprint(filename, power=3):
    """
    Difference Hash (computes differences horizontally)
    Follows http://www.hackerfactor.com/blog/index.php?/archives/529-Kind-of-Like-That.html
    """
    size = 2 ** power
    image = pyvips.Image.thumbnail(filename, size, height=size, size="force")
    image = image.flatten().colourspace("b-w")[0]
    pixels = image.tolist()
    diff = []
    for row in pixels:
        diff.extend([a > b for a, b in zip(row[1:], row[:-1])])
    return diff


def assert_format(format, filename):
    with Image.open(filename) as im:
        assert format == im.format


def assert_dimensions(dimensions, filename):
    with pyvips.Image.new_from_file(filename) as im:
        print("DIMENSIONS:", [im.width, im.height], dimensions)
        assert [im.width, im.height] == dimensions


get_size = os.path.getsize
