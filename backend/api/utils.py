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
    pdf_file.addPage()
    pdf_file.addFont("Calibri", "", font, uni=True)
    pdf_file.setFont("Calibri", 14)
    line = 1
    for ingredients in queryset:
        pdf_file.cell(12, 12, txt=ingredients, ln=line)
        line += 1
    pdf_file.output('reports.pdf', 'F')
    return FileResponse(
        open('reports.pdf', 'rb'),
        as_attachment=True,
        content='application/pdf'
    )
