import os
import json
from datetime import datetime
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

# Загружаем переменные из .env файла
load_dotenv(dotenv_path='.env')

# Конфигурация
BOT_TOKEN = os.getenv('BOT_TOKEN', 'YOUR_BOT_TOKEN_HERE')
STORIES_FILE = 'stories.json'
STORIES_TEXT_FILE = 'stories.txt'  # Читаемый текстовый файл
# ID админов (через запятую, например: "123456789,987654321")
ADMIN_IDS = [int(id.strip()) for id in os.getenv('ADMIN_IDS', '').split(',') if id.strip()]
# ID чата/канала для автоматической отправки историй (опционально)
CHAT_ID = os.getenv('CHAT_ID', '')

# Приветственное сообщение
WELCOME_MESSAGE = """Привет! 👋🏻

В этом боте ты можешь рассказать о преподавателе нашего университета, которого считаешь своим наставником, и поделиться, почему именно он (она) сыграл(а) важную роль в твоей жизни.

Лучшие истории мы опубликуем в группе СтудСовета ко Дню международного наставничества 💙

Не забудь вместе с историей указать своё ФИО и номер группы 📝"""

def load_stories():
    """Загружает истории из файла"""
    if os.path.exists(STORIES_FILE):
        with open(STORIES_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return []

def save_story(user_id, username, text):
    """Сохраняет историю студента"""
    stories = load_stories()
    story = {
        'user_id': user_id,
        'username': username,
        'text': text,
        'timestamp': datetime.now().isoformat()
    }
    stories.append(story)
    
    # Сохраняем в JSON
    with open(STORIES_FILE, 'w', encoding='utf-8') as f:
        json.dump(stories, f, ensure_ascii=False, indent=2)
    
    # Сохраняем в читаемый текстовый файл
    save_stories_to_text(stories)
    
    return story

def save_stories_to_text(stories):
    """Сохраняет все истории в читаемый текстовый файл"""
    with open(STORIES_TEXT_FILE, 'w', encoding='utf-8') as f:
        f.write("=" * 80 + "\n")
        f.write("ИСТОРИИ О НАСТАВНИКАХ\n")
        f.write("=" * 80 + "\n\n")
        f.write(f"Всего историй: {len(stories)}\n")
        f.write(f"Дата создания отчёта: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n\n")
        f.write("=" * 80 + "\n\n")
        
        for i, story in enumerate(stories, 1):
            username = story.get('username', 'Неизвестно')
            text = story.get('text', '')
            timestamp = story.get('timestamp', '')
            
            try:
                dt = datetime.fromisoformat(timestamp)
                date_str = dt.strftime('%d.%m.%Y %H:%M')
            except:
                date_str = timestamp
            
            f.write(f"ИСТОРИЯ #{i}\n")
            f.write("-" * 80 + "\n")
            f.write(f"Автор: {username}\n")
            f.write(f"Дата: {date_str}\n")
            f.write("-" * 80 + "\n")
            f.write(f"{text}\n")
            f.write("\n" + "=" * 80 + "\n\n")

async def forward_story_to_chat(application, message):
    """Пересылает сообщение в чат/канал"""
    if not CHAT_ID:
        print("[WARN] CHAT_ID не указан, пересылка пропущена")
        return
    
    try:
        chat_id = int(CHAT_ID)
        print(f"[INFO] Пересылаю сообщение в чат {chat_id}")
        # Пересылаем оригинальное сообщение
        await application.bot.forward_message(
            chat_id=chat_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id
        )
        print(f"[OK] Сообщение успешно переслано")
    except Exception as e:
        # Игнорируем ошибки пересылки, чтобы не прерывать работу бота
        error_type = type(e).__name__
        if error_type == 'BadRequest':
            print(f"[WARN] Не удалось переслать сообщение (возможно, сообщение недоступно): {e}")
        else:
            print(f"[ERROR] Не удалось переслать в чат {CHAT_ID}: {e}")
            print(f"[ERROR] Тип ошибки: {error_type}")
        # Не прерываем выполнение - бот продолжает работать

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    await update.message.reply_text(WELCOME_MESSAGE)

async def export(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Команда для экспорта всех историй (только для админов)"""
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ У вас нет доступа к этой команде.")
        return
    
    stories = load_stories()
    
    if not stories:
        await update.message.reply_text("📭 Пока нет сохранённых историй.")
        return
    
    # Формируем сообщение с историями
    message = f"📊 Всего историй: {len(stories)}\n\n"
    
    for i, story in enumerate(stories, 1):
        timestamp = story.get('timestamp', 'Неизвестно')
        try:
            dt = datetime.fromisoformat(timestamp)
            date_str = dt.strftime('%d.%m.%Y %H:%M')
        except:
            date_str = timestamp
        
        username = story.get('username', 'Unknown')
        text = story.get('text', '')
        
        message += f"━━━━━━━━━━━━━━━━━━━━\n"
        message += f"#{i} | {date_str}\n"
        message += f"👤 {username}\n\n"
        message += f"{text}\n\n"
        
        # Telegram ограничение на длину сообщения (4096 символов)
        if len(message) > 3500:
            await update.message.reply_text(message)
            message = ""
    
    if message:
        await update.message.reply_text(message)
    
    # Отправляем текстовый файл (читаемый)
    if os.path.exists(STORIES_TEXT_FILE):
        with open(STORIES_TEXT_FILE, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename='stories.txt',
                caption="📄 Текстовый файл со всеми историями (читаемый формат)"
            )
    
    # Также отправляем JSON файл
    if os.path.exists(STORIES_FILE):
        with open(STORIES_FILE, 'rb') as f:
            await update.message.reply_document(
                document=f,
                filename='stories.json',
                caption="📄 JSON файл со всеми историями (для программной обработки)"
            )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Статистика по историям (только для админов)"""
    user = update.effective_user
    
    if user.id not in ADMIN_IDS:
        await update.message.reply_text("❌ У вас нет доступа к этой команде.")
        return
    
    stories = load_stories()
    
    message = f"📈 Статистика:\n\n"
    message += f"Всего историй: {len(stories)}\n"
    
    if stories:
        # Последняя история
        last = stories[-1]
        try:
            dt = datetime.fromisoformat(last.get('timestamp', ''))
            message += f"Последняя: {dt.strftime('%d.%m.%Y %H:%M')}\n"
        except:
            pass
    
    await update.message.reply_text(message)

async def chatid(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Показывает ID текущего чата"""
    chat = update.effective_chat
    
    message = f"📋 Информация о чате:\n\n"
    message += f"Chat ID: `{chat.id}`\n"
    message += f"Тип: {chat.type}\n"
    
    if chat.title:
        message += f"Название: {chat.title}\n"
    
    message += f"\n💡 Скопируйте Chat ID и добавьте в .env файл:\n"
    message += f"`CHAT_ID={chat.id}`"
    
    await update.message.reply_text(message, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user = update.effective_user
    text = update.message.text
    chat = update.effective_chat
    
    # Обрабатываем ТОЛЬКО сообщения из личного чата с ботом
    if chat.type != 'private':
        return
    
    # Игнорируем команды
    if text.startswith('/'):
        return
    
    # Сохраняем историю
    story = save_story(
        user_id=user.id,
        username=user.username or user.first_name or 'Unknown',
        text=text
    )
    
    # Пересылаем в чат, если указан CHAT_ID
    if CHAT_ID:
        print(f"[DEBUG] CHAT_ID найден: {CHAT_ID}, пересылаю сообщение...")
        await forward_story_to_chat(context.application, update.message)
    else:
        print(f"[WARN] CHAT_ID не указан в конфигурации")
    
    # Отвечаем пользователю
    await update.message.reply_text(
        "Спасибо! Ваша история сохранена. Вы можете написать ещё, если хотите добавить что-то."
    )

def main():
    """Запуск бота"""
    if BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
        print("[!] Установите BOT_TOKEN в переменную окружения или в коде!")
        return
    
    # Проверяем конфигурацию
    print(f"[INFO] BOT_TOKEN загружен: {'Да' if BOT_TOKEN else 'Нет'}")
    print(f"[INFO] ADMIN_IDS: {ADMIN_IDS if ADMIN_IDS else 'Не указаны'}")
    print(f"[INFO] CHAT_ID: {CHAT_ID if CHAT_ID else 'Не указан (пересылка отключена)'}")
    
    # Обновляем текстовый файл, если истории уже есть
    stories = load_stories()
    if stories:
        save_stories_to_text(stories)
        print(f"[INFO] Загружено историй: {len(stories)}")
        print(f"[INFO] Текстовый файл обновлён: {STORIES_TEXT_FILE}")
    
    # Создаём приложение
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Регистрируем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("export", export))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("chatid", chatid))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Запускаем бота
    print("[OK] Бот запущен...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
