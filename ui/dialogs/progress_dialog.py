from PyQt6.QtWidgets import QDialog, QVBoxLayout, QProgressBar, QLabel, QTextEdit, QPushButton

class ProgressDialog(QDialog):
    def __init__(self, total, parent=None):
        super().__init__(parent)
        self.setWindowTitle('正在处理...')
        self.setModal(True)
        self.setFixedSize(450, 300)
        self.canceled = False
        self._setup_ui(total)

    def _setup_ui(self, total):
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 20, 20, 20)

        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, total)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)

        self.status_label = QLabel('准备发送...')
        layout.addWidget(self.status_label)

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setFixedHeight(150)
        layout.addWidget(self.info_text)

        self.cancel_btn = QPushButton('取消')
        self.cancel_btn.clicked.connect(self.on_cancel)
        layout.addWidget(self.cancel_btn)

    def update_progress(self, current, total, recipient_name, recipient_email, content):
        self.progress_bar.setValue(current)
        self.status_label.setText(f'正在发送 ({current}/{total})...')
        content_preview = content[:20] + '...' if len(content) > 20 else content
        info = f"收件人：{recipient_name}\n收件人邮箱：{recipient_email}\n内容：{content_preview}\n\n"
        self.info_text.append(info)
        self.info_text.verticalScrollBar().setValue(self.info_text.verticalScrollBar().maximum())

    def on_cancel(self):
        self.canceled = True