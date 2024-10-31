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


from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Cours
import nltk
import random

def generate_quiz(request, course_id):
    course = get_object_or_404(Cours, id=course_id)
    description = course.description

    # Tokenize and tag words in the description
    words = nltk.word_tokenize(description)
    tagged = nltk.pos_tag(words)

    # Prepare list for generated questions
    questions = []

    # Set to keep track of generated words for unique questions
    generated_words = set()

    # Process words in the description to generate questions
    for word, tag in tagged:
        if tag.startswith('NN') and word not in generated_words:  # Noun-based question
            generated_words.add(word)
            question = f"What is {word}?"
            correct_answer = f"{word} is related to {description}"
        
            # Generate distractors based on context
            distractors = [
                f"{word} refers to something else",
                f"{word} is unrelated",
                f"{word} is a type of {random.choice(['fruit', 'animal', 'concept'])}."
            ]
            options = [correct_answer] + distractors
            random.shuffle(options)  # Shuffle to randomize option order

            questions.append({
                'question': question,
                'options': options,
                'correct_answer': correct_answer
            })

        elif tag.startswith('VB') and word not in generated_words:  # Verb-based question
            generated_words.add(word)
            question = f"What does it mean to {word}?"
            correct_answer = f"To {word} means {description}."
        
            # Generate distractors
            distractors = [
                f"It means something else.",
                f"It implies the opposite of {random.choice(words)}.",
                f"None of the above."
            ]
            options = [correct_answer] + distractors
            random.shuffle(options)

            questions.append({
                'question': question,
                'options': options,
                'correct_answer': correct_answer
            })

        elif tag.startswith('JJ') and word not in generated_words:  # Adjective-based question
            generated_words.add(word)
            question = f"What does '{word}' signify in this context?"
            correct_answer = f"'{word}' signifies {description}."
        
            # Generate distractors
            distractors = [
                f"'{word}' signifies nothing important.",
                f"It means something else.",
                f"None of the above."
            ]
            options = [correct_answer] + distractors
            random.shuffle(options)

            questions.append({
                'question': question,
                'options': options,
                'correct_answer': correct_answer
            })

    # Default question if no questions generated
    if not questions:
        questions.append({
            'question': "No questions could be generated from the description.",
            'options': ["Not applicable"],
            'correct_answer': "Not applicable"
        })

    return JsonResponse({'questions': questions})
