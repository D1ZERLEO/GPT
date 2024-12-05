# Asynchronous Example
from asyncio import sleep
from mistralai import Mistral, models
import os

from config import AI_TOKEN
#from app.user import model_name
async def generate(content):
    delay = 1
    retries = 10
    for i in range(retries):
        try:
            s = Mistral(
                api_key=AI_TOKEN,
            )
            res = await s.chat.complete_async(model="mistral-small-latest", messages=[
                {
                    "content": content,
                    "role": "user",
                },
            ])
            if res is not None:
                # handle response
                return res
        except Exception as e:
            if "429" in str(e):
                await sleep(delay)
                delay+=1
