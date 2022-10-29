import re
from typing import TYPE_CHECKING

import pyvips

if TYPE_CHECKING:
    from pathlib import Path
    from typing import Optional, Union
    from pyvips import Image


CENTRE = pyvips.Interesting.CENTRE
MAX_COORD = 10000000

# Default sharpening mask that provides a fast and mild sharpen.
SHARPEN_MASK = pyvips.Image.new_from_array(
    [[-1, -1, -1], [-1, 32, -1], [-1, -1, -1]], 24
)

ANTI_GRAVITY = {
    "north": "south",
    "south": "north",
    "east": "west",
    "west": "east",
}


def multi_replace(string, substitutions):
    substrings = sorted(substitutions, key=len, reverse=True)
    regex = re.compile("|".join(map(re.escape, substrings)))
    return regex.sub(lambda match: substitutions[match.group(0)], string)


class VipsProcessor:
    def save(
        self,
        *,
        source: str,
        loader: dict,
        operations: "list[tuple[str, tuple, dict]]",
        destination: str,
        saver: dict,
        save: bool = True,
    ) -> str:
        autorot = loader.pop("autorot", loader.pop("autorotate", True))
        image = self._load_image(source, autorot=autorot, **loader)

        for name, args, kw in operations:
            op = getattr(self, name, None)
            if op:
                image = op(image, *args, **kw)
            else:
                image = getattr(image, name)(*args, **kw)

        if not save:
            return image
        return self._save_image(image, destination, **saver)

    def resize_to_limit(
        self,
        image: "Image",
        width: "Optional[int]" = None,
        height: "Optional[int]" = None,
        **options
    ) -> "Image":
        """
        Resizes the image to not be larger than the specified dimensions,
        while retaining the original aspect ratio.

        ```python
        pipeline = ImageProcessing(image) # 600x800
        result = pipeline.resize_to_limit(400, 400).run()
        pyvips.Image.new_from_file(result.path).size #=> [300, 400]
        ```

        It's possible to omit one dimension, in which case the image will be resized
        only by the provided dimension.

        ```python
        pipeline.resize_to_limit(400, None)
        # or
        pipeline.resize_to_limit(None, 400)
        ```

        Any other options are forwarded to `pyvips.Image.thumbnail_image()`:

        ```python
        pipeline.resize_to_limit(400, 400, linear: true)
        ```

        See [vips_thumbnail()](https://www.libvips.org/API/current/libvips-resample.html#vips-thumbnail)
        for more details.
        """
        iwidth, iheight = self._default_dimensions(width, height)
        return self._thumbnail(
            image, iwidth, iheight, size=pyvips.Size.DOWN, **options
        )

    def resize_to_fit(
        self,
        image: "Image",
        width: "Optional[int]" = None,
        height: "Optional[int]" = None,
        **options
    ) -> "Image":
        """
        Resizes the image to fit within the specified dimensions while retaining
        the original aspect ratio. Will downsize the image if it's larger than the
        specified dimensions or upsize if it's smaller.

        ```python
        pipeline = ImageProcessing(image) # 600x800
        result = pipeline.resize_to_fit(400, 400).run()
        pyvips.Image.new_from_file(result.path).size #=> [300, 400]
        ```

        It's possible to omit one dimension, in which case the image will be resized
        only by the provided dimension.

        ```python
        pipeline.resize_to_fit(400, None)
        # or
        pipeline.resize_to_fit(None, 400)
        ```

        Any other options are forwarded to `pyvips.Image.thumbnail_image()`:

        ```python
        pipeline.resize_to_fit(400, 400, linear: true)
        ```

        See [vips_thumbnail()](https://www.libvips.org/API/current/libvips-resample.html#vips-thumbnail)
        for more details.
        """
        iwidth, iheight = self._default_dimensions(width, height)
        return self._thumbnail(image, iwidth, iheight, **options)

    def resize_to_fill(
        self, image: "Image", width: int, height: int, **options
    ) -> "Image":
        """
        Resizes the image to fill the specified dimensions while retaining
        the original aspect ratio. If necessary, will crop the image in the
        larger dimension.

        ```python
        pipeline = ImageProcessing(image) # 600x800
        result = pipeline.resize_to_fill(400, 400).run()
        pyvips.Image.new_from_file(result.path).size #=> [400, 400]
        ```

        Any other options are forwarded to `pyvips.Image.thumbnail_image()`:

        ```python
        pipeline.resize_to_fill(400, 400, crop="attention") # smart crop
        ```

        See [vips_thumbnail()](https://www.libvips.org/API/current/libvips-resample.html#vips-thumbnail)
        for more details.
        """
        options.setdefault("crop", CENTRE)
        return self._thumbnail(image, width, height, **options)

    def resize_and_pad(
        self,
        image: "Image",
        width: int,
        height: int,
        *,
        gravity: str = CENTRE,
        extend: str = pyvips.Extend.BLACK,
        background: "Optional[list[float]]" = None,
        alpha: bool = False,
        **options
    ) -> "Image":
        """
        Resizes the image to fit within the specified dimensions while retaining
        the original aspect ratio. If necessary, will pad the remaining area with
        transparent color if source image has alpha channel, black otherwise.

        ```python
        pipeline = ImageProcessing(image) # 600x800
        result = pipeline.resize_and_pad(400, 400).run()
        pyvips.Image.new_from_file(result.path).size #=> [400, 400]
        ```

        If you're converting from a format that doesn't support transparent
        colors (e.g. JPEG) to a format that does (e.g. PNG), setting `alpha`
        to `True` will add the alpha channel to the image:

        ```python
        pipeline.resize_and_pad(400, 400, alpha=True)
        ```

        The `extend` and `background` options are also accepted and are forwarded
        to pyvips.Image.gravity():

        ```python
        pipeline.resize_and_pad(400, 400, extend="copy")
        ```

        The `gravity` option can be used to specify the direction where the source
        image will be positioned (defaults to "centre").

        ```python
        pipeline.resize_and_pad(400, 400, gravity="north-west")
        ```

        Any other options are forwarded to `pyvips.Image.thumbnail_image()`:

        ```python
        pipeline.resize_to_fill!(400, 400, linear=True)
        ```

        See [vips_thumbnail()](https://www.libvips.org/API/current/libvips-resample.html#vips-thumbnail)
        and [vips_gravity()](https://www.libvips.org/API/current/libvips-conversion.html#vips-gravity)
        for more details.
        """
        image = self._thumbnail(image, width, height, **options)
        if alpha and not image.hasalpha():
            image = image.addalpha()  # type: ignore
        background = background or [0, 0, 0]
        return image.gravity(
            gravity, width, height, extend=extend, background=background  # type: ignore
        )

    def rotate(
        self,
        image: "Image",
        degrees: float,
        *,
        background: "Optional[list[float]]" = None,
        **options
    ) -> "Image":
        """Rotates the image by an arbitrary angle.

        ```python
        ImageProcessing(source).rotate(90)
        ```

        For degrees that are not a multiple of 90, you can also specify a
        background color for the empty triangles in the corners, left over
        from rotating the image.

        ```python
        ImageProcessing(source).rotate(45, background: [0, 0, 0])
        ```

        Any other options are forwarded to `pyvips.Image.similarity()`.
        See [vips_similarity()](http://libvips.github.io/libvips/API/current/libvips-resample.html#vips-similarity)
        for more details.
        """
        background = background or [0, 0, 0]
        return image.similarity(angle=degrees, background=background, **options)  # type: ignore

    def composite(
        self,
        image: "Image",
        overlay: "Union[str, Path, Image, list[Union[str, Path, Image]]]",
        *,
        blend: str = "over",
        gravity: "Optional[str]" = "north-west",
        offset: "Optional[list[float]]" = None,
        **options
    ) -> "Image":
        """
        Blend the specified image or array of images over the current one.
        One use case for this can be applying a watermark.

        ```pyhton
        watermarked = ImageProcessing("source.png").composite("watermark.png").save()

        # OR

        watermarked = ImageProcessing("source.png") \
            .composite(["watermark1.png", "watermark2.png"]) \
            .save()
        ```

        The overlay can be a string, a `Path`, or a `pyvips.Image`.
        The blend mode can be specified via the `blend=` option (defaults to "over").

        ```pyhton
        .composite(overlay, blend="atop")
        ```

        The direction and position of the overlayed image can be controlled via
        the `gravity=` and `offset=` options:

        ```pyhton
        .composite(overlay, gravity="south-east")
        .composite(overlay, gravity="north-west", offset=[55, 55])
        ```

        Any additional options are forwarded to `pyvips.Image.composite()`.

        ```pyhton
        .composite(overlay, premultiplied=True)
        ```

        See [vips_composite()](http://libvips.github.io/libvips/API/current/libvips-conversion.html#vips-composite)
        for more details.
        """
        sources = overlay if isinstance(overlay, list) else [overlay]
        overlays = [self._to_image_with_alpha(source) for source in sources]

        if gravity:
            # apply offset with correct gravity and make remainder transparent
            if offset:
                overlays_ = []
                for ov in overlays:
                    anti_gravity = multi_replace(gravity, ANTI_GRAVITY)
                    ov = ov.gravity(
                        anti_gravity, image.width + offset[0], image.height + offset[-1]  # type: ignore
                    )
                    overlays_.append(ov)
                overlays = overlays_

            # create image-sized transparent background and apply specified gravity
            overlays = [
                ov.gravity(gravity, image.width, image.height) for ov in overlays  # type: ignore
            ]

        # apply the composition
        return image.composite(overlays, blend, **options)  # type: ignore

    def set(self, image: "Image", *args) -> "Image":
        image = image.copy()  # type: ignore
        image.set(*args)
        return image

    def set_type(self, image: "Image", *args) -> "Image":
        image = image.copy()  # type: ignore
        image.set_type(*args)
        return image

    def set_value(self, image: "Image", *args) -> "Image":
        image = image.copy()  # type: ignore
        image.set_value(*args)
        return image

    def remove(self, image: "Image", *args) -> "Image":
        image = image.copy()  # type: ignore
        image.remove(*args)
        return image

    # Private

    def _load_image(self, source: str, autorot: bool = True, **options) -> "Image":
        """
        Loads the image on disk into a pyvips.Image object. Accepts additional
        loader-specific options (e.g. interlacing). Afterwards auto-rotates the
        image to be upright (according to the EXIF data).
        """
        image = pyvips.Image.new_from_file(source, **options)
        if autorot:
            image = image.autorot()  # type: ignore
        return image  # type: ignore

    def _save_image(
        self,
        image: "Image",
        destination: str,
        *,
        quality: "Optional[int]" = None,
        **options
    ) -> str:
        """
        Writes the `pyvips.Image` object to disk. This starts the processing
        pipeline defined in the Image object. Accepts additional
        saver-specific options (e.g. quality).
        """
        if quality:
            options["Q"] = quality
        image.write_to_file(destination, **options)
        return destination

    def _thumbnail(
        self,
        image: "Image",
        width: int,
        height: int,
        sharpen: "Optional[Image]" = SHARPEN_MASK,  # type: ignore
        **options
    ) -> "Image":
        """Resizes the image according to the specified parameters,
        and sharpens the resulting thumbnail.
        """
        # We're already autorotating when loading the image
        if pyvips.at_least_libvips(8, 8):  # pragma: no cover
            options["no_rotate"] = True
        else:  # pragma: no cover
            options["auto_rotate"] = False

        image = image.thumbnail_image(width, height=height, **options)  # type: ignore
        if sharpen:
            image = image.conv(sharpen, precision=pyvips.Precision.INTEGER)  # type: ignore
        return image

    def _default_dimensions(
        self, width: "Optional[int]", height: "Optional[int]"
    ) -> "tuple[int, int]":
        if not (width or height):
            raise ValueError("either width or height must be specified")
        return width or MAX_COORD, height or MAX_COORD

    def _to_image_with_alpha(self, source: "Union[str, Path, Image]") -> "Image":
        if isinstance(source, pyvips.Image):
            image = source
        else:
            image = pyvips.Image.new_from_file(source)
        if not image.hasalpha():  # type: ignore
            image = image.addalpha()  # type: ignore
        return image  # type: ignore
