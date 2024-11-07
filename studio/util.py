import json

from arcane import ApiException
from django.shortcuts import redirect, render
from django.urls import reverse


def handle_engine_api_exception(request, e: ApiException, owner: str, repo: str):

    if e.data and e.data.error:
        msg = e.data.error
    else:
        try:
            json_msg = json.loads(e.body)
            msg = json_msg.get("details", str(e))
        except json.JSONDecodeError:
            msg = str(e)
    # TODO this is a hack to check if the engine is not installed, fix once proper error codes are available
    if "Arcane Engine is not installed" in msg:
        return redirect(reverse('repositories:install_repo', args=[owner, repo]))
    return render(request, "error.html", {
        "error": f"Failed to create task: {msg}",
    })