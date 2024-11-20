import pdfplumber
import re

def is_likely_page_number(number, text_obj, page_num, total_pages):
    """
    Helper function to determine if a number is likely to be a page number
    """
    # Check if number is within reasonable range
    if not (0 <= number <= total_pages + 10):
        return False
    
    # Check if the text is standalone
    cleaned_text = text_obj['text'].strip('.- ')
    if not cleaned_text.isdigit():
        return False
    
    # Width check
    if text_obj['width'] > 100:
        return False
    
    # Page number proximity check
    if abs(number - (page_num + 1)) > 10:
        return False
        
    return True

def check_page_numbers(pdf_path):
    """
    Check each page of the PDF for page numbers using prioritized margin checking
    Returns a list of dictionaries containing information about page numbers
    """
    results = []
    INCH_IN_POINTS = 72
    
    # Define margin checks in priority order: (margin_size, position)
    MARGIN_CHECKS = [
        (0.6, "bottom", "strict"),    # First check bottom 0.6 inch
        (0.6, "top", "strict"),       # Then top 0.6 inch
        (1.1, "bottom", "normal"),    # Then bottom 1.1 inch
        (1.1, "top", "normal"),       # Then top 1.1 inch
        (1.3, "bottom", "relaxed"),   # Then bottom 1.3 inch
        (1.3, "top", "relaxed")       # Finally top 1.3 inch
    ]
    
    with pdfplumber.open(pdf_path) as pdf:
        total_pages = len(pdf.pages)
        
        for page_num in range(total_pages):
            page = pdf.pages[page_num]
            page_height = page.height
            
            # Extract text with position information
            text_with_coords = page.extract_words(
                keep_blank_chars=True,
                x_tolerance=4,
                y_tolerance=4
            )
            
            # Initialize variables
            page_number_found = False
            position = None
            actual_number = None
            margin_used = None
            
            # Check each margin position in priority order
            for margin_size, check_position, strictness in MARGIN_CHECKS:
                if page_number_found:
                    break
                    
                margin_in_points = INCH_IN_POINTS * margin_size
                
                for text_obj in text_with_coords:
                    text = text_obj['text'].strip()
                    if re.match(r'^[-. ]*\d+[-. ]*$', text):
                        number = int(''.join(filter(str.isdigit, text)))
                        y_position = text_obj['top']
                        
                        if not is_likely_page_number(number, text_obj, page_num, total_pages):
                            continue
                        
                        # Check position based on priority
                        if check_position == "bottom" and y_position >= (page_height - margin_in_points):
                            page_number_found = True
                            actual_number = number
                            position = "bottom"
                            margin_used = margin_size
                            break
                        elif check_position == "top" and y_position <= margin_in_points:
                            page_number_found = True
                            actual_number = number
                            position = "top"
                            margin_used = margin_size
                            break
            
            results.append({
                'page': page_num + 1,
                'has_page_number': page_number_found,
                'position': position,
                'found_number': actual_number,
                'margin_size': margin_used
            })
    
    return results

def print_results(results):
    """Print the results in a readable format"""
    for result in results:
        page_status = "✓" if result['has_page_number'] else "✗"
        position_text = f"at {result['position']}" if result['position'] else "not found"
        found_number = f"(number {result['found_number']})" if result['found_number'] else ""
        margin_info = f"[{result['margin_size']} inch margin]" if result['margin_size'] else ""
        
        print(f"Page {result['page']}: {page_status} Page number {position_text} {found_number} {margin_info}")

def main():
    input_file = input("Enter the path to your PDF file: ")
    try:
        results = check_page_numbers(input_file)
        print("\nPage Number Analysis Results:")
        print("-" * 50)
        print_results(results)
        
        # Print summary statistics
        total_pages = len(results)
        pages_with_numbers = sum(1 for r in results if r['has_page_number'])
        
        print("\nSummary:")
        print("-" * 50)
        print(f"Total pages: {total_pages}")
        print(f"Pages with numbers: {pages_with_numbers}")
        print(f"Pages missing numbers: {total_pages - pages_with_numbers}")
        
        # Print detailed statistics
        position_stats = {'bottom': 0, 'top': 0}
        margin_stats = {}
        for r in results:
            if r['position']:
                position_stats[r['position']] += 1
            if r['margin_size']:
                margin_stats[r['margin_size']] = margin_stats.get(r['margin_size'], 0) + 1
        
        if margin_stats:
            print("\nDetailed Statistics:")
            print("-" * 50)
            print("Position Distribution:")
            for pos, count in position_stats.items():
                print(f"Numbers found at {pos}: {count} pages")
            
            print("\nMargin Distribution:")
            for margin, count in sorted(margin_stats.items()):
                print(f"Numbers found in {margin} inch margin: {count} pages")
        
    except Exception as e:
        print(f"Error processing PDF: {str(e)}")


if __name__ == "__main__":
    main()


