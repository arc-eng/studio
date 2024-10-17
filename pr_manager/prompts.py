PR_DESCRIPTION = """
I've made some changes and opened a new PR: #{pr_number}.

I need a PR title and a description that summarizes these changes.

Use the following guidelines:

- Start the title with a verb in the imperative mood (e.g., "Add", "Fix", "Update").
- {emoji_in_title}
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
        return "Add emojis, to enhance the readability. Use UTF-8 encoding for emojis"
    elif form_select == "readability_and_fun":
        return "Add lots of emojis to enhance readability and for visual eye candy and fun! Use UTF-8 encoding for emojis"
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
