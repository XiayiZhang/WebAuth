import smtplib
from email.mime.text import MIMEText
from email.utils import formataddr
import secrets

# 配置邮件服务器（以微软邮箱为例）
SMTP_SERVER = "smtp.office365.com"
SMTP_PORT = 587
EMAIL_ADDRESS = ""
EMAIL_PASSWORD = ""  # 使用授权码而非邮箱密码

def send_verification_email(email, token):
    verification_link = f"http://accurately-usable-filly.ngrok-free.app/verify-email?token={token}"
    
    msg = MIMEText(f"""
    <h2>Minecraft 账号验证</h2>
    <p>请点击以下链接完成邮箱验证：</p>
    <a href="{verification_link}">{verification_link}</a>
    <p>验证码有效期30分钟</p>
    """, 'html')
    
    msg['Subject'] = '【重要】请验证您的邮箱'
    msg['From'] = formataddr(("ᴘʜɪʟᴏsᴏᴘʜᴇʀ♂ 𝐒𝐄𝐑𝐕𝐄𝐑", EMAIL_ADDRESS))
    msg['To'] = email
    
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(EMAIL_ADDRESS, EMAIL_PASSWORD)
        server.send_message(msg)