"""Minimal byte samples with real file signatures, for upload tests."""

import io
import zipfile

PDF = b"%PDF-1.4\n1 0 obj<<>>endobj\ntrailer<<>>\n%%EOF\n"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
JPEG = b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + b"\x00" * 64
WINDOWS_EXECUTABLE = b"MZ\x90\x00" + b"\x00" * 64
WHATSAPP_CHAT = "[12/03/2026, 10:31] Ana: El contrato llegó firmado.\n".encode()


def zip_archive() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("nota.txt", "contenido")
    return buffer.getvalue()


def docx_document() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("[Content_Types].xml", "<Types/>")
        archive.writestr("word/document.xml", "<w:document/>")
    return buffer.getvalue()
