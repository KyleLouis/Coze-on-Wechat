import streamlit as st
import json
import os
from utils.auth import check_password, logout

# 检查登录状态
if not check_password():
    st.stop()

# 添加自定义CSS样式，与home.py保持一致
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 1rem;
        background: linear-gradient(to right, #4e54c8, #8f94fb);
        color: white;
        border-radius: 10px;
        margin-bottom: 20px;
    }
    .status-card {
        padding: 20px;
        border-radius: 10px;
        margin-bottom: 15px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .running {
        background-color: #d4edda;
        border-left: 5px solid #28a745;
    }
    .stopped {
        background-color: #f8d7da;
        border-left: 5px solid #dc3545;
    }
    .control-button {
        width: 100%;
        height: 50px;
        margin: 5px 0;
    }
    .stButton>button {
        width: 100%;
        height: 50px;
    }
    .config-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
    }
    .footer {
        text-align: center;
        margin-top: 30px;
        padding: 10px;
        font-size: 0.8em;
        color: #6c757d;
    }
</style>
""", unsafe_allow_html=True)

# 标题和介绍，使用与home.py相同的样式
st.markdown("""
<div class="main-header">
    <h1>Coze on WeChat - 机器人配置</h1>
    <p>在这里配置您的Coze机器人参数</p>
</div>
""", unsafe_allow_html=True)

# 尝试显示图标
try:
    # 获取项目根目录
    current_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(current_dir)
    project_root = os.path.dirname(parent_dir)
    
    coze_icon_path = os.path.join(project_root, "docs", "coze_icon.png")
    if os.path.exists(coze_icon_path):
        st.image(coze_icon_path, width=100)
    else:
        st.info("Coze图标文件不存在")
except Exception as e:
    st.error(f"加载图标失败: {str(e)}")

# 获取配置文件路径
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # web目录
project_root = os.path.dirname(parent_dir)  # 项目根目录
config_path = os.path.join(project_root, "config.json")

# 默认配置
default_config = {
    "accept_friend_commands": "加好友",
    "always_reply_voice": False,
    "channel_type": "gewechat",
    "coze_api_base": "https://api.coze.cn",
    "coze_api_key": "",
    "coze_bot_id": "",
    "coze_space_id": "",
    "coze_voice_id": "",
    "debug": False,
    "gewechat_app_id": "",
    "gewechat_base_url": "",
    "gewechat_callback_url": "",
    "gewechat_download_url": "",
    "gewechat_token": "",
    "group_at_off": False,
    "group_chat_keyword": "",
    "group_chat_prefix": ["@机器人"],
    "group_chat_reply_prefix": "",
    "group_chat_reply_suffix": "",
    "group_name_white_list": [],
    "group_speech_recognition": False,
    "model": "coze",
    "no_need_at": False,
    "single_chat_prefix": [""],
    "single_chat_reply_prefix": "",
    "single_chat_reply_suffix": "",
    "speech_recognition": False,
    "text_to_voice": "coze",
    "voice_reply_voice": False,
    "voice_to_text": "coze"
}

# 读取配置文件，如果不存在则创建默认配置
if not os.path.exists(config_path):
    st.warning(f"配置文件 {config_path} 不存在，将创建默认配置文件")
    try:
        with open(config_path, 'w', encoding='utf-8') as f:
            json.dump(default_config, f, indent=4, ensure_ascii=False)
        st.success("已创建默认配置文件")
        config = default_config
    except Exception as e:
        st.error(f"创建配置文件失败: {str(e)}")
        config = default_config
else:
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
    except Exception as e:
        st.error(f"读取配置文件失败: {str(e)}")
        config = default_config

# 创建两列布局，与home.py保持一致
col1, col2 = st.columns([1, 2])

try:
    with col1:
        st.markdown("""
        <div class="status-card running">
            <h3>⚙️ 配置管理</h3>
            <p>修改配置后请点击保存按钮</p>
        </div>
        """, unsafe_allow_html=True)
        
        # 添加GitHub链接
        st.markdown("### 项目链接")
        st.markdown("[🔗 GitHub 项目主页](https://github.com/JC0v0/Coze-on-Wechat)")
        
        # 添加刷新按钮
        if st.button("🔄 刷新页面", key="refresh_button"):
            st.rerun()
            
        # 添加退出登录按钮
        if st.button("🚪 退出登录", type="secondary", key="logout_button"):
            logout()
        
    with col2:
        st.markdown("### 📝 机器人配置")
        
        # 使用可折叠区域显示配置
        with st.expander("Coze 配置", expanded=True):
            # 显示Coze相关配置
            st.text_input("Coze API Base", value=config.get("coze_api_base", ""), key="coze_api_base")
            st.text_input("Coze API Key", value=config.get("coze_api_key", ""), type="password", key="coze_api_key",help="请输入Coze API Key,在coze平台获取 https://www.coze.cn/open/oauth/pats")
            st.text_input("Coze Bot ID", value=config.get("coze_bot_id", ""), key="coze_bot_id",help="请输入Coze Bot ID,在coze平台获取 https://www.coze.cn/space/341****/bot/73428668*****")
            st.text_input("Coze Space ID", value=config.get("coze_space_id", ""), key="coze_space_id",help="Coze 工作空间ID")
            st.text_input("Coze Voice ID", value=config.get("coze_voice_id", ""), key="coze_voice_id",help="Coze 音色ID")
        
        # 微信配置 - 单聊
        with st.expander("微信单聊配置"):
            st.text_input("单聊回复前缀", value=config.get("single_chat_reply_prefix", ""), key="single_chat_reply_prefix",placeholder="私聊时自动回复的前缀，用于区分真人,例如：机器人")
            st.text_input("单聊回复后缀", value=config.get("single_chat_reply_suffix", ""), key="single_chat_reply_suffix",placeholder="私聊时自动回复的后缀，例如：机器人")
        
        # 微信配置 - 群聊
        with st.expander("微信群聊配置"):
            st.text_input("群聊前缀", value=", ".join(config.get("group_chat_prefix", [])), key="group_chat_prefix",placeholder="群聊时包含该前缀则会触发机器人回复,例如：@机器人")
            st.text_input("群聊白名单", value=", ".join(config.get("group_name_white_list", [])), key="group_name_white_list",placeholder="群聊白名单,请输入群聊名称,多个群聊名称用逗号隔开,例如:ChatGPT测试群,ChatGPT测试群2")
            
            no_need_at = config.get("no_need_at", "")
            no_need_at_value = False
            if isinstance(no_need_at, str):
                no_need_at_value = no_need_at.lower() == "true"
            elif isinstance(no_need_at, bool):
                no_need_at_value = no_need_at
                
            st.selectbox("群聊回复时是否不需要艾特", options=["false", "true"], 
                        index=1 if no_need_at_value else 0, 
                        key="no_need_at",
                        help="选择是否在群聊中不需要@机器人也能触发回复")
            
            st.text_input("群聊时包含该关键词则会触发机器人回复", value=config.get("group_chat_keyword", ""), key="group_chat_keyword",placeholder="群聊时包含该关键词则会触发机器人回复,例如：你好")
            st.text_input("群聊时自动回复的前缀", value=config.get("group_chat_reply_prefix", ""), key="group_chat_reply_prefix",placeholder="群聊时自动回复的前缀,例如：机器人")
            st.text_input("群聊时自动回复的后缀", value=config.get("group_chat_reply_suffix", ""), key="group_chat_reply_suffix",placeholder="群聊时自动回复的后缀,例如：机器人")
            
            group_at_off = config.get("group_at_off", "")
            group_at_off_value = False
            if isinstance(group_at_off, str):
                group_at_off_value = group_at_off.lower() == "true"
            elif isinstance(group_at_off, bool):
                group_at_off_value = group_at_off
                
            st.selectbox("是否关闭群聊时@bot的触发", options=["false", "true"], 
                        index=1 if group_at_off_value else 0, 
                        key="group_at_off",
                        help="选择是否关闭群聊中@机器人的触发功能")
        
        # 渠道配置
        with st.expander("渠道配置"):
            st.text_input("gewechat_app_id", value=config.get("gewechat_app_id", ""), key="gewechat_app_id",help="gewechat_app_id",placeholder="请勿配置，第一次运行自动生成")
            st.text_input("gewechat_token", value=config.get("gewechat_token", ""), key="gewechat_token",help="gewechat_token",placeholder="请勿配置，第一次运行自动生成")
            st.text_input("gewechat_base_url", value=config.get("gewechat_base_url", ""), key="gewechat_base_url",help="gewechat_base_url",placeholder="http://服务器 IP 地址:2531/v2/api")
            st.text_input("gewechat_callback_url", value=config.get("gewechat_callback_url", ""), key="gewechat_callback_url",help="gewechat_callback_url",placeholder="http://服务器 IP 地址:9919/v2/api/callback/collect")
            st.text_input("gewechat_download_url", value=config.get("gewechat_download_url", ""), key="gewechat_download_url",help="gewechat_download_url",placeholder="http://服务器 IP 地址:2532/download")
        
        # 语音配置
        with st.expander("语音配置"):
            speech_recognition = config.get("speech_recognition", "")
            speech_recognition_value = False
            if isinstance(speech_recognition, str):
                speech_recognition_value = speech_recognition.lower() == "true"
            elif isinstance(speech_recognition, bool):
                speech_recognition_value = speech_recognition
                
            st.selectbox("是否开启语音识别", options=["false", "true"], 
                        index=1 if speech_recognition_value else 0, 
                        key="speech_recognition",
                        help="选择是否开启语音识别功能")
            
            group_speech_recognition = config.get("group_speech_recognition", "")
            group_speech_recognition_value = False
            if isinstance(group_speech_recognition, str):
                group_speech_recognition_value = group_speech_recognition.lower() == "true"
            elif isinstance(group_speech_recognition, bool):
                group_speech_recognition_value = group_speech_recognition
                
            st.selectbox("是否开启群组语音识别", options=["false", "true"], 
                        index=1 if group_speech_recognition_value else 0, 
                        key="group_speech_recognition",
                        help="选择是否开启群组语音识别功能")
            
            voice_reply_voice = config.get("voice_reply_voice", "")
            voice_reply_voice_value = False
            if isinstance(voice_reply_voice, str):
                voice_reply_voice_value = voice_reply_voice.lower() == "true"
            elif isinstance(voice_reply_voice, bool):
                voice_reply_voice_value = voice_reply_voice
                
            st.selectbox("是否使用语音回复语音", options=["false", "true"], 
                        index=1 if voice_reply_voice_value else 0, 
                        key="voice_reply_voice",
                        help="选择是否使用语音回复语音消息")
            
            always_reply_voice = config.get("always_reply_voice", "")
            always_reply_voice_value = False
            if isinstance(always_reply_voice, str):
                always_reply_voice_value = always_reply_voice.lower() == "true"
            elif isinstance(always_reply_voice, bool):
                always_reply_voice_value = always_reply_voice
                
            st.selectbox("是否一直使用语音回复", options=["false", "true"], 
                        index=1 if always_reply_voice_value else 0, 
                        key="always_reply_voice",
                        help="选择是否总是使用语音回复")
            
            st.text_input("语音识别引擎", value=config.get("voice_to_text", ""), key="voice_to_text")
            st.text_input("语音合成引擎", value=config.get("text_to_voice", ""), key="text_to_voice")
        
        # 其他配置
        with st.expander("其他配置"):
            st.text_input("自动接受好友请求的申请信息", value=config.get("accept_friend_commands", ""), key="accept_friend_commands",help="自动接受好友请求的申请信息",placeholder="自动接受好友请求的申请信息,例如：加好友")
        
        # 保存按钮 - 使用主要按钮样式
        if st.button("💾 保存配置", type="primary"):
            # 更新配置
            config["coze_api_base"] = st.session_state.coze_api_base
            config["coze_api_key"] = st.session_state.coze_api_key
            config["coze_bot_id"] = st.session_state.coze_bot_id
            config["coze_space_id"] = st.session_state.coze_space_id
            config["coze_voice_id"] = st.session_state.coze_voice_id
            
            config["single_chat_reply_prefix"] = st.session_state.single_chat_reply_prefix
            config["single_chat_reply_suffix"] = st.session_state.single_chat_reply_suffix
            
            config["group_chat_prefix"] = [x.strip() for x in st.session_state.group_chat_prefix.split(",") if x.strip()]
            config["group_name_white_list"] = [x.strip() for x in st.session_state.group_name_white_list.split(",") if x.strip()]
            
            config["no_need_at"] = st.session_state.no_need_at.lower() == "true"
            config["group_at_off"] = st.session_state.group_at_off.lower() == "true"
            
            config["group_chat_keyword"] = st.session_state.group_chat_keyword
            config["group_chat_reply_prefix"] = st.session_state.group_chat_reply_prefix
            config["group_chat_reply_suffix"] = st.session_state.group_chat_reply_suffix
            
            config["gewechat_app_id"] = st.session_state.gewechat_app_id
            config["gewechat_token"] = st.session_state.gewechat_token
            config["gewechat_base_url"] = st.session_state.gewechat_base_url
            config["gewechat_callback_url"] = st.session_state.gewechat_callback_url
            config["gewechat_download_url"] = st.session_state.gewechat_download_url
            
            config["speech_recognition"] = st.session_state.speech_recognition.lower() == "true"
            config["group_speech_recognition"] = st.session_state.group_speech_recognition.lower() == "true"
            config["voice_reply_voice"] = st.session_state.voice_reply_voice.lower() == "true"
            config["always_reply_voice"] = st.session_state.always_reply_voice.lower() == "true"
            config["voice_to_text"] = st.session_state.voice_to_text
            config["text_to_voice"] = st.session_state.text_to_voice
            
            config["accept_friend_commands"] = st.session_state.accept_friend_commands
            
            # 写入配置文件
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            st.success("配置已保存")
        
        # 页脚
        st.markdown("""
        <div class="footer">
            <p>Coze on WeChat © 2025 | 如果我的项目对您有帮助请点一个star吧~</p>
        </div>
        """, unsafe_allow_html=True)
        
except Exception as e:
    st.error(f"读取配置文件失败: {str(e)}")
    st.info(f"配置文件路径: {config_path}")
