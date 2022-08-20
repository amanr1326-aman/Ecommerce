from io import BytesIO

from django.conf import settings
import uuid

from django.template.loader import get_template
from xhtml2pdf.document import pisaDocument
from xhtml2pdf.parser import pisaParser
from xhtml2pdf.pisa import CreatePDF


def save_pdf(params: dict):
    template = get_template('pdfs/invoice.html')
    html = template.render(params)
    filename = f'{uuid.uuid4()}.pdf'
    response = BytesIO()
    pdf = CreatePDF(BytesIO(html.encode('UTF-8')), response, encoding='URF-8')

    try:
        with open(str(settings.BASE_DIR) + f'/public/static/pdfs/{filename}', 'wb+') as output:
            pdf = CreatePDF(BytesIO(html.encode('UTF-8')), output, encoding='URF-8')
    except Exception as e:
        print(e)
    if pdf.err:
        return '', False

    return filename, True
