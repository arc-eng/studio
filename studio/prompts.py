

GENERATE_REPORT = """
I want to generate a report for the repository. This report should include the following information:

{report_description}

It should be called "{title}".

Do the following:

1. Use your capabilities to find the required information.
2. Compile the information into a coherent, comprehensive report.
3. Generate the report has HTML code

The HTML code should meet the following requirements:

- Uses BulmaCSS classes, components, elements and layout to style the report
- At the beginning of every header, use a FontAwesome icon
- The outer most tag is a simple div with the class `box`
- The top to bottom structure should be title, executive summary, table of contents, sections, and references

Return only the HTML code, nothing else. Do not wrap it in backticks or code blocks.
"""

