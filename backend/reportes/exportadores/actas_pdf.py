import os
import shutil
import subprocess
import tempfile
from pathlib import Path

from .actas_excel import ExportadorActaExcel

PDF_TIMEOUT_SECONDS = int(os.environ.get("ACTAS_PDF_TIMEOUT_SECONDS", "60"))


class ExportadorActaPDF:
    """Genera PDF convirtiendo el XLSX institucional final con LibreOffice headless."""

    def generar(self, contexto):
        xlsx_bytes = ExportadorActaExcel().generar(contexto)
        return convertir_xlsx_a_pdf(xlsx_bytes)


def convertir_xlsx_a_pdf(xlsx_bytes):
    binary = _libreoffice_binary()
    with tempfile.TemporaryDirectory(prefix="sca_acta_pdf_") as tmpdir:
        tmp_path = Path(tmpdir)
        xlsx_path = tmp_path / "acta.xlsx"
        xlsx_path.write_bytes(xlsx_bytes)
        env = os.environ.copy()
        env.setdefault("HOME", str(tmp_path))
        cmd = [
            binary,
            "--headless",
            "--nologo",
            "--nofirststartwizard",
            "--convert-to",
            "pdf",
            "--outdir",
            str(tmp_path),
            str(xlsx_path),
        ]
        try:
            completed = subprocess.run(
                cmd,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=PDF_TIMEOUT_SECONDS,
                env=env,
            )
        except subprocess.TimeoutExpired as exc:
            raise RuntimeError("La conversión de acta XLSX a PDF excedió el tiempo permitido.") from exc

        pdf_path = xlsx_path.with_suffix(".pdf")
        if completed.returncode != 0 or not pdf_path.exists():
            stdout = completed.stdout.decode("utf-8", errors="ignore").strip()
            stderr = completed.stderr.decode("utf-8", errors="ignore").strip()
            detail = stderr or stdout or "LibreOffice no generó el PDF."
            raise RuntimeError(f"No fue posible convertir el acta XLSX a PDF: {detail}")
        return pdf_path.read_bytes()


def _libreoffice_binary():
    configured = os.environ.get("LIBREOFFICE_BINARY")
    candidates = [configured] if configured else []
    candidates.extend(["soffice", "libreoffice"])
    for candidate in candidates:
        if candidate and shutil.which(candidate):
            return candidate
    raise RuntimeError(
        "LibreOffice no está disponible para convertir actas XLSX a PDF. "
        "Instala LibreOffice en el contenedor backend o configura LIBREOFFICE_BINARY."
    )
