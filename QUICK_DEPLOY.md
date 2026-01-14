# 🚀 Быстрый деплой бота (5 минут)

## Вариант 1: VPS (рекомендуется, ~200₽/мес)

### Шаг 1: Купите VPS
- **Timeweb**: https://timeweb.com/ru/services/vps (от 199₽/мес)
- **Beget**: https://beget.com/ru/vps (от 149₽/мес)

### Шаг 2: Подключитесь к серверу
```bash
ssh root@ваш_сервер_ip
```

### Шаг 3: Запустите скрипт установки
```bash
# Загрузите файлы проекта на сервер (через scp или git)
# Затем запустите:
chmod +x deploy.sh
sudo ./deploy.sh
```

### Шаг 4: Настройте .env
```bash
nano /home/botuser/telegram-bot/.env
# Добавьте ваш BOT_TOKEN, ADMIN_IDS, CHAT_ID
```

### Шаг 5: Запустите бота
```bash
sudo systemctl start telegram-bot
sudo systemctl status telegram-bot
```

Готово! 🎉

---

## Вариант 2: Railway (бесплатно)

### Шаг 1: Зарегистрируйтесь
https://railway.app

### Шаг 2: Создайте новый проект
1. Нажмите "New Project"
2. Выберите "Deploy from GitHub repo" (или загрузите файлы)

### Шаг 3: Настройте переменные окружения
В настройках проекта добавьте:
- `BOT_TOKEN` - ваш токен бота
- `ADMIN_IDS` - 665509323,1478853053
- `CHAT_ID` - ваш chat ID

### Шаг 4: Настройте команду запуска
В настройках проекта укажите:
- **Start Command**: `python bot.py`

Готово! Бот запустится автоматически.

---

## Полезные команды

```bash
# Просмотр логов
sudo journalctl -u telegram-bot -f

# Перезапуск бота
sudo systemctl restart telegram-bot

# Остановка бота
sudo systemctl stop telegram-bot

# Статус бота
sudo systemctl status telegram-bot
```

---

## Резервное копирование

Настройте автоматический бэкап:
```bash
# Установите скрипт бэкапа
chmod +x backup.sh
sudo mv backup.sh /home/botuser/

# Добавьте в crontab (ежедневно в 3:00)
crontab -e
# Добавьте: 0 3 * * * /home/botuser/backup.sh
```

---

Подробная инструкция: [DEPLOY.md](DEPLOY.md)
