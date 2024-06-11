from django.shortcuts import render
from django.http import HttpResponse
import google.generativeai as genai
from odf.opendocument import OpenDocumentText
from odf.text import P, H, Span
from odf.style import Style, TextProperties, ParagraphProperties

API_KEY = 'AIzaSyAXdYyD8lTKYf5O45S_cE8w0Uab4imLN2E'
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel('gemini-1.5-flash-latest')

def index(request):
    return render(request, 'generar-examen.html')

def generar_examen(request):
    if request.method == 'POST':
        materia = request.POST.get('materia')
        dificultad = request.POST.get('dificultad')
        tipo_pregunta = request.POST.get('tipo-pregunta')
        idioma_pregunta = request.POST.get('idioma-pregunta')
        numero_preguntas = request.POST.get('numeroPreguntas')
        instrucciones_extra = request.POST.get('instruccionesExtra')

        # Validar que todos los campos están llenos
        if not (materia and dificultad and tipo_pregunta and idioma_pregunta and numero_preguntas):
            return render(request, 'generar-examen.html', {'error': 'Todos los campos son obligatorios'})

        # Construir la consulta detallada
        consulta = (f"Como experto en diseño de evaluaciones, redacte un conjunto de preguntas y problemas con dificultad {dificultad} "
                    f"que abarquen los conceptos clave aprendidos en el tema de {materia}. El examen debe constar de {numero_preguntas} preguntas en total. "
                    f"Las preguntas deben ser del tipo {tipo_pregunta} y en el idioma {idioma_pregunta}.")
        
        if instrucciones_extra:
            consulta += f" Además, {instrucciones_extra}."

        consulta += " Asegúrese de que las preguntas evalúen tanto la comprensión básica como la capacidad de aplicar los conocimientos de manera creativa y analítica. Ademas de incluir un Answer Sheet al final."

        # Generar contenido con Gemini
        response = model.generate_content(consulta)
        respuesta_chat = response.text

        return render(request, 'generar-examen.html', {'respuesta_chat': respuesta_chat})
        
    return render(request, 'generar-examen.html')

def export_to_odf(request):
    if request.method == 'POST':
        response_text = request.POST.get('respuesta_chat', '')

        # Crear un documento ODF
        doc = OpenDocumentText()

        # Crear estilos
        h1_style = Style(name="Heading 1", family="paragraph")
        h1_style.addElement(TextProperties(attributes={"fontsize": "24pt", "fontweight": "bold"}))
        h2_style = Style(name="Heading 2", family="paragraph")
        h2_style.addElement(TextProperties(attributes={"fontsize": "18pt", "fontweight": "bold"}))
        doc.styles.addElement(h1_style)
        doc.styles.addElement(h2_style)

        # Dividir el texto por líneas y procesar cada línea
        lines = response_text.splitlines()
        answer_key_lines = []
        is_answer_key = False

        for i, line in enumerate(lines):
            if "answer key" in line.lower():
                is_answer_key = True
                answer_key_lines.append(line)
                continue

            if is_answer_key:
                answer_key_lines.append(line)
                continue

            if i == 0:
                # Primera línea como Heading 1 en negrita
                h1 = H(outlinelevel=1, stylename=h1_style, text=line)
                doc.text.addElement(h1)
            elif line.startswith("**") and line.endswith("**"):
                # Líneas con doble asterisco como Heading 2 en negrita
                h2 = H(outlinelevel=2, stylename=h2_style, text=line.strip("**"))
                doc.text.addElement(h2)
            else:
                # Otras líneas como párrafos normales
                p = P(text=line)
                doc.text.addElement(p)

        # Crear una nueva hoja para la Answer Key si existe
        if answer_key_lines:
            answer_key_doc = OpenDocumentText()

            for line in answer_key_lines:
                p = P(text=line)
                answer_key_doc.text.addElement(p)

            # Añadir la hoja de Answer Key al documento principal
            doc.text.addElement(P(text=" "))
            doc.text.addElement(P(text="Answer Key", stylename=h1_style))
            for elem in answer_key_doc.text.childNodes:
                doc.text.addElement(elem)

        # Guardar el documento en una variable de respuesta HTTP
        response = HttpResponse(content_type='application/vnd.oasis.opendocument.text')
        response['Content-Disposition'] = 'attachment; filename="respuesta.odt"'

        doc.save(response)

        return response

    return HttpResponse(status=400)