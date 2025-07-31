import json
from openai import OpenAI
import sys
from get_parameter import get_parameter
import os
from pydantic import BaseModel
from typing import Literal

class ConversationResolutionResponse(BaseModel):
    conversation_resolution: Literal["resolved", "unresolved"]

def send_message(prompt, model):
    OPENAI_API_KEY=get_parameter('OPENAI_API_KEY')
    client = OpenAI(api_key=OPENAI_API_KEY)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def send_message_parse(prompt, model):
    completion = client.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Você é um classificador especializado em analisar conversas."
            },
            {
                "role": "user", 
                "content": prompt
            }
        ],
        # temperature=temperature,
        # max_tokens=500,
        response_format=ConversationResolutionResponse
    )
    
    # Extrai o conteúdo da resposta
    response = completion.choices[0].message.parsed
    
    # Converte o objeto Pydantic para dicionário
    response_dict = response.model_dump() if hasattr(response, 'model_dump') else response.__dict__

    return response_dict

def classify_text(text, model):
    prompt = f'''Você é um especialista em analisar se uma conversa teve o problema do usuário resolvido ou não, ou se o usuário abandonou a conversa, ou seja você classifica entre "resolved" e "unresolved", faça isso olhando para a conversa toda e seguindo as intruções abaixo.

    instruções:
      - APENAS CLASSIFIQUE ENTRE "resolved" e "unresolved", NADA A MAIS QUE ISSO
      - "unresolved" É QUANDO O chatbot confirma que não vai conseguir resolver a situação do cliente ou que o usuário NÃO CONTINUOU A CONVERSA e saiu SEM RESOLVER O PROBLEMA.
      - "resolved" É QUANDO O CHATBOT RESOLVE TODOS OS  PROBLEMAS.
      - NÃO EXPLIQUE O PORQUE OU COMO FEZ A TAREFA APENAS FAÇA.
      - SEU OUTPUT DEVE SER APENAS OU A TAG DE "resolved" OU A TAG DE "unresolved", NADA  MAIS.

      Conversa completa: {text}


      OUTPUT:
    '''

    print(f"Prompt: {prompt}")

    return send_message_parse(prompt, model)

def format_conversation_messages(conversation_dict):
    messages = conversation_dict.get("messages", [])
    formatted = "\n".join(f'{m["sender"]}: {m["content"]}' for m in messages)
    return formatted

def lambda_handler(event, context):
    conversation_data = event.get("conversation", "")
    model = event.get("model", "gpt-4.1-nano")

    if not conversation_data:
        return {
            'statusCode': 400,
            'body': {
                "error": "Entrada 'conversation' está vazia ou ausente."
            }
        }

    try:
        # Se for dicionário estruturado com messages
        if isinstance(conversation_data, dict) and "messages" in conversation_data:
            input_text = format_conversation_messages(conversation_data)
        else:
            # Se já vier como string simples (modo legado)
            input_text = conversation_data

        response = classify_text(input_text, model)
        classification = response.get("conversation_resolution", "")
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
