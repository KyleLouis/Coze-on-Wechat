import base64
import uuid
import re
from bridge.context import ContextType
from channel.chat_message import ChatMessage
from common.log import logger
from common.tmp_dir import TmpDir
from config import conf
from lib.gewechat import GewechatClient
import requests
import xml.etree.ElementTree as ET
import os

# 私聊信息示例
"""
{
    "TypeName": "AddMsg",
    "Appid": "wx_xxx",
    "Data": {
        "MsgId": 177581074,
        "FromUserName": {
            "string": "wxid_fromuser"
        },
        "ToUserName": {
            "string": "wxid_touser"
        },
        "MsgType": 49,
        "Content": {
            "string": ""
        },
        "Status": 3,
        "ImgStatus": 1,
        "ImgBuf": {
            "iLen": 0
        },
        "CreateTime": 1733410112,
        "MsgSource": "<msgsource>xx</msgsource>\n",
        "PushContent": "xxx",
        "NewMsgId": 5894648508580188926,
        "MsgSeq": 773900156
    },
    "Wxid": "wxid_gewechat_bot"  // 使用gewechat登录的机器人wxid
}
"""

# 群聊信息示例
"""
{
    "TypeName": "AddMsg",
    "Appid": "wx_xxx",
    "Data": {
        "MsgId": 585326344,
        "FromUserName": {
            "string": "xxx@chatroom"
        },
        "ToUserName": {
            "string": "wxid_gewechat_bot" // 接收到此消息的wxid, 即使用gewechat登录的机器人wxid
        },
        "MsgType": 1,
        "Content": {
            "string": "wxid_xxx:\n@name msg_content" // 发送消息人的wxid和消息内容(包含@name)
        },
        "Status": 3,
        "ImgStatus": 1,
        "ImgBuf": {
            "iLen": 0
        },
        "CreateTime": 1733447040,
        "MsgSource": "<msgsource>\n\t<atuserlist><![CDATA[,wxid_wvp31dkffyml19]]></atuserlist>\n\t<pua>1</pua>\n\t<silence>0</silence>\n\t<membercount>3</membercount>\n\t<signature>V1_cqxXBat9|v1_cqxXBat9</signature>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "PushContent": "xxx在群聊中@了你",
        "NewMsgId": 8449132831264840264,
        "MsgSeq": 773900177
    },
    "Wxid": "wxid_gewechat_bot"  // 使用gewechat登录的机器人wxid
}
"""

# 群邀请消息示例
"""
{
    "TypeName": "AddMsg",
    "Appid": "wx_xxx",
    "Data": {
        "MsgId": 488566999,
        "FromUserName": {
            "string": "xxx@chatroom"
        },
        "ToUserName": {
            "string": "wxid_gewechat_bot"
        },
        "MsgType": 10002,
        "Content": {
            "string": "53760920521@chatroom:\n<sysmsg type=\"sysmsgtemplate\">\n\t<sysmsgtemplate>\n\t\t<content_template type=\"tmpl_type_profile\">\n\t\t\t<plain><![CDATA[]]></plain>\n\t\t\t<template><![CDATA[\"$username$\"邀请\"$names$\"加入了群聊]]></template>\n\t\t\t<link_list>\n\t\t\t\t<link name=\"username\" type=\"link_profile\">\n\t\t\t\t\t<memberlist>\n\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t<username><![CDATA[wxid_eaclcf34ny6221]]></username>\n\t\t\t\t\t\t\t<nickname><![CDATA[刘贺]]></nickname>\n\t\t\t\t\t\t</member>\n\t\t\t\t\t</memberlist>\n\t\t\t\t</link>\n\t\t\t\t<link name=\"names\" type=\"link_profile\">\n\t\t\t\t\t<memberlist>\n\t\t\t\t\t\t<member>\n\t\t\t\t\t\t\t<username><![CDATA[wxid_mmwc3zzkfcl922]]></username>\n\t\t\t\t\t\t\t<nickname><![CDATA[郑德娟]]></nickname>\n\t\t\t\t\t\t</member>\n\t\t\t\t\t</memberlist>\n\t\t\t\t\t<separator><![CDATA[、]]></separator>\n\t\t\t\t</link>\n\t\t\t</link_list>\n\t\t</content_template>\n\t</sysmsgtemplate>\n</sysmsg>\n"
        },
        "Status": 4,
        "ImgStatus": 1,
        "ImgBuf": {
            "iLen": 0
        },
        "CreateTime": 1736820013,
        "MsgSource": "<msgsource>\n\t<tmp_node>\n\t\t<publisher-id></publisher-id>\n\t</tmp_node>\n</msgsource>\n",
        "NewMsgId": 5407479395895269893,
        "MsgSeq": 821038175
    },
    "Wxid": "wxid_gewechat_bot"
}
"""

"""
{
    "TypeName": "ModContacts",
    "Appid": "wx_xxx",
    "Data": {
        "UserName": {
            "string": "xxx@chatroom"
        },
        "NickName": {
            "string": "测试2"
        },
        "PyInitial": {
            "string": "CS2"
        },
        "QuanPin": {
            "string": "ceshi2"
        },
        "Sex": 0,
        "ImgBuf": {
            "iLen": 0
        },
        "BitMask": 4294967295,
        "BitVal": 2,
        "ImgFlag": 1,
        "Remark": {},
        "RemarkPyinitial": {},
        "RemarkQuanPin": {},
        "ContactType": 0,
        "RoomInfoCount": 0,
        "DomainList": [
            {}
        ],
        "ChatRoomNotify": 1,
        "AddContactScene": 0,
        "PersonalCard": 0,
        "HasWeiXinHdHeadImg": 0,
        "VerifyFlag": 0,
        "Level": 0,
        "Source": 0,
        "ChatRoomOwner": "wxid_xxx",
        "WeiboFlag": 0,
        "AlbumStyle": 0,
        "AlbumFlag": 0,
        "SnsUserInfo": {
            "SnsFlag": 0,
            "SnsBgobjectId": 0,
            "SnsFlagEx": 0
        },
        "CustomizedInfo": {
            "BrandFlag": 0
        },
        "AdditionalContactList": {
            "LinkedinContactItem": {}
        },
        "ChatroomMaxCount": 10008,
        "DeleteFlag": 0,
        "Description": "\b\u0004\u0012\u001c\n\u0013wxid_xxx0\u0001@\u0000\u0001\u0000\u0012\u001c\n\u0013wxid_xxx0\u0001@\u0000\u0001\u0000\u0012\u001c\n\u0013wxid_xxx0\u0001@\u0000\u0001\u0000\u0012\u001c\n\u0013wxid_xxx0\u0001@\u0000\u0001\u0000\u0018\u0001\"\u0000(\u00008\u0000",
        "ChatroomStatus": 5,
        "Extflag": 0,
        "ChatRoomBusinessType": 0
    },
    "Wxid": "wxid_xxx"
}
"""

# 群聊中移除用户示例
"""
{
    "UserName": {
        "string": "xxx@chatroom"
    },
    "NickName": {
        "string": "AITestGroup"
    },
    "PyInitial": {
        "string": "AITESTGROUP"
    },
    "QuanPin": {
        "string": "AITestGroup"
    },
    "Sex": 0,
    "ImgBuf": {
        "iLen": 0
    },
    "BitMask": 4294967295,
    "BitVal": 2,
    "ImgFlag": 1,
    "Remark": {},
    "RemarkPyinitial": {},
    "RemarkQuanPin": {},
    "ContactType": 0,
    "RoomInfoCount": 0,
    "DomainList": [
        {}
    ],
    "ChatRoomNotify": 1,
    "AddContactScene": 0,
    "PersonalCard": 0,
    "HasWeiXinHdHeadImg": 0,
    "VerifyFlag": 0,
    "Level": 0,
    "Source": 0,
    "ChatRoomOwner": "wxid_xxx",
    "WeiboFlag": 0,
    "AlbumStyle": 0,
    "AlbumFlag": 0,
    "SnsUserInfo": {
        "SnsFlag": 0,
        "SnsBgobjectId": 0,
        "SnsFlagEx": 0
    },
    "CustomizedInfo": {
        "BrandFlag": 0
    },
    "AdditionalContactList": {
        "LinkedinContactItem": {}
    },
    "ChatroomMaxCount": 10037,
    "DeleteFlag": 0,
    "Description": "\b\u0002\u0012\u001c\n\u0013wxid_eacxxxx\u0001@\u0000�\u0001\u0000\u0012\u001c\n\u0013wxid_xxx\u0001@\u0000�\u0001\u0000\u0018\u0001\"\u0000(\u00008\u0000",
    "ChatroomStatus": 4,
    "Extflag": 0,
    "ChatRoomBusinessType": 0
}
"""

