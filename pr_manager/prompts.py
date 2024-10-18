from enum import Enum
from typing import List

from pydantic import BaseModel, Field


class Criticality(Enum):
    MINOR = "Minor"
    MAJOR = "Major"
    CRITICAL = "Critical"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value


class Category(Enum):
    SECURITY = "Security"
    PERFORMANCE = "Performance"
    USABILITY = "Usability"
    FUNCTIONALITY = "Functionality"
    MAINTAINABILITY = "Maintainability"
    READABILITY = "Readability"
    STYLE = "Style"
    OTHER = "Other"

    def __str__(self):
        return self.value

    def __repr__(self):
        return self.value

class CodeReviewFinding(BaseModel):
    file: str = Field(title="File Path", description="Path of the file that is being reviewed")
    issue: str = Field(title="Issue", description="Issue found in the file changes")
    line_start: int = Field(title="First line number", description="First line number of the issue")
    line_end: int = Field(title="Last line number", description="Last line number of the issue")
    criticality: Criticality = Field(title="Criticality", description="Criticality of the issue", )
    category: Category = Field(title="Category", description="Category of the file changes")
    recommendation: str = Field(title="Recommendation", description="Recommendation to fix the issue")

class CodeReview(BaseModel):
    summary: str = Field(title="Summary", description="A brief summary of the code review")
    findings: List[CodeReviewFinding] = Field(title="Findings", description="Findings from the code review")

CODE_REVIEW = """
There is a pull request I want you to review: #{pr_number}.
I need you to review the changes made in the files and provide a list of findings.

### What constitutes a "finding"
- An issue found in the file changes that should be addressed
- A recommendation to fix the issue
- The criticality of the issue (Minor, Major, Critical)
- The category of the file changes (Security, Performance, Usability, Functionality, Maintainability, Readability, Style, Other)

### What to look out for
- Code that could lead to security issues like SQL injection, XSS, etc.
- Code that could lead to performance issues
- Code smells like duplicated code, long methods, etc.
- Lack of comments or docstrings
- Code style violations
- Incorrect or missing error handling
- Incorrect or missing tests for complex logic
- Poorly written code that could be refactored for better readability and maintainability

### Formatting
Use Markdown formatting in the findings issues and recommendations to enhance readability.

Do the following:
1. Read the PR #{pr_number} to understand the file changes
2. Review the file changes and identify issues that need to be addressed
3. Create a list of findings for each issue found
4. Write a summary of the findings

It is OK to have an empty list of findings if there are no issues found. If that is the case, 
point out in the summary that there are no findings and it looks good to go. 
"""

APPLY_RECOMMENDATION = """
In a code review, we have identified an issue in the file `{file}` that needs to be addressed:

{issue}

The recommendation to fix the issue is:
{recommendation}

Apply the code changes to fix the issue.
"""

PR_DESCRIPTION = """
I've made some changes and opened a new PR: #{pr_number}.

I need a PR title and a description that summarizes these changes.

Use the following guidelines:

- Start the title with a verb in the imperative mood (e.g., "Add", "Fix", "Update").
- At the very top, provide short paragraph summarizing the changes and their impact.
- Use the present tense and the active voice.
- Be specific - Include names, paths, identifiers, names, versions, etc
- Where possible, make file names/paths clickable using Markdown links. Use this format for the URL: `https://github.com/<github_project>/blob/<pr_branch>/<file_path>`
- If/when writing sections, use bold text instead of '#' for section headers

## Mandatory Requirements
The new PR description MUST adhere to the following requirements:
- {structure}
- {emojis}
- {style}
{additional_instructions}
- If the PR already has a description, DISCARD it. Start completely from scratch.

---

# Your task
Do the following:
1. Read PR #{pr_number} to understand the file changes. IGNORE the existing description/title
2. Generate a new title and description that follows the requirements above
3. Update the PR with the new title and description
4. Respond a short confirmation and link to the PR
"""


def structure_prompt(form_select):
    if form_select == "topics":
        return ("List the changes made in bullet points and separate them into sections."
                "Each section should be a topic / category related to the file changes."
                "There should be no more than 3-4 topics.")
    elif form_select == "files":
        return "Write a section for each file changed, and describe the changes made in that file in bullet points"
    else:
        return "Explain the file changes in prose and paragraphs."

def emoji_prompt(form_select):
    if form_select == "readability":
        return "Add emojis to the beginning of headers and the title to enhance the readability. Use UTF-8 encoding for emojis"
    elif form_select == "readability_and_fun":
        return "Add emojis to the beginning of headers and the title. Also use lots of emojis in the description to enhance readability and for visual eye candy and fun! Use UTF-8 encoding for emojis"
    elif form_select == "no_emojis":
        return "Do not use emojis"
    else:
        raise ValueError()

def style_prompt(form_select):
    if form_select == "medium":
        return "Keep it concise, but elaborate when necessary."
    elif form_select == "detailed":
        return "Describe the changes in detail and elaborate"
    elif form_select == "brief":
        return "Keep it brief and concise. Cover everything, but don't elaborate."
    else:
        raise ValueError()
