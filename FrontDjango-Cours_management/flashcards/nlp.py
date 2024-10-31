import torch
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem import WordNetLemmatizer
from transformers import BartTokenizer, BartForConditionalGeneration, pipeline, AutoModelForQuestionAnswering, AutoTokenizer
from sentence_transformers import SentenceTransformer
import numpy as np

# Télécharger les ressources NLTK nécessaires (à exécuter une seule fois)
nltk.download('punkt')
nltk.download('wordnet')
nltk.download('stopwords')
nltk.download('averaged_perceptron_tagger')

# Charger les modèles une seule fois au démarrage pour éviter le rechargement à chaque requête
class NLPProcessor:
    def __init__(self):
        # Charger le tokenizer et le modèle BART pour la génération de bullet points
        self.model_name = 'facebook/bart-large-cnn'
        self.tokenizer = BartTokenizer.from_pretrained(self.model_name)
        self.model = BartForConditionalGeneration.from_pretrained(self.model_name)

        # Initialiser Sentence-BERT pour l'encodage des phrases (si nécessaire)
        self.sentence_bert_model = SentenceTransformer('average_word_embeddings_glove.6B.300d')

        # Initialiser les stopwords et le lemmatizer
        self.stopwords = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()

        # Initialiser le pipeline de génération de questions avec T5
        self.pipe_qg = pipeline("text2text-generation", model='lmqg/t5-large-squad-qg')

        # Charger le modèle BART pour le Question Answering
        self.tokenizer_qa = AutoTokenizer.from_pretrained("valhalla/bart-large-finetuned-squadv1")
        self.model_qa = AutoModelForQuestionAnswering.from_pretrained("valhalla/bart-large-finetuned-squadv1")

    def preprocess_text(self, text):
        # Tokeniser le texte en phrases
        sentences = sent_tokenize(text)

        # Suppression des stopwords et lemmatisation
        filtered_sentences = []
        for sentence in sentences:
            tokens = word_tokenize(sentence.lower())
            filtered_tokens = [self.lemmatizer.lemmatize(word) for word in tokens if word not in self.stopwords and word.isalpha()]
            filtered_sentence = " ".join(filtered_tokens)
            filtered_sentences.append(filtered_sentence)

        return filtered_sentences

    def generate_bullet_points(self, filtered_sentences):
        bullet_points = []
        for sentence in filtered_sentences:
            # Encoder la phrase
            inputs = self.tokenizer.encode(
                sentence,
                add_special_tokens=True,
                truncation=True,
                max_length=512,
                padding='max_length',
                return_tensors="pt"
            )

            # Générer le résumé (bullet point)
            summary_ids = self.model.generate(
                inputs,
                num_beams=4,
                min_length=10,
                max_length=150,
                length_penalty=2.0,
                early_stopping=True
            )
            summary = self.tokenizer.decode(summary_ids[0], skip_special_tokens=True)
            bullet_points.append(summary.strip())

        return bullet_points

    def generate_questions(self, sentences):
        questions = []
        for sentence in sentences:
            input_text = 'generate question: ' + sentence
            question = self.pipe_qg(input_text)
            if isinstance(question, list) and len(question) > 0 and 'generated_text' in question[0]:
                question_text = question[0]['generated_text']
                if isinstance(question_text, str):
                    questions.append(question_text)
        return questions

    def rank_questions(self, questions):
        # Encoder les questions en embeddings
        question_embeddings = self.sentence_bert_model.encode(questions)

        # Calculer les scores de similarité (exemple simple)
        ranking_scores = question_embeddings.dot(question_embeddings.T).mean(axis=1)

        # Conversion en array NumPy de type float
        ranking_scores = np.array(ranking_scores).astype(float)

        return ranking_scores

    def extract_answers(self, questions, context):
        answers = []
        for question in questions:
            inputs = self.tokenizer_qa.encode_plus(question, context, add_special_tokens=True, return_tensors="pt")
            input_ids = inputs["input_ids"].tolist()[0]

            outputs = self.model_qa(**inputs)
            answer_start_scores = outputs.start_logits
            answer_end_scores = outputs.end_logits

            answer_start = torch.argmax(answer_start_scores)
            answer_end = torch.argmax(answer_end_scores) + 1

            # Extraire la réponse
            answer = self.tokenizer_qa.convert_tokens_to_string(
                self.tokenizer_qa.convert_ids_to_tokens(input_ids[answer_start:answer_end])
            )
            answer = answer.replace("#", "").strip()
            answers.append(answer)

        return answers

    def generate_flashcards(self, text, num_flashcards):
        try:
            # Convertir num_flashcards en entier
            num_flashcards = int(num_flashcards)
            if num_flashcards <= 0:
                raise ValueError("Le nombre de flashcards doit être supérieur à 0.")
        except ValueError as ve:
            raise ValueError("num_flashcards_limit doit être un nombre entier positif.") from ve

        # S'assurer que le texte est une chaîne de caractères
        if isinstance(text, list):
            text = " ".join(text)
        elif not isinstance(text, str):
            raise TypeError("text doit être une chaîne de caractères ou une liste de chaînes.")

        print(f"Processed text: {text}")  # Débogage

        # Tokeniser le texte en phrases
        sentences = sent_tokenize(text)
        print(f"Tokenized sentences: {sentences}")  # Débogage

        # Générer des bullet points à partir des phrases
        bullet_points = self.generate_bullet_points(sentences)
        print(f"Bullet points: {bullet_points}")  # Débogage

        # Générer des questions à partir des bullet points
        questions = self.generate_questions(bullet_points)
        print(f"Generated questions: {questions}")  # Débogage

        if not questions:
            raise ValueError("Aucune question générée à partir du texte fourni.")

        # Encodage et classement des questions
        ranking_scores = self.rank_questions(questions)
        print(f"Ranking scores: {ranking_scores}")  # Débogage

        # S'assurer que le nombre de flashcards demandé ne dépasse pas le nombre de questions générées
        num_flashcards = min(num_flashcards, len(questions))

        # Sélectionner les indices des questions les plus pertinentes
        selected_indices = ranking_scores.argsort()[-num_flashcards:][::-1]
        selected_questions = [questions[i] for i in selected_indices]
        print(f"Selected questions: {selected_questions}")  # Débogage

        # Extraction des réponses
        answers = self.extract_answers(selected_questions, text)
        print(f"Generated answers: {answers}")  # Débogage

        # Création des flashcards
        flashcards = [{'question': q, 'answer': a} for q, a in zip(selected_questions, answers)]
        print(f"Flashcards: {flashcards}")  # Débogage

        return flashcards

# Initialiser le processeur NLP au démarrage de Django
nlp_processor = NLPProcessor()