# 群聊中移除用户示例
"""
{
    "TypeName": "ModContacts",
    "Appid": "wx_xxx",
    "Data": {
        "UserName": {
            "string": "xxx@chatroom"
        },
        "NickName": {
            "string": "测试2"
        },
        "PyInitial": {
            "string": "CS2"
        },
        "QuanPin": {
            "string": "ceshi2"
        },
        "Sex": 0,
        "ImgBuf": {
            "iLen": 0
        },
        "BitMask": 4294967295,
        "BitVal": 2,
        "ImgFlag": 2,
        "Remark": {},
        "RemarkPyinitial": {},
        "RemarkQuanPin": {},
        "ContactType": 0,
        "RoomInfoCount": 0,
        "DomainList": [
            {}
        ],
        "ChatRoomNotify": 1,
        "AddContactScene": 0,
        "PersonalCard": 0,
        "HasWeiXinHdHeadImg": 0,
        "VerifyFlag": 0,
        "Level": 0,
        "Source": 0,
        "ChatRoomOwner": "wxid_xxx",
        "WeiboFlag": 0,
        "AlbumStyle": 0,
        "AlbumFlag": 0,
        "SnsUserInfo": {
            "SnsFlag": 0,
            "SnsBgobjectId": 0,
            "SnsFlagEx": 0
        },
        "SmallHeadImgUrl": "https://wx.qlogo.cn/mmcrhead/xxx/0",
        "CustomizedInfo": {
            "BrandFlag": 0
        },
        "AdditionalContactList": {
            "LinkedinContactItem": {}
        },
        "ChatroomMaxCount": 10007,
        "DeleteFlag": 0,
        "Description": "\b\u0003\u0012\u001c\n\u0013wxid_xxx0\u0001@\u0000\u0001\u0000\u0012\u001c\n\u0013wxid_xxx0\u0001@\u0000\u0001\u0000\u0012\u001c\n\u0013wxid_xxx0\u0001@\u0000\u0001\u0000\u0018\u0001\"\u0000(\u00008\u0000",
        "ChatroomStatus": 5,
        "Extflag": 0,
        "ChatRoomBusinessType": 0
    },
    "Wxid": "wxid_xxx"
}
"""

class BaseMessageHandler:
    """基础消息处理类"""
    def __init__(self, msg, client):
        self.msg = msg
        self.client = client
        self.data = msg.get('Data', {})
        self.app_id = conf().get("gewechat_app_id")
        
    def get_basic_info(self):
        """获取消息基本信息"""
        return {
            'msg_id': self.data.get('NewMsgId'),
            'create_time': self.data.get('CreateTime', 0),
            'from_user_id': self.data.get('FromUserName', {}).get('string'),
            'to_user_id': self.data.get('ToUserName', {}).get('string'),
            'is_group': "@chatroom" in self.data.get('FromUserName', {}).get('string', '')
        }

class MessageTypeHandler:
    """消息类型处理类"""
    @staticmethod
    def handle_text(msg_data):
        """处理文本消息"""
        return ContextType.TEXT, msg_data['Content']['string']
    
    @staticmethod
    def handle_voice(msg_data):
        """处理语音消息"""
        if 'ImgBuf' in msg_data and 'buffer' in msg_data['ImgBuf'] and msg_data['ImgBuf']['buffer']:
            silk_data = base64.b64decode(msg_data['ImgBuf']['buffer'])
            silk_file_name = f"voice_{str(uuid.uuid4())}.silk"
            silk_file_path = TmpDir().path() + silk_file_name
            with open(silk_file_path, "wb") as f:
                f.write(silk_data)
            return ContextType.VOICE, silk_file_path
        return None, None

    @staticmethod
    def handle_image(msg_data, msg_id):
        """处理图片消息"""
        return ContextType.IMAGE, TmpDir().path() + str(msg_id) + ".jpg"

class GroupMessageHandler:
    """群消息处理类"""
    def __init__(self, msg, client):
        self.msg = msg
        self.client = client
        self.data = msg.get('Data', {})
        self.app_id = conf().get("gewechat_app_id")
        
    def process_group_message(self):
        """处理群消息"""
        result = {
            'is_at': self._check_is_at(),
            'actual_user_info': self._get_actual_user_info(),
            'content': self._process_content()
        }
        return result

    def _check_is_at(self):
        """检查是否被@"""
        msg_source = self.data.get('MsgSource', '')
        to_user_id = self.data['ToUserName']['string']
        try:
            root = ET.fromstring(msg_source)
            atuserlist_elem = root.find('atuserlist')
            if atuserlist_elem is not None:
                return to_user_id in atuserlist_elem.text
        except ET.ParseError:
            pass
        return '在群聊中@了你' in self.data.get('PushContent', '')

    def _get_actual_user_info(self):
        """获取实际发送者信息"""
        content = self.data.get('Content', {}).get('string', '')
        actual_user_id = content.split(':', 1)[0]
        
        chatroom_member_list_response = self.client.get_chatroom_member_list(self.app_id, self.data['FromUserName']['string'])
        actual_user_nickname = actual_user_id
        
        if chatroom_member_list_response.get('ret', 0) == 200:
            member_list = chatroom_member_list_response.get('data', {}).get('memberList', [])
            for member_info in member_list:
                if member_info['wxid'] == actual_user_id:
                    actual_user_nickname = member_info.get('displayName') or member_info.get('nickName', actual_user_id)
                    break
                    
        return {
            'actual_user_id': actual_user_id,
            'actual_user_nickname': actual_user_nickname
        }
    
    def _process_content(self):
        """处理群消息内容"""
        content = self.data.get('Content', {}).get('string', '')
        actual_user_id = content.split(':', 1)[0]
        content = re.sub(f'{actual_user_id}:\n', '', content)
        return re.sub(r'@[^\u2005]+\u2005', '', content)

