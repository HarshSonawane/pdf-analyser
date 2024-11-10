import pdfplumber
from reportlab.pdfgen import canvas
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter, PdfMerger, PageObject
from django.core.files.base import ContentFile

INCH_TO_POINTS = 72

TOP_MARGIN = 1 * INCH_TO_POINTS
LEFT_MARGIN = 1.5 * INCH_TO_POINTS
RIGHT_MARGIN = 1 * INCH_TO_POINTS
BOTTOM_MARGIN = 1 * INCH_TO_POINTS


class PlumberAnalyzer:

    def __init__(self, input_path):
        output_path = "output.pdf"
        self.output = PdfWriter()
        pdf_reader = PdfReader(input_path)
        self.results = []

        with pdfplumber.open(input_path) as pdf:
            result_object = {}
            for i, page in enumerate(pdf.pages):
                text_percentage = len(page.extract_text().strip()) / (page.width * page.height) * 100
                text_percentage = round(text_percentage, 4)
                print(f"Page {i + 1}:")
                print("Text Percentage:", text_percentage)

                text = page.extract_text()
                whitespace = page.extract_text().isspace()
                newline = page.extract_text() == '\n'
                only_page_number = page.extract_text().isdigit()

                print("Is completely blank:", not page.extract_text() or whitespace or newline or only_page_number)
                margines_followed = self.is_text_in_boundry(page)
                print("Follows the 1-inch margin rule:", margines_followed)
                if not margines_followed:
                    page_obj = pdf_reader.pages[i]
                    margin_page = self.draw_boundries(page_obj)
                    modified_page = self.overlay_page(page_obj, margin_page)
                    self.output.add_page(modified_page)

                images_inside_margins = self.are_images_inside_boundry(page)
                if not images_inside_margins:
                    page_obj = pdf_reader.pages[i]

                    margin_page = self.draw_boundries(page_obj, color=(1, 0, 0))
                    modified_page = self.overlay_page(page_obj, margin_page)
                    self.output.add_page(modified_page)

                result_object = {
                    "page_number": i + 1,
                    "inside_borders": margines_followed and images_inside_margins,
                    "text_percentage": text_percentage,
                    "is_blank": self.is_page_blank(page),
                }

                self.results.append(result_object)

        # self.output.write(output_path)
        return None

    def get_pdf_bytes(self):
        pdf_bytes = BytesIO()
        self.output.write(pdf_bytes)
        pdf_bytes.seek(0)
        return pdf_bytes

    def is_text_in_boundry(self, page):
        media_box = page.bbox
        left_margin = LEFT_MARGIN
        top_margin = TOP_MARGIN
        right_margin = RIGHT_MARGIN
        bottom_margin = BOTTOM_MARGIN
        page_width = media_box[2] - media_box[0]
        page_height = media_box[3] - media_box[1]
        text = page.extract_words()
        for word in text:
            x0, y0, x1, y1 = word['x0'], word['top'], word['x1'], word['bottom']
            if (
                x0 < left_margin - 2 or
                x1 > (page_width - right_margin + 2) or
                y0 < bottom_margin - 2 or
                y1 > (page_height - top_margin + 2)
            ):
                print(f"Page {page.page_number} has text outside the margins.")
                return False
        else:
            print(f"Page {page.page_number} respects the margins")
            return True

    def are_images_inside_boundry(self, page):
        media_box = page.bbox
        left_margin = LEFT_MARGIN
        top_margin = TOP_MARGIN
        right_margin = RIGHT_MARGIN
        bottom_margin = BOTTOM_MARGIN
        page_width = media_box[2] - media_box[0]
        page_height = media_box[3] - media_box[1]
        images = page.images
        for image in images:
            x0, y0, x1, y1 = image['x0'], image['top'], image['x1'], image['bottom']
            if (
                x0 < left_margin or
                x1 > (page_width - right_margin) or
                y0 < bottom_margin or
                y1 > (page_height - top_margin)
            ):
                print(f"Page {page.page_number} has images outside the margins.")
                return False
        else:
            print(f"Page {page.page_number} respects the margins.")
            return True

    def draw_boundries(self, page_obj, color = (1, 0, 0)):
        left_margin = LEFT_MARGIN
        top_margin = TOP_MARGIN
        right_margin = RIGHT_MARGIN
        bottom_margin = BOTTOM_MARGIN

        packet = BytesIO()
        can = canvas.Canvas(packet, pagesize=(float(page_obj.mediabox[2]), float(page_obj.mediabox[3])))

        can.setStrokeColorRGB(*color)
        page_width = float(page_obj.mediabox[2])
        page_height = float(page_obj.mediabox[3])

        can.rect(left_margin, bottom_margin, page_width - left_margin - right_margin, page_height - bottom_margin - top_margin, stroke=1, fill=0)
        can.save()

        packet.seek(0)
        return PdfReader(packet)

    def overlay_page(self, original_page, overlay_page):
        merged_page = PageObject.create_blank_page(width=original_page.mediabox[2], height=original_page.mediabox[3])
        merged_page.merge_page(original_page)
        merged_page.merge_page(overlay_page.pages[0])  # Overlay the first (and only) page from overlay PDF
        return merged_page

    def is_page_blank(self, page):
        length = len(page.extract_text().strip())
        images = len(page.images)
        tables = len(page.extract_tables())
        only_page_number = page.extract_text().isdigit()
        return (length == 0 or length == 1 or length == 2) and images == 0 and tables == 0 or  only_page_number
