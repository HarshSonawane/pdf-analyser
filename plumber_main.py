import pdfplumber
from reportlab.pdfgen import canvas
from io import BytesIO
from PyPDF2 import PdfReader, PdfWriter, PdfMerger, PageObject
import re


INCH_TO_POINTS = 72
LEFT_MARGIN_POINTS = 1.5 * INCH_TO_POINTS
MARGIN = 1.1 * INCH_TO_POINTS


def is_roman_numeral(s):
    pattern = re.compile(r'^M{0,4}(CM|CD|D?C{0,3})(XC|XL|L?X{0,3})(IX|IV|V?I{0,3})$', re.IGNORECASE)
    return bool(pattern.match(s))

def determine_page_number_location(y, height):
    if y < MARGIN:
        return "top"
    elif y > height - MARGIN:
        return "bottom"
    return None

def is_likely_page_number(text, page_index, total_pages, actual_first_page):
    # if page_index == 11:
    #     breakpoint()
    if text.isdigit():
        num = int(text)
        expected_num = page_index - actual_first_page + 1
        return 1 <= num <= total_pages and abs(num - expected_num) <= 2
    elif is_roman_numeral(text):
        return len(text) <= 4
    return False


if __name__ == "__main__":
    output = PdfWriter()
    pdf_reader = PdfReader("data/Test_Doc4_1.pdf")
    actual_first_page = 10 # considers 0th index as first page

    with pdfplumber.open("data/Test_Doc4_1.pdf") as pdf:
        total_pages = len(pdf.pages)
        for i, page in enumerate(pdf.pages):
            # is the page blank?
            text = page.extract_text()
            whitespace = page.extract_text().isspace()
            newline = page.extract_text() == '\n'
            only_page_number = page.extract_text().isdigit()
            is_blank = not text or whitespace or newline or only_page_number
            print(f"Page {i + 1} is blank: {is_blank}")

            # does the page has page number printed on it?
            words = page.extract_words()
            height = page.height
            
            first_word = words[0] if words else None
            last_word = words[-1] if words else None
            
            page_number = None
            page_number_location = None

            for word in [first_word, last_word]:
                if word and is_likely_page_number(word['text'], i + 1, total_pages, actual_first_page):
                    location = determine_page_number_location(word['top'], height)
                    if location:
                        page_number = word['text']
                        page_number_location = location
                        break

            print(f"Page {i + 1}:")
            if page_number:
                print(f"  Page number found: Yes")
                print(f"  Page number: {page_number}")
                print(f"  Page number type: {'digit' if page_number.isdigit() else 'roman'}")
                print(f"  Page number location: {page_number_location}")
            else:
                print(f"  Page number found: No")



            