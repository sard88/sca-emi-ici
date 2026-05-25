from .actas_excel import ExportadorActaExcel
from .libreoffice_utils import convertir_xlsx_a_pdf as convertir_xlsx_a_pdf_generico
from .libreoffice_utils import libreoffice_binary as _libreoffice_binary


class ExportadorActaPDF:
    """Genera PDF convirtiendo el XLSX institucional final con LibreOffice headless."""

    def generar(self, contexto):
        xlsx_bytes = ExportadorActaExcel().generar(contexto)
        return convertir_xlsx_a_pdf(xlsx_bytes)


def convertir_xlsx_a_pdf(xlsx_bytes):
    return convertir_xlsx_a_pdf_generico(xlsx_bytes, prefix="sca_acta_pdf_", stem="acta")
