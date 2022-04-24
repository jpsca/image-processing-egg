import pytest

from image_processing import ImageProcessing
from image_processing.vips_processor import SHARPEN_MASK

from .utils import (
    assert_dimensions,
    assert_similar,
    fixture_image,
    get_size,
)


@pytest.fixture
def pipeline():
    return ImageProcessing(fixture_image("portrait.jpg"))


def test_shrinks_image_to_fit_specified_dimensions(pipeline):
    assert_dimensions(
        [300, 400],
        pipeline.resize_to_fit(400, 400).save()
    )


def test_enlarges_image_if_its_smaller_than_given_dimensions(pipeline):
    assert_dimensions(
        [750, 1000],
        pipeline.resize_to_fit(1000, 1000).save()
    )


def test_doesnt_require_both_dimensions(pipeline):
    assert_dimensions(
        [300, 400],
        pipeline.resize_to_fit(300, None).save()
    )
    assert_dimensions(
        [750, 1000],
        pipeline.resize_to_fit(750, None).save()
    )
    assert_dimensions(
        [300, 400],
        pipeline.resize_to_fit(None, 400).save()
    )
    assert_dimensions(
        [750, 1000],
        pipeline.resize_to_fit(None, 1000).save()
    )


def test_raises_exception_when_neither_dimension_is_specified(pipeline):
    with pytest.raises(ValueError):
        pipeline.resize_to_limit(None, None).save()


def test_produces_correct_image(pipeline):
    assert_similar(
        fixture_image("fit.jpg"),
        pipeline.resize_to_fit(400, 400).save()
    )


def test_accepts_thumbnail_options(pipeline):
    assert_dimensions(
        [400, 400],
        pipeline.resize_to_fit(400, 400, crop="centre").save()
    )


def test_accepts_sharpening_options(pipeline):
    sharpened = pipeline \
        .resize_to_fit(400, 400, sharpen=SHARPEN_MASK).save()
    normal = pipeline \
        .resize_to_fit(400, 400, sharpen=False).save()
    assert get_size(sharpened) > get_size(normal), \
        "Expected sharpened thumbnail to have bigger filesize"


def test_sharpening_uses_integer_precision(pipeline):
    sharpened_img = pipeline.resize_to_limit(400, 400).save(save=False)
    assert "uchar" == sharpened_img.format
