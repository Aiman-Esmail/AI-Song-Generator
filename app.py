import streamlit as st
import anthropic
import requests
import json
import re
import time
import os

# Config
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")
APIFRAME_KEY = os.environ.get("APIFRAME_API_KEY")

st.set_page_config(page_title="🎵 مولّد الأغاني بالذكاء الاصطناعي", layout="centered")

st.title("🎵 مولّد الأغاني بالذكاء الاصطناعي")
st.markdown("اكتب موضوع أغنيتك وسيتولّد لك أغنية كاملة بصوت وموسيقى!")

# إدخال المستخدم
theme = st.text_input("🎤 موضوع الأغنية", placeholder="مثال: الغربة والحنين للوطن")
language = st.selectbox("🌍 اللغة", ["عربي", "ألماني", "إنجليزي"])
mood = st.selectbox("🎭 المزاج", ["حزين", "رومانسي", "سعيد", "حماسي"])
genre = st.selectbox("🎸 النوع", ["شرقي", "بوب", "جاز", "هيب هوب"])

lang_map = {"عربي": "Arabic", "ألماني": "German", "إنجليزي": "English"}
mood_map = {"حزين": "sad", "رومانسي": "romantic", "سعيد": "happy", "حماسي": "energetic"}
genre_map = {"شرقي": "oriental", "بوب": "pop", "جاز": "jazz", "هيب هوب": "hip-hop"}

if st.button("🎵 ولّد الأغنية!", type="primary"):
    if not theme:
        st.error("اكتب موضوع الأغنية أولاً!")
    else:
        # كتابة الكلمات
        with st.spinner("✍️ جاري كتابة كلمات الأغنية..."):
            client = anthropic.Anthropic(api_key=ANTHROPIC_KEY)
            prompt = "Write a complete song in " + lang_map[language] + " about: " + theme
            prompt += ". Mood: " + mood_map[mood] + ". Return ONLY valid JSON: "
            prompt += '{"title":"العنوان","full_lyrics":"الكلمات","music_prompt":"description"}'
            
            msg = client.messages.create(
                model="claude-sonnet-4-5",
                max_tokens=2048,
                messages=[{"role": "user", "content": prompt}]
            )
            text = msg.content[0].text.strip()
            text = re.sub(r'```json|```', '', text).strip()
            text = text.replace(': null', ': ""')
            text = re.sub(r',\s*}', '}', text)
            lyrics = json.loads(text)
        
        st.success("✅ الكلمات جاهزة!")
        st.markdown("### 📝 " + lyrics['title'])
        st.text_area("كلمات الأغنية", lyrics['full_lyrics'], height=200)
        
        # توليد الأغنية
        with st.spinner("🎵 جاري توليد الأغنية... (1-2 دقيقة)"):
            url = "https://api.apiframe.ai/v2/music/generate"
            headers = {"X-API-Key": APIFRAME_KEY, "Content-Type": "application/json"}
            payload = {
                "model": "suno",
                "prompt": lyrics['full_lyrics'],
                "sunoParams": {
                    "custom_mode": True,
                    "instrumental": False,
                    "model_version": "V5",
                    "title": lyrics['title']
                }
            }
            response = requests.post(url, headers=headers, json=payload)
            job = response.json()
            job_id = job['jobId']
            
            # انتظار النتيجة
            for i in range(20):
                time.sleep(15)
                r = requests.get("https://api.apiframe.ai/v2/jobs/" + job_id, headers={"X-API-Key": APIFRAME_KEY})
                result = r.json()
                if result['status'] == 'COMPLETED':
                    tracks = result['result']['tracks']
                    st.success("🎉 الأغنية جاهزة!")
                    for i, track in enumerate(tracks):
                        st.markdown(f"### 🎵 النسخة {i+1}")
                        st.audio(track['audioUrl'])
                        st.markdown(f"[📥 تحميل MP3]({track['audioUrl']})")
                    break
