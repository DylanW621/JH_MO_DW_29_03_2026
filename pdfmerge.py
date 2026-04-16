from pypdf import PdfReader, PdfWriter, Transformation
import io
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

main_reader = PdfReader("JH_MO_DW_29_03_2026-plan.pdf")
insert_reader = PdfReader("JH_MO_DW_29_03_2026-ee.pdf")

# load in therion font specifically.
# TODO - Make it auto detect on other user systems
pdfmetrics.registerFont(TTFont('CMUSanSerif', r'C:\Users\Dylan wase 1\AppData\Local\Microsoft\Windows\Fonts\cmunss.ttf'))

writer = PdfWriter()

# first page denoted by 0 index
main_page = main_reader.pages[0]
insert_page = insert_reader.pages[0]

main_page.cropbox = main_page.mediabox
insert_page.cropbox = insert_page.mediabox

main_width = float(main_page.mediabox.width)
main_height = float(main_page.mediabox.height)
insert_width = float(insert_page.mediabox.width)
insert_height = float(insert_page.mediabox.height)

scale = 0.67
margin = 15
border = 2
label_height = 16

scaled_w = insert_width * scale
scaled_h = insert_height * scale

# extend page downwards a bit
extension = scaled_h + label_height + (margin * 2) # top and bottom

new_height = main_height + extension

# Shift the original page content up by the extension amount
main_page.add_transformation(Transformation().translate(0, extension))
main_page.mediabox = main_page.cropbox = main_page.mediabox.__class__(
    (0, 0, main_width, new_height)
)

# Position insert in the new extended area (bottom-right)
x = main_width - scaled_w - margin
y = margin  # sits near the bottom of the extension

# insert
main_page.merge_transformed_page(
    insert_page,
    Transformation().scale(scale).translate(x, y)
)

# Step 2: draw border and label on top
packet = io.BytesIO()
c = canvas.Canvas(packet, pagesize=(main_width, new_height))

label_bar_y = y + scaled_h
c.setFillColorRGB(0, 0, 0)
c.rect(x, label_bar_y, scaled_w, label_height, fill=1, stroke=0)

c.setFillColorRGB(1, 1, 1)
c.setFont("CMUSanSerif", 14)
c.drawCentredString(x + scaled_w / 2, label_bar_y + 4, "Extended Elevation")

c.setStrokeColorRGB(0, 0, 0)
c.setLineWidth(border)
c.rect(x, y, scaled_w, scaled_h + label_height, fill=0, stroke=1)

c.save()
packet.seek(0)

overlay_reader = PdfReader(packet)
main_page.merge_page(overlay_reader.pages[0])

writer.add_page(main_page)

with open("output.pdf", "wb") as f:
    writer.write(f)