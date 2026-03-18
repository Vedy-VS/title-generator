from flask import Flask, render_template, request, send_file
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import date
import os  # Импортируем для работы с именами файлов

app = Flask(__name__)

# --- Регистрация шрифтов Times New Roman ---
# Убедись, что файлы times.ttf и timesbd.ttf лежат в той же папке, что и app.py
pdfmetrics.registerFont(TTFont('TimesNewRoman', 'times.ttf'))  
pdfmetrics.registerFont(TTFont('TimesNewRomanBold', 'timesbd.ttf'))  


@app.route('/')
def index():
    # Flask автоматически ищет index.html в папке templates/
    return render_template('index.html')


@app.route('/generate', methods=['POST'])
def generate_pdf():
    """
    Принимает данные из формы, генерирует PDF и отправляет его пользователю.
    """
    data = request.form.to_dict()
    
    # --- Улучшение 1: Динамическое имя файла ---
    # Берем название проекта, убираем пробелы и спецсимволы, чтобы Windows не ругалась.
    project_title_safe = data.get("projectTitle", "title_sheet").replace(' ', '_').replace('/', '-')
    
    # Имя файла будет уникальным для каждого проекта.
    pdf_filename = f'title_sheet_{project_title_safe}.pdf'
    
    # Генерируем сам титульный лист
    generate_title_sheet(pdf_filename, data)
    
    # Отправляем файл пользователю. as_attachment=True заставляет браузер скачать файл.
    return send_file(pdf_filename, as_attachment=True)


def generate_title_sheet(filename, data):
    """
    Функция "рисует" титульный лист на PDF-странице.
    """
    w, h = A4 # Размеры листа А4
    c = canvas.Canvas(filename, pagesize=A4)

    # Константы полей (переводим миллиметры в пункты)
    LEFT_MARGIN = 3 * 28.3465  # 3 см
    RIGHT_MARGIN = 1.5 * 28.3465 # 1.5 см
    TOP_MARGIN = 2 * 28.3465     # 2 см
    BOTTOM_MARGIN = 2 * 28.3465  # 2 см

    # Вычисляем центр страницы с учетом полей
    center_x = (w - LEFT_MARGIN - RIGHT_MARGIN) / 2 + LEFT_MARGIN

    # --- Верхняя шапка (Министерство/Школа) ---
    c.setFont("TimesNewRoman", 14)
    c.drawCentredString(center_x, h - TOP_MARGIN - 14, "Департамент образования Администрации города Екатеринбурга")
    c.drawCentredString(center_x, h - TOP_MARGIN - 42, "Муниципальное автономное общеобразовательное учреждение лицей №100")

    # --- Основная информация о проекте (Название и Тип) ---
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import Paragraph
    from reportlab.lib.enums import TA_CENTER

    # Стиль для заголовка: жирный, по центру
    title_style = ParagraphStyle(
        name='TitleStyle',
        fontName='TimesNewRomanBold',
        fontSize=16,
        leading=24,
        alignment=TA_CENTER
    )
    
    project_title_paragraph = Paragraph(data["projectTitle"], title_style)
    width, height = project_title_paragraph.wrapOn(c, w - LEFT_MARGIN - RIGHT_MARGIN, None)
    
    # Рисуем заголовок по центру страницы (вертикально чуть выше середины)
    project_title_paragraph.drawOn(c, center_x - width/2, h/2 + 60 - height)

    # Тип проекта рисуем ниже заголовка
    c.setFont("TimesNewRoman", 14)
    type_position_y = h/2 + 60 - height - 25 # Отступ от заголовка
    c.drawCentredString(center_x, type_position_y, f"{data['projectType']} проект")


    # --- Левый столбец (Исполнитель, Класс и т.д.) ---
    left_column_x = 10.5 * 28.3465  # 10.5 см от левого края

    lines = [
        f"Исполнитель: {data['studentName']}",
        f"Учащийся: {data['classNumber']} класса",
        f"Руководитель: {data['supervisorName']}",
        f"Учитель {data['subjectTeacher'].lower()}"
    ]
    
    vertical_position_y = h/2 - 80 # Начинаем выводить блок ниже середины листа
    line_spacing = 25 # Расстояние между строками

    for line in lines:
        c.setFont("TimesNewRoman", 14)
        c.drawString(left_column_x, vertical_position_y, line)
        vertical_position_y -= line_spacing


    # --- Нижний колонтитул (Город и Год) ---
    bottom_text = f"Екатеринбург, {date.today().year}"
    c.setFont("TimesNewRoman", 14)
    c.drawCentredString(center_x, BOTTOM_MARGIN + 14, bottom_text)

    # Сохраняем страницу и закрываем холст
    c.showPage()
    c.save()


if __name__ == "__main__":
    app.run(debug=True)