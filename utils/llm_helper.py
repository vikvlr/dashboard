import os 
from openai import OpenAI 
from dotenv import load_dotenv 
 
load_dotenv() 
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY")) 
 
def get_llm_comment(prompt): 
    try: 
        response = client.chat.completions.create( 
            model="gpt-3.5-turbo", 
            messages=[{"role": "user", "content": prompt}] 
        ) 
        return response.choices[0].message.content 
    except: 
        return "Ошибка: LLM недоступна" 
