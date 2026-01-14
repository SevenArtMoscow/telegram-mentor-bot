#!/bin/bash
# Скрипт для резервного копирования историй

BOT_DIR="/home/botuser/telegram-bot"
BACKUP_DIR="/home/botuser/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Создаём директорию для бэкапов
mkdir -p $BACKUP_DIR

# Копируем файлы
if [ -f "$BOT_DIR/stories.json" ]; then
    cp "$BOT_DIR/stories.json" "$BACKUP_DIR/stories_$DATE.json"
    echo "✅ Скопирован stories.json"
fi

if [ -f "$BOT_DIR/stories.txt" ]; then
    cp "$BOT_DIR/stories.txt" "$BACKUP_DIR/stories_$DATE.txt"
    echo "✅ Скопирован stories.txt"
fi

# Удаляем старые бэкапы (старше 30 дней)
find $BACKUP_DIR -name "stories_*.json" -mtime +30 -delete
find $BACKUP_DIR -name "stories_*.txt" -mtime +30 -delete

echo "✅ Резервное копирование завершено: $DATE"
