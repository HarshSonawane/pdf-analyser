import pdfplumber
from reportlab.pdfgen import canvas
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter, PdfMerger, PageObject

def main():
    with pdfplumber.open("data/paper3.pdf") as pdf:
        print(pdf.metadata)
        for page in pdf.pages:
            # does page has page number
            print(page.page_number)
            # is page nuber in the footer
            breakpoint()
            # margins converted to inches
            print(page.cropbox)
            print("Margin left: ", page.cropbox[0]/72)
            print("Margin top: ", page.cropbox[1]/72)
            print("Margin right: ", page.cropbox[2]/72)
            print("Margin bottom: ", page.cropbox[3]/72)

            # text in the page
            print(page.extract_text())

INCH_TO_POINTS = 72
# left margin is 1.5 inches
LEFT_MARGIN_POINTS = 1.5 * INCH_TO_POINTS

TOP_MARGIN = 1 * INCH_TO_POINTS
LEFT_MARGIN = 1.5 * INCH_TO_POINTS
RIGHT_MARGIN = 1 * INCH_TO_POINTS
BOTTOM_MARGIN = 1 * INCH_TO_POINTS


def has_content_inside_margins(page):
    media_box = page.bbox  # (x0, y0, x1, y1)

    # Define expected margin from all sides (1 inch = 72 points)
    margin = INCH_TO_POINTS
    left_margin = LEFT_MARGIN_POINTS


    # Get page dimensions
    page_width = media_box[2] - media_box[0]
    page_height = media_box[3] - media_box[1]

    # Extract the bounding boxes of all the content on the page
    content = page.extract_words()
    for word in content:
        x0, y0, x1, y1 = word['x0'], word['top'], word['x1'], word['bottom']

        # Check if the content is outside the 1-inch margin from all sides
        if (
            x0 < left_margin or  # Left margin
            x1 > (page_width - margin) or  # Right margin
            y0 < margin or  # Top margin
            y1 > (page_height - margin)  # Bottom margin
        ):
            print(f"Page {page.page_number} has content outside the 1-inch margin.")
            return False
    else:
        print(f"Page {page.page_number} respects the 1-inch margin.")
        return True


