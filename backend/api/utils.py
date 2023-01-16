import os

from django.conf import settings
from django.http import FileResponse
from fpdf import FPDF

font = os.path.join(
    settings.BASE_DIR,
    'calibri.ttf',
)


def generate_pdf(queryset):
    pdf_file = FPDF()
    pdf_file.add_page()
    pdf_file.add_font("Calibri", "", font, uni=True)
    pdf_file.set_font("Calibri", 14)
    line = 1
    for ingredients in queryset:
        pdf_file.cell(12, 12, txt=ingredients, align='L', ln=line)
        line += 1
    pdf_file.output('reports.pdf', 'F')
    return FileResponse(
        open('reports.pdf', 'rb'),
        as_attachment=True,
        content_type='application/pdf'
    )
