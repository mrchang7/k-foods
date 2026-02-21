import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
genai.configure(api_key=os.environ['GEMINI_API_KEY'])

model = genai.GenerativeModel('gemini-3-flash-preview')

try:
    response = model.generate_content("여기 있는 유튜브 영상 링크(https://www.youtube.com/watch?v=qtFCqtifaaQ)의 레시피를 요약해 줘.")
    print("Response:", response.text)
except Exception as e:
    print("Error:", e)
