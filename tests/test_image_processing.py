from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import MagicMock

import pytest

from image_processing import ImageProcessing


str_source = "source1.gif"
str_source2 = "source2.gif"
path_source1 = Path(str_source)
path_source2 = Path(str_source2)


def test_accepts_str_source():
    pp = ImageProcessing(str_source)
    assert pp.options["source"] == str_source

    pp = pp.source(str_source2)
    assert pp.options["source"] == str_source2


def test_accepts_path_source():
    pp = ImageProcessing(path_source1)
    assert pp.options["source"] == str_source

    pp = pp.source(path_source2)
    assert pp.options["source"] == str_source2


def test_accepts_empty_source():
    pp = ImageProcessing()
    assert pp.options["source"] == ""

    pp = pp.source(str_source)
    assert pp.options["source"] == str_source


def test_accepts_loader():
    pp = ImageProcessing().loader(lorem="ipsum")
    assert pp.options["loader"] == {"lorem": "ipsum"}


def test_update_loader():
    pp = ImageProcessing().loader(lorem="ipsum", x=3)
    pp = pp.loader(foo="bar")
    assert pp.options["loader"] == {
        "lorem": "ipsum",
        "x": 3,
        "foo": "bar"
    }


def test_accepts_saver():
    pp = ImageProcessing().saver(lorem="ipsum")
    assert pp.options["saver"] == {"lorem": "ipsum"}


def test_update_saver():
    pp = ImageProcessing().saver(lorem="ipsum", x=3)
    pp = pp.saver(foo="bar")
    assert pp.options["saver"] == {
        "lorem": "ipsum",
        "x": 3,
        "foo": "bar"
    }


def test_fail_if_saved_without_source():
    pp = ImageProcessing()
    with pytest.raises(ValueError):
        pp.save()


def test_accepts_convert():
    pp = ImageProcessing().convert("png")
    assert pp.options["format"] == "png"

    pp = pp.convert("jpg")
    assert pp.options["format"] == "jpg"


def test_add_operations():
    pp = (
        ImageProcessing()
        .crop(10, 15, 120, 300)
        .resize_to_fill(120, 300, linear=True)
    )
    assert pp.options["operations"] == [
        ("crop", (10, 15, 120, 300), {}),
        ("resize_to_fill", (120, 300), {"linear": True}),
    ]


def test_operation_cant_start_with_underscore():
    with pytest.raises(AttributeError):
        ImageProcessing()._thumbnail(120, 340)


def test_processor_called():
    pp = ImageProcessing(str_source)
    pp._processor.save = MagicMock()
    pp.save()

    pp._processor.save.assert_called


def test_processor_called_with_destination():
    pp = ImageProcessing(str_source)
    pp._processor.save = MagicMock()
    pp.save("destination.png")

    pp._processor.save.assert_called_with(
        source=str_source,
        loader={},
        operations=[],
        destination="destination.png",
        saver={},
        save=True,
    )


def test_convert_sets_format():
    pp = ImageProcessing(str_source).convert("png")
    pp._processor.save = MagicMock()
    pp.save("destination")

    _, kw = pp._processor.save.call_args
    assert "destination.png" == kw["destination"]


def test_format_is_jpeg_by_default():
    pp = ImageProcessing("source")
    pp._processor.save = MagicMock()
    pp.save("destination")

    _, kw = pp._processor.save.call_args
    assert "destination.jpeg" == kw["destination"]


def test_source_format_before_default():
    pp = ImageProcessing("source.gif")
    pp._processor.save = MagicMock()
    pp.save("destination")

    _, kw = pp._processor.save.call_args
    assert "destination.gif" == kw["destination"]


def test_destination_format_overwrites_convert():
    pp = ImageProcessing(str_source).convert("png")
    pp._processor.save = MagicMock()
    pp.save("destination.jpeg")

    _, kw = pp._processor.save.call_args
    assert "destination.jpeg" == kw["destination"]


def test_save_to_custom_temp_folder():
    with TemporaryDirectory() as temp:
        pp = ImageProcessing(str_source, temp_folder=temp)
        pp._processor.save = MagicMock()
        finalpath = pp.save()
        assert finalpath.startswith(temp)
