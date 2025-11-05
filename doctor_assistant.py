import os
import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory

# Sayfa yapılandırması
st.set_page_config(
    page_title="Doktor Asistanı",
    page_icon="🏥",
    layout="centered"
)

# CSS ile özel stil
st.markdown("""
    <style>
    .main {
        background-color: #f0f2f6;
    }
    .stTextInput > div > div > input {
        background-color: white;
    }
    .chat-message {
        padding: 1.5rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
        display: flex;
        flex-direction: column;
    }
    .user-message {
        background-color: #e3f2fd;
        border-left: 5px solid #2196F3;
    }
    .assistant-message {
        background-color: #f1f8e9;
        border-left: 5px solid #4CAF50;
    }
    </style>
""", unsafe_allow_html=True)

# API anahtarını yükle
load_dotenv()
api_key = os.getenv("API_KEY")

# Session state başlatma
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.messages = []
    st.session_state.name = ""
    st.session_state.age = ""

# LLM ve memory'yi başlat
@st.cache_resource
def initialize_llm():
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash-lite",
        temperature=0.7,
        google_api_key=api_key
    )
    return llm

def initialize_conversation(name, age):
    llm = initialize_llm()
    memory = ConversationBufferMemory(return_messages=True)
    conversation = ConversationChain(llm=llm, memory=memory, verbose=False)
    
    intro = (
        f"Sen bir doktor asistanısın. Hasta {name} {age} yaşında. "
        "Sağlık sorunları hakkında konuşmak istiyor. "
        "Yaşına uygun dikkatli ve nazik tavsiyeler ver. İsmiyle hitap et."
    )
    
    memory.chat_memory.add_user_message(intro)
    return conversation

# Başlık
st.title("🏥 Doktor Asistanı")
st.markdown("---")

# Kullanıcı bilgileri formu
if not st.session_state.initialized:
    st.subheader("👤 Hoş Geldiniz")
    st.write("Lütfen bilgilerinizi girin:")
    
    with st.form("user_info_form"):
        name = st.text_input("Adınız:", placeholder="Örn: Ahmet")
        age = st.text_input("Yaşınız:", placeholder="Örn: 35")
        submit = st.form_submit_button("Başla")
        
        if submit:
            if name and age:
                st.session_state.name = name
                st.session_state.age = age
                st.session_state.conversation = initialize_conversation(name, age)
                st.session_state.initialized = True
                
                # Hoş geldin mesajı
                welcome_msg = f"Merhaba {name}, ben bir doktor asistanıyım. Size nasıl yardımcı olabilirim?"
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": welcome_msg
                })
                st.rerun()
            else:
                st.error("Lütfen tüm alanları doldurun!")

# Chat arayüzü
else:
    # Sidebar - Kullanıcı bilgileri ve kontroller
    with st.sidebar:
        st.subheader("📋 Kullanıcı Bilgileri")
        st.write(f"**Ad:** {st.session_state.name}")
        st.write(f"**Yaş:** {st.session_state.age}")
        st.markdown("---")
        
        if st.button("🔄 Yeni Sohbet Başlat"):
            st.session_state.initialized = False
            st.session_state.messages = []
            st.rerun()
        
        st.markdown("---")
        st.info("💡 **Not:** Bu asistan tıbbi tavsiye vermez, yalnızca bilgilendirme amaçlıdır.")
    
    # Chat geçmişini göster
    chat_container = st.container()
    with chat_container:
        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f"""
                    <div class="chat-message user-message">
                        <strong>👤 {st.session_state.name}:</strong><br>
                        {message["content"]}
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                    <div class="chat-message assistant-message">
                        <strong>🏥 Asistan:</strong><br>
                        {message["content"]}
                    </div>
                """, unsafe_allow_html=True)
    
    # Mesaj giriş alanı
    st.markdown("---")
    user_input = st.text_input(
        "Mesajınız:",
        key="user_input",
        placeholder="Sorunuzu yazın...",
        label_visibility="collapsed"
    )
    
    col1, col2 = st.columns([6, 1])
    with col1:
        send_button = st.button("📤 Gönder", use_container_width=True)
    with col2:
        if st.button("🗑️"):
            st.session_state.messages = []
            st.rerun()
    
    # Mesaj gönderme
    if send_button and user_input:
        # Kullanıcı mesajını ekle
        st.session_state.messages.append({
            "role": "user",
            "content": user_input
        })
        
        # Asistan cevabını al
        with st.spinner("Düşünüyor..."):
            response = st.session_state.conversation.predict(input=user_input)
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })
        
        st.rerun()

# Alt bilgi
st.markdown("---")
st.markdown(
    "<center><small>🏥 Doktor Asistanı | Geliştirici: Mustafa Derinöz</small></center>",
    unsafe_allow_html=True
)