import pytest
import pyvips
from image_processing import ImageProcessing

from .utils import (
    assert_dimensions,
    assert_similar,
    assert_format,
    fixture_image,
    get_size,
)


portrait = fixture_image("portrait.jpg")


def test_applies_vips_operations(tmp_path):
    actual = ImageProcessing(portrait).invert().save()
    expected = str(tmp_path / "result.jpg")
    image = pyvips.Image.new_from_file(portrait)
    image = image.invert()
    image.write_to_file(expected)
    assert_similar(actual, expected)


def test_applies_macro_operations(tmp_path):
    actual = ImageProcessing(portrait).resize_to_limit(400, 400).save()
    expected = str(tmp_path / "result.jpg")
    image = pyvips.Image.new_from_file(portrait)
    image = image.thumbnail_image(400, height=400, size="down")
    image.write_to_file(expected)
    assert_similar(actual, expected)


def test_allows_changing_metadata():
    image = (
        ImageProcessing(portrait)
        .set("icc-profile-data", b"foobar")
        .set_type(pyvips.GValue.blob_type, "foo", b"bar")
        .set_value("foo", b"meh")
        .remove("exif-data")
        .save(save=False)
    )

    assert b"foobar" == image.get("icc-profile-data")
    assert b"meh" == image.get("foo")
    with pytest.raises(pyvips.Error):
        image.get("exif-data")


def test_applies_format():
    result = ImageProcessing(portrait).convert("png").save()
    assert result.endswith(".png")
    assert_format("PNG", result)


def test_auto_rotates_by_default():
    rotated = fixture_image("rotated.jpg")

    result = ImageProcessing(rotated).save()
    assert_dimensions([600, 800], result)

    result = ImageProcessing(rotated).resize_to_limit(1000, 1000).save()
    assert_dimensions([600, 800], result)

    result = ImageProcessing(rotated).loader(fail=True) \
        .resize_to_limit(1000, 1000).save()
    assert_dimensions([600, 800], result)

    result = ImageProcessing(rotated).loader(autorot=False).save()
    assert_dimensions([800, 600], result)

    result = ImageProcessing(rotated).loader(autorotate=False).save()
    assert_dimensions([800, 600], result)


def test_applies_loader_options():
    result = ImageProcessing(portrait).loader(shrink=2).save()
    assert_dimensions([300, 400], result)


def test_raises_vips_error_on_unknown_image_format(tmp_path):
    empty = str(tmp_path / "meh")
    with pytest.raises(pyvips.Error) as error:
        ImageProcessing(empty).convert("jpg").save()
        assert "not a known file format" in error.message


def test_applies_loader_type():
    with pytest.raises(pyvips.Error) as error:
        ImageProcessing(portrait).loader(loader="tiff").save()
        assert "Not a TIFF" in error.message


def test_applies_saver_options():
    result = ImageProcessing(portrait).saver(strip=True).save()
    image_fields = pyvips.Image.new_from_file(result).get_fields()
    assert "exif-data" not in image_fields


def test_converts_quality_saver_option_to_Q():
    result1 = ImageProcessing(portrait).saver(quality=50).save()
    result2 = ImageProcessing(portrait).saver(quality=100).save()
    assert get_size(result1) < get_size(result2)


def test_ignores_saver_options_that_are_not_defined():
    ImageProcessing(portrait).saver(Q=85).convert("png").save()


def test_invalid_image_raises_error():
    pipeline = (
        ImageProcessing(fixture_image("invalid.jpg"))
        .loader(fail=True)
        .resize_to_fit(400, 400)
    )

    with pytest.raises(pyvips.Error) as error:
        pipeline.save()
        assert "Corrupt JPEG data" in error.message
