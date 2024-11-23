# service/openai_service.py

import requests
import json
from config import YOUR_OPENAI_API_KEY, YOUR_OPENAI_ENDPOINT
from openai import AzureOpenAI

api_key = YOUR_OPENAI_API_KEY
endpoint = YOUR_OPENAI_ENDPOINT
client = AzureOpenAI(api_key=api_key, api_version="2024-02-15-preview", azure_endpoint=endpoint)

def generate_response_text(prompt):
    # Generate text using the assistant
    response = client.chat.completions.create(
        model="gpt-35-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that generates job descriptions based on parameters."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

def call_openai_api(prompt):
    try:
        # Call the OpenAI API to get the similarity score
        response = client.chat.completions.create(
            model="gpt-35-turbo",
            messages=[
                {"role": "system", "content": "You are an AI assistant that evaluates resumes based on job descriptions. Only provide a numeric similarity score out of 100, without additional remarks."},
                {"role": "user", "content": prompt}
            ]
        )

        res = response.choices[0].message.content
        res = res.strip()  # Clean any surrounding whitespace
        print(f"Raw response from OpenAI: '{res}'")  # Debug output
        return res

    except Exception as e:
        print(f"Error calling OpenAI API: {str(e)}")
        raise
