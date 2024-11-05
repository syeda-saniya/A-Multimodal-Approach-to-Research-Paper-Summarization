import re

def split_into_paragraphs(text):
    # Define regex pattern to split paragraphs
    # Assume paragraphs are separated by two or more newlines, optionally with spaces/tabs in between
    return re.split(r'\n\s*\n', text)

def extract_paragraphs_with_figures_from_sections(sections):
    # Create a regex pattern to match all figure references, e.g., "Fig. 1", "Fig. 2", etc.
    figure_pattern = re.compile(r'\bFig\.\s*\d+\b', re.IGNORECASE)

    # Dictionary to collect matching paragraphs for each figure number
    figures_dict = {}

    # Iterate over each section in the dictionary
    for section_name, section_content in sections.items():
        # Split the content of each section into paragraphs
        paragraphs = split_into_paragraphs(section_content)

        # Iterate over each paragraph and check for figure references
        for para in paragraphs:
            matches = figure_pattern.findall(para)  # Find all figure references in the paragraph

            # If there are figure references, process them
            for fig in matches:
                # Initialize the figure in the dictionary if not already there
                if fig not in figures_dict:
                    figures_dict[fig] = []

                # Add the paragraph and section name to the figure entry
                figures_dict[fig].append(f"Section: {section_name}")
                figures_dict[fig].append(para.strip())
                figures_dict[fig].append("-" * 50)

    return figures_dict

# Store the output in a variable

