import pytest

import pyvips
from image_processing import ImageProcessing
from image_processing.vips_processor import SHARPEN_MASK

from .utils import (
    assert_different,
    assert_dimensions,
    assert_similar,
    fixture_image,
    get_size,
)


@pytest.fixture
def pipeline():
    return ImageProcessing(fixture_image("portrait.jpg"))


def test_resizes_and_fills_out_the_remaining_space(pipeline):
    assert_dimensions(
        [400, 400],
        pipeline.resize_and_pad(400, 400).save()
    )


def test_enlarges_image_and_fills_out_the_remaining_space(pipeline):
    assert_dimensions(
        [1000, 1000],
        pipeline.resize_and_pad(1000, 1000).save()
    )


def test_produces_correct_image_when_shrinking(pipeline):
    result = pipeline.convert("png").resize_and_pad(400, 400, alpha=True).save()
    assert_similar(fixture_image("pad.png"), result)
    assert 4 == pyvips.Image.new_from_file(result).bands

    transparent_png = pipeline.addalpha().convert("png").save()
    result = pipeline.source(transparent_png).resize_and_pad(400, 400, alpha=True).save()
    assert_similar(fixture_image("pad.png"), result)
    assert 4 == pyvips.Image.new_from_file(result).bands


def test_produces_correct_image_when_enlarging():
    result = (
        ImageProcessing(fixture_image("landscape.jpg"))
        .resize_and_pad(1000, 1000, background=[55, 126, 34])
        .save()
    )
    assert_similar(fixture_image("pad-large.jpg"), result)


def test_accepts_gravity(pipeline):
    centre = pipeline \
        .resize_and_pad(400, 400).save()
    northwest = pipeline \
        .resize_and_pad(400, 400, gravity="north-west").save()
    assert_different(centre, northwest)


def test_accepts_thumbnail_options(pipeline):
    pad = pipeline \
        .resize_and_pad(400, 400).save()
    crop = pipeline \
        .resize_and_pad(400, 400, crop="centre").save()
    assert_different(pad, crop)


def test_accepts_sharpening_options(pipeline):
    sharpened = pipeline \
        .resize_and_pad(400, 400, sharpen=SHARPEN_MASK).save()
    normal = pipeline \
        .resize_and_pad(400, 400, sharpen=False).save()
    assert get_size(sharpened) > get_size(normal), \
        "Expected sharpened thumbnail to have bigger filesize"


def test_sharpening_uses_integer_precision(pipeline):
    sharpened_img = pipeline.resize_to_limit(400, 400).save(save=False)
    assert "uchar" == sharpened_img.format
