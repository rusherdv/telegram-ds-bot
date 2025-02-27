# Telegram-Discord Bot

Este bot integra Telegram y Discord para gestionar usuarios en canales de voz mediante comandos de texto y voz.

## Funcionalidades
- **Listado de Usuarios:** Muestra los usuarios conectados en canales de voz, omitiendo aquellos con IDs en la blacklist.
- **Comandos Flexibles:** Responde a frases como "quien esta en discord", "estan en ds", etc.
- **Desconexión de Usuarios:** Permite desconectar usuarios con comandos como "desconecta a", "desconectame a", "sacalo a" o "lo desconectas a" usando alias predefinidos.
- **Procesamiento de Audio:** Transcribe audios (OGG a WAV) para ejecutar los mismos comandos por voz.

## Requisitos
- Python 3.7+
- Librerías:  
  `pyTelegramBotAPI`, `discord.py`, `asyncio`, `SpeechRecognition`, `pydub`, `python-dotenv` (opcional)  
  *(Nota: `pydub` requiere `ffmpeg` instalado)*

## Configuración y Uso
1. **Configura el Código:**  
   - Reemplaza `DISCORD_TOKEN` y `TELEGRAM_TOKEN` con tus tokens.
   - Define `GUILD_IDS` con los IDs de los servidores de Discord.
   - Configura `BLACKLISTED_CHANNEL_IDS` con los IDs de los canales a omitir.
   - Asigna alias a los user IDs en `ALIAS_TO_USER`.

2. **Instala Dependencias:**  
   Ejecuta:
   ```   
   pip install pyTelegramBotAPI discord.py SpeechRecognition pydub python-dotenv
   python bot.py
   ```
## Uso
- **Listar Usuarios en Discord:** Envía mensajes como "quien esta en discord" o "estan en ds".
- **Desconectar Usuarios:** Envía comandos (texto o voz) como "desconecta a [alias]" o "sacalo a [alias]".
- **Comandos por Voz:** El bot transcribe el audio y ejecuta el comando correspondiente.

---

Desarrollado por [Rusher](https://www.rusher.net.ar/)
