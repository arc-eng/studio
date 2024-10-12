PR_DESCRIPTION = """
I've made some changes and opened a new PR: #{pr_number}.

I need a PR title and a description that summarizes these changes.
The PR description will also be used as merge commit message, so it should be clear and informative.

Use the following guidelines:

## PR Title
- Start with a verb in the imperative mood (e.g., "Add", "Fix", "Update").
- {emoji_in_title}

## PR Body

- At the very top, provide short paragraph summarizing the changes and their impact.
- Use the present tense and the active voice.
- Be specific - Include names, paths, identifiers, names, versions, etc
- Where possible, make file names/paths clickable using Markdown links. Use this format for the URL: `https://github.com/<github_project>/blob/<pr_branch>/<file_path>`
- Use bold text instead of sections/sub-sections
- {structure}
- {emojis}
- {style}
{additional_instructions}

---

# Your task
Do the following:
1. Read PR #{pr_number}
2. Generate title and description to reflect the changes made in this PR
3. Update the PR with the title and description
4. Respond with a copy of the PR description
"""


def structure_prompt(form_select):
    if form_select == "topics":
        return ("List the changes made in bullet points and separate them into sections."
                "Each section should be a topic / category related to the file changes."
                "There should be no more than 3-4 topics.")
    elif form_select == "files":
        return "List the changes made in bullet points and group the changes by file."
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
