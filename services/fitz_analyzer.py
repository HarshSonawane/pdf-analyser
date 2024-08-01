import fitz
import re

from core.models import PageResult

class FitsAnalyzer:
    def __init__(self, pdf_path, review_request):
        self.pdf = fitz.open(pdf_path)
        self.analysis = {}
        self.analyse()
        self.save_results(review_request)

    def save_results(self, review_request):
        for page_num, details in self.analysis.items():
            PageResult.objects.create(
                review_request=review_request,
                page_number=page_num,
                service='fitz',
                details=details
            )

    def analyse(self):
        for page_num in range(len(self.pdf.pages)):
            page = self.pdf.pages[page_num]
            self.analysis[page_num] = {
                'margins': self.get_page_margins(page),
                'is_blank': self.is_blank_page(page),
                'is_single_side': self.is_single_side_page(page),
                'is_double_side': self.is_double_side_page(page),
                'side': 'single' if self.is_single_side_page(page) else 'double',
                'is_page_numbered': self.is_page_numbered(page),
                'page_number_coordinates': self.page_numbers_and_coordinates(page),
                'is_landscaped': self.is_landscaped(page),
                'is_portraited': self.is_portraited(page),
                'orientation': 'landscape' if self.is_landscaped(page) else 'portrait',
                'text_percentage': self.get_text_percentage(page)
            }

    def get_page_margins(self, page):
        return page.mediabox.left, page.mediabox.bottom, page.mediabox.right, page.mediabox.top

    def is_blank_page(self, page):
        text = page.extract_text()
        return not text or text.isspace() or text == '\n' or text.isdigit()

    def is_single_side_page(self, page):
        return page.mediabox.left == 0 and page.mediabox.bottom == 0

    def is_double_side_page(self, page):
        return page.mediabox.left != 0 and page.mediabox.bottom != 0

    def is_page_numbered(self, page):
        text = page.extract_text()
        lat_lon_pattern = re.compile(r'([-+]?\d{1,2}\.\d+),\s*([-+]?\d{1,3}\.\d+)')
        matches = lat_lon_pattern.findall(text)
        return bool(matches)

    def page_numbers_and_coordinates(self, page):
        lat_lon_pattern = re.compile(r'([-+]?\d{1,2}\.\d+),\s*([-+]?\d{1,3}\.\d+)')
        text = page.extract_text()
        matches = lat_lon_pattern.findall(text)
        return matches

    def is_landscaped(self, page):
        return page.mediabox.right > page.mediabox.top

    def is_portraited(self, page):
        return page.mediabox.right < page.mediabox.top

    def get_text_percentage(self, page):
        text = page.extract_text()
        return len(text) / (page.mediabox.right * page.mediabox.top) * 100
