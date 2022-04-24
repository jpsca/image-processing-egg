import pytest

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


def test_resizes_and_crops_the_image_to_fill_the_dimensions(pipeline):
    assert_dimensions(
        [400, 400],
        pipeline.resize_to_fill(400, 400).save()
    )


def test_enlarges_image_and_crops_it_if_smaller_than_dimensions(pipeline):
    assert_dimensions(
        [1000, 1000],
        pipeline.resize_to_fill(1000, 1000).save()
    )


def test_produces_correct_image(pipeline):
    assert_similar(
        fixture_image("fill.jpg"),
        pipeline.resize_to_fill(400, 400).save()
    )


def test_accepts_thumbnail_options(pipeline):
    attention = pipeline \
        .resize_to_fill(400, 400, crop="attention").save()
    centre = pipeline \
        .resize_to_fill(400, 400, crop="centre").save()
    assert_different(centre, attention)


def test_accepts_sharpening_options(pipeline):
    sharpened = pipeline \
        .resize_to_fill(400, 400, sharpen=SHARPEN_MASK).save()
    normal = pipeline \
        .resize_to_fill(400, 400, sharpen=False).save()
    assert get_size(sharpened) > get_size(normal), \
        "Expected sharpened thumbnail to have bigger filesize"


def test_sharpening_uses_integer_precision(pipeline):
    sharpened_img = pipeline \
        .resize_to_limit(400, 400).save(save=False)
    assert "uchar" == sharpened_img.format
