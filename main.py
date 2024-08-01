# take pdf file from the user and get the margins of each page of the pdf file
# and save the margins in a json file

import PyPDF2
# import json
import simplejson as json
import re
import fitz
import numpy as np


def get_pdf_margins(pdf):
    pdf_margins = {}

    for page_num in range(len(pdf.pages)):
        page = pdf.pages[page_num]
        pdf_margins[page_num] = page.mediabox.left, page.mediabox.bottom, page.mediabox.right, page.mediabox.top

    return pdf_margins


def page_numbers_and_coordinates(pdf):
    page_numbers_and_coordinates = {}
    lat_lon_pattern = re.compile(r'([-+]?\d{1,2}\.\d+),\s*([-+]?\d{1,3}\.\d+)')
    results = []
    for page_num in range(len(pdf.pages)):
        page = pdf.pages[page_num]
        text = page.extract_text()

        matches = lat_lon_pattern.findall(text)
        if matches:
            results.append({
                'page_number': page_num + 1,  # Page numbers are 1-based
                'coordinates': matches
            })

    return results


def blank_pages(pdf):
    blank_pages = []
    for page_num in range(len(pdf.pages)):
        page = pdf.pages[page_num]
        text = page.extract_text()
        if not text:
            blank_pages.append(page_num)

        # also add if the page has only whitespace
        if text.isspace():
            blank_pages.append(page_num)

        # also add if the page has only newline characters
        if text == '\n':
            blank_pages.append(page_num)

    return blank_pages


def get_page_margins(page):
    return page.mediabox.left, page.mediabox.bottom, page.mediabox.right, page.mediabox.top


def is_blank_page(page):
    text = page.extract_text()
    # we have to check for empty string, whitespace and newline characters and also
    # if there's only page number in the page then it's also considered as blank
    return not text or text.isspace() or text == '\n' or text.isdigit()

def is_single_side_page(page):
    return page.mediabox.left == 0 and page.mediabox.bottom == 0

def is_double_side_page(page):
    return page.mediabox.left != 0 and page.mediabox.bottom != 0

def is_page_numbered(page):
    return page.extract_text().isdigit()

def is_landscaped(page):
    return page.mediabox.left > page.mediabox.bottom

def is_portraited(page):
    return page.mediabox.left < page.mediabox.bottom

# def get_page_orientation(page):
#     if page.mediabox.left > page.mediabox.bottom:
#         return 'landscape'
#     return 'portrait'

def get_text_percentage(page):
    text = page.extract_text()
    if not text:
        return 0
    return len(text) / (page.mediabox.right * page.mediabox.top)

def gte_number_of_columns(page):
    pass


def get_page_orientation(pdf_path, page_number):
    document = fitz.open(pdf_path)
    page = document.load_page(page_number)
    rotation = page.rotation

    if rotation == 0:
        orientation = 'Portrait'
    elif rotation == 90:
        orientation = 'Landscape (Clockwise)'
    elif rotation == 180:
        orientation = 'Portrait (Upside Down)'
    elif rotation == 270:
        orientation = 'Landscape (Counter-Clockwise)'
    else:
        orientation = 'Unknown'

    return orientation


def get_text_blocks(page):
    """Extract text blocks from a page."""
    blocks = page.get_text("blocks")
    return blocks

def determine_column_layout(blocks, page_width):
    """Determine if the page layout is single or double column based on text blocks."""
    columns = []

    # Classify each block as left, center, or right
    for block in blocks:
        x0, y0, x1, y1, _, _, _, _ = block
        mid_x = (x0 + x1) / 2

        if mid_x < page_width / 3:
            columns.append("left")
        elif mid_x > 2 * page_width / 3:
            columns.append("right")
        else:
            columns.append("center")

    # Count the number of left, center, and right blocks
    left_count = columns.count("left")
    center_count = columns.count("center")
    right_count = columns.count("right")

    # Heuristic: if there are more left and right blocks than center blocks, it's likely double column
    if left_count > 0 and right_count > 0 and center_count < left_count + right_count:
        return "Double Column"
    else:
        return "Single Column"

def get_page_column_layout(pdf_path, page_number):
    # Open the PDF file
    document = fitz.open(pdf_path)

    # Select the page
    page = document.load_page(page_number)

    # Get the width of the page
    page_width = page.rect.width

    # Extract text blocks
    blocks = get_text_blocks(page)

    # Determine the column layout
    layout = determine_column_layout(blocks, page_width)
    return layout


if __name__ == '__main__':
    pdf_file = input("Enter the pdf file path: ")
    pdf = PyPDF2.PdfReader(pdf_file)
    # pdf_margins = get_pdf_margins(pdf)
    # print(pdf_margins)
    # print('-----------------------------------')
    # print(page_numbers_and_coordinates(pdf))
    # print('-----------------------------------')
    # print(blank_pages(pdf))
    results = []
    for page_num in range(len(pdf.pages)):
        page = pdf.pages[page_num]
        results.append({
            'page_number': page_num + 1,
            'margins': get_page_margins(page),
            'is_blank': is_blank_page(page),
            'is_single_side': is_single_side_page(page),
            'is_double_side': is_double_side_page(page),
            'is_page_numbered': is_page_numbered(page),
            'is_landscaped': is_landscaped(page),
            'is_portraited': is_portraited(page),
            # 'orientation': get_page_orientation(page),
            'orientation': get_page_orientation(pdf_file, page_num),
            # 'text_blocks': get_page_column_layout(pdf_file, page_num),
            'text_percentage': get_text_percentage(page)
        })

    print('-----------------------------------')
    # print('Results:', results)
    print(json.dumps(results, indent=4))
