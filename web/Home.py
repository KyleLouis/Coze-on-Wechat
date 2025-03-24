import streamlit as st
import subprocess
import os
import sys
import time
import json
import shutil
from PIL import Image
from utils.auth import check_password, logout

# 使用绝对路径
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
icon_path = os.path.join(project_root, "docs", "ico.ico")
app_path = os.path.join(project_root, "app.py")

# 检查登录状态
if not check_password():
    st.stop()

if os.path.exists(icon_path):
    icon = Image.open(icon_path)
else:
    print(f"图标文件不存在: {icon_path}")

st.set_page_config(
    page_title="Coze on WeChat", 
    page_icon=icon,
    layout="wide",
    initial_sidebar_state="collapsed",
    menu_items={
        'Report a bug': "https://github.com/JC0v0/Coze-on-Wechat/issues",
        'About': "本项目基于chatgpt-on-wechat和dify-on-wechat 二次开发，主要是对接 coze 平台如果我的项目对您有帮助请点一个star吧~"
    }
)

# 添加自定义CSS样式
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
    .log-container {
        background-color: #f8f9fa;
        border-radius: 10px;
        padding: 10px;
        height: 400px;
        overflow-y: auto;
    }
    .footer {
        text-align: center;
        margin-top: 30px;
        padding: 10px;
        font-size: 0.8em;
        color: #6c757d;
    }
    /* 新增日志滚动容器样式 */
    .log-scroll-container {
        height: 400px;
        overflow-y: auto;
        border: 1px solid #e6e6e6;
        border-radius: 5px;
        padding: 10px;
        background-color: #f8f9fa;
        font-family: monospace;
    }
    /* 优化日志行样式 */
    .log-scroll-container pre {
        margin: 0;
        white-space: pre-wrap;
        word-wrap: break-word;
    }
    .log-scroll-container span {
        display: block;
        line-height: 1.5;
        margin-bottom: 2px;
        padding: 2px 0;
    }
</style>
""", unsafe_allow_html=True)

# 标题和介绍
st.markdown("""
<div class="main-header">
    <h1>Coze on WeChat</h1>
    <p>本项目基于chatgpt-on-wechat和dify-on-wechat 二次开发，主要是对接 coze 平台</p>
</div>
""", unsafe_allow_html=True)

# 尝试显示图标
try:
    coze_icon_path = os.path.join(project_root, "docs", "coze_icon.png")
    if os.path.exists(coze_icon_path):
        st.image(coze_icon_path, width=100)
    else:
        st.info("Coze图标文件不存在")
except Exception as e:
    st.error(f"加载图标失败: {str(e)}")

# 创建一个会话状态变量来跟踪程序是否正在运行
if 'process' not in st.session_state:
    st.session_state.process = None
    st.session_state.running = False
    st.session_state.output = []

# 检查配置文件是否存在，如果不存在则创建
def ensure_config_exists():
    config_template_path = os.path.join(project_root, "config-template.json")
    config_path = os.path.join(project_root, "config.json")
    
    if not os.path.exists(config_path):
        if os.path.exists(config_template_path):
            # 复制模板文件
            shutil.copy(config_template_path, config_path)
            st.success("已创建配置文件 config.json")
            return True
        else:
            st.error(f"配置模板文件不存在: {config_template_path}")
            return False
    return True

def start_app():
    if not st.session_state.running:
        # 先确保配置文件存在
        if not ensure_config_exists():
            st.error("无法启动程序，因为配置文件不存在")
            return
            
        try:
            # 使用Python解释器运行app.py
            process = subprocess.Popen(
                [sys.executable, app_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                cwd=project_root  # 设置工作目录为项目根目录
            )
            st.session_state.process = process
            st.session_state.running = True
            st.session_state.output = []
            
            # 显示成功消息
            st.success("程序已启动！")
        except Exception as e:
            st.error(f"启动失败: {str(e)}")
    else:
        st.warning("程序已经在运行中")

def stop_app():
    if st.session_state.running and st.session_state.process:
        try:
            # 在Windows上使用taskkill强制终止进程及其子进程
            if os.name == 'nt':
                subprocess.run(['taskkill', '/F', '/T', '/PID', str(st.session_state.process.pid)])
            else:
                st.session_state.process.terminate()
                st.session_state.process.wait(timeout=5)
            
            st.session_state.process = None
            st.session_state.running = False
            st.success("程序已停止")
        except Exception as e:
            st.error(f"停止失败: {str(e)}")
    else:
        st.warning("程序未在运行")

# 创建两列布局
col1, col2 = st.columns([1, 2])

with col1:
    # 状态卡片
    if st.session_state.running:
        # 检查进程是否仍在运行
        if st.session_state.process and st.session_state.process.poll() is not None:
            st.session_state.running = False
            st.markdown("""
            <div class="status-card stopped">
                <h3>⚠️ 程序已意外停止</h3>
                <p>退出代码：{}</p>
            </div>
            """.format(st.session_state.process.returncode), unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class="status-card running">
                <h3>✅ 程序状态: 运行中</h3>
                <p>Coze on WeChat 正在后台运行</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="status-card stopped">
            <h3>⏹️ 程序状态: 已停止</h3>
            <p>点击"启动程序"按钮开始运行</p>
        </div>
        """, unsafe_allow_html=True)
    
    # 控制按钮
    st.markdown("### 控制面板")
    if st.button("🚀 启动程序", type="primary", key="start_button"):
        start_app()
    
    if st.button("⏹️ 停止程序", type="secondary", key="stop_button"):
        stop_app()
    
    # 添加GitHub链接
    st.markdown("### 项目链接")
    st.markdown("[🔗 GitHub 项目主页](https://github.com/JC0v0/Coze-on-Wechat)")
    
    # 添加机器人配置按钮
    if st.button("⚙️ 机器人配置", key="bot_config_button"):
        # 使用最新版本的Streamlit导航方式
        st.switch_page("pages/01_机器人配置.py")
    
    # 添加刷新按钮
    if st.button("🔄 刷新页面", key="refresh_button"):
        st.rerun()
        
    # 添加退出登录按钮
    if st.button("🚪 退出登录", type="secondary", key="logout_button"):
        logout()

with col2:
    # 日志显示区域
    st.markdown("### 📋 程序日志")
    
    # 添加日志过滤选项
    log_filter = st.selectbox(
        "日志级别过滤",
        ["全部", "INFO", "WARNING", "ERROR", "DEBUG"],
        index=0
    )
    
    # 读取run.log文件内容
    log_file_path = os.path.join(project_root, "run.log")
    if os.path.exists(log_file_path):
        try:
            with open(log_file_path, "r", encoding="utf-8") as f:
                log_content = f.readlines()
            
            # 根据选择的日志级别过滤
            if log_filter != "全部":
                log_content = [line for line in log_content if f"[{log_filter}]" in line]
            
            # 限制显示最新的100行日志
            if len(log_content) > 100:
                log_content = log_content[-100:]
            
            # 使用st.markdown和HTML创建可滚动容器
            log_html = "<div class=\"log-scroll-container\"><pre>"
            
            # 用于检测是否有二维码链接
            qr_code_url = None
            qr_image_path = None
            # 检测是否已登录成功
            login_success = False
            
            for line in log_content:
                # 检测登录成功信息
                if any(success_text in line for success_text in [
                    "用户昵称",
                ]):
                    login_success = True
                
                # 检测二维码链接
                if "您可以访问下方链接获取二维码" in line and "https://api.qrserver.com/v1/create-qr-code/?data=" in line:
                    try:
                        # 提取二维码链接
                        start_idx = line.find("https://api.qrserver.com/v1/create-qr-code/?data=")
                        if start_idx != -1:
                            qr_code_url = line[start_idx:].strip()
                    except:
                        pass
                
                # 检测二维码图片路径（绝对路径）
                if "二维码已保存至" in line:
                    try:
                        # 提取路径
                        start_idx = line.find("二维码已保存至") + len("二维码已保存至")
                        path_part = line[start_idx:].strip()
                        if os.path.exists(path_part):
                            qr_image_path = path_part
                        elif "/tmp/login.png" in path_part:
                            # 尝试从路径中提取tmp/login.png部分
                            tmp_idx = path_part.find("/tmp/login.png")
                            if tmp_idx != -1:
                                relative_path = path_part[tmp_idx+1:]  # 去掉开头的/
                                if os.path.exists(relative_path):
                                    qr_image_path = relative_path
                    except:
                        pass
                
                # 根据日志级别添加不同的颜色
                if "[ERROR]" in line:
                    log_html += f"<span style='color: red;'>{line}</span>"
                elif "[WARNING]" in line:
                    log_html += f"<span style='color: orange;'>{line}</span>"
                elif "[INFO]" in line:
                    log_html += f"<span style='color: green;'>{line}</span>"
                elif "[DEBUG]" in line:
                    log_html += f"<span style='color: blue;'>{line}</span>"
                else:
                    log_html += f"<span>{line}</span>"
            log_html += "</pre></div>"
            
            st.markdown(log_html, unsafe_allow_html=True)
            
            
            
            # 如果找到二维码图片路径且未登录成功，显示二维码
            if qr_image_path and not login_success:
                st.markdown("### 登录二维码")
                try:
                    # 检查文件是否存在
                    if os.path.exists(qr_image_path):
                        st.image(qr_image_path, caption="扫描此二维码登录")
                        st.success("二维码已加载成功")
                    else:
                        st.error(f"二维码文件不存在: {qr_image_path}")
                        # 尝试在tmp目录中查找login.png
                        tmp_login_path = os.path.join(os.getcwd(), 'tmp', 'login.png')
                        if os.path.exists(tmp_login_path) and not login_success:
                            st.image(tmp_login_path, caption="扫描此二维码登录")
                            st.success(f"已从备用路径加载二维码: {tmp_login_path}")
                except Exception as e:
                    st.error(f"加载二维码图片失败: {str(e)}")
                    st.error(f"图片路径: {qr_image_path}")
            else:
                # 即使没有在日志中检测到二维码路径，也尝试在tmp目录中查找login.png
                tmp_login_path = os.path.join(os.getcwd(), 'tmp', 'login.png')
                if os.path.exists(tmp_login_path) and not login_success:
                    st.markdown("### 登录二维码")
                    st.image(tmp_login_path, caption="扫描此二维码登录")
                    st.success(f"已从默认路径加载二维码: {tmp_login_path}")
            
            # 如果已登录成功，显示登录成功信息
            if login_success:
                st.success("✅ 已成功登录微信")
        except Exception as e:
            st.error(f"读取日志文件失败: {str(e)}")
    else:
        st.info("日志文件尚未创建")

# 页脚
st.markdown("""
<div class="footer">
    <p>Coze on WeChat © 2025 | 如果我的项目对您有帮助请点一个star吧~</p>
</div>
""", unsafe_allow_html=True)

# 使用Streamlit的原生自动刷新功能
if st.session_state.running:
    time.sleep(2)  # 延迟时间稍微增加，减少刷新频率
    st.rerun()  # 使用st.rerun()代替JavaScript刷新