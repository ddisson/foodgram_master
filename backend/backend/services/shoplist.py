import io
import os
from django.http import FileResponse
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
import logging

logging.basicConfig(level=logging.DEBUG)

# Import constants from constants.py
from backend.constants import (
    FONTS_ROOT,
    HEADER_FONT_SIZE,
    HEADER_TOP_MARGIN,
    HEADER_BOTTOM_MARGIN,
    BODY_FONT_SIZE,
    BODY_LINE_SPACING,
    TEXT_TOP_MARGIN,
    TEXT_BOTTOM_MARGIN,
    TEXT_RIGHT_MARGIN,
    TEXT_LEFT_MARGIN,
    SPACER,
    STREAM_POSITION,
)

def header(doc, title, size, space, ta):
    doc.append(Spacer(SPACER, HEADER_TOP_MARGIN))
    doc.append(Paragraph(title, ParagraphStyle(
        name='Header', fontName='arial', fontSize=size, alignment=ta
    )))
    doc.append(Spacer(SPACER, space))
    return doc

def body(doc, text, size):
    for line in text:
        doc.append(Paragraph(line, ParagraphStyle(
            name='Body', fontName='arial', fontSize=size, alignment=TA_LEFT
        )))
        doc.append(Spacer(SPACER, BODY_LINE_SPACING))
    return doc

def download_pdf(data):
    try:
        buffer = io.BytesIO()
        font_path = os.path.join(FONTS_ROOT, 'arial.ttf')
        pdfmetrics.registerFont(TTFont('arial', font_path))
        doc = header([], 'Список покупок', HEADER_FONT_SIZE, HEADER_BOTTOM_MARGIN, TA_CENTER)
        pdf = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            topMargin=TEXT_TOP_MARGIN,
            bottomMargin=TEXT_BOTTOM_MARGIN,
            rightMargin=TEXT_RIGHT_MARGIN,
            leftMargin=TEXT_LEFT_MARGIN,
        )
        pdf.build(body(doc, data, BODY_FONT_SIZE))
        buffer.seek(STREAM_POSITION)
        return FileResponse(buffer, as_attachment=True, filename='shopping_list.pdf')
    except Exception as e:
        logging.exception("An error occurred while generating PDF")
        raise e

