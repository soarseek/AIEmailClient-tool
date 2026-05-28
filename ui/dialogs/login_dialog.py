from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox, QCheckBox
from config.env_config import load_env_config, save_env_config

class SMTPLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle('SMTP登录')
        self.setModal(True)
        self.setFixedSize(350, 280)
        self.login_data = None
        self._setup_ui()
        self._load_saved_config()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        info_label = QLabel('请输入SMTP服务器信息（安全加密传输）')
        info_label.setStyleSheet('color: #666; font-size: 12px;')
        layout.addWidget(info_label)

        server_layout = QHBoxLayout()
        server_layout.addWidget(QLabel('SMTP服务器:'))
        self.server_edit = QLineEdit()
        self.server_edit.setText('smtp.qq.com')
        server_layout.addWidget(self.server_edit)
        layout.addLayout(server_layout)

        port_layout = QHBoxLayout()
        port_layout.addWidget(QLabel('端口:'))
        self.port_edit = QLineEdit()
        self.port_edit.setText('587')
        port_layout.addWidget(self.port_edit)
        layout.addLayout(port_layout)

        username_layout = QHBoxLayout()
        username_layout.addWidget(QLabel('邮箱:'))
        self.username_edit = QLineEdit()
        username_layout.addWidget(self.username_edit)
        layout.addLayout(username_layout)

        password_layout = QHBoxLayout()
        password_layout.addWidget(QLabel('授权码:'))
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.EchoMode.Password)
        password_layout.addWidget(self.password_edit)
        layout.addLayout(password_layout)

        secure_label = QLabel('端口465使用SSL加密，端口587使用TLS加密')
        secure_label.setStyleSheet('color: #888; font-size: 11px;')
        layout.addWidget(secure_label)

        self.save_checkbox = QCheckBox('记住登录信息')
        self.save_checkbox.setChecked(True)
        layout.addWidget(self.save_checkbox)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(10)
        self.login_btn = QPushButton('登录')
        self.login_btn.clicked.connect(self.on_login)
        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(self.login_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

    def _load_saved_config(self):
        config = load_env_config()
        if config.get('SMTP_SERVER'):
            self.server_edit.setText(config['SMTP_SERVER'])
        if config.get('SMTP_PORT'):
            self.port_edit.setText(config['SMTP_PORT'])
        if config.get('SMTP_USERNAME'):
            self.username_edit.setText(config['SMTP_USERNAME'])
        if config.get('SMTP_PASSWORD'):
            self.password_edit.setText(config['SMTP_PASSWORD'])

    def _save_config(self):
        if self.save_checkbox.isChecked():
            config = {
                'SMTP_SERVER': self.server_edit.text().strip(),
                'SMTP_PORT': self.port_edit.text().strip(),
                'SMTP_USERNAME': self.username_edit.text().strip(),
                'SMTP_PASSWORD': self.password_edit.text().strip()
            }
            save_env_config(config)

    def on_login(self):
        server = self.server_edit.text().strip()
        port = self.port_edit.text().strip()
        username = self.username_edit.text().strip()
        password = self.password_edit.text().strip()

        if not server:
            QMessageBox.warning(self, '警告', '请输入SMTP服务器')
            return
        if not port:
            QMessageBox.warning(self, '警告', '请输入端口')
            return
        if not username:
            QMessageBox.warning(self, '警告', '请输入邮箱')
            return
        if not password:
            QMessageBox.warning(self, '警告', '请输入授权码')
            return

        try:
            port = int(port)
        except ValueError:
            QMessageBox.warning(self, '警告', '端口必须是数字')
            return

        self._save_config()

        self.login_data = {
            'smtp_server': server,
            'smtp_port': port,
            'smtp_username': username,
            'smtp_password': password,
            'use_tls': port != 465
        }
        self.accept()