# Настройка Git репозитория

## ✅ Что уже сделано:
- Git инициализирован
- Файлы добавлены в репозиторий
- Первый коммит создан
- `.env` файл правильно игнорируется

## 📤 Создание репозитория на GitHub

### Шаг 1: Создайте репозиторий на GitHub

1. Перейдите на https://github.com
2. Нажмите **"New repository"** (или **"+"** → **"New repository"**)
3. Заполните:
   - **Repository name**: `telegram-mentor-bot` (или любое другое имя)
   - **Description**: "Telegram bot for collecting mentor stories"
   - **Visibility**: 
     - ✅ **Private** (рекомендуется, если не хотите публиковать код)
     - ⚪ Public (если хотите открытый репозиторий)
   - ❌ **НЕ** ставьте галочки на "Add README", "Add .gitignore", "Choose a license" (у нас уже есть эти файлы)
4. Нажмите **"Create repository"**

### Шаг 2: Подключите локальный репозиторий к GitHub

После создания репозитория GitHub покажет инструкции. Выполните команды:

```bash
# Добавьте удаленный репозиторий (замените YOUR_USERNAME и REPO_NAME)
git remote add origin https://github.com/YOUR_USERNAME/REPO_NAME.git

# Переименуйте ветку в main (если нужно)
git branch -M main

# Отправьте код на GitHub
git push -u origin main
```

**Пример:**
```bash
git remote add origin https://github.com/SevenArtQ/telegram-mentor-bot.git
git branch -M main
git push -u origin main
```

### Шаг 3: Проверьте

Откройте ваш репозиторий на GitHub - все файлы должны быть там!

---

## 🔄 Работа с репозиторием

### Отправка изменений на GitHub:
```bash
git add .
git commit -m "Описание изменений"
git push
```

### Клонирование на сервер:
```bash
ssh root@85.198.98.152
cd /root
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git telegram-bot
cd telegram-bot
```

---

## 🔐 Безопасность

⚠️ **Важно:** Убедитесь, что файл `.env` НЕ попал в репозиторий!

Проверьте:
```bash
git ls-files | grep .env
```

Если команда ничего не вывела - всё хорошо! ✅

Если вывела `.env` - удалите его из индекса:
```bash
git rm --cached .env
git commit -m "Remove .env from repository"
git push
```

---

## 📝 Полезные команды

```bash
# Проверить статус
git status

# Посмотреть историю коммитов
git log

# Посмотреть удаленные репозитории
git remote -v

# Обновить код с GitHub
git pull
```
