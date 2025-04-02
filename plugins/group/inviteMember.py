import plugins
from bridge.context import ContextType
from bridge.reply import Reply, ReplyType
from channel.chat_message import ChatMessage
from common.log import logger
from plugins import *
from config import conf
from lib.gewechat.client import GewechatClient

@plugins.register(
    name="InviteMember",
    desire_priority=100,
    hidden=True,
    desc="群聊邀请成员",
    version="0.1",
    author="JCOvO",
)
class InviteMember(Plugin):
    def __init__(self):
        super().__init__()
        self.client = GewechatClient(conf().get("gewechat_base_url"), conf().get("gewechat_token"))
        # 加载配置，如果没有则使用默认配置
        self.config = super().load_config()
        if self.config is None:
            self.config = {
                "invite_member_commands": ["加群"]  # 设置默认触发命令
            }
            # 保存默认配置
            super().save_config(self.config)
            logger.info("[InviteMember] 创建了默认配置文件")
        
        self.handlers[Event.ON_HANDLE_CONTEXT] = self.on_handle_context
        logger.info("[InviteMember] inited")
        self.app_id = conf().get("gewechat_app_id")
        self.chatroom_id = conf().get("invite_chatroom_id")
        
        # 检查关键配置是否存在
        if not self.chatroom_id:
            logger.warning("[InviteMember] invite_chatroom_id 未配置，插件可能无法正常工作")
            
    def on_handle_context(self, e_context: EventContext):
        if e_context["context"].type == ContextType.TEXT:
            commands = self.config.get("invite_member_commands", ["加群"])  # 使用默认值防止配置为None
            logger.info(f"[InviteMember] 检查命令: {e_context['context'].content} 是否在 {commands} 中")
            
            if e_context["context"].content in commands:
                if not self.chatroom_id:
                    logger.error("[InviteMember] invite_chatroom_id 未配置，无法邀请用户")
                    reply = Reply()
                    reply.type = ReplyType.TEXT
                    reply.content = "系统配置错误，无法完成邀请"
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS
                    return
                
                logger.info(f"[InviteMember] 邀请用户 {e_context['context']['msg'].from_user_id} 到群 {self.chatroom_id}")
                re=self.client.invite_member(
                    app_id=self.app_id, 
                    wxids=e_context["context"]["msg"].from_user_id, 
                    chatroom_id=self.chatroom_id,
                    reason="无"
                )
                if re["ret"] == 200:
                    logger.info("[InviteMember] 邀请成功")
                    reply = Reply()
                    reply.type = ReplyType.TEXT
                    reply.content = "邀请成功"
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS
                else:
                    logger.error(f"[InviteMember] 邀请失败: {re}")
                    reply = Reply()
                    reply.type = ReplyType.TEXT
                    reply.content = f"邀请失败: {re.get('msg', '未知错误')}"
                    e_context["reply"] = reply
                    e_context.action = EventAction.BREAK_PASS

