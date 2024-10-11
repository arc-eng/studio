
DISCOVER_BUILD_FILES = """
Find out about this project's build system:

1. List the . directory
2. Find and read any files related to building/compiling/running the project
3. For each file, recommend actions to improve it
4. Return a description of the build system as a JSON object
"""

APPLY_RECOMMENDATION = """
Apply the following changes to `{path}`:

{changes}

The goal is: {goal}
"""