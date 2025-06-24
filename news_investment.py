import os
import requests
import smtplib
from bs4 import BeautifulSoup
from email.mime.text import MIMEText
import openai

# ตั้งค่า OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# ดึงข่าวจาก Bloomberg Markets
def fetch_news():
    url = "https://www.bloomberg.com/markets"
    headers = {"User-Agent": "Mozilla/5.0"}
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")

    # ลองเลือกหลายๆแบบ (จากมากไปน้อย)
    selectors = [
        "a.story-package-module__story__headline-link",
        "h3",
        "div.headline",
        "a[data-testid='link']"
    ]

    headlines = []
    for selector in selectors:
        tags = soup.select(selector)
        if tags:
            headlines = [tag.text.strip() for tag in tags if tag.text.strip()]
            if headlines:
                break  # เจอแล้วไม่ต้องหา selector อื่น
    return "\n".join(headlines[:5]) if headlines else "ไม่พบข่าวจากเว็บไซต์"


# สรุปข่าวด้วย GPT
def summarize_news(news_text):
    messages = [{
        "role": "user",
        "content": f"""สรุปข่าวการลงทุนต่อไปนี้ให้อยู่ในรูปแบบ Timeline (เช่น  08:00 — [ข่าว])
จัดเรียงตามเวลาประมาณของเหตุการณ์ และกระชับให้เข้าใจง่าย:

ข่าว:
{news_text}
"""
    }]
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=messages
    )
    return response.choices[0].message.content.strip()

# ส่งอีเมลผ่าน Gmail
def send_email(subject, body):
    msg = MIMEText(body, "plain", "utf-8")
    msg["Subject"] = subject
    msg["From"] = os.getenv("EMAIL_USER")
    msg["To"] = os.getenv("EMAIL_TO")

    # ส่งผ่าน Gmail SMTP
    server = smtplib.SMTP_SSL("smtp.gmail.com", 465)
    server.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
    server.sendmail(msg["From"], [msg["To"]], msg.as_string())
    server.quit()

# รันโปรแกรม
if __name__ == "__main__":
    news = fetch_news()
    summary = summarize_news(news)
    send_email("📈 สรุปข่าวลงทุนรายวัน", summary)
