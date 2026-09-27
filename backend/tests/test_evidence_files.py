import hashlib
import io

import pytest

from aletheia.core.errors import AppError
from aletheia.modules.evidence.errors import (
    EmptyFileError,
    FileTooLargeError,
    FileTypeMismatchError,
    UnsupportedFileTypeError,
)
from aletheia.modules.evidence.files import inspect_upload, normalize_filename
from tests import samples

MAX_BYTES = 1024 * 1024


# --- file names --------------------------------------------------------------


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("contrato.pdf", "contrato.pdf"),
        ("../../etc/passwd.pdf", "passwd.pdf"),
        ("C:\\Users\\ana\\Desktop\\acta.pdf", "acta.pdf"),
        ("acta\x00\x1f final.pdf", "acta final.pdf"),
        ("  espacios   múltiples .pdf ", "espacios múltiples .pdf"),
        ("", "unnamed"),
        (None, "unnamed"),
    ],
)
def test_filenames_are_normalized(raw: str | None, expected: str) -> None:
    assert normalize_filename(raw) == expected


def test_long_filenames_keep_their_extension() -> None:
    name = normalize_filename("a" * 400 + ".pdf")

    assert len(name) == 255
    assert name.endswith(".pdf")


# --- accepted files ----------------------------------------------------------


@pytest.mark.parametrize(
    ("filename", "content", "media_type"),
    [
        ("contrato.pdf", samples.PDF, "application/pdf"),
        ("foto.PNG", samples.PNG, "image/png"),
        ("captura.jpg", samples.JPEG, "image/jpeg"),
        ("chat.txt", samples.WHATSAPP_CHAT, "text/plain"),
        (
            "demanda.docx",
            samples.docx_document(),
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        ),
    ],
)
def test_accepted_files_are_identified_by_their_content(
    filename: str, content: bytes, media_type: str
) -> None:
    inspected = inspect_upload(io.BytesIO(content), filename, max_bytes=MAX_BYTES)

    assert inspected.media_type == media_type
    assert inspected.size_bytes == len(content)
    assert inspected.sha256 == hashlib.sha256(content).hexdigest()


def test_inspection_rewinds_the_file_for_the_upload() -> None:
    file = io.BytesIO(samples.PDF)

    inspect_upload(file, "contrato.pdf", max_bytes=MAX_BYTES)

    assert file.read() == samples.PDF


# --- rejected files ----------------------------------------------------------


@pytest.mark.parametrize(
    ("filename", "content", "error"),
    [
        ("programa.exe", samples.WINDOWS_EXECUTABLE, UnsupportedFileTypeError),
        ("archivo.zip", samples.zip_archive(), UnsupportedFileTypeError),
        ("sin_extension", samples.PDF, UnsupportedFileTypeError),
        ("factura.pdf", samples.WINDOWS_EXECUTABLE, FileTypeMismatchError),
        ("foto.pdf", samples.JPEG, FileTypeMismatchError),
        ("chat.txt", b"\xff\xfe\x00binary", FileTypeMismatchError),
        ("chat.txt", b"texto con \x00 nulo", FileTypeMismatchError),
        ("vacio.pdf", b"", EmptyFileError),
    ],
)
def test_unacceptable_files_are_rejected(
    filename: str, content: bytes, error: type[AppError]
) -> None:
    with pytest.raises(error):
        inspect_upload(io.BytesIO(content), filename, max_bytes=MAX_BYTES)


def test_files_over_the_size_limit_are_rejected() -> None:
    content = samples.PDF + b"\x00" * 2048

    with pytest.raises(FileTooLargeError):
        inspect_upload(io.BytesIO(content), "grande.pdf", max_bytes=1024)
