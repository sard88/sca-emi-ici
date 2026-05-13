import os
import shutil
import subprocess
import tempfile
from pathlib import Path

PDF_TIMEOUT_SECONDS = int(os.environ.get("REPORTES_PDF_TIMEOUT_SECONDS", os.environ.get("ACTAS_PDF_TIMEOUT_SECONDS", "60")))


def convertir_xlsx_a_pdf(xlsx_bytes, *, prefix="sca_pdf_", stem="documento"):
    binary = libreoffice_binary()
    with tempfile.TemporaryDirectory(prefix=prefix) as tmpdir:
        tmp_path = Path(tmpdir)
        xlsx_path = tmp_path / f"{stem}.xlsx"
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
            raise RuntimeError("La conversión XLSX a PDF excedió el tiempo permitido.") from exc

        pdf_path = xlsx_path.with_suffix(".pdf")
        if completed.returncode != 0 or not pdf_path.exists():
            stdout = completed.stdout.decode("utf-8", errors="ignore").strip()
            stderr = completed.stderr.decode("utf-8", errors="ignore").strip()
            detail = stderr or stdout or "LibreOffice no generó el PDF."
            raise RuntimeError(f"No fue posible convertir XLSX a PDF: {detail}")
        return pdf_path.read_bytes()


def libreoffice_binary():
    configured = os.environ.get("LIBREOFFICE_BINARY")
    candidates = [configured] if configured else []
    candidates.extend(["soffice", "libreoffice"])
    for candidate in candidates:
        if candidate and shutil.which(candidate):
            return candidate
    raise RuntimeError(
        "LibreOffice no está disponible para convertir XLSX a PDF. "
        "Instala LibreOffice en el contenedor backend o configura LIBREOFFICE_BINARY."
    )
