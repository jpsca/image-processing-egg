from pathlib import Path

import pytest
import pyvips
from image_processing import ImageProcessing

from .utils import (
    assert_different,
    assert_dimensions,
    assert_similar,
    fixture_image,
)


composited = fixture_image("composited.jpg")
landscape = fixture_image("landscape.jpg")


@pytest.fixture
def pipeline():
    return ImageProcessing(fixture_image("portrait.jpg"))


def test_accepts_string_or_path_objects(pipeline):
    assert_similar(
        composited,
        pipeline.composite(landscape).save()
    )
    assert_similar(
        composited,
        pipeline.composite(Path(landscape)).save()
    )
    pyvips_image = pyvips.Image.new_from_file(landscape)
    assert_similar(
        composited,
        pipeline.composite(pyvips_image).save()
    )


def test_accepts_mode(pipeline):
    assert_different(
        composited,
        pipeline.composite(landscape, blend="clear").save()
    )


def test_accepts_gravity(pipeline):
    result = pipeline.composite(landscape, gravity="centre").save()
    assert_different(composited, result)
    assert_dimensions([600, 800], result)
    with pytest.raises(pyvips.Error):
        pipeline.composite(landscape, gravity="foo").save()


def test_no_gravity(pipeline):
    assert_similar(
        composited,
        pipeline.composite(landscape, gravity=None).save()
    )


def test_accepts_offset(pipeline):
    result = pipeline.composite(landscape, offset=[50, -50]).save()
    assert_different(composited, result)
    assert_dimensions([600, 800], result)


def test_accepts_additional_options(pipeline):
    pipeline.composite(landscape, compositing_space="grey16").save()
    with pytest.raises(pyvips.Error):
        pipeline.composite(landscape, compositing_space="foo").save()


def test_accepts_overlay_list(pipeline):
    original = pipeline.composite(landscape, blend="over").save()

    assert_similar(
        original,
        pipeline.composite([landscape], blend="over").save()
    )
    assert_similar(
        original,
        pipeline.composite([Path(landscape)], blend="over").save()
    )


def test_overlay_with_alpha():
    assert_similar(
        fixture_image("composited-alpha.jpg"),
        ImageProcessing(landscape)
        .composite(fixture_image("alpha.png"))
        .save()
    )
