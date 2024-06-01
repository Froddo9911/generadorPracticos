from django.shortcuts import render
from django.http import HttpResponse
import google.generativeai as genai


API_KEY = 'AIzaSyAXdYyD8lTKYf5O45S_cE8w0Uab4imLN2E'
genai.configure(api_key=API_KEY)

model = genai.GenerativeModel('gemini-1.5-flash-latest')

def index(request):
    return render(request, 'generar-examen.html')

def generar_examen(request):
    if request.method == 'POST':
        materia = request.POST.get('materia')
        dificultad = request.POST.get('dificultad')
        numero_preguntas = request.POST.get('numeroPreguntas')

        response = model.generate_content(f"Como experto en diseño de evaluaciones, redacte un conjunto de preguntas y problemas con dificultad de nivel {dificultad}. Que abarquen los conceptos clave aprendidos en el tema de {materia}. El examen debe constar de {numero_preguntas} preguntas en total. Asegúrese de que las preguntas evalúen tanto la comprensión básica como la capacidad de aplicar los conocimientos de manera creativa y analítica.")

        respuesta_chat = response.text

        return render(request, 'generar-examen.html', {'respuesta_chat': respuesta_chat})

    return render(request, 'generar-examen.html')