import os
import telebot
import discord
import asyncio
import speech_recognition as sr
from pydub import AudioSegment
from pydub.utils import make_chunks
from dotenv import load_dotenv
from io import BytesIO

# Configuraciones
DISCORD_TOKEN = ""
TELEGRAM_TOKEN = ""
GUILD_IDS = []

BLACKLISTED_CHANNELS = []

ALIAS_TO_USER = {}

DISCONNECT_COMMANDS = ["desconecta a", "desconecta", "saca a", "sacalo a", "sacame a", "desconectame a", "sacalo a", "lo desconectas a", "desconectarlo", "me desconectas a"]

DISCORD_STATUS_TRIGGERS = [
    "quien esta en discord",
    "hay alguien en discord",
    "hay gente en discord",
    "hay gente",
    "estan en ds",
    "ds"
]

bot = telebot.TeleBot(TELEGRAM_TOKEN)

intents = discord.Intents.default()
intents.voice_states = True
intents.guilds = True
intents.members = True
client = discord.Client(intents=intents)

async def get_voice_channel_users():
    message = "🌐 Usuarios en Discord:\n"
    for guild_id in GUILD_IDS:
        guild = client.get_guild(guild_id)
        if not guild:
            continue

        for channel in guild.voice_channels:
            # Omitir canales que estén en la blacklist
            if channel.id in BLACKLISTED_CHANNELS:
                continue
            members = channel.members
            if members:
                message += f"🔹 {channel.name}: {', '.join([member.name for member in members])}\n"
            else:
                message += f"🔹 {channel.name}: vacío\n"
    return message if message != "🌐 Usuarios en Discord:\n" else "No encontré información."

async def disconnect_user(user_id):
    for guild in client.guilds:
        for channel in guild.voice_channels:
            for member in channel.members:
                if member.id == int(user_id):
                    try:
                        # Mueve al miembro a "None" para desconectarlo del canal de voz
                        await member.move_to(None)
                        return f"Desconectado {member.name} de {channel.name}."
                    except Exception as e:
                        return f"Error al desconectar: {str(e)}"
    return "No se encontró al usuario en un canal de voz."

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "¡Hola! Envíame un audio o un mensaje de texto con tu consulta.")

@bot.message_handler(func=lambda message: True)
def handle_text(message):
    text_lower = message.text.lower().strip()

    # Primero, detectar el comando de desconexión (por ejemplo, "desconecta a Tino")
    for command in DISCONNECT_COMMANDS:
        if text_lower.startswith(command):
            alias = text_lower.replace(command, "").strip()
            if alias in ALIAS_TO_USER:
                user_id = ALIAS_TO_USER[alias]
                # Enviar la tarea al event loop del cliente Discord
                future = asyncio.run_coroutine_threadsafe(disconnect_user(user_id), client.loop)
                try:
                    # Esperamos un resultado con un timeout (por ejemplo, 10 segundos)
                    result = future.result(timeout=10)
                except Exception as e:
                    result = f"Error al desconectar: {str(e)}"
                bot.reply_to(message, result)
            else:
                bot.reply_to(message, "No se encontró el usuario para desconectar.")
            return

    # Verificar si el mensaje contiene alguno de los triggers para estado de Discord
    if any(trigger in text_lower for trigger in DISCORD_STATUS_TRIGGERS):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        discord_info = loop.run_until_complete(get_voice_channel_users())
        bot.reply_to(message, discord_info)
    else:
        # Respuesta fija para otros mensajes
        fixed_response = f"Esta es una respuesta fija a tu mensaje: {message.text}"
        bot.reply_to(message, fixed_response)

@bot.message_handler(content_types=['voice'])
def handle_audio(message):
    file_info = bot.get_file(message.voice.file_id)
    file = bot.download_file(file_info.file_path)

    # Convertir audio a formato WAV
    audio = AudioSegment.from_file(BytesIO(file), format="ogg")
    audio.export("audio.wav", format="wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile("audio.wav") as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language="es-ES")
            bot.send_message(message.chat.id, f"🔊 Texto detectado: {text}")
            text_lower = text.lower().strip()

            # Comando para desconectar (por audio) usando múltiples variantes
            for command in DISCONNECT_COMMANDS:
                if text_lower.startswith(command):
                    alias = text_lower.replace(command, "").strip()
                    if alias in ALIAS_TO_USER:
                        user_id = ALIAS_TO_USER[alias]
                        future = asyncio.run_coroutine_threadsafe(disconnect_user(user_id), client.loop)
                        try:
                            result = future.result(timeout=10)
                        except Exception as e:
                            result = f"Error al desconectar: {str(e)}"
                        bot.send_message(message.chat.id, result)
                    else:
                        bot.send_message(message.chat.id, "No se encontró el usuario para desconectar.")
                    return

            # Verificar comando de estado de Discord
            if any(trigger in text_lower for trigger in DISCORD_STATUS_TRIGGERS):
                future = asyncio.run_coroutine_threadsafe(get_voice_channel_users(), client.loop)
                try:
                    discord_info = future.result(timeout=10)
                except Exception as e:
                    discord_info = f"Error: {str(e)}"
                bot.send_message(message.chat.id, discord_info)
            else:
                fixed_analysis = f"Esta es una respuesta fija a tu consulta: {text}"
                bot.send_message(message.chat.id, fixed_analysis)

        except sr.UnknownValueError:
            bot.send_message(message.chat.id, "No entendí el audio.")
        except sr.RequestError:
            bot.send_message(message.chat.id, "Error al procesar el audio.")

    file_info = bot.get_file(message.voice.file_id)
    file = bot.download_file(file_info.file_path)

    # Convertir audio a formato WAV
    audio = AudioSegment.from_file(BytesIO(file), format="ogg")
    audio.export("audio.wav", format="wav")

    recognizer = sr.Recognizer()
    with sr.AudioFile("audio.wav") as source:
        audio_data = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio_data, language="es-ES")
            bot.send_message(message.chat.id, f"🔊 Texto detectado: {text}")
            text_lower = text.lower().strip()

            # Comando para desconectar (por audio)
            if text_lower.startswith("desconecta a"):
                alias = text_lower.replace("desconecta a", "").strip()
                if alias in ALIAS_TO_USER:
                    user_id = ALIAS_TO_USER[alias]
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    result = loop.run_until_complete(disconnect_user(user_id))
                    bot.send_message(message.chat.id, result)
                else:
                    bot.send_message(message.chat.id, "No se encontró el usuario para desconectar.")
                return

            # Verificar comando de estado de Discord
            if any(trigger in text_lower for trigger in DISCORD_STATUS_TRIGGERS):
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                discord_info = loop.run_until_complete(get_voice_channel_users())
                bot.send_message(message.chat.id, discord_info)
            else:
                fixed_analysis = f"Esta es una respuesta fija a tu consulta: {text}"
                bot.send_message(message.chat.id, fixed_analysis)

        except sr.UnknownValueError:
            bot.send_message(message.chat.id, "No entendí el audio.")
        except sr.RequestError:
            bot.send_message(message.chat.id, "Error al procesar el audio.")

if __name__ == "__main__":
    from threading import Thread
    Thread(target=lambda: bot.polling()).start()
    client.run(DISCORD_TOKEN)