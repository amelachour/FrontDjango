import openai
import PyPDF2
from docx import Document
import logging
import torch
from transformers import pipeline
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle

from .models import Summary
from .forms import SummaryForm

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load summarization model at the start
device = 0 if torch.cuda.is_available() else -1  # Use GPU if available
summarization_pipeline = pipeline("summarization", model="facebook/bart-large-cnn", device=device)

# Warm-up the model
def warm_up_model():
    try:
        summarization_pipeline("This is a warm-up text.", max_length=50, min_length=20, do_sample=False)
        logger.info("Model warmed up successfully.")
    except Exception as e:
        logger.error(f"Error during warm-up: {e}")

# Call warm-up during startup
warm_up_model()

def extract_text_from_pdf(pdf_file):
    try:
        reader = PyPDF2.PdfReader(pdf_file)
        text = ""
        for page in reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        logger.error(f"Error extracting text from PDF: {e}")
        raise

def extract_text_from_word(word_file):
    try:
        doc = Document(word_file)
        full_text = []
        for para in doc.paragraphs:
            full_text.append(para.text)
        return '\n'.join(full_text)
    except Exception as e:
        logger.error(f"Error extracting text from Word document: {e}")
        raise

def split_text_into_chunks(text, chunk_size=1000):
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

# Create a new summary
def create_summary(request):
    if request.method == 'POST':
        form = SummaryForm(request.POST, request.FILES)
        if form.is_valid():
            summary = form.save(commit=False)
            try:
                # Extract text logic here
                if summary.document.name.endswith('.pdf'):
                    extracted_text = extract_text_from_pdf(summary.document)
                elif summary.document.name.endswith('.docx'):
                    extracted_text = extract_text_from_word(summary.document)
                else:
                    logger.error("Unsupported file type")
                    return JsonResponse({'success': False, 'errors': 'Unsupported file type'})

                # Split text into chunks if too large
                text_chunks = split_text_into_chunks(extracted_text)
                summary_text = ""

                # Generate summary for each chunk and concatenate
                for chunk in text_chunks:
                    logger.info(f"Generating summary for chunk: {chunk[:50]}...")
                    generated_summary = summarization_pipeline(chunk, max_length=150, min_length=40, do_sample=False)
                    summary_text += generated_summary[0]['summary_text'] + "\n"

                summary.summary = summary_text

                # Save the summary in a well-formatted PDF file
                pdf_file_name = f"summaries/{summary.title}_summary.pdf"
                buffer = BytesIO()
                doc = SimpleDocTemplate(buffer, pagesize=letter)
                styles = getSampleStyleSheet()

                # Custom style for summary
                summary_style = ParagraphStyle(
                    name="SummaryStyle",
                    parent=styles["BodyText"],
                    fontSize=12,
                    textColor=colors.darkblue,
                    spaceAfter=12,
                )

                elements = []
                elements.append(Paragraph(f"<b>Summary for:</b> {summary.title}", styles["Title"]))
                elements.append(Spacer(1, 12))

                for line in summary_text.split("\n"):
                    elements.append(Paragraph(line, summary_style))
                    elements.append(Spacer(1, 10))

                doc.build(elements)

                buffer.seek(0)
                summary.document.save(pdf_file_name, ContentFile(buffer.read()))
                buffer.close()

                summary.save()

                logger.info("Summary successfully generated and saved.")

                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'download_url': summary.document.url})
                return redirect('list_summaries')
            except Exception as e:
                logger.error(f"Error during summary creation: {e}")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'errors': str(e)})
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = SummaryForm()
    return render(request, 'summaries/create_summary.html', {'form': form})

# Read all summaries
def list_summaries(request):
    summaries = Summary.objects.all()
    return render(request, 'summaries/list_summaries.html', {'summaries': summaries})

# Update an existing summary
def update_summary(request, pk):
    summary = get_object_or_404(Summary, pk=pk)
    if request.method == 'POST':
        form = SummaryForm(request.POST, request.FILES, instance=summary)
        if form.is_valid():
            try:
                if 'document' in request.FILES:
                    # A new document has been uploaded, generate a new summary
                    if request.FILES['document'].name.endswith('.pdf'):
                        extracted_text = extract_text_from_pdf(request.FILES['document'])
                    elif request.FILES['document'].name.endswith('.docx'):
                        extracted_text = extract_text_from_word(request.FILES['document'])
                    else:
                        logger.error("Unsupported file type")
                        return JsonResponse({'success': False, 'errors': 'Unsupported file type'})

                    # Split text into chunks if too large
                    text_chunks = split_text_into_chunks(extracted_text)
                    summary_text = ""

                    # Show loading alert while summary is being generated
                    logger.info("Generating new summary, please wait...")

                    # Generate summary for each chunk and concatenate
                    for chunk in text_chunks:
                        logger.info(f"Generating summary for chunk: {chunk[:50]}...")
                        generated_summary = summarization_pipeline(chunk, max_length=150, min_length=40, do_sample=False)
                        summary_text += generated_summary[0]['summary_text'] + "\n"

                    summary.summary = summary_text

                    # Save the summary in a well-formatted PDF file
                    pdf_file_name = f"summaries/{summary.title}_summary.pdf"
                    buffer = BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=letter)
                    styles = getSampleStyleSheet()

                    # Custom style for summary
                    summary_style = ParagraphStyle(
                        name="SummaryStyle",
                        parent=styles["BodyText"],
                        fontSize=12,
                        textColor=colors.darkblue,
                        spaceAfter=12,
                    )

                    elements = []
                    elements.append(Paragraph(f"<b>Summary for:</b> {form.cleaned_data['title']}", styles["Title"]))
                    elements.append(Spacer(1, 12))

                    for line in summary_text.split("\n"):
                        elements.append(Paragraph(line, summary_style))
                        elements.append(Spacer(1, 10))

                    doc.build(elements)

                    buffer.seek(0)
                    summary.document.save(pdf_file_name, ContentFile(buffer.read()))
                    buffer.close()

                summary.title = form.cleaned_data['title']
                summary.save()
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': True, 'download_url': summary.document.url})
                return redirect('list_summaries')
            except Exception as e:
                logger.error(f"Error during summary update: {e}")
                if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                    return JsonResponse({'success': False, 'errors': str(e)})
        else:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
    else:
        form = SummaryForm(instance=summary)
    return render(request, 'summaries/update_summary.html', {'form': form, 'summary': summary})

# Delete a summary
@csrf_exempt
def delete_summary(request, pk):
    summary = get_object_or_404(Summary, pk=pk)
    if request.method == 'POST':
        summary.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'success': True})
        return redirect('list_summaries')
    return render(request, 'summaries/delete_summary.html', {'summary': summary})
