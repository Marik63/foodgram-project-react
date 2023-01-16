import os

from django.conf import settings
from django.http import FileResponse
from fpdf import FPDF

font = os.path.join(
    settings.BASE_DIR,
    'calibri.ttf',
)


def generate_pdf(cart):
    pdf = FPDF()
    pdf.add_page()
    pdf.add_font("Calibri", "", font, uni=True)
    pdf.set_font("Calibri", 14)
    line = 1
    for ingredient in cart:
        pdf.cell(12, 12, txt=ingredient, align='L', ln=line)
        line += 1
    pdf.output('report.pdf', 'F')
    return FileResponse(
        open('report.pdf', 'rb'),
        as_attachment=True,
        content_type='application/pdf'
    )
