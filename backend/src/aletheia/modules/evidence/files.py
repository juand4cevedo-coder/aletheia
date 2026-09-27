import codecs
import hashlib
import re
import unicodedata
from dataclasses import dataclass
from pathlib import PurePosixPath, PureWindowsPath
from typing import BinaryIO

import filetype

from aletheia.modules.evidence.errors import (
    EmptyFileError,
    FileTooLargeError,
    FileTypeMismatchError,
    UnsupportedFileTypeError,
)

CHUNK_SIZE = 1024 * 1024
DETECTION_BYTES = 8192
MAX_FILENAME_LENGTH = 255

# Binary formats: accepted extensions and the media types their content may be detected as.
BINARY_TYPES: dict[str, frozenset[str]] = {
    "pdf": frozenset({"application/pdf"}),
    "jpg": frozenset({"image/jpeg"}),
    "jpeg": frozenset({"image/jpeg"}),
    "png": frozenset({"image/png"}),
    "gif": frozenset({"image/gif"}),
    "webp": frozenset({"image/webp"}),
    "heic": frozenset({"image/heic"}),
    "tif": frozenset({"image/tiff"}),
    "tiff": frozenset({"image/tiff"}),
    "mp3": frozenset({"audio/mpeg"}),
    "m4a": frozenset({"audio/mp4", "video/mp4"}),
    "ogg": frozenset({"audio/ogg"}),
    "opus": frozenset({"audio/ogg"}),
    "wav": frozenset({"audio/x-wav"}),
    "aac": frozenset({"audio/aac"}),
    "amr": frozenset({"audio/amr"}),
    "mp4": frozenset({"video/mp4"}),
    "mov": frozenset({"video/quicktime"}),
    "webm": frozenset({"video/webm"}),
    "3gp": frozenset({"video/3gpp"}),
    "docx": frozenset({"application/vnd.openxmlformats-officedocument.wordprocessingml.document"}),
    "xlsx": frozenset({"application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"}),
    "pptx": frozenset(
        {"application/vnd.openxmlformats-officedocument.presentationml.presentation"}
    ),
}

# Text formats have no magic bytes: their content must be valid UTF-8 without NUL bytes.
TEXT_TYPES: dict[str, str] = {
    "txt": "text/plain",
    "csv": "text/csv",
    "eml": "message/rfc822",
}

_CONTROL_CHARACTERS = re.compile(r"[\x00-\x1f\x7f]")
_WHITESPACE = re.compile(r"\s+")


@dataclass(frozen=True)
class InspectedFile:
    filename: str
    media_type: str
    size_bytes: int
    sha256: str


def normalize_filename(raw: str | None) -> str:
    """Return a display-safe file name: no directories, control characters or odd whitespace."""
    name = unicodedata.normalize("NFC", raw or "")
    name = PureWindowsPath(PurePosixPath(name).name).name
    name = _CONTROL_CHARACTERS.sub("", name)
    name = _WHITESPACE.sub(" ", name).strip().strip(".")
    if not name:
        return "unnamed"
    if len(name) <= MAX_FILENAME_LENGTH:
        return name
    stem, dot, extension = name.rpartition(".")
    if dot and len(extension) < 16:
        return stem[: MAX_FILENAME_LENGTH - len(extension) - 1] + "." + extension
    return name[:MAX_FILENAME_LENGTH]


def inspect_upload(file: BinaryIO, raw_filename: str | None, *, max_bytes: int) -> InspectedFile:
    """Hash, measure and identify an uploaded file, rejecting anything not accepted as evidence.

    The file is read once in chunks, so its size is enforced without loading it into memory.
    Its position is reset to the beginning afterwards.
    """
    filename = normalize_filename(raw_filename)
    extension = filename.rpartition(".")[2].lower() if "." in filename else ""
    if extension not in BINARY_TYPES and extension not in TEXT_TYPES:
        raise UnsupportedFileTypeError()

    digest = hashlib.sha256()
    size = 0
    head = b""
    text_decoder = codecs.getincrementaldecoder("utf-8")() if extension in TEXT_TYPES else None

    file.seek(0)
    while chunk := file.read(CHUNK_SIZE):
        size += len(chunk)
        if size > max_bytes:
            raise FileTooLargeError()
        digest.update(chunk)
        if len(head) < DETECTION_BYTES:
            head += chunk[: DETECTION_BYTES - len(head)]
        if text_decoder is not None:
            _check_text_chunk(text_decoder, chunk)
    file.seek(0)

    if size == 0:
        raise EmptyFileError()

    if text_decoder is not None:
        _check_text_chunk(text_decoder, b"", final=True)
        media_type = TEXT_TYPES[extension]
    else:
        media_type = _detect_binary_type(head, extension)

    return InspectedFile(
        filename=filename, media_type=media_type, size_bytes=size, sha256=digest.hexdigest()
    )


def _detect_binary_type(head: bytes, extension: str) -> str:
    kind = filetype.guess(head)
    if kind is None or kind.mime not in BINARY_TYPES[extension]:
        raise FileTypeMismatchError()
    return kind.mime


def _check_text_chunk(
    decoder: codecs.IncrementalDecoder, chunk: bytes, final: bool = False
) -> None:
    if b"\x00" in chunk:
        raise FileTypeMismatchError()
    try:
        decoder.decode(chunk, final=final)
    except UnicodeDecodeError as error:
        raise FileTypeMismatchError() from error
