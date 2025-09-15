#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Sistema de extração de PDF com alta precisão usando:
- ocrmypdf: Para OCR de alta qualidade
- qpdf: Para remoção de assinaturas digitais
- PyPDF2: Para manipulação de PDFs
"""

import os
import re
import subprocess
import tempfile
import time
import logging
from typing import Dict, Optional
import platform

# Logging
logging.basicConfig(level=logging.INFO, format="%(levelname)s - %(message)s")
logger = logging.getLogger("PDFExtractor")

# Configuração Tesseract
os.environ['TESSDATA_PREFIX'] = r'C:\Program Files\Tesseract-OCR\tessdata'

# Configuração Ghostscript (Windows)
if platform.system() == "Windows":
    gs_path = r"C:\Program Files\gs\gs10.06.0\bin"
    if os.path.exists(gs_path) and gs_path not in os.environ.get('PATH', ''):
        os.environ['PATH'] = gs_path + os.pathsep + os.environ.get('PATH', '')
    os.environ['GS'] = os.path.join(gs_path, "gswin64c.exe")

# Detectar qpdf
QPDF_PATH = "qpdf"
if platform.system() == "Windows":
    for path in [
        r"C:\Program Files\qpdf\bin\qpdf.exe",
        r"C:\Program Files (x86)\qpdf\bin\qpdf.exe",
        os.path.expanduser(r"~\OneDrive\Documentos\qpdf-12.2.0-mingw64\bin\qpdf.exe"),
        r"C:\qpdf\bin\qpdf.exe",
        "qpdf"
    ]:
        if os.path.exists(path):
            QPDF_PATH = path
            break

# Dependências
OCR_AVAILABLE = False
PDF_AVAILABLE = False
QPDF_AVAILABLE = False
TESSERACT_AVAILABLE = False

try:
    import ocrmypdf
    OCR_AVAILABLE = True
    logger.info(f"OCRmyPDF disponível ({ocrmypdf.__version__})")
except Exception as e:
    logger.warning(f"OCRmyPDF indisponível: {e}")

try:
    from PyPDF2 import PdfReader, PdfWriter
    PDF_AVAILABLE = True
except ImportError:
    logger.warning("PyPDF2 não disponível")

try:
    if subprocess.run(['tesseract', '--version'], capture_output=True).returncode == 0:
        TESSERACT_AVAILABLE = True
except Exception:
    pass

try:
    if subprocess.run([QPDF_PATH, '--version'], capture_output=True).returncode == 0:
        QPDF_AVAILABLE = True
except Exception:
    pass


class PDFExtractor:
    """Classe para extrair e limpar texto de matrículas PDF"""

    def __init__(self):
        logger.info("PDFExtractor inicializado")

    # --------------------
    # Dependências
    # --------------------
    def is_ready(self):
        return OCR_AVAILABLE and PDF_AVAILABLE and TESSERACT_AVAILABLE
    
    def is_ocr_available(self):
        """Compatibilidade com app.py"""
        return self.is_ready()
    
    def is_qpdf_available(self):
        """Compatibilidade com app.py"""
        return QPDF_AVAILABLE

    # --------------------
    # Assinatura digital
    # --------------------
    def _is_pdf_signed(self, filepath: str) -> bool:
        """Detecta assinatura digital no PDF"""
        try:
            reader = PdfReader(filepath)
            for page in reader.pages:
                if "/Annots" in page or "/AcroForm" in reader.trailer.get("/Root", {}):
                    return True
        except Exception:
            return False
        return False

    def _remove_signature(self, input_path, output_path) -> bool:
        """Remove assinatura com qpdf"""
        if not QPDF_AVAILABLE:
            return False
        try:
            subprocess.run([QPDF_PATH, "--decrypt", input_path, output_path], check=True)
            return True
        except Exception as e:
            logger.warning(f"Falha no qpdf: {e}")
            return False

    # --------------------
    # OCR
    # --------------------
    def _apply_ocr(self, input_pdf, output_pdf):
        """Executa OCR robusto com fallback para PDFs assinados"""
        if not self.is_ready():
            raise RuntimeError("OCR não disponível")

        try:
            # Primeira tentativa: OCR normal
            ocrmypdf.ocr(
                input_pdf, output_pdf,
                language="por+eng",
                deskew=True,
                force_ocr=True,
                tesseract_config="--psm 6 --oem 3",
                optimize=1,
                image_dpi=300,
                skip_big=50
            )
        except Exception as e:
            error_msg = str(e).lower()
            if "digital signature" in error_msg or "signature" in error_msg:
                logger.warning("PDF assinado detectado, tentando OCR com skip_text")
                try:
                    # Segunda tentativa: OCR com skip_text para PDFs assinados
                    ocrmypdf.ocr(
                        input_pdf, output_pdf,
                        language="por+eng",
                        deskew=True,
                        skip_text=True,  # Pula texto existente para evitar conflitos
                        tesseract_config="--psm 6 --oem 3"
                    )
                except Exception as e2:
                    logger.warning(f"OCR com skip_text falhou, tentando modo básico: {e2}")
                    # Terceira tentativa: OCR mais básico
                    ocrmypdf.ocr(
                        input_pdf, output_pdf,
                        language="por",
                        skip_text=True
                    )
            else:
                logger.warning(f"OCR falhou, tentando modo básico: {e}")
                ocrmypdf.ocr(input_pdf, output_pdf, language="por", force_ocr=True)

    # --------------------
    # Texto
    # --------------------
    def _extract_text(self, pdf_path: str) -> str:
        """Extrai texto do PDF já processado"""
        text = ""
        try:
            with open(pdf_path, "rb") as f:
                reader = PdfReader(f)
                for p in reader.pages:
                    txt = p.extract_text()
                    if txt:
                        text += txt + "\n"
        except Exception as e:
            logger.error(f"Erro lendo PDF processado: {e}")
        return text.strip()

    def _clean_text(self, text: str) -> str:
        """Normaliza texto OCR com regex e correções"""
        if not text:
            return ""

        # Correções comuns
        replacements = {
            r"m[\?\]]": "m²",
            r"\bN[ºo]\b": "nº",
            r"\bR\$ ?": "R$ ",
            r"\s{2,}": " ",
        }
        for pat, repl in replacements.items():
            text = re.sub(pat, repl, text, flags=re.IGNORECASE)

        # Limpa ruídos curtos
        lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 2]
        return "\n".join(lines)

    # --------------------
    # Extração principal
    # --------------------
    def extract_text_from_pdf(self, pdf_file, as_json: bool = False) -> str | Dict:
        """Extrai texto limpo ou JSON estruturado"""
        if not self.is_ready():
            raise RuntimeError("Dependências OCR ausentes")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_in:
            tmp_in.write(pdf_file.read())
            in_path = tmp_in.name
        out_path = in_path + "_ocr.pdf"

        # Processar OCR
        if self._is_pdf_signed(in_path):
            logger.info("PDF assinado detectado, tentando remover assinatura")
            tmp_unsigned = in_path + "_unsigned.pdf"
            if self._remove_signature(in_path, tmp_unsigned):
                logger.info("Assinatura removida com sucesso")
                in_path = tmp_unsigned
            else:
                logger.warning("Falha ao remover assinatura, tentando OCR direto")
        
        self._apply_ocr(in_path, out_path)

        # Extrair texto
        raw = self._extract_text(out_path)
        clean = self._clean_text(raw)

        # Limpar arquivos temporários
        try:
            os.unlink(in_path)
            os.unlink(out_path)
        except Exception:
            pass

        # Retornar texto puro ou JSON simples
        if not as_json:
            return clean
        return self._to_json(clean)

    def _to_json(self, text: str) -> Dict:
        """Extrai campos principais em JSON básico"""
        data = {}
        patterns = {
            "proprietario": r"PROPRIET[ÁA]RIO[AS]?:\s*(.+)",
            "inscricao": r"INSCRIÇÃO IMOBILIÁRIA[: ]+(\S+)",
            "valor": r"R\$ ?([\d\.,]+)",
            "matricula": r"Matrícula nº (\S+)"
        }
        for key, pat in patterns.items():
            m = re.search(pat, text, re.IGNORECASE)
            if m:
                data[key] = m.group(1).strip()
        return data
    
    def get_pdf_info(self, pdf_file) -> Dict:
        """Compatibilidade com app.py - obtém informações básicas do PDF"""
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                tmp.write(pdf_file.read())
                tmp_path = tmp.name
            
            reader = PdfReader(tmp_path)
            metadata = reader.metadata
            
            info = {
                "num_pages": len(reader.pages),
                "title": metadata.get("/Title", "PDF Processado com OCR") if metadata else "PDF Processado com OCR",
                "author": metadata.get("/Author", "N/A") if metadata else "N/A",
                "subject": metadata.get("/Subject", "Matrícula de Imóvel") if metadata else "Matrícula de Imóvel"
            }
            
            os.unlink(tmp_path)
            return info
            
        except Exception as e:
            logger.error(f"Erro ao obter informações do PDF: {e}")
            return {
                "num_pages": 0,
                "title": "Erro ao processar PDF",
                "author": "N/A",
                "subject": "N/A"
            }