class FileHandler:
    """文件处理类"""
    def __init__(self, client, app_id):
        self.client = client
        self.app_id = app_id
        
    def download_image(self, msg_data, save_path):
        """下载图片"""
        try:
            content_xml = msg_data['Content']['string']
            xml_start = content_xml.find('<?xml version=')
            content_xml = content_xml[xml_start:] if xml_start != -1 else content_xml
            
            for img_type in [1, 2]:
                try:
                    image_info = self.client.download_image(
                        app_id=self.app_id,
                        xml=content_xml,
                        type=img_type
                    )
                    if image_info.get('ret') == 200 and image_info.get('data'):
                        return self._save_image(image_info, save_path)
                except Exception as e:
                    logger.warning(f"[gewechat] Image download failed for type {img_type}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"[gewechat] Image download failed: {str(e)}")
            return False
            
    def _save_image(self, image_info, save_path):
        """保存图片"""
        try:
            file_url = image_info['data']['fileUrl']
            download_url = conf().get("gewechat_download_url").rstrip('/')
            full_url = f"{download_url}/{file_url}"
            
            response = requests.get(full_url, stream=True, timeout=(5, 10))
            response.raise_for_status()
            
            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except Exception as e:
            logger.error(f"[gewechat] Save image failed: {str(e)}")
            return False
            
    def download_voice(self, msg_wxid, msg_id, save_path):
        """下载语音"""
        try:
            voice_data = self.client.download_voice(msg_wxid, msg_id)
            with open(save_path, "wb") as f:
                f.write(voice_data)
            return True
        except Exception as e:
            logger.error(f"[gewechat] Failed to download voice file: {e}")
            return False

def Friend_request_message(msg_data):
        """处理好友请求消息"""

        content_str = msg_data['Data']['Content']['string']
        
        try:
            # 检查内容是否包含XML格式的消息
            if "<msg " in content_str:
                # 解析XML消息
                xml_start = content_str.find("<msg ")
                xml_content = content_str[xml_start:]
                root = ET.fromstring(xml_content)
                
                v3=root.get("encryptusername", "")
                nickname=root.get("fromnickname", "")
                content=root.get("content", "")
                v4=root.get("ticket", "")
            logger.info(f"收到{nickname}的好友请求:{content}")
            return v3,v4,nickname,content
        except Exception as e:
            logger.error(f"[gewechat] 好友请求消息处理异常: {e}")
            return None,None,None,None
                
   


class GeWeChatMessage(ChatMessage):
    def __init__(self, msg, client: GewechatClient):
        super().__init__(msg)
        self.msg = msg
        self.client = client
        self.app_id = conf().get("gewechat_app_id")
        # 初始化处理器
        self.base_handler = BaseMessageHandler(msg, client)
        self.file_handler = FileHandler(client, self.base_handler.app_id)
        self._prepare_fn = None
        
        # 获取基本信息
        basic_info = self.base_handler.get_basic_info()
        self.msg_id = basic_info['msg_id']
        self.create_time = basic_info['create_time']
        self.from_user_id = basic_info['from_user_id']
        self.to_user_id = basic_info['to_user_id']
        self.is_group = basic_info['is_group']
        self.other_user_id = self.from_user_id
        
        if not self.msg.get('Data'or"data"):
            logger.warning("[gewechat] Missing 'Data' in message")
            return
            
        if 'NewMsgId' not in self.msg['Data']:
            logger.warning("[gewechat] Missing 'NewMsgId' in message data")
            return
            
        # 检查是否是非用户消息
        if self._is_non_user_message(self.msg['Data'].get('MsgSource', ''), self.from_user_id):
            self.ctype = ContextType.NON_USER_MSG
            self.content = self.msg['Data']['Content']['string']
            logger.debug(f"[gewechat] detected non-user message from {self.from_user_id}: {self.content}")
            return
            
        # 处理消息
        self._process_message()
        
    def _process_message(self):
        """处理消息"""
        msg_type = self.msg['Data']['MsgType']
        
        if msg_type == 1:  # 文本消息
            self.ctype, self.content = MessageTypeHandler.handle_text(self.msg['Data'])
            logger.info(f"[gewechat] text message: {self.content}")
        elif msg_type == 34:  # 语音消息
            self.ctype, self.content = MessageTypeHandler.handle_voice(self.msg['Data'])
        elif msg_type == 3:  # 图片消息
            if self.is_group:
                # 群聊图片不处理
                logger.info(f"[gewechat] 忽略群聊中的图像: {self.from_user_id}")
                self._prepare_fn = None  # 清除准备函数
            else:
                # 私聊图片处理（保持原有逻辑）
                self.ctype, self.content = MessageTypeHandler.handle_image(self.msg['Data'], self.msg_id)
                self._prepare_fn = lambda: self.file_handler.download_image(self.msg['Data'], self.content)
            
        elif msg_type == 49:  # 引用消息，小程序，公众号等
            self._handle_reference_message()
            
        elif msg_type == 51:  # 状态同步消息
            self.ctype = ContextType.STATUS_SYNC
            self.content = self.msg['Data']['Content']['string']
            return
        

        elif msg_type == 37: # 好友添加请求通知
            self.ctype=ContextType.ACCEPT_FRIEND
            self._addContacts()
            return
            
        elif msg_type == 10002:  # 群系统消息
            self._handle_group_system_message()
        else:
            raise NotImplementedError(f"Unsupported message type: Type:{msg_type}")

 
        # 获取用户信息
        self._get_user_info()
        
        # 处理群消息
        if self.is_group:
            self._handle_group_message()
            
        self.my_msg = self.msg['Wxid'] == self.from_user_id
        
    def _handle_reference_message(self):
        """处理引用消息"""
        content_xml = self.msg['Data']['Content']['string']
        xml_start = content_xml.find('<?xml version=')
        if xml_start != -1:
            content_xml = content_xml[xml_start:]
            
        try:
            root = ET.fromstring(content_xml)
            appmsg = root.find('appmsg')
            
            if appmsg is not None:
                msg_type = appmsg.find('type')
                if msg_type is not None:
                    if msg_type.text == '57':  # 引用消息
                        self._handle_quote_message(appmsg)
                    elif msg_type.text == '5':  # 可能是公众号文章
                        self._handle_article_message(appmsg)
                    else:  # 其他消息类型
                        self.ctype = ContextType.TEXT
                        self.content = content_xml
            else:
                self.ctype = ContextType.TEXT
                self.content = content_xml
        except ET.ParseError as e:
            logger.error(f"[gewechat] Failed to parse reference message XML: {e}")
            self.ctype = ContextType.TEXT
            self.content = content_xml
            
    def _handle_quote_message(self, appmsg):
        """处理引用消息"""
        self.ctype = ContextType.TEXT
        refermsg = appmsg.find('refermsg')
        if refermsg is not None:
            displayname = refermsg.find('displayname').text
            quoted_content = refermsg.find('content').text
            title = appmsg.find('title').text
            self.content = f"「{displayname}: {quoted_content}」----------\n{title}"
        else:
            self.content = appmsg.find('title').text
            
    def _handle_article_message(self, appmsg):
        """处理文章消息"""
        title = appmsg.find('title').text if appmsg.find('title') is not None else "无标题"
        if "加入群聊" in title:
            self.ctype = ContextType.TEXT
            self.content = self.msg['Data']['Content']['string']
        else:
            self.ctype = ContextType.SHARING
            url = appmsg.find('url').text if appmsg.find('url') is not None else ""
            self.content = url
            
    def _handle_group_system_message(self):
        """处理群系统消息"""
        if not self.is_group:
            return
            
        content = self.msg['Data']['Content']['string']
        notes_bot_join_group = ["邀请你", "invited you", "You've joined", "你通过扫描"]
        notes_join_group = ["加入群聊", "加入了群聊", "invited", "joined"]
        
        if any(note in content for note in notes_bot_join_group):
            logger.warn("机器人加入群聊消息，不处理~")
            return
            
        if any(note in content for note in notes_join_group):
            try:
                xml_content = content.split(':\n', 1)[1] if ':\n' in content else content
                root = ET.fromstring(xml_content)
                
                sysmsgtemplate = root.find('.//sysmsgtemplate')
                if sysmsgtemplate is not None:
                    content_template = sysmsgtemplate.find('.//content_template')
                    if content_template is not None and content_template.get('type') == 'tmpl_type_profile':
                        template = content_template.find('.//template')
                        if template is not None and '加入了群聊' in template.text:
                            self._process_join_group_message(root)
            except ET.ParseError as e:
                logger.error(f"[gewechat] Failed to parse group join XML: {e}")
                
    def _process_join_group_message(self, root):
        """处理加入群聊消息"""
        self.ctype = ContextType.JOIN_GROUP
        
        inviter_link = root.find(".//link[@name='username']//nickname")
        inviter_nickname = inviter_link.text if inviter_link is not None else "未知用户"
        
        invited_link = root.find(".//link[@name='names']//nickname")
        invited_nickname = invited_link.text if invited_link is not None else "未知用户"
        
        self.content = f'"{inviter_nickname}"邀请"{invited_nickname}"加入了群聊'
        self.actual_user_nickname = invited_nickname
        
    def _get_user_info(self):
        """获取用户信息"""
        brief_info_response = self.client.get_brief_info(self.base_handler.app_id, [self.other_user_id])
        if brief_info_response['ret'] == 200 and brief_info_response['data']:
            brief_info = brief_info_response['data'][0]
            self.other_user_nickname = brief_info.get('nickName', '') or self.other_user_id
            
    def _handle_group_message(self):
        """处理群消息"""
        group_handler = GroupMessageHandler(self.msg, self.client)
        group_info = group_handler.process_group_message()
        
        self.is_at = group_info['is_at']
        self.content = group_info['content']
        
        user_info = group_info['actual_user_info']
        self.actual_user_id = user_info['actual_user_id']
        self.actual_user_nickname = user_info['actual_user_nickname']
        
    def prepare(self):
        """准备消息内容（如下载文件等）"""
        if self._prepare_fn:
            self._prepare_fn()
            
    def _is_non_user_message(self, msg_source: str, from_user_id: str) -> bool:
        """检查是否为非用户消息"""
        special_accounts = ["Tencent-Games", "weixin"]
        if from_user_id in special_accounts or from_user_id.startswith("gh_"):
            logger.debug(f"[gewechat] non-user message detected by sender id: {from_user_id}")
            return True
            
        non_user_indicators = [
            "<tips>3</tips>",
            "<bizmsgshowtype>",
            "</bizmsgshowtype>",
            "<bizmsgfromuser>",
            "</bizmsgfromuser>"
        ]
        if any(indicator in msg_source for indicator in non_user_indicators):
            logger.debug(f"[gewechat] non-user message detected by msg_source indicators")
            return True
            
        return False

    def _addContacts(self):
        """处理添加好友"""
        v3,v4,nickname,content=Friend_request_message(self.msg)
        if content in conf().get("accept_friend_commands",[]):
            
            re=self.client.add_contacts(app_id=self.app_id,
                                    scene=14,
                                    content="hallo",
                                    v4=v4,
                                    v3=v3,
                                    option=3
                                    )
            if re['ret'] == 200:
                logger.info(f"成功添加好友{nickname}")
            else:
                logger.error(f"添加好友失败{re}")


