import pytest

from image_processing import ImageProcessing

from .utils import assert_dimensions, fixture_image


@pytest.fixture
def pipeline():
    return ImageProcessing(fixture_image("portrait.jpg"))


def test_rotates_by_muliples_of_90(pipeline):
    assert_dimensions(
        [600, 800],
        pipeline.rotate(0).save()
    )
    assert_dimensions(
        [800, 600],
        pipeline.rotate(90).save()
    )
    assert_dimensions(
        [600, 800],
        pipeline.rotate(180).save()
    )
    assert_dimensions(
        [800, 600],
        pipeline.rotate(270).save()
    )


def test_works_for_angles_outside_of_0_360_degrees(pipeline):
    assert_dimensions(
        [600, 800],
        pipeline.rotate(360).save()
    )
    assert_dimensions(
        [800, 600],
        pipeline.rotate(450).save()
    )
    assert_dimensions(
        [800, 600],
        pipeline.rotate(-90).save()
    )


def test_rotates_by_arbitrary_angle(pipeline):
    assert_dimensions(
        [990, 990],
        pipeline.rotate(45).save()
    )


def test_accepts_background_color(pipeline):
    assert_dimensions(
        [990, 990],
        pipeline.rotate(45, background=[0, 0, 0]).save()
    )
