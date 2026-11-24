import streamlit as st
import os
import openai
import datetime as time
import json
from pathlib import Path
from python_rag_lyra.rag import rag
from python_rag_lyra.session import session as session_rag
"""

"""
r = rag("data/BCPONY.txt")
sessions_rag = session_rag(r.get_collection())

#初始化系统提示词
DEFAULT_PROMPT_PATH = Path(os.getenv("DEFAULT_PROMPT_PATH", "data/default_prompt.md"))
ROLE_PROMPT_PATH = Path(os.getenv("SYSTEM_PROMPT_PATH", "data/tianqin.md"))
DEFAULT_SYSTEM_PROMPT = DEFAULT_PROMPT_PATH.read_text(encoding="utf-8")
DEFAULT_ROLE_PROMPT = ROLE_PROMPT_PATH.read_text(encoding="utf-8")


def save_session():
    if st.session_state.current_session:
        session_date={
            "nick_name":st.session_state.nick_name,
            "role_prompt": st.session_state.role_prompt,
            "current_session":st.session_state.current_session,
            "messages":st.session_state.message
        }
    if not os.path.exists("sessions"):
        os.mkdir("sessions")
    with open(f"sessions/{st.session_state.current_session}.json","w",encoding="utf-8") as f:
        json.dump(session_date,f,ensure_ascii=False,indent=2)

def load_sessions():
    session_list = []
    if os.path.exists("sessions"):
        file_list = os.listdir("sessions")
        for filename in file_list:
            if filename.endswith(".json"):
                session_list.append(filename[:-5])
                session_list.sort(reverse=True)
    return session_list

def load_sessions_add(session_name):
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            with open(f"sessions/{session_name}.json","r",encoding="utf-8") as f:
                session_date=json.load(f)
                st.session_state.message=session_date["messages"]
                st.session_state.nick_name=session_date["nick_name"]
                st.session_state.nature=session_date["role_prompt"]
                st.session_state.current_session = session_name

    except Exception as e:
        st.error("error")

def delete_sessions(session_name):
    """"""
    try:
        if os.path.exists(f"sessions/{session_name}.json"):
            os.remove(f"sessions/{session_name}.json")
            if session_name == st.session_state.current_session:
                st.session_state.message = []
                st.session_state.current_session = generate_session_name()

    except Exception as e:
        st.error("error")

def generate_session_name():
    return time.datetime.now().strftime("%Y_%m_%d_%H_%M_%S")


# ==================== 页面基础配置 ====================
st.set_page_config(#st.session_state.message,
    page_title="角色扮演",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

#默认值设置
if "message" not in st.session_state:
    st.session_state.message = []

if "nick_name" not in st.session_state:
    st.session_state.nick_name = "天琴心弦"

if "role_prompt" not in st.session_state:
    st.session_state.role_prompt = DEFAULT_ROLE_PROMPT

if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

AVATARS = {"user": "✏️", "assistant": "🪉"}
#加载历史信息
for message in st.session_state.message:
    st.chat_message(
        message["role"],
        avatar=AVATARS.get(message["role"]),   
    
    ).write(message["content"])


client = openai.OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),base_url=os.getenv("DEEPSEEK_BASE_URL"))

#侧边栏
with (st.sidebar):
    st.subheader("ai控制面板")
    if st.button("新建会话", width="stretch"):
        if st.session_state.message:
        #保存会话print("tesprint("test")t")
            save_session()
        #创建新会话
            st.session_state.message=[]
            st.session_state.current_session=generate_session_name()
            save_session()
            st.rerun()
        else :
            pass

    possible_values = st.select_slider(
        "思考强度 none 关闭思考模式",
        options=[
            "none",
            "low",
            "high",
            "max",
            
        ],
    )
    #设置思考模式参数
    if possible_values == "none":
        thinking_type = "disabled"
    else:
        thinking_type = "enabled"
    col1, col2 = st.columns([1,1])
    with col1:
        temperature_value = st.number_input(
            "Temperature", value=1.0, placeholder="Type a number...",
            max_value=2.0,min_value=0.2,format="%0.1f",step=0.1) 
    with col2:  
        top_p_value = st.number_input(
                "Top_p", value=1.0, placeholder="Type a number...",
                max_value=1.0,min_value=0.1,format="%0.1f",step=0.1)   
    top_k_value =int( st.number_input(
        "Top_K", value=25, placeholder="Type a number...",
        max_value=100,min_value=25,step=1)) 
    
    st.divider()
    
    #参数设置
    st.subheader("角色信息")
    nick_name = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    role_prompt = st.text_area(
        "角色提示词（默认来自 data/tianqin.md）",
        value=st.session_state.role_prompt,
        height=300,)
    st.session_state.role_prompt = role_prompt

    if st.button("恢复默认角色提示词"):
        st.session_state.role_prompt = DEFAULT_ROLE_PROMPT
        st.rerun()
    #会话历史
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1, col2 = st.columns([4,1])
        with col1:
            if st.button(session,width="stretch",icon="📄",type="primary" if session == st.session_state.current_session else "secondary"):
                
                load_sessions_add(session)
                st.rerun()
        with col2:
            if st.button("", width="stretch",icon="🗑️",key=f"delete_{session}"):
                delete_sessions(session)
                st.rerun()
prompt = st.chat_input("请输入文字")

          
nick = (st.session_state.nick_name or "").strip() or "天琴心弦"

role = st.session_state.role_prompt.replace("天琴心弦", nick)

system_prompt = (
    f"{DEFAULT_SYSTEM_PROMPT}\n\n"
    f"{role}\n\n"
    f"【当前扮演】你的名字是「{nick}」，回答中以此自称。"
)
print(system_prompt)
if prompt:
    st.chat_message("user",avatar=AVATARS["user"]).write(prompt)
    print(prompt)
    print("collection count:", sessions_rag.collection.count())

    st.session_state.message.append({
        "role":"user",
        "content":prompt,
        })

    response = (client.chat.completions.create(
        model=os.getenv("DEEPSEEK_MODEL"),
        messages=[
        {
            "role": "system", 
            "content": system_prompt
        },
        *st.session_state.message,
        {
        "role":"user",
        "content":sessions_rag.context_chunks(prompt, top_k=top_k_value)
        }
        ],
        stream=True,
        temperature=temperature_value,
        top_p=top_p_value,
        max_tokens=512,
        extra_body={"thinking": {"type": thinking_type}},
        reasoning_effort = possible_values,

    ))

#流式输出
    response_message = st.empty()
    full_response = ""
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            full_response += content
            response_message.chat_message("assistant",avatar=AVATARS["assistant"]).write(full_response)

    # print(response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)
    st.session_state.message.append({
        "role":"assistant",
        "content":full_response
        })
    save_session()