from pyrogram import Client, filters
from config import API_ID, API_HASH # Данные юзера, что можно получить на https://my.telegram.org/
from fusion_brain_manager import create_image

app = Client("my_account", api_id=API_ID, api_hash=API_HASH)

@app.on_message(filters.text)
async def answer(client, message):
    if message.text.startswith("/generate"):
        if message.text != "/generate":
            await message.reply("Генерирую...")
            await app.send_photo(message.chat.id, photo=await create_image(message.chat.id, message.text.replace('/generate', '')))
        else:
            await message.reply("Отправьте описание изображения")

app.run()