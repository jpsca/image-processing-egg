import re
import tempfile
import unicodedata
import uuid
from pathlib import Path
from typing import TYPE_CHECKING

from .vips_processor import VipsProcessor

if TYPE_CHECKING:
    from typing import Callable, Optional, Union


DEFAULT_FORMAT = "jpeg"


class ImageProcessing:
    def __init__(
        self,
        source: "Union[str, Path]" = "",
        *,
        temp_folder: "Union[str, Path, None]" = None,
    ):
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

    def source(self, path: "Union[str, Path]") -> "ImageProcessing":
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

    def save(self, destination: "Union[str, Path, None]" = "", save: bool = True) -> str:
        """
        Run the defined processing and get the result. Allows specifying
        the source file and destination.
        """
        if not self._source:
            raise ValueError("You must define a source path using `.source(path)`")

        destination = Path(destination) if destination else None
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

    # Private

    def _copy(self) -> "ImageProcessing":
        copy = self.__class__(self._source)
        copy._processor = self._processor
        copy._loader = self._loader.copy()
        copy._format = self._format
        copy._saver = self._saver.copy()
        copy._operations = self._operations[:]
        return copy

    def _get_destination_format(self, destination: "Optional[Path]") -> str:
        format = ""
        if destination:
            format = self._get_format(destination)
        format = format or self._format
        format = format or self._get_format(self._source)
        return format or DEFAULT_FORMAT

    def _get_destination(self, destination: "Optional[Path]", format: str) -> str:
        destination = destination or self._get_temp_destination()
        return str(destination.with_suffix(f".{format}"))

    def _get_temp_destination(self) -> Path:
        if not self._temp_folder:
            return Path(tempfile.NamedTemporaryFile(delete=False).name)

        filename = self._slugify(self._source)
        return self._temp_folder / uuid.uuid4().hex / filename

    def _get_format(self, file_path: "Union[str, Path]") -> str:
        return Path(file_path).suffix.lstrip(".")

    def _slugify(self, value):
        """
        Converts to lowercase, removes non-word characters (alphanumerics and
        underscores) and converts internal spaces to hyphens.
        """
        value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
        value = re.sub(r"[^\w\s-]", "", value).strip().lower()
        return re.sub(r"[-\s]+", "-", value)
