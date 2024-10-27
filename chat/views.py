import random

import nltk
from django.http import JsonResponse
from django.shortcuts import render
from nltk import word_tokenize, pos_tag, ne_chunk
from textblob import TextBlob

from .models import Message

resources = [
    'punkt',
    'averaged_perceptron_tagger',
    'maxent_ne_chunker',
    'punkt_tab',
    'averaged_perceptron_tagger_eng',
    'maxent_ne_chunker_tab',
    'words'
]


# Функция для проверки наличия ресурса
def download_if_not_installed(resource):
    try:
        # Проверяем, установлен ли ресурс
        nltk.data.find(f'tokenizers/{resource}')
    except LookupError:
        nltk.download(resource)


# Загрузка каждого ресурса, если он не установлен
for resource in resources:
    download_if_not_installed(resources)


def extract_name(user_input):
    """Извлекает имена собственные из текста с использованием nltk."""
    words = word_tokenize(user_input)  # Токенизация
    pos_tags = pos_tag(words)  # Определение частей речи
    tree = ne_chunk(pos_tags)  # Извлечение именованных сущностей

    names = []
    for subtree in tree:
        if isinstance(subtree, nltk.Tree) and subtree.label() == 'PERSON':
            names.append(' '.join(leaf[0] for leaf in subtree.leaves()))
    return names


# Predefined bot responses
positive_responses = ["I'm pleased to hear that!", "That's fantastic! How can I assist you further?", "Great!"]
negative_responses = ["I'm sorry to hear you're having trouble.", "I'm here to assist. What seems to be the issue?"]
neutral_responses = ["Understood! How can I assist you further?", "Alright, please share more details.",
                     "I'm not quite sure what you mean.", "Could you clarify that?",
                     "I'm here to help, but I didn't quite catch that."]


# Generate a bot response based on sentiment
def get_response(user_input):
    sentiment = TextBlob(user_input).sentiment.polarity
    name = extract_name(user_input)
    if name:
        return f"Nice to meet you, {name}!"

    if sentiment > 0:
        return random.choice(positive_responses) + " 😊"
    elif sentiment < 0:
        return random.choice(negative_responses) + " 😔"
    else:
        return random.choice(neutral_responses) + " 😐"


# Main chat view
def chat_view(request):
    if request.method == 'POST':
        user_input = request.POST.get("message", "").strip()
        session_id = request.session.session_key or request.session.create()  # Create session if it doesn't exist

        # Save message to database
        Message.objects.create(session_id=session_id, sender="User", message=user_input)

        # Generate bot response
        bot_response = get_response(user_input)

        # Save bot response to database
        Message.objects.create(session_id=session_id, sender="Bot", message=bot_response)

        return JsonResponse({"response": bot_response})

    session_id = request.session.session_key or request.session.create()  # Create session if it doesn't exist
    chat_history = Message.objects.filter(session_id=session_id)  # Retrieve chat history for the session

    return render(request, 'chat/index.html', {'chat_history': chat_history})
