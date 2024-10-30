from django.core.paginator import Paginator
from django.http import HttpResponse
from django.shortcuts import render, redirect
from .forms import CourseForm
from cours.models import Cours 
import logging
from django.shortcuts import get_object_or_404 ,render


logger = logging.getLogger(__name__)

def course_list(request):
    logger.info("Début du traitement de la requête course_list")
    try:
        courses = Cours.objects.all()
        
        logger.info(f"Nombre de cours récupérés : {courses.count()}")
        return render(request, "courses.html", {'courses': courses})  # Ajouter les cours au contexte
    except Exception as e:
        logger.error(f"Erreur capturée dans course_list: {str(e)}")
        return HttpResponse(f"Une erreur est survenue : {str(e)}")



def course_detail(request, course_id):
    course = get_object_or_404(Cours, id=course_id)
    return render(request, 'course-single.html', {'course': course})



# from django.http import JsonResponse
# from django.shortcuts import get_object_or_404
# from .models import Cours
# import nltk
# import random

# def generate_quiz(request, course_id):
#     course = get_object_or_404(Cours, id=course_id)
#     description = course.description

#     # Tokenization and tagging of words in the description
#     words = nltk.word_tokenize(description)
#     tagged = nltk.pos_tag(words)

#     # Prepare the list for generated questions
#     questions = []
#     generated_words = set()  # To keep track of already generated words

#     # Process words in the description to generate questions
#     for word, tag in tagged:
#         if word not in generated_words:  # Avoid duplicates
#             question = None  # Initialize question
#             correct_answer = None  # Initialize correct_answer

#             if tag.startswith('NN'):  # Noun-based question
#                 generated_words.add(word)
#                 question = f"Qu'est-ce que {word} dans ce contexte?"
#                 correct_answer = f"{word} fait référence à {description}."
#                 distractors = [
#                     f"{word} est un exemple de {random.choice(['sujet', 'objet', 'concept'])} dans ce texte.",
#                     f"{word} est un terme utilisé dans un autre contexte.",
#                     f"{word} n'a pas de lien avec la description."
#                 ]
#                 options = [correct_answer] + distractors
#                 random.shuffle(options)  # Shuffle to randomize order

#             elif tag.startswith('VB'):  # Verb-based question
#                 generated_words.add(word)
#                 question = f"Que signifie le verbe {word} dans ce contexte?"
#                 correct_answer = f"{word} implique {description}."
#                 distractors = [
#                     f"{word} signifie généralement le contraire de {random.choice(words)}.",
#                     f"{word} peut aussi signifier quelque chose de totalement différent.",
#                     f"{word} n'est pas utilisé dans ce contexte."
#                 ]
#                 options = [correct_answer] + distractors
#                 random.shuffle(options)

#             elif tag.startswith('JJ'):  # Adjective-based question
#                 generated_words.add(word)
#                 question = f"Comment {word} décrit-il le sujet ici?"
#                 correct_answer = f"'{word}' implique une certaine qualité décrite dans {description}."
#                 distractors = [
#                     f"'{word}' signifie le contraire de ce qui est décrit.",
#                     f"'{word}' ne signifie rien dans ce contexte.",
#                     f"'{word}' pourrait désigner un aspect sans rapport."
#                 ]
#                 options = [correct_answer] + distractors
#                 random.shuffle(options)

#             # Append question only if it was generated
#             if question and correct_answer:
#                 questions.append({
#                     'question': question,
#                     'options': options,
#                     'correct_answer': correct_answer
#                 })

#     # Default question if no questions generated
#     if not questions:
#         questions.append({
#             'question': "Aucune question n'a pu être générée à partir de la description.",
#             'options': ["Non applicable"],
#             'correct_answer': "Non applicable"
#         })

#     return JsonResponse({'questions': questions})


import spacy
import random
import pdfplumber
from nltk.corpus import wordnet
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Cours

import nltk
nltk.download('wordnet')
nltk.download('omw-1.4')  

def extract_pdf_text(file_path):
    with pdfplumber.open(file_path) as pdf:
        text = ""
        for page in pdf.pages:
            text += page.extract_text() or ''  
    return text

def get_synonyms(word):
    synonyms = set()
    for syn in wordnet.synsets(word, lang='fra'): 
        for lemma in syn.lemmas('fra'):
            synonyms.add(lemma.name().replace('_', ' '))
    return list(synonyms)


def generate_quiz(request, course_id):
    course = get_object_or_404(Cours, id=course_id)
    
    if not course.file:
        return JsonResponse({'error': 'Aucun fichier PDF associé à ce cours.'})

    text = extract_pdf_text(course.file.path)
    if not text:
        return JsonResponse({'error': 'Échec de l\'extraction du texte du PDF.'})

    # Charger le modèle spaCy pour le français
    nlp = spacy.load('fr_core_news_sm')
    doc = nlp(text)

    sentences = [sent.text.strip() for sent in doc.sents if len(sent.text.strip()) > 15]
    questions = []
    generated_questions = set()

    while len(questions) < 10 and sentences:
        sentence = random.choice(sentences)
        sent_doc = nlp(sentence)
        nouns = [token.text for token in sent_doc if token.pos_ in ["NOUN", "PROPN"]]

        if not nouns:
            continue

        subject = random.choice(nouns)
        question_stem = sentence.replace(subject, "_______", 1)

        answer_choices = [subject]
        distractors = get_synonyms(subject)

        while len(distractors) < 3:
            new_distractor = random.choice([token.text for token in nlp.vocab if token.is_alpha and token.text.lower() != subject.lower()])
            if new_distractor.lower() not in [d.lower() for d in distractors]:  # Éviter les doublons
                distractors.append(new_distractor)

        answer_choices.extend(random.sample(distractors, min(3, len(distractors))))
        random.shuffle(answer_choices)

        questions.append({
            'question': question_stem,
            'options': answer_choices,
            'correct_answer': subject
        })
        generated_questions.add((question_stem, subject))

    return JsonResponse({'questions': questions})





# Étape 1 : Installer spaCy et le modèle
# pip install spacy pdfplumber nltk
# python -m spacy download fr_core_news_sm
# python -m nltk.downloader wordnet
# python -m nltk.downloader omw-1.4

# Étape 2 : Importer le modèle dans votre code
# import spacy

# Étape 3 : Charger le modèle dans votre fonction
#  # Charger le modèle spaCy
#     nlp = spacy.load('fr_en_core_web_sm')