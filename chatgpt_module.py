import logging
import os
import json
import time

from PyPDF2 import PdfReader
from openai import OpenAI

def process_resume(file_path, logger):

    # Чтение PDF файла

    text = read_pdf(file_path)

    prompt = build_prompt(text)
    # запишем в логи время процессинга ответа от чатгпт
    logger.info(f"Start processing resume: {file_path}")
    start_time = time.time()
    # Необходимо заменить на свой API ключ
    # берем ключ из переменной окружения
    key = os.environ.get('OPENAI_API_KEY')
    if key is None:
        logger.info("OPENAI_API_KEY is not set")
        return ""
    else:
        logger.info(f"OPENAI_API_KEY is set to: {key}")

    client = OpenAI(api_key=key)

    result = request_chatgpt(client, prompt)

    end_time = time.time()
    logger.info(f"End processing resume: {file_path}. Time: {end_time - start_time:.3f} seconds")

    return result


def request_chatgpt(client, prompt):
    # Отправка запроса к OpenAI API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system",
             "content": "Ты - ассистент по анализу резюме. Твоя задача - извлечь ключевую информацию из предоставленного резюме и структурировать ее в формате JSON."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.2,  # Низкая температура для более детерминированных ответов
        max_tokens=1000  # Максимальное количество токенов в ответе
    )
    # Извлечение JSON из ответа
    result = json.loads(response.choices[0].message.content)
    return result


def build_prompt(text):
    # Подготовка промпта
    prompt = f"""Проанализируй следующее резюме и извлеки ключевую информацию в формате JSON:

{text}

Верни только JSON-объект следующей структуры без дополнительных комментариев:

{{
  "name": "Имя кандидата",
  "position": "Должность",
  "skills": [
    {{
      "category": "Категория навыка",
      "items": ["Навык 1", "Навык 2", "Навык 3"]
    }}
  ],
  "experience": [
    {{
      "company": "Название компании",
      "position": "Должность",
      "duration": "Продолжительность работы"
    }}
  ],
  "education": {{
    "degree": "Степень или уровень образования",
    "institution": "Учебное заведение"
  }}
}}
"""
    return prompt


def read_pdf(file_path):
    # Чтение PDF файла
    with open(file_path, 'rb') as file:
        pdf_reader = PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
    return text