def has_text_inside_margins_with_all_margins(page):
    media_box = page.bbox  # (x0, y0, x1, y1)

    left_margin = LEFT_MARGIN
    top_margin = TOP_MARGIN
    right_margin = RIGHT_MARGIN
    bottom_margin = BOTTOM_MARGIN

    # Get page dimensions
    page_width = media_box[2] - media_box[0]
    page_height = media_box[3] - media_box[1]

    # Extract the bounding boxes of all the text on the page
    text = page.extract_words()
    for word in text:
        x0, y0, x1, y1 = word['x0'], word['top'], word['x1'], word['bottom']

        # Check if the text is outside the margins
        if (
            x0 < left_margin or  # Left margin
            x1 > (page_width - right_margin) or  # Right margin
            y0 < bottom_margin or  # Bottom margin
            y1 > (page_height - top_margin)  # Top margin
        ):
            print(f"Page {page.page_number} has text outside the margins.")
            return False

    else:
        print(f"Page {page.page_number} respects the margins
        return True


def has_images_inside_margins(page):

    media_box = page.bbox  # (x0, y0, x1, y1)

    # Define expected margin from all sides (1 inch = 72 points)
    margin = INCH_TO_POINTS
    left_margin = LEFT_MARGIN_POINTS

    # Get page dimensions
    page_width = media_box[2] - media_box[0]
    page_height = media_box[3] - media_box[1]

    # Extract the bounding boxes of all the images on the page
    images = page.images
    for image in images:
        x0, y0, x1, y1 = image['x0'], image['top'], image['x1'], image['bottom']

        # Check if the image is outside the 1-inch margin from all sides
        if (
            x0 < left_margin or  # Left margin
            x1 > (page_width - margin) or  # Right margin
            y0 < margin or  # Top margin
            y1 > (page_height - margin)  # Bottom margin
        ):
            print(f"Page {page.page_number} has images outside the 1-inch margin.")
            return False
    else:
        print(f"Page {page.page_number} respects the 1-inch margin.")
        return True


def has_images_inside_margins_with_all_margins(page):

    media_box = page.bbox  # (x0, y0, x1, y1)

    left_margin = LEFT_MARGIN
    top_margin = TOP_MARGIN
    right_margin = RIGHT_MARGIN
    bottom_margin = BOTTOM_MARGIN

    # Get page dimensions
    # Extract the bounding boxes of all the images on the page
    images = page.images
    for image in images:
        x0, y0, x1, y1 = image['x0'], image['top'], image['x1'], image['bottom']

        # Check if the image is outside the margins
        if (
            x0 < left_margin or  # Left margin
            x1 > (page_width - right_margin) or  # Right margin
            y0 < bottom_margin or  # Bottom margin
            y1 > (page_height - top_margin)  # Top margin
        ):
            print(f"Page {page.page_number} has images outside the margins.")
            return False

    else:
        print(f"Page {page.page_number} respects the margins.")
        return True


def draw_margins_on_page(page_obj, left_margin, margin_size, color = (1, 0, 0)):
    """Draw margin lines on a new overlay page."""
    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(float(page_obj.mediabox[2]), float(page_obj.mediabox[3])))

    can.setStrokeColorRGB(*color)

    page_width = float(page_obj.mediabox[2])
    page_height = float(page_obj.mediabox[3])

    # Draw a rectangle to represent the margins
    can.rect(left_margin, margin_size, page_width - 2 * margin_size, page_height - 2 * margin_size, stroke=1, fill=0)
    can.save()

    packet.seek(0)
    return PdfReader(packet)


def draw_margins_on_page_with_all_margins(page_obj, color = (1, 0, 0)):
    left_margin = LEFT_MARGIN
    top_margin = TOP_MARGIN
    right_margin = RIGHT_MARGIN
    bottom_margin = BOTTOM_MARGIN

    packet = BytesIO()
    can = canvas.Canvas(packet, pagesize=(float(page_obj.mediabox[2]), float(page_obj.mediabox[3])))

    can.setStrokeColorRGB(*color)

    page_width = float(page_obj.mediabox[2])
    page_height = float(page_obj.mediabox[3])

    # Draw a rectangle to represent the margins
    can.rect(left_margin, bottom_margin, page_width - left_margin - right_margin, page_height - bottom_margin - top_margin, stroke=1, fill=0)
    can.save()

    packet.seek(0)
    return PdfReader(packet)


def overlay_page(original_page, overlay_page):
    """Overlay the content of one page onto another."""
    # Create a new PageObject by merging the two pages
    merged_page = PageObject.create_blank_page(width=original_page.mediabox[2], height=original_page.mediabox[3])
    merged_page.merge_page(original_page)
    merged_page.merge_page(overlay_page.pages[0])  # Overlay the first (and only) page from overlay PDF
    return merged_page


