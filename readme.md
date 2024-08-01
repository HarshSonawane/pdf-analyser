

    # def get_pdf_margins(self):
    #     pdf_margins = {}

    #     for page_num in range(len(self.pdf.pages)):
    #         page = self.pdf.pages[page_num]
    #         pdf_margins[page_num] = page.mediabox.left, page.mediabox.bottom, page.mediabox.right, page.mediabox.top

    #     return pdf_margins

    # def page_numbers_and_coordinates(self):
    #     page_numbers_and_coordinates = {}
    #     lat_lon_pattern = re.compile(r'([-+]?\d{1,2}\.\d+),\s*([-+]?\d{1,3}\.\d+)')
    #     results = []
    #     for page_num in range(len(self.pdf.pages)):
    #         page = self.pdf.pages[page_num]
    #         text = page.extract_text()

    #         matches = lat_lon_pattern.findall(text)
    #         if matches:
    #             results.append({
    #                 'page_number': page_num + 1,  # Page numbers are 1-based
    #                 'coordinates': matches
    #             })

    #     return results

    # def blank_pages(self):
    #     blank_pages = []
    #     for page_num in range(len(self.pdf.pages)):
    #         page = self.pdf.pages[page_num]
    #         text = page.extract_text()
    #         if not text:
    #             blank_pages.append(page_num)

    #         # also add if the page has only whitespace
    #         if text.isspace():
    #             blank_pages.append(page_num)

    #         # also add if the page has only newline characters
    #         if text == '\n':
    #             blank_pages.append(page_num)

    #     return blank_pages

    # def get_page_margins(self, page):
    #     return page.mediabox.left, page.mediabox.bottom, page.mediabox.right, page.mediabox.top

    # def is_blank_page(self, page):
    #     text = page.extract_text()
    #     if not text:
    #         return True

    #     # also add if the page has only whitespace
    #     if text.isspace():
    #         return True

    #     # also add if the page has only newline characters
    #     if text == '\n':
    #         return True

    #     return False
