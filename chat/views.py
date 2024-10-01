import threading

import markdown
from arcane.engine import ArcaneEngine
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from chat.models import ChatConversation, ChatMessage
from repositories.models import BookmarkedRepo
from studio.decorators import needs_api_key


@login_required
@needs_api_key
def view_chat(request, chat_id, api_key):
    if request.method == "POST":
        message = request.POST.get("message")
        if not message:
            raise ValueError("Message is required.")
        else:
            chat = ChatConversation.objects.get(pk=chat_id)
            chat.continue_conversation(message, api_key)
            return redirect("view_chat", chat_id=chat_id)

    chat = ChatConversation.objects.get(pk=chat_id)
    messages = chat.messages.all()
    for message in messages:
        if not message.result:
            task = ArcaneEngine(api_key).get_task(message.task_id)
            message.result = task.result
            message.save()
        if message.result:
            message.result = markdown.markdown(message.result, extensions=['nl2br', 'fenced_code', 'extra'])
        message.message = markdown.markdown(message.message, extensions=['nl2br', 'fenced_code', 'extra'])
    return render(request, "view_chat.html", {
        "chats": ChatConversation.objects.order_by('-id').all(),
        "selected_chat": chat,
        "messages": messages,
        "active_tab": "chat",
    })


@login_required
@needs_api_key
def start_conversation(request, api_key):
    if request.method == "POST":
        message = request.POST.get("message")
        repo_id = request.POST.get("repo_id")
        if not message:
            raise ValueError("Message is required.")
        else:
            repo = BookmarkedRepo.objects.get(pk=repo_id)
            chat = ChatConversation.objects.create(user=request.user,
                                                   repo=repo)
            new_task = ArcaneEngine(api_key).create_task(repo.full_name, message)
            ChatMessage.objects.create(conversation=chat, message=message, task_id=new_task.id)
            thread = threading.Thread(target=chat.generate_title, args=(api_key,))
            thread.start()
            return redirect("view_chat", chat_id=chat.id)

    return render(request, "start_conversation.html", {
        "bookmarked_repos": BookmarkedRepo.objects.all(),
        "chats": ChatConversation.objects.order_by('-id').all(),
        "active_tab": "chat",
   })


@login_required
def delete_chat(request, chat_id):
    chat = ChatConversation.objects.get(pk=chat_id)
    chat.delete()
    return redirect("start_conversation")