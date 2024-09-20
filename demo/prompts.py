PR_DESCRIPTION = """
I've made some changes and opened a new PR: #{pr_number}.

I need a PR title and a description that summarizes these changes in short, concise bullet points.
The PR description will also be used as merge commit message, so it should be clear and informative.

Use the following guidelines:

## PR Title
- Start with a verb in the imperative mood (e.g., "Add", "Fix", "Update").
- Put an emoji at the beginning that reflects the nature of the changes

## PR Body

- At the very top, provide short paragraph summarizing the changes and their impact.
- Below, list the changes made in bullet points.
- Use bold text instead of sections/sub-sections to separate the bullet points into topics
- There should be no more than 3-4 topics
- Use the present tense and the active voice.
- Be specific - Include names, paths, identifiers, names, versions, etc
- Where possible, make file names/paths clickable using Markdown links. Use this format for the URL: `https://github.com/<github_project>/blob/<pr_branch>/<file_path>`


# Your task
Edit PR #{pr_number} title and description to reflect the changes made in this PR.
Respond in the following format:

```
I've updated the title and description of <number and title of PR, hyperlink>

---

<pr description>
```
"""


GENERATE_REPORT = """
I want to generate a report for the repository. This report should include the following information:

{report_description}

Do the following:

1. Use your capabilities to find the required information.
2. Compile the information into a coherent, comprehensive report.
3. Generate the report has HTML code

The HTML code should meet the following requirements:

- Uses BulmaCSS classes, components, elements and layout to style the report
- Use Fa icons everywhere to make it look good
- The outer most tag is a simple div with the class `container`
- The top to bottom structure should be title, executive summary, table of contents, sections, and references

Return only the HTML code, nothing else. Do not wrap it in backticks or code blocks.
"""