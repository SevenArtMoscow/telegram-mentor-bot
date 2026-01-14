#!/bin/bash
# Скрипт для автоматической установки бота на сервер

set -e

echo "🚀 Начинаем установку Telegram бота..."

# Проверяем, что скрипт запущен от root
if [ "$EUID" -ne 0 ]; then 
    echo "❌ Пожалуйста, запустите скрипт от root (sudo ./deploy.sh)"
    exit 1
fi

# Установка зависимостей системы
echo "📦 Устанавливаем системные зависимости..."
if [ -f /etc/debian_version ]; then
    apt update
    apt install -y python3 python3-pip python3-venv git
elif [ -f /etc/redhat-release ]; then
    yum install -y python3 python3-pip git
else
    echo "❌ Неподдерживаемая ОС. Установите Python 3.10+ вручную."
    exit 1
fi

# Создание пользователя
echo "👤 Создаём пользователя botuser..."
if ! id "botuser" &>/dev/null; then
    adduser --disabled-password --gecos "" botuser
    echo "✅ Пользователь botuser создан"
else
    echo "ℹ️  Пользователь botuser уже существует"
fi

# Создание директории
echo "📁 Создаём директорию для бота..."
BOT_DIR="/home/botuser/telegram-bot"
mkdir -p $BOT_DIR
chown botuser:botuser $BOT_DIR

# Копирование файлов (если они есть в текущей директории)
echo "📋 Копируем файлы проекта..."
if [ -f "bot.py" ]; then
    cp bot.py requirements.txt $BOT_DIR/
    if [ -f "pytest.ini" ]; then
        cp pytest.ini $BOT_DIR/
    fi
    chown -R botuser:botuser $BOT_DIR
    echo "✅ Файлы скопированы"
else
    echo "⚠️  Файлы bot.py и requirements.txt не найдены в текущей директории"
    echo "   Пожалуйста, загрузите файлы проекта в $BOT_DIR"
fi

# Настройка виртуального окружения
echo "🐍 Настраиваем Python окружение..."
sudo -u botuser bash << EOF
cd $BOT_DIR
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
if [ -f requirements.txt ]; then
    pip install -r requirements.txt
fi
EOF

# Создание .env файла
echo "⚙️  Настраиваем .env файл..."
if [ ! -f "$BOT_DIR/.env" ]; then
    sudo -u botuser bash << EOF
cd $BOT_DIR
cat > .env << EOL
BOT_TOKEN=ваш_токен_бота_здесь
ADMIN_IDS=665509323,1478853053
CHAT_ID=ваш_chat_id_здесь
EOL
EOF
    echo "✅ Файл .env создан. Пожалуйста, отредактируйте его: nano $BOT_DIR/.env"
else
    echo "ℹ️  Файл .env уже существует"
fi

# Установка systemd service
echo "🔧 Настраиваем systemd service..."
SERVICE_FILE="/etc/systemd/system/telegram-bot.service"
if [ -f "telegram-bot.service" ]; then
    cp telegram-bot.service $SERVICE_FILE
else
    cat > $SERVICE_FILE << EOF
[Unit]
Description=Telegram Bot для сбора историй о наставниках
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=$BOT_DIR
Environment="PATH=$BOT_DIR/venv/bin"
ExecStart=$BOT_DIR/venv/bin/python $BOT_DIR/bot.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF
fi

systemctl daemon-reload
systemctl enable telegram-bot

echo ""
echo "✅ Установка завершена!"
echo ""
echo "📝 Следующие шаги:"
echo "1. Отредактируйте .env файл: nano $BOT_DIR/.env"
echo "2. Запустите бота: sudo systemctl start telegram-bot"
echo "3. Проверьте статус: sudo systemctl status telegram-bot"
echo "4. Просмотр логов: sudo journalctl -u telegram-bot -f"
echo ""
