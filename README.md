# ImageProcessing 🥚

[![Tests status](https://github.com/jpsca/image-processing-egg/actions/workflows/tests.yml/badge.svg)](https://github.com/jpsca/image-processing-egg/actions/workflows/tests.yml)

Provides higher-level image processing helpers that are commonly needed when handling image uploads.

This package process images with the [libvips] library.
Libvips is a library that can process images [very rapidly][libvips performance] (often multiple times faster than ImageMagick).


## Requirements

You need to install first the `libvips` library.

- In a MacOS terminal ([using Homebrew](https://brew.sh/)) run: `brew install vips`
- In a Debian/Ubuntu terminal run: `sudo apt install libvips-tools`

## Installation

Install this library with pip, or add it to your requirements/dependencies:

```sh
pip install image-processing-egg
```


## Usage

Processing is performed through the **`ImageProcessing`** class that
uses a chainable API for defining the processing pipeline:

```python
from image_processing import ImageProcessing

processed = (
  ImageProcessing(source_path)
  .resize_to_limit(400, 400)
  .convert("png")
  .save()
)

processed #=> /temp/.../20180316-18446-1j247h6.png>
```

This allows easy branching when generating multiple derivates:

```python
from image_processing import ImageProcessing

pipeline = ImageProcessing(source_path).convert("png")

large  = pipeline.resize_to_limit(800, 800).save()
medium = pipeline.resize_to_limit(500, 500).save()
small  = pipeline.resize_to_limit(300, 300).save()
```

The processing is executed with `save()`.

```python
processed = ImageProcessing(source_path) \
  .convert("png") \
  .resize_to_limit(400, 400) \
  .save()

```

You can inspect the pipeline options at any point before executing it:

```python
pipeline = ImageProcessing(source_path) \
  .loader(page=1) \
  .convert("png") \
  .resize_to_limit(400, 400) \
  .strip()

pipeline.options
# => {
#  'source': '/path/to/source.jpg',
#  'loader': {'page': 1},
#  'saver': {},
#  'format': 'png',
#  'operations': [
#    ['resize_to_limit', [400, 400], {}],
#    ['strip', [], {}],
#   ]
# }
```

The source object needs to be a string or a `Path`.
Note that the processed file is always saved to a new location,
in-place processing is not supported.

```python
ImageProcessing("source.jpg")
ImageProcessing(Path("source.jpg"))
```

You can define the source at any time using `source()`

```python
ImageProcessing().source("source.jpg")
ImageProcessing().source(Path("source.jpg"))
```

When `save()` is called without options, the result of processing is a temp file. You can save the processing result to a specific location by passing a `destination`, as a string or a Path, to `save()`.

```python
pipeline = ImageProcessing(source_path)

pipeline.save()  #=> tempfile
pipeline.save("/path/to/destination")
```


## Credits

This library is a port to Python of the Ruby [image_processing gem][gem].


## License

[MIT](MIT-LICENSE)

[libvips]: http://libvips.github.io/libvips/
[libvips performance]: https://github.com/libvips/libvips/wiki/Speed-and-memory-use
[gem]: https://github.com/janko/image_processing
