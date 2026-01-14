# Инструкция по деплою бота на хостинг

## Варианты хостинга (до 300₽/мес)

### 1. **Timeweb VPS** (рекомендуется) - от 199₽/мес
- Минимум: 1 CPU, 512MB RAM, 10GB SSD
- Ссылка: https://timeweb.com/ru/services/vps
- Подходит для Telegram бота

### 2. **Beget VPS** - от 149₽/мес
- Минимум: 1 CPU, 512MB RAM, 10GB SSD
- Ссылка: https://beget.com/ru/vps
- Хорошая поддержка

### 3. **Selectel** - от 290₽/мес
- Минимум: 1 CPU, 512MB RAM, 10GB SSD
- Ссылка: https://selectel.ru/services/cloudservers/
- Надежный хостинг

### 4. **Railway** (бесплатно, с ограничениями)
- Бесплатный тариф: $5 кредитов/мес
- Ссылка: https://railway.app
- Подходит для тестирования

## Пошаговая инструкция деплоя

### Шаг 1: Подготовка сервера

1. **Подключитесь к серверу по SSH:**
```bash
ssh root@ваш_сервер_ip
```

2. **Обновите систему:**
```bash
# Для Ubuntu/Debian
apt update && apt upgrade -y

# Для CentOS/RHEL
yum update -y
```

3. **Установите Python 3.10+ и pip:**
```bash
# Ubuntu/Debian
apt install -y python3 python3-pip python3-venv git

# CentOS/RHEL
yum install -y python3 python3-pip git
```

### Шаг 2: Создание пользователя для бота

```bash
# Создаём пользователя
adduser --disabled-password --gecos "" botuser

# Переключаемся на пользователя
su - botuser
```

### Шаг 3: Загрузка проекта

```bash
# Создаём директорию для бота
mkdir -p ~/telegram-bot
cd ~/telegram-bot

# Клонируем проект (или загружаем файлы через scp/sftp)
# Если используете Git:
git clone https://github.com/ваш_username/ваш_репозиторий.git .

# Или загрузите файлы через scp с вашего компьютера:
# scp -r * botuser@ваш_сервер_ip:~/telegram-bot/
```

### Шаг 4: Настройка окружения

```bash
cd ~/telegram-bot

# Создаём виртуальное окружение
python3 -m venv venv

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем зависимости
pip install --upgrade pip
pip install -r requirements.txt
```

### Шаг 5: Создание .env файла

```bash
# Создаём .env файл
nano .env
```

Добавьте в файл:
```env
BOT_TOKEN=ваш_токен_бота
ADMIN_IDS=665509323,1478853053
CHAT_ID=ваш_chat_id
```

Сохраните (Ctrl+O, Enter, Ctrl+X)

### Шаг 6: Настройка systemd для автозапуска

```bash
# Выйдите из пользователя botuser
exit

# Создаём systemd service (от root)
sudo nano /etc/systemd/system/telegram-bot.service
```

Добавьте следующее содержимое:

```ini
[Unit]
Description=Telegram Bot для сбора историй о наставниках
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/home/botuser/telegram-bot
Environment="PATH=/home/botuser/telegram-bot/venv/bin"
ExecStart=/home/botuser/telegram-bot/venv/bin/python /home/botuser/telegram-bot/bot.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Сохраните файл.

### Шаг 7: Запуск бота

```bash
# Перезагружаем systemd
sudo systemctl daemon-reload

# Включаем автозапуск
sudo systemctl enable telegram-bot

# Запускаем бота
sudo systemctl start telegram-bot

# Проверяем статус
sudo systemctl status telegram-bot
```

### Шаг 8: Просмотр логов

```bash
# Просмотр логов в реальном времени
sudo journalctl -u telegram-bot -f

# Просмотр последних 100 строк
sudo journalctl -u telegram-bot -n 100
```

## Полезные команды

```bash
# Остановить бота
sudo systemctl stop telegram-bot

# Перезапустить бота
sudo systemctl restart telegram-bot

# Проверить статус
sudo systemctl status telegram-bot

# Отключить автозапуск
sudo systemctl disable telegram-bot
```

## Резервное копирование

Рекомендуется настроить автоматическое резервное копирование файлов `stories.json` и `stories.txt`:

```bash
# Создаём скрипт для бэкапа
nano /home/botuser/backup.sh
```

Добавьте:
```bash
#!/bin/bash
BACKUP_DIR="/home/botuser/backups"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR
cp /home/botuser/telegram-bot/stories.json $BACKUP_DIR/stories_$DATE.json
cp /home/botuser/telegram-bot/stories.txt $BACKUP_DIR/stories_$DATE.txt
# Удаляем старые бэкапы (старше 30 дней)
find $BACKUP_DIR -name "stories_*.json" -mtime +30 -delete
find $BACKUP_DIR -name "stories_*.txt" -mtime +30 -delete
```

Сделайте скрипт исполняемым:
```bash
chmod +x /home/botuser/backup.sh
```

Добавьте в crontab (ежедневно в 3:00):
```bash
crontab -e
# Добавьте строку:
0 3 * * * /home/botuser/backup.sh
```

## Обновление бота

```bash
# Остановите бота
sudo systemctl stop telegram-bot

# Обновите код (если используете Git)
cd ~/telegram-bot
git pull

# Или загрузите новые файлы через scp

# Обновите зависимости (если нужно)
source venv/bin/activate
pip install -r requirements.txt --upgrade

# Запустите бота снова
sudo systemctl start telegram-bot
```

## Решение проблем

### Бот не запускается
1. Проверьте логи: `sudo journalctl -u telegram-bot -n 50`
2. Проверьте .env файл: `cat /home/botuser/telegram-bot/.env`
3. Проверьте права доступа: `ls -la /home/botuser/telegram-bot/`

### Бот падает
1. Проверьте, что Python установлен: `python3 --version`
2. Проверьте зависимости: `pip list`
3. Проверьте токен бота в .env файле

### Файлы не сохраняются
1. Проверьте права на запись: `chmod 755 /home/botuser/telegram-bot`
2. Проверьте место на диске: `df -h`

## Безопасность

1. **Настройте firewall:**
```bash
# Разрешаем только SSH
sudo ufw allow 22/tcp
sudo ufw enable
```

2. **Отключите вход по паролю (используйте SSH ключи):**
```bash
sudo nano /etc/ssh/sshd_config
# Установите: PasswordAuthentication no
sudo systemctl restart sshd
```

3. **Регулярно обновляйте систему:**
```bash
sudo apt update && sudo apt upgrade -y
```

## Мониторинг

Для мониторинга использования ресурсов:
```bash
# Использование CPU и памяти
htop

# Использование диска
df -h

# Логи системы
journalctl -xe
```
