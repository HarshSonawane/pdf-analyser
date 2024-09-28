import pdfplumber

# Open the PDF file
file_path = 'data/Test_Doc4_1.pdf'
output_file_path = 'page_numbers_results.txt'

with pdfplumber.open(file_path) as pdf, open(output_file_path, 'w') as output_file:
    for page_num, page in enumerate(pdf.pages):
        result = f"Page {page_num + 1}:\n"

        # Get the width and height of the page
        width, height = page.width, page.height

        # Get the top and bottom 10% of the page 
        top_page_part = page.crop((0, 0, width, height * 0.1))  
        bottom_page_part = page.crop((0, height * 0.9, width, height))  
        
        # determine position (left, center, right)
        def get_horizontal_position(text, width):
            text_width = text["x0"]
            if text_width <= width * 0.25:
                return "left"
            elif width * 0.25 < text_width <= width * 0.75:
                return "center"
            else:
                return "right"
        
        # find the page number text and location in a specific region
        def find_page_number_position(region, page_num, width):
            text = region.extract_words()
            for word in text:
                if str(page_num + 1) in word["text"]:
                    return get_horizontal_position(word, width)
            return None
        
        # Check top and bottom page areas for the page number
        page_location = None
        top_position = find_page_number_position(top_page_part, page_num, width)
        bottom_position = find_page_number_position(bottom_page_part, page_num, width)

        # Determine if the page number is found at the top or bottom
        if top_position:
            page_location = f"top {top_position}"
        elif bottom_position:
            page_location = f"bottom {bottom_position}"
        
        # Output the result
        if page_location:
            result += f"Page number {page_num + 1} found at the {page_location} of the page.\n"
        else:
            result += f"Page number {page_num + 1} not found explicitly.\n"
        
        # Write result
        output_file.write(result)
