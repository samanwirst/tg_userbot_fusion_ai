import json
import asyncio
import aiohttp
import base64
from config import FUSION_BRAIN_API_KEY, FUSION_BRAIN_SECRET_KEY
import random

class Text2ImageAPI:

    def __init__(self, url, api_key, secret_key):
        self.URL = url
        self.AUTH_HEADERS = {
            'X-Key': f'Key {api_key}',
            'X-Secret': f'Secret {secret_key}',
        }

    async def get_model(self):
        async with aiohttp.ClientSession(headers=self.AUTH_HEADERS) as session:
            async with session.get(self.URL + 'key/api/v1/models') as response:
                response.raise_for_status()
                data = await response.json()
                return data[0]['id']

    async def generate(self, prompt, model, images=1, width=1024, height=1024):
        params = json.dumps({
            "type": "GENERATE",
            "generateParams": {
                "query": f"{prompt}"
            },
            "width": width,
            "height": height,
            "num_images": images
        })
        form_data = aiohttp.FormData()
        form_data.add_field('params', params, content_type='application/json')
        form_data.add_field('model_id', str(model))  # Преобразуем model_id в строку


        async with aiohttp.ClientSession(headers=self.AUTH_HEADERS) as session:
            async with session.post(self.URL + 'key/api/v1/text2image/run', data=form_data) as response:
                response.raise_for_status()
                data = await response.json()
                return data['uuid']

    async def check_generation(self, request_id, attempts=10, delay=10):
        async with aiohttp.ClientSession(headers=self.AUTH_HEADERS) as session:
            while attempts > 0:
                async with session.get(self.URL + f'key/api/v1/text2image/status/{request_id}') as response:
                    response.raise_for_status()
                    data = await response.json()
                    if data['status'] == 'DONE':
                        return data['images']

                attempts -= 1
                await asyncio.sleep(delay)
        raise TimeoutError("Image generation did not complete in the allowed time")

async def create_image(chat_id, prompt):
    api = Text2ImageAPI('https://api-key.fusionbrain.ai/', FUSION_BRAIN_API_KEY, FUSION_BRAIN_SECRET_KEY)
    model_id = await api.get_model()
    uuid = await api.generate(prompt, model_id)
    images = await api.check_generation(uuid)
    image_data = base64.b64decode(images[0])
    file_path = f'generated_images/{chat_id}_image_{"".join([str(random.randint(0, 9)) for _ in range(16)])}.png'
    with open(file_path, "wb") as file:
        file.write(image_data)
    return file_path
