from django.shortcuts import render
import pandas as pd
import joblib

def load_model():
    """Load the model and label encoder."""
    model = joblib.load('stress_management/models/stress_model.pkl')
    le = joblib.load('stress_management/models/label_encoder.pkl')
    return model, le

from django.templatetags.static import static  # Assure-toi d'importer le bon module

def get_recommendations(stress_level):
    """Get recommendations based on the stress level."""
    recommendations_dict = {
        'Dormir suffisamment, Se déconnecter des écrans': [
            {'text': 'Get enough sleep', 'image': static('images/sleep.png')},  
            {'text': 'Disconnect from screens', 'image': static('images/disconnect.png')} 
        ],
        'Pratiquer des exercices de respiration': [
            {'text': 'Practice breathing exercises', 'video': 'https://www.youtube.com/watch?v=cHuUs483S4Q'}, 
            {'text': 'Take a walk', 'image': static('images/walk.png')}  
        ],
        'Lecture': [
            {'text': 'Reading', 'video': 'https://www.example.com/reading_video.mp4'},  
            {'text': 'Light exercises', 'image': static('images/light_exercise.png')}  
        ],
        'Yoga': [
            {'text': 'Yoga', 'image': static('images/yoga.png')},  
            {'text': 'Meditation', 'video': '<iframe width="560" height="315" src="https://www.youtube.com/embed/ssss7V1_eyA?si=wie4eIZNgQwhUE4K" title="YouTube video player" frameborder="0" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'}  # Video for meditation
        ],
        'Consulter un professionnel, Faire des exercices de relaxation': [
            {'text': 'Consult a professional', 'image': static('images/professional_help.png')},  
            {'text': 'Meditation', 'video': 'https://www.youtube.com/embed/ssss7V1_eyA'}  
        ],
    }
    return recommendations_dict.get(stress_level, [])




def stress_evaluation(request):
    if request.method == 'POST':
        # Récupérer les données du formulaire
        q1 = request.POST.get('Q1')
        q2 = request.POST.get('Q2')
        q3 = request.POST.get('Q3')
        q4 = request.POST.get('Q4')
        q5 = request.POST.get('Q5')

        # Vérifier les saisies
        if not all([q1, q2, q3, q4, q5]):
            return render(request, 'stress_management/stress_results.html', {
                'stress_level': 'Erreur : Toutes les questions doivent être remplies.',
                'recommendations': []
            })

        # Créer un DataFrame avec les données requises
        input_data = pd.DataFrame([[None, q1, q2, q3, q4, q5, None]], 
                                   columns=['ID', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Recommandations'])

        # Charger le modèle et l'encodeur
        try:
            model, le = load_model()

            # Prédire le niveau de stress et décoder
            predicted_stress_level = model.predict(input_data)[0]
            decoded_stress_level = le.inverse_transform([predicted_stress_level])[0]

            # Vérifier que le niveau de stress est valide
            print(f"Niveau de stress prédit : {decoded_stress_level}")  # Debug

            # Obtenir les recommandations pour le niveau prédit
            recommendations = get_recommendations(decoded_stress_level)

        except FileNotFoundError:
            return render(request, 'stress_management/stress_results.html', {
                'stress_level': 'Erreur : Modèle introuvable.',
                'recommendations': []
            })
        except Exception as e:
            return render(request, 'stress_management/stress_results.html', {
                'stress_level': f'Erreur lors de la prédiction : {str(e)}',
                'recommendations': []
            })

        # Envoyer les résultats au template
        return render(request, 'stress_management/stress_results.html', {
            'stress_level': decoded_stress_level,
            'recommendations': recommendations
        })

    # Rendre le formulaire pour les requêtes GET
    return render(request, 'stress_management/stress_evaluation.html')



# from django.shortcuts import render
# import pandas as pd
# import joblib

# def load_model():
#     """Load the model and label encoder."""
#     model = joblib.load('stress_management/models/stress_model.pkl')
#     le = joblib.load('stress_management/models/label_encoder.pkl')
#     return model, le

# def get_recommendations(stress_level):
#     """Get recommendations based on the stress level."""
#     recommendations_dict = {
#         'Faible': [
#             {'text': 'Pratiquer des exercices de respiration', 'image': 'images/breathing.png'},
#             {'text': 'Faire une promenade', 'image': 'images/walk.png'}
#         ],
#         'Moyen': [
#             {'text': 'Lecture', 'video': 'https://www.example.com/reading_video.mp4'},
#             {'text': 'Exercices légers', 'image': 'images/light_exercise.png'}
#         ],
#         'Élevé': [
#             {'text': 'Yoga', 'image': 'images/yoga.png'},
#             {'text': 'Méditation', 'video': 'https://www.example.com/meditation_video.mp4'}
#         ],
#         'Critique': [
#             {'text': 'Consultation d’un professionnel', 'image': 'images/professional_help.png'},
#             {'text': 'Prendre du temps pour soi', 'image': 'images/relax.png'}
#         ]
#     }
#     return recommendations_dict.get(stress_level, [])

# def stress_evaluation(request):
#     if request.method == 'POST':
#         # Retrieve form data
#         q1 = request.POST.get('Q1')
#         q2 = request.POST.get('Q2')
#         q3 = request.POST.get('Q3')
#         q4 = request.POST.get('Q4')
#         q5 = request.POST.get('Q5')

#         # Check for missing inputs
#         if not all([q1, q2, q3, q4, q5]):
#             return render(request, 'stress_management/stress_results.html', {
#                 'stress_level': 'Erreur : Toutes les questions doivent être remplies.',
#                 'recommendations': []
#             })

#         # Create a DataFrame with required columns
#         input_data = pd.DataFrame([[None, q1, q2, q3, q4, q5, None]], 
#                                    columns=['ID', 'Q1', 'Q2', 'Q3', 'Q4', 'Q5', 'Recommandations'])

#         # Load model and encoder
#         try:
#             model, le = load_model()

#             # Predict stress level and decode
#             predicted_stress_level = model.predict(input_data)[0]
#             decoded_stress_level = le.inverse_transform([predicted_stress_level])[0]

#             # Get recommendations for predicted level
#             recommendations = get_recommendations(decoded_stress_level)

#         except FileNotFoundError:
#             return render(request, 'stress_management/stress_results.html', {
#                 'stress_level': 'Erreur : Modèle introuvable.',
#                 'recommendations': []
#             })
#         except Exception as e:
#             return render(request, 'stress_management/stress_results.html', {
#                 'stress_level': f'Erreur lors de la prédiction : {str(e)}',
#                 'recommendations': []
#             })

#         # Send the results to the template
#         return render(request, 'stress_management/stress_results.html', {
#             'stress_level': decoded_stress_level,
#             'recommendations': recommendations
#         })

#     # Render the form for GET requests
#     return render(request, 'stress_management/stress_evaluation.html')