if __name__ == "__main__":

    output = PdfWriter()
    pdf_reader = PdfReader("data/Test_Doc4_1.pdf")

    # with pdfplumber.open("data/paper3.pdf") as pdf:
    #     for i, page in enumerate(pdf.pages):
    #         text = page.extract_text()
    #         # Extract specific areas for header and footer
    #         header_text = page.within_bbox((0, 0, page.width, 100)).extract_text()  # Top 100 pixels
    #         footer_text = page.within_bbox((0, page.height - 100, page.width, page.height)).extract_text()  # Bottom 100 pixels

            # print(f"Page {i + 1}:")
            # print("Header:", header_text)
            # print("Footer:", footer_text)

    ## to check if page has margins from all the sides or not
    ## margins should be 1 inch from all the sides
    ## if not then we can consider it as a single side page
    ## if the page has only one side margin then we can consider it as a single side page
    ## if the page has no margin then we can consider it as a single side page

    with pdfplumber.open("data/Test_Doc4_1.pdf") as pdf:
        for i, page in enumerate(pdf.pages):
            text_percentage = len(page.extract_text().strip()) / (page.width * page.height) * 100
            text_percentage = round(text_percentage, 4)
            print(f"Page {i + 1}:")
            # print("Cropbox:", page.cropbox)
            # print("MediaBox:", page.mediabox)
            # print("TrimBox:", page.trimbox)
            # print("BleedBox:", page.bleedbox)
            # print("ArtBox:", page.artbox)
            # print("Has margins:", all(page.cropbox))
            # print("Is single side:", not any(page.cropbox))
            # print("Is blank:",
            #     not page.extract_text().strip() or
            #     not page.extract_text().isdigit()
            # )

            print("Text Percentage:", text_percentage)
            # we need to find if the page is completely blank or not
            # we have to also conside the page number in the page
            # if the page has only page number then it's also considered as blank
            # if the page has only whitespace then it's also considered as blank
            # if the page has only newline characters then it's also considered as blank
            # if i == 14:
            #     breakpoint()

            text = page.extract_text()
            whitespace = page.extract_text().isspace()
            newline = page.extract_text() == '\n'
            only_page_number = page.extract_text().isdigit()

            # text = page.extract_text()
            # whitespace = page.extract_text().isspace()
            # newline = page.extract_text() == '\n'
            # only_page_number = page.extract_text().isdigit()
            # is_blank = not text or whitespace or newline or only_page_number
            # print(f"Page {i + 1} is blank: {is_blank}")

            print("Is completely blank:", not page.extract_text() or whitespace or newline or only_page_number)
            margines_followed = has_content_inside_margins(page)
            print("Follows the 1-inch margin rule:", margines_followed)
            ## draw the lines on the page where the margins are not followed
            if not margines_followed:
                print("Drawing lines on the page where the margins are not followed.")
                # Draw lines on the page where the margins are not followed
                page_obj = pdf_reader.pages[i]
                # page_obj.media_box = page_obj.cropbox
                # page_obj.bleed_box = page_obj.cropbox
                # draw red lines rectangle representing the 1-inch margin
                # left
                # output.add_page(page_obj)
                # output.pages[i].draw_rect(0, 0, INCH_TO_POINTS, page_obj.media_box[3], fill=None, stroke=(1, 0, 0))
                # output.pages[i].draw_rect(0, page_obj.media_box[3] - INCH_TO_POINTS, page_obj.media_box[2], page_obj.media_box[3], fill=None, stroke=(1, 0, 0))
                # output.pages[i].draw_rect(page_obj.media_box[2] - INCH_TO_POINTS, 0, page_obj.media_box[2], page_obj.media_box[3], fill=None, stroke=(1, 0, 0))
                # output.pages[i].draw_rect(0, 0, page_obj.media_box[2], INCH_TO_POINTS, fill=None, stroke=(1, 0, 0))

                margin_page = draw_margins_on_page(page_obj, LEFT_MARGIN_POINTS, INCH_TO_POINTS)
                modified_page = overlay_page(page_obj, margin_page)
                output.add_page(modified_page)


            images_inside_margins = has_images_inside_margins(page)
            print("Images inside margins:", images_inside_margins)
            if not images_inside_margins:
                print("Drawing lines on the page where the images are not inside the margins.")
                page_obj = pdf_reader.pages[i]

                margin_page = draw_margins_on_page(page_obj, LEFT_MARGIN_POINTS, INCH_TO_POINTS, color=(0, 1, 0))
                modified_page = overlay_page(page_obj, margin_page)
                output.add_page(modified_page)



    output.write("data/Test_Doc4_1_output.pdf")
    print("Output PDF generated successfully.")
