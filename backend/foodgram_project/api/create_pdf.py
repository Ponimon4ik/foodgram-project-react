import io

from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

HEADING_PDF_SHOPPING_CART = 'Список покупок'

def create_pdf_shopping_cart(shopping_cart):
    buffer = io.BytesIO()
    pdfmetrics.registerFont(TTFont('FreeSans', 'static/FreeSans.ttf'))
    p = canvas.Canvas(buffer)
    p.setFont('FreeSans', 8)
    axis_y = 780
    p.drawString(350, 800, HEADING_PDF_SHOPPING_CART)
    for ingredient in shopping_cart:
        (
            name,
            measurement_unit,
            amount
        ) = ingredient.values()
        p.drawString(
            100,
            axis_y,
            f'{name} {amount} {measurement_unit}'
        )
        axis_y -= 15
        if axis_y <= 0:
            axis_y = 800
            p.showPage()
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer