import smtplib
import ssl
import socket
from PyQt6.QtCore import QThread, pyqtSignal
from core.utils import is_valid_email

SMTP_TIMEOUT = 15

class EmailWorker(QThread):
    progress = pyqtSignal(int, int, str, str, str)
    status_update = pyqtSignal(int, bool)
    finished = pyqtSignal(int, int)
    canceled = pyqtSignal()

    def __init__(self, email_list, smtp_config, sender_email):
        super().__init__()
        self.email_list = email_list
        self.smtp_config = smtp_config
        self.sender_email = sender_email
        self._canceled = False
        self._server = None

    def cancel(self):
        self._canceled = True

    def _check_connection(self) -> bool:
        try:
            smtp_port = self.smtp_config['smtp_port']
            if smtp_port == 465:
                context = ssl.create_default_context()
                self._server = smtplib.SMTP_SSL(self.smtp_config['smtp_server'], smtp_port, context=context, timeout=SMTP_TIMEOUT)
            else:
                self._server = smtplib.SMTP(self.smtp_config['smtp_server'], smtp_port, timeout=SMTP_TIMEOUT)
                self._server.ehlo()
                if self.smtp_config['use_tls']:
                    context = ssl.create_default_context()
                    self._server.starttls(context=context)
                    self._server.ehlo()
            self._server.login(self.smtp_config['smtp_username'], self.smtp_config['smtp_password'])
            return True
        except (socket.timeout, smtplib.SMTPException, OSError):
            if self._server:
                try:
                    self._server.quit()
                except:
                    pass
                self._server = None
            return False
        except Exception:
            if self._server:
                try:
                    self._server.quit()
                except:
                    pass
                self._server = None
            return False

    def _send_one(self, to_addr: str, subject: str, body: str, attachments) -> bool:
        try:
            from email.mime.text import MIMEText
            from email.mime.multipart import MIMEMultipart
            from email.mime.application import MIMEApplication
            from email.utils import formataddr
            import os

            msg = MIMEMultipart()
            msg['From'] = formataddr(('发送者', self.sender_email))
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
            self._server.sendmail(self.sender_email, to_addr, msg.as_string())
            return True
        except Exception:
            return False

    def run(self):
        if not self._check_connection():
            for r in range(len(self.email_list)):
                self.status_update.emit(r, False)
            self.finished.emit(0, len(self.email_list))
            return

        success = 0
        fail = 0
        total = len(self.email_list)

        for r, item in enumerate(self.email_list):
            if self._canceled:
                break

            self.progress.emit(r + 1, total, item['recipient_name'], item['recipient_email'], item['content'])

            if not item['recipient_email'] or not is_valid_email(item['recipient_email']):
                self.status_update.emit(r, False)
                fail += 1
                continue

            subject = item.get('subject', '') if item.get('subject', '') else '批量邮件发送'
            body = item['content'] if item['content'] else f"收件人: {item['recipient_name']}"
            attachments = item['attachments'] if isinstance(item['attachments'], list) else []

            if self._send_one(item['recipient_email'], subject, body, attachments):
                self.status_update.emit(r, True)
                success += 1
            else:
                self.status_update.emit(r, False)
                fail += 1

        if self._server:
            try:
                self._server.quit()
            except:
                pass
            self._server = None

        self.finished.emit(success, fail)