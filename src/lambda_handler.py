import json
from openai import OpenAI
import sys
from get_parameter import get_parameter

OPENAI_API_KEY=get_parameter('OPENAI_API_KEY')

client = OpenAI(api_key=OPENAI_API_KEY)

def send_message(prompt):
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def classify_text(text):
    prompt = f'''Você é um especialista em analisar se uma conversa teve o problema do usuário resolvido ou não, ou se o usuário abandonou a conversa, ou seja você classifica entre "resolved" e "unresolved" ou "abandoned, faça isso olhando para a conversa toda e seguindo as intruções abaixo.

    instruções:
      - APENAS CLASSIFIQUE ENTRE "resolved" e "unresolved" ou "abandoned", NADA A MAIS QUE ISSO
      - "abandoned" É QUANDO O USUÁRIO ABANDONA A CONVERSA.
      - NÃO EXPLIQUE O PORQUE OU COMO FEZ A TAREFA APENAS FAÇA.
      - SEU OUTPUT DEVE SER APENAS OU A TAG DE "resolvido" OU A TAG DE "não resolvido", NADA  MAIS.

      Conversa completa: {text}

      OUTPUT:
    '''
    return send_message(prompt)

def lambda_handler(event, context):
    input_text = event.get("conversation", "")
    
    if not input_text:
        return {
            'statusCode': 400,
            'body': {
                "error": "Entrada 'conversation' está vazia ou ausente."
            }
        }

    try:
        classification = classify_text(input_text)
        return {
            'statusCode': 200,
            'body': {
                'result': classification
            }
        }
    except Exception as e:
        return {
            'statusCode': 500,
            'body': {
                "error": f"Erro ao classificar: {str(e)}"
            }
        }
