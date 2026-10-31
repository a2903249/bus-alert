import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv

load_dotenv()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 465


def send_email(to_email: str, subject: str, body: str) -> None:
    """用 Gmail SMTP 寄一封純文字信。失敗時會丟出例外。"""
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    from_name = os.getenv("SMTP_FROM_NAME", "Bus Alert")

    msg = EmailMessage()
    msg["From"] = f"{from_name} <{user}>"
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT, timeout=15) as server:
        server.login(user, password)
        server.send_message(msg)


def build_arrival_message(route_name: str, stop_name: str, eta_seconds: int) -> tuple[str, str]:
    """組出通知信的標題與內文。"""
    minutes = max(1, round(eta_seconds / 60))
    subject = f"【公車即將到站】{route_name} 路 約 {minutes} 分鐘後到 {stop_name}"
    body = (
        f"您訂閱的 {route_name} 路公車，預估約 {minutes} 分鐘後抵達「{stop_name}」。\n"
        f"預估時間會隨路況變動，請提前前往站牌。\n"
    )
    return subject, body