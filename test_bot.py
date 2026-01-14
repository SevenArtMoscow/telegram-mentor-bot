"""
Тесты для Telegram бота сбора историй о наставниках
"""
import os
import json
import pytest
import tempfile
import shutil
from datetime import datetime
from unittest.mock import Mock, AsyncMock, patch, MagicMock
from telegram import Update, Message, Chat, User
from telegram.ext import ContextTypes

# Импортируем функции из bot.py
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import bot
from bot import (
    load_stories,
    save_story,
    save_stories_to_text,
    WELCOME_MESSAGE
)


class TestFileOperations:
    """Тесты для работы с файлами"""
    
    def setup_method(self):
        """Создаём временную директорию для тестов"""
        self.test_dir = tempfile.mkdtemp()
        self.original_stories_file = bot.STORIES_FILE
        self.original_stories_text_file = bot.STORIES_TEXT_FILE
        
        # Мокаем пути к файлам
        bot.STORIES_FILE = os.path.join(self.test_dir, 'stories.json')
        bot.STORIES_TEXT_FILE = os.path.join(self.test_dir, 'stories.txt')
    
    def teardown_method(self):
        """Удаляем временную директорию"""
        shutil.rmtree(self.test_dir)
        bot.STORIES_FILE = self.original_stories_file
        bot.STORIES_TEXT_FILE = self.original_stories_text_file
    
    def test_load_stories_empty_file(self):
        """Тест загрузки историй из несуществующего файла"""
        stories = load_stories()
        assert stories == []
        assert isinstance(stories, list)
    
    def test_load_stories_existing_file(self):
        """Тест загрузки существующих историй"""
        test_stories = [
            {
                'user_id': 123,
                'username': 'test_user',
                'text': 'Test story',
                'timestamp': '2024-01-01T12:00:00'
            }
        ]
        with open(bot.STORIES_FILE, 'w', encoding='utf-8') as f:
            json.dump(test_stories, f, ensure_ascii=False, indent=2)
        
        stories = load_stories()
        assert len(stories) == 1
        assert stories[0]['user_id'] == 123
        assert stories[0]['username'] == 'test_user'
        assert stories[0]['text'] == 'Test story'
    
    def test_save_story_new(self):
        """Тест сохранения новой истории"""
        story = save_story(
            user_id=456,
            username='new_user',
            text='New story text'
        )
        
        assert story['user_id'] == 456
        assert story['username'] == 'new_user'
        assert story['text'] == 'New story text'
        assert 'timestamp' in story
        
        # Проверяем, что история сохранена в файл
        stories = load_stories()
        assert len(stories) == 1
        assert stories[0]['user_id'] == 456
    
    def test_save_story_multiple(self):
        """Тест сохранения нескольких историй"""
        save_story(1, 'user1', 'Story 1')
        save_story(2, 'user2', 'Story 2')
        save_story(3, 'user3', 'Story 3')
        
        stories = load_stories()
        assert len(stories) == 3
        assert stories[0]['text'] == 'Story 1'
        assert stories[1]['text'] == 'Story 2'
        assert stories[2]['text'] == 'Story 3'
    
    def test_save_stories_to_text(self):
        """Тест сохранения историй в текстовый файл"""
        test_stories = [
            {
                'user_id': 111,
                'username': 'user1',
                'text': 'First story',
                'timestamp': '2024-01-01T10:00:00'
            },
            {
                'user_id': 222,
                'username': 'user2',
                'text': 'Second story',
                'timestamp': '2024-01-02T11:00:00'
            }
        ]
        
        save_stories_to_text(test_stories)
        
        assert os.path.exists(bot.STORIES_TEXT_FILE)
        
        with open(bot.STORIES_TEXT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'ИСТОРИИ О НАСТАВНИКАХ' in content
        assert 'Всего историй: 2' in content
        assert 'user1' in content
        assert 'user2' in content
        assert 'First story' in content
        assert 'Second story' in content
    
    def test_save_story_creates_text_file(self):
        """Тест, что сохранение истории создаёт текстовый файл"""
        save_story(999, 'test', 'Test story')
        
        assert os.path.exists(bot.STORIES_TEXT_FILE)
        
        with open(bot.STORIES_TEXT_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        assert 'test' in content
        assert 'Test story' in content


class TestCommandHandlers:
    """Тесты для обработчиков команд"""
    
    @pytest.fixture
    def mock_update(self):
        """Создаёт мок объекта Update"""
        update = Mock(spec=Update)
        update.message = Mock(spec=Message)
        update.message.reply_text = AsyncMock()
        update.message.reply_document = AsyncMock()
        update.effective_user = Mock(spec=User)
        update.effective_chat = Mock(spec=Chat)
        return update
    
    @pytest.fixture
    def mock_context(self):
        """Создаёт мок объекта Context"""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.application = Mock()
        context.application.bot = Mock()
        context.application.bot.forward_message = AsyncMock()
        return context
    
    @pytest.mark.asyncio
    async def test_start_command(self, mock_update):
        """Тест команды /start"""
        from bot import start
        
        await start(mock_update, None)
        
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args[0][0]
        assert WELCOME_MESSAGE in call_args or call_args == WELCOME_MESSAGE
    
    @pytest.mark.asyncio
    async def test_export_command_no_admin(self, mock_update, mock_context):
        """Тест команды /export без прав админа"""
        from bot import export
        import bot
        
        # Сохраняем оригинальные ADMIN_IDS
        original_admin_ids = bot.ADMIN_IDS
        bot.ADMIN_IDS = [999999]
        
        mock_update.effective_user.id = 123456
        
        await export(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        assert 'нет доступа' in mock_update.message.reply_text.call_args[0][0].lower()
        
        # Восстанавливаем
        bot.ADMIN_IDS = original_admin_ids
    
    @pytest.mark.asyncio
    async def test_export_command_admin_no_stories(self, mock_update, mock_context):
        """Тест команды /export для админа без историй"""
        from bot import export
        import bot
        
        # Создаём временную директорию
        test_dir = tempfile.mkdtemp()
        original_stories_file = bot.STORIES_FILE
        bot.STORIES_FILE = os.path.join(test_dir, 'stories.json')
        
        # Удаляем файл, если существует
        if os.path.exists(bot.STORIES_FILE):
            os.remove(bot.STORIES_FILE)
        
        original_admin_ids = bot.ADMIN_IDS
        bot.ADMIN_IDS = [123456]
        mock_update.effective_user.id = 123456
        
        try:
            await export(mock_update, mock_context)
            
            mock_update.message.reply_text.assert_called_once()
            assert 'нет сохранённых историй' in mock_update.message.reply_text.call_args[0][0].lower()
        finally:
            # Восстанавливаем
            bot.ADMIN_IDS = original_admin_ids
            bot.STORIES_FILE = original_stories_file
            shutil.rmtree(test_dir)
    
    @pytest.mark.asyncio
    async def test_stats_command_no_admin(self, mock_update, mock_context):
        """Тест команды /stats без прав админа"""
        from bot import stats
        import bot
        
        original_admin_ids = bot.ADMIN_IDS
        bot.ADMIN_IDS = [999999]
        
        mock_update.effective_user.id = 123456
        
        await stats(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        assert 'нет доступа' in mock_update.message.reply_text.call_args[0][0].lower()
        
        bot.ADMIN_IDS = original_admin_ids
    
    @pytest.mark.asyncio
    async def test_chatid_command(self, mock_update, mock_context):
        """Тест команды /chatid"""
        from bot import chatid
        
        mock_update.effective_chat.id = -1001234567890
        mock_update.effective_chat.type = 'group'
        mock_update.effective_chat.title = 'Test Group'
        
        await chatid(mock_update, mock_context)
        
        mock_update.message.reply_text.assert_called_once()
        call_args = mock_update.message.reply_text.call_args
        assert '-1001234567890' in call_args[0][0]
        assert 'CHAT_ID' in call_args[0][0]


class TestMessageHandler:
    """Тесты для обработчика сообщений"""
    
    @pytest.fixture
    def mock_update_private(self):
        """Создаёт мок Update для личного чата"""
        update = Mock(spec=Update)
        update.message = Mock(spec=Message)
        update.message.text = 'Test story message'
        update.message.reply_text = AsyncMock()
        update.message.chat = Mock(spec=Chat)
        update.message.chat.id = 123456
        update.message.chat.type = 'private'
        update.message.message_id = 1
        update.effective_user = Mock(spec=User)
        update.effective_user.id = 123456
        update.effective_user.username = 'testuser'
        update.effective_user.first_name = 'Test'
        # effective_chat используется в handle_message
        update.effective_chat = update.message.chat
        return update
    
    @pytest.fixture
    def mock_context(self):
        """Создаёт мок объекта Context"""
        context = Mock(spec=ContextTypes.DEFAULT_TYPE)
        context.application = Mock()
        context.application.bot = Mock()
        context.application.bot.forward_message = AsyncMock()
        return context
    
    @pytest.mark.asyncio
    async def test_handle_message_private_chat(self, mock_update_private, mock_context):
        """Тест обработки сообщения из личного чата"""
        import bot
        
        # Убеждаемся, что все атрибуты правильно установлены
        assert mock_update_private.message.chat.type == 'private'
        assert mock_update_private.message.text == 'Test story message'
        assert not mock_update_private.message.text.startswith('/')
        
        # Сохраняем оригинальные значения
        original_save_story = bot.save_story
        original_chat_id = bot.CHAT_ID
        
        # Мокаем save_story, чтобы проверить, что она вызывается
        mock_save_story = Mock(return_value={
            'user_id': 123456,
            'username': 'testuser',
            'text': 'Test story message',
            'timestamp': '2024-01-01T12:00:00'
        })
        bot.save_story = mock_save_story
        bot.CHAT_ID = ''  # Отключаем пересылку для теста
        
        try:
            await bot.handle_message(mock_update_private, mock_context)
            
            # Проверяем, что save_story была вызвана
            mock_save_story.assert_called_once()
            # Проверяем аргументы вызова (save_story вызывается с именованными аргументами)
            call_args = mock_save_story.call_args
            assert call_args is not None
            # Проверяем именованные аргументы
            assert call_args.kwargs['user_id'] == 123456
            assert call_args.kwargs['username'] in ['testuser', 'Test']
            assert call_args.kwargs['text'] == 'Test story message'
            
            # Проверяем, что функция ответила пользователю
            mock_update_private.message.reply_text.assert_called_once()
            assert 'сохранена' in mock_update_private.message.reply_text.call_args[0][0].lower()
        finally:
            # Восстанавливаем
            bot.save_story = original_save_story
            bot.CHAT_ID = original_chat_id
    
    @pytest.mark.asyncio
    async def test_handle_message_group_chat_ignored(self, mock_update_private, mock_context):
        """Тест, что сообщения из группы игнорируются"""
        from bot import handle_message
        import bot
        
        test_dir = tempfile.mkdtemp()
        original_stories_file = bot.STORIES_FILE
        bot.STORIES_FILE = os.path.join(test_dir, 'stories.json')
        
        mock_update_private.message.chat.type = 'group'
        
        try:
            await handle_message(mock_update_private, mock_context)
            
            # Сообщение не должно быть сохранено
            stories = load_stories()
            assert len(stories) == 0
            
            # Ответ не должен быть отправлен
            mock_update_private.message.reply_text.assert_not_called()
        finally:
            bot.STORIES_FILE = original_stories_file
            shutil.rmtree(test_dir)
    
    @pytest.mark.asyncio
    async def test_handle_message_command_ignored(self, mock_update_private, mock_context):
        """Тест, что команды игнорируются"""
        from bot import handle_message
        import bot
        
        test_dir = tempfile.mkdtemp()
        original_stories_file = bot.STORIES_FILE
        bot.STORIES_FILE = os.path.join(test_dir, 'stories.json')
        
        mock_update_private.message.text = '/start'
        
        try:
            await handle_message(mock_update_private, mock_context)
            
            # Команда не должна быть сохранена
            stories = load_stories()
            assert len(stories) == 0
        finally:
            bot.STORIES_FILE = original_stories_file
            shutil.rmtree(test_dir)


class TestConfiguration:
    """Тесты для проверки конфигурации"""
    
    def test_welcome_message_exists(self):
        """Тест, что приветственное сообщение существует"""
        assert WELCOME_MESSAGE
        assert len(WELCOME_MESSAGE) > 0
        assert 'наставник' in WELCOME_MESSAGE.lower() or 'преподаватель' in WELCOME_MESSAGE.lower()
    
    @patch.dict(os.environ, {'BOT_TOKEN': 'test_token_123'})
    def test_bot_token_loading(self):
        """Тест загрузки токена бота"""
        from dotenv import load_dotenv
        import bot
        load_dotenv()
        
        # Проверяем, что токен загружается
        token = os.getenv('BOT_TOKEN')
        assert token == 'test_token_123'
    
    @patch.dict(os.environ, {'ADMIN_IDS': '123,456,789'})
    def test_admin_ids_loading(self):
        """Тест загрузки ID админов"""
        from dotenv import load_dotenv
        import bot
        load_dotenv()
        
        admin_ids_str = os.getenv('ADMIN_IDS', '')
        admin_ids = [int(id.strip()) for id in admin_ids_str.split(',') if id.strip()]
        
        assert len(admin_ids) == 3
        assert 123 in admin_ids
        assert 456 in admin_ids
        assert 789 in admin_ids


class TestEdgeCases:
    """Тесты для граничных случаев"""
    
    def test_save_story_empty_text(self):
        """Тест сохранения истории с пустым текстом"""
        test_dir = tempfile.mkdtemp()
        original_stories_file = bot.STORIES_FILE
        bot.STORIES_FILE = os.path.join(test_dir, 'stories.json')
        
        try:
            story = save_story(111, 'user', '')
            
            assert story['text'] == ''
            stories = load_stories()
            assert len(stories) == 1
        finally:
            bot.STORIES_FILE = original_stories_file
            shutil.rmtree(test_dir)
    
    def test_save_story_special_characters(self):
        """Тест сохранения истории со специальными символами"""
        test_dir = tempfile.mkdtemp()
        original_stories_file = bot.STORIES_FILE
        bot.STORIES_FILE = os.path.join(test_dir, 'stories.json')
        
        try:
            text = 'История с эмодзи 😊 и спецсимволами: <>&"\''
            story = save_story(222, 'user', text)
            
            assert story['text'] == text
            stories = load_stories()
            assert stories[0]['text'] == text
        finally:
            bot.STORIES_FILE = original_stories_file
            shutil.rmtree(test_dir)
    
    def test_save_story_unicode_username(self):
        """Тест сохранения истории с юникод именем пользователя"""
        test_dir = tempfile.mkdtemp()
        original_stories_file = bot.STORIES_FILE
        bot.STORIES_FILE = os.path.join(test_dir, 'stories.json')
        
        try:
            story = save_story(333, 'Пользователь_123', 'Test')
            
            assert story['username'] == 'Пользователь_123'
            stories = load_stories()
            assert stories[0]['username'] == 'Пользователь_123'
        finally:
            bot.STORIES_FILE = original_stories_file
            shutil.rmtree(test_dir)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
