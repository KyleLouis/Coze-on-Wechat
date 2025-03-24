from cozepy import Coze
from .user_session import UserSessionManager
from common.log import logger
from typing import Optional
import time
import threading
import random

class ConversationManager:
    def __init__(self, coze_client: Coze, session_manager: UserSessionManager):
        self.coze = coze_client
        self.session_manager = session_manager
        self._lock = threading.Lock()
        self._conversation_locks = {}
        self._max_retries = 3
        self._retry_delay = 1  # 基础延迟时间（秒）

    def _get_conversation_lock(self, conversation_id: str) -> threading.Lock:
        """获取会话锁"""
        with self._lock:
            if conversation_id not in self._conversation_locks:
                self._conversation_locks[conversation_id] = threading.Lock()
            return self._conversation_locks[conversation_id]

    def create_conversation(self, user_id: str = None) -> Optional[str]:
        """创建新会话并保存到数据库"""
        try:
            conversation = self.coze.conversations.create()
            conversation_id = conversation.id
            if user_id:
                self.session_manager.create_session(user_id, conversation_id)
                logger.info(f"创建会话: {conversation_id} for user: {user_id}")
            return conversation_id
        except Exception as e:
            logger.error(f"创建会话失败: {str(e)}")
            return None

    def handle_conversation_error(self, conversation_id: str, user_id: str) -> Optional[str]:
        """处理会话错误，创建新会话"""
        try:
            # 删除旧会话
            self.session_manager.delete_session(user_id)
            # 创建新会话
            new_conversation_id = self.create_conversation(user_id)
            if new_conversation_id:
                logger.info(f"会话 {conversation_id} 发生错误，已创建新会话 {new_conversation_id}")
                return new_conversation_id
        except Exception as e:
            logger.error(f"处理会话错误失败: {str(e)}")
        return None

    def ensure_conversation(self, conversation_id: str, user_id: str) -> Optional[str]:
        """确保会话可用，如果不可用则创建新会话"""
        conv_lock = self._get_conversation_lock(conversation_id)
        with conv_lock:
            try:
                # 尝试获取会话消息列表来验证会话是否可用
                self.coze.conversations.messages.list(conversation_id=conversation_id)
                return conversation_id
            except Exception as e:
                if "Conversation occupied" in str(e):
                    # 添加随机延迟，避免多个请求同时重试
                    time.sleep(self._retry_delay + random.random())
                    return self.handle_conversation_error(conversation_id, user_id)
                logger.error(f"验证会话失败: {str(e)}")
                return None

    def retry_with_new_conversation(self, func, *args, **kwargs) -> Optional[any]:
        """使用重试机制执行操作，如果失败则创建新会话"""
        for attempt in range(self._max_retries):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                if "Conversation occupied" in str(e):
                    if attempt < self._max_retries - 1:
                        # 添加指数退避延迟
                        delay = self._retry_delay * (2 ** attempt) + random.random()
                        logger.info(f"会话被占用，等待 {delay:.1f} 秒后重试...")
                        time.sleep(delay)
                        continue
                    else:
                        logger.error("达到最大重试次数，创建新会话")
                        return None
                raise  # 如果不是会话占用错误，则抛出异常
        return None 