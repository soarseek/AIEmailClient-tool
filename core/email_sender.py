import os
import smtplib
import socket
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.utils import formataddr
from typing import List, Optional

SMTP_TIMEOUT = 15

class EmailSender:
    def __init__(self, smtp_server: str, smtp_port: int, username: str, password: str, use_tls: bool = True):
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.username = username
        self.password = password
        self.use_tls = use_tls

    def check_connection(self) -> tuple[bool, str]:
        try:
            if self.smtp_port == 465:
                context = ssl.create_default_context()
                with smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context, timeout=SMTP_TIMEOUT) as server:
                    server.login(self.username, self.password)
            else:
                with smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=SMTP_TIMEOUT) as server:
                    server.ehlo()
                    if self.use_tls:
                        context = ssl.create_default_context()
                        server.starttls(context=context)
                        server.ehlo()
                    server.login(self.username, self.password)
            return True, ""
        except socket.timeout:
            return False, "连接超时"
        except smtplib.SMTPAuthenticationError:
            return False, "认证失败"
        except smtplib.SMTPException as e:
            return False, f"SMTP错误"
        except Exception:
            return False, "连接失败"

    def _create_server(self) -> smtplib.SMTP:
        if self.smtp_port == 465:
            context = ssl.create_default_context()
            return smtplib.SMTP_SSL(self.smtp_server, self.smtp_port, context=context, timeout=SMTP_TIMEOUT)
        else:
            server = smtplib.SMTP(self.smtp_server, self.smtp_port, timeout=SMTP_TIMEOUT)
            server.ehlo()
            if self.use_tls:
                context = ssl.create_default_context()
                server.starttls(context=context)
                server.ehlo()
            return server

    def send_email(self, from_addr: str, to_addr: str, subject: str, body: str, attachments: Optional[List[str]] = None) -> bool:
        connected, error_msg = self.check_connection()
        if not connected:
            print(f"发送邮件失败: {error_msg}")
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = formataddr(('发送者', from_addr))
            msg['To'] = formataddr(('接收者', to_addr))
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain', 'utf-8'))
            if attachments:
                for file_path in attachments:
                    if os.path.exists(file_path):
                        with open(file_path, 'rb') as f:
                            part = MIMEApplication(f.read())
                            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(file_path))
                            msg.attach(part)
            server = self._create_server()
            server.login(self.username, self.password)
            server.sendmail(from_addr, to_addr, msg.as_string())
            server.quit()
            return True
        except smtplib.SMTPAuthenticationError:
            print(f"发送邮件失败: 认证失败")
            return False
        except smtplib.SMTPException:
            print(f"发送邮件失败: SMTP错误")
            return False
        except Exception:
            print(f"发送邮件失败")
            return False