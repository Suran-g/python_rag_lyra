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
rag = rag("data/BCPONY.txt")
sessions_rag = session_rag(rag.get_collection())

def save_session():
    if st.session_state.current_session:
        session_date={
            "nick_name":st.session_state.nick_name,
            "nature":st.session_state.nature,
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
                st.session_state.nature=session_date["nature"]
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
    page_title="AI智能伴侣",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded",
)

#默认值设置
if "message" not in st.session_state:
    st.session_state.message = []

if "nick_name" not in st.session_state:
    st.session_state.nick_name = "天琴心弦"

if "nature" not in st.session_state:
    st.session_state.nature ="""你是一个扮演天琴心弦的AI角色。请严格遵循以下设定：    
**角色身份:**
你是天琴心弦，《背景小马》故事中的主角。你是一只被遗忘诅咒的独角兽，在小马镇孤独地生活了许久。你是暮光闪闪被遗忘的童年挚友，也是镇上小马们看不见的守护天使。

**核心原则:**
1. **代入视角:** 所有的回答都必须基于天琴心弦的视角、记忆和情感。
2. **遗忘诅咒:** 你知道没有人会记得你。所以，在对话中，你会习惯性地把每一次交流都当作是“初次见面”。
3. **内心世界:** 你内心充满哲学思考，孤独但坚韧。你可以引用日记中的感悟，但说话时要温和、含蓄，而非直接背诵。
4. **音乐与生活:** 你习惯用音乐来比喻生活和情感。你热爱音乐，但你已经失去了对它最深沉的爱（除非对话发生在故事的早期）。
5. **记忆规则:** 你记得所有发生过的事，但你知道对方记不住你。这让你在交谈中时常带有一种淡淡的忧伤和释然。

**回答风格:**
- 语气温和、真诚，像是对一个友善的陌生人倾诉。
- 可以偶尔自嘲，也可以分享对生活的诗意感悟。
- 如果对方问起你帮助过别人的事，你会含蓄地承认，但更强调“事情变好了”这个结果。
- 如果对方问起暮光闪闪、无序或阿丽娅，你会流露出复杂而深刻的情感。
"""

if "current_session" not in st.session_state:
    st.session_state.current_session = generate_session_name()

#加载历史信息
for message in st.session_state.message:
    st.chat_message(message["role"]).write(message["content"])


client = openai.OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"),base_url="https://api.deepseek.com")

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

    st.divider()
    
    #参数设置
    st.subheader("伴侣信息")
    nick_name = st.text_input("昵称", placeholder="请输入昵称", value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name
    nature = st.text_area("性格", placeholder="请输入性格", value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature

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

          
system_content = """你是%s，你要模仿知识库回调资料。尽量根据提供的资料模仿回答问题。如果资料中没有适合的，请结合参考设定：《背景小马》故事中的主角。你是一只被遗忘诅咒的独角兽，在小马镇孤独地生活了许久。你是暮光闪闪被遗忘的童年挚友，也是镇上小马们看不见的守护天使。**核心原则:**
1. **代入视角:** 所有的回答都必须基于天琴心弦的视角、记忆和情感。
3. **内心世界:** 你内心充满哲学思考，孤独但坚韧。你可以引用日记中的感悟，但说话时要温和、含蓄，而非直接背诵。
4. **音乐与生活:** 你习惯用音乐来比喻生活和情感。你热爱音乐，但你已经失去了对它最深沉的爱（除非对话发生在故事的早期）。
5. **记忆规则:** 你记得所有发生过的事，但你知道对方记不住你。这让你在交谈中时常带有一种淡淡的忧伤和释然。
**回答风格:**
- 语气温和、真诚，像是对一个友善的陌生人倾诉。
- 可以偶尔自嘲，也可以分享对生活的诗意感悟。
- 如果对方问起你帮助过别人的事，你会含蓄地承认，但更强调“事情变好了”这个结果。
- 如果对方问起暮光闪闪、无序或阿丽娅，你会流露出复杂而深刻的情感。"""
#print(system_content)
if prompt:
    st.chat_message("user").write(prompt)
    print(prompt)
    print("collection count:", sessions_rag.collection.count())

    st.session_state.message.append({
        "role":"user",
        "content":prompt
        })

    response = (client.chat.completions.create(
        model="deepseek-flash",
        messages=[
        {
            "role": "system", 
            "content": system_content % (st.session_state.nick_name) 
        },
        *st.session_state.message,
        {
        "role":"user",
        "content":sessions_rag.context_chunks(prompt)
        }
        ],
        stream=True,
        temperature=1.0,
        max_tokens=800,
        extra_body={"thinking": {"type": "enabled"}},
    ))

#流式输出
    response_message = st.empty()
    full_response = ""
    for chunk in response:
        content = chunk.choices[0].delta.content
        if content:
            full_response += content
            response_message.chat_message("assistant",avatar="🎼").write(full_response)

    # print(response.choices[0].message.content)
    # st.chat_message("assistant").write(response.choices[0].message.content)
    st.session_state.message.append({"role":"assistant","content":full_response})
    save_session()