import tempfile
from hashlib import md5
from pathlib import Path
from typing import TYPE_CHECKING

from .vips_processor import VipsProcessor

if TYPE_CHECKING:
    from typing import Callable, Union

    TStrOrPath = Union[str, Path]


DEFAULT_FORMAT = "jpeg"


class ImageProcessing:
    def __init__(self, source: "TStrOrPath" = "", *, temp_folder: "TStrOrPath" = ""):
        self._processor = VipsProcessor()
        self._source: str = str(source)
        self._loader: dict = {}
        self._format: str = ""
        self._saver: dict = {}
        self._operations: "list[tuple[str, tuple, dict]]" = []
        self._temp_folder = Path(temp_folder) if temp_folder else None

    @property
    def options(self) -> dict:
        return {
            "source": self._source,
            "format": self._format,
            "loader": self._loader,
            "saver": self._saver,
            "operations": self._operations,
        }

    def __getattr__(self, __name: str) -> "Callable":
        if __name.startswith("_"):
            raise AttributeError(__name)

        def operation(*args, **kw) -> "ImageProcessing":
            copy = self._copy()
            copy._operations.append((__name, args, kw))
            return copy

        return operation

    def source(self, path: "TStrOrPath") -> "ImageProcessing":
        """ """
        copy = self._copy()
        copy._source = str(path)
        return copy

    def loader(self, **kw) -> "ImageProcessing":
        """ """
        copy = self._copy()
        copy._loader.update(kw)
        return copy

    def saver(self, **kw) -> "ImageProcessing":
        """ """
        copy = self._copy()
        copy._saver.update(kw)
        return copy

    def convert(self, format: str) -> "ImageProcessing":
        """
        Specifies the output format.

        ```python
        pipeline = ImageProcessing(image)
        result = pipeline.convert("png").run()
        result.suffix  #=> ".png"
        ```

        By default the original format is retained when writing the image to a file.
        If the source file doesn't have a file extension, the format will default to JPEG.
        """
        copy = self._copy()
        copy._format = format
        return copy

    def save(self, destination: "TStrOrPath" = "", save: bool = True) -> str:
        """
        Run the defined processing and get the result. Allows specifying
        the source file and destination.
        """
        if not self._source:
            raise ValueError("You must define a source path using `.source(path)`")

        destination = Path(destination) if destination else ""
        format = self._get_destination_format(destination)
        final_destination = self._get_destination(destination, format)

        return self._processor.save(
            source=self._source,
            loader=self._loader,
            operations=self._operations,
            destination=final_destination,
            saver=self._saver,
            save=save,
        )

    def get_temp_filename(self, destination: "TStrOrPath" = "") -> str:
        """Return a filename that, for the same source path, options,
        operations (in the same order), etc., will be the same.
        """
        ops = str(self.options).encode("utf8", errors="ignore")
        hash = md5(ops).hexdigest()
        format = self._get_destination_format(destination)
        return f"{hash}.{format}"

    # Private

    def _copy(self) -> "ImageProcessing":
        copy = self.__class__(self._source)
        copy._processor = self._processor
        copy._loader = self._loader.copy()
        copy._format = self._format
        copy._saver = self._saver.copy()
        copy._operations = self._operations[:]
        return copy

    def _get_destination_format(self, destination: "TStrOrPath") -> str:
        format = ""
        if destination:
            format = self._get_format(destination)
        return (
            format
            or self._format
            or self._get_format(self._source)
            or DEFAULT_FORMAT
        )

    def _get_destination(self, destination: "TStrOrPath", format: str) -> str:
        if destination:
            destination = Path(destination)
        else:
            destination = self._get_temp_destination()
        return str(destination.with_suffix(f".{format}"))

    def _get_temp_destination(self) -> "Path":
        filename = self.get_temp_filename()
        if not self._temp_folder:
            self._temp_folder = Path(tempfile.mkdtemp())
        return self._temp_folder / filename

    def _get_format(self, file_path: "TStrOrPath") -> str:
        return Path(file_path).suffix.lstrip(".")
