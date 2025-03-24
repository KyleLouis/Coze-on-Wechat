import streamlit as st

def check_password():
    """检查用户是否已登录"""
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
    
    if not st.session_state.logged_in:
        st.markdown("""
        <style>
            .login-container {
                max-width: 400px;
                margin: 100px auto;
                padding: 20px;
                background: white;
                border-radius: 10px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }
            .login-title {
                text-align: center;
                color: #4e54c8;
                margin-bottom: 20px;
            }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        st.markdown('<h2 class="login-title">Coze on WeChat 登录</h2>', unsafe_allow_html=True)
        
        username = st.text_input("用户名")
        password = st.text_input("密码", type="password")
        
        if st.button("登录"):
            # 这里设置默认的用户名和密码，你可以根据需要修改
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
                st.rerun()
            else:
                st.error("用户名或密码错误！")
        
        st.markdown('</div>', unsafe_allow_html=True)
        return False
    
    return True

def logout():
    """退出登录"""
    st.session_state.logged_in = False
    st.rerun() 