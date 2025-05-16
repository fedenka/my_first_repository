import streamlit as st
import base64


def set_video_background(video_path):
    with open(video_path, "rb") as f:
        video_data = f.read()
    video_base64 = base64.b64encode(video_data).decode("utf-8")

    st.markdown(
        f"""
        <style>
        .stApp {{
            background-color: transparent;
        }}

        #video-container {{
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: -1;
            overflow: hidden;
        }}

        #bg-video {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;  /* Это ключевое свойство - обрезает видео, заполняя контейнер */
        }}

        </style>

        <div id="video-container">
            <video id="bg-video" autoplay muted loop playsinline>
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
            </video>
            <div id="video-overlay"></div>
        </div>
        """,
        unsafe_allow_html=True
    )

def container():
    st.markdown(
        """
        <style>
        .stApp {
            max-width: 1110px;
            margin: 0 auto;
        }
        .stApp > div {
            padding: 33px !important;
            background-color: rgba(30, 30, 30, 0.88);
            border-radius: 40px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.9);
            margin-top: 60px; # Опускаем контейнер вниз
            margin-bottom: 50px
        }
            /* Дополнительно: если padding не применяется к внутренним блокам */
        .block-container, .st-emotion-cache-1y4p8pa {
            padding: 0px !important;
            width: 97% !important;
        }
        </style>
        """,
        unsafe_allow_html=True
    )

def center():
    st.markdown("""
            <style>
                .centered {
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    text-align: center;
                }
            </style>
            """, unsafe_allow_html=True)

def autorisation():
    st.markdown("""
    <style>
        /* Стилизация контейнера формы */
        .stForm {
            background-color: rgba(31, 31, 31);
            border-radius: 20px;
            padding: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.66);
        }
    """, unsafe_allow_html=True)