import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QTextEdit, QPushButton, QListWidget, QListWidgetItem, QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QBrush

class EmailFormWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        sender_row = QWidget()
        sender_layout = QHBoxLayout(sender_row)
        sender_layout.setSpacing(10)

        sn_layout = QVBoxLayout()
        sn_layout.addWidget(QLabel('发件人姓名:'))
        self.sender_name_edit = QLineEdit()
        self.sender_name_edit.setPlaceholderText('输入发件人姓名')
        sn_layout.addWidget(self.sender_name_edit)
        sender_layout.addLayout(sn_layout)

        se_layout = QVBoxLayout()
        se_layout.addWidget(QLabel('发件人邮箱:'))
        self.sender_email_edit = QLineEdit()
        self.sender_email_edit.setReadOnly(True)
        self.sender_email_edit.setStyleSheet('QLineEdit:read-only { background-color: #f0f0f0; }')
        se_layout.addWidget(self.sender_email_edit)
        sender_layout.addLayout(se_layout)
        layout.addWidget(sender_row)

        subject_layout = QVBoxLayout()
        subject_layout.addWidget(QLabel('邮件标题:'))
        self.subject_edit = QLineEdit()
        self.subject_edit.setPlaceholderText('输入邮件标题')
        subject_layout.addWidget(self.subject_edit)
        layout.addLayout(subject_layout)

        self.recipient_row_widget = QWidget()
        recipient_layout = QHBoxLayout(self.recipient_row_widget)
        recipient_layout.setSpacing(10)

        rn_layout = QVBoxLayout()
        rn_layout.addWidget(QLabel('收件人姓名:'))
        self.recipient_name_edit = QLineEdit()
        self.recipient_name_edit.setPlaceholderText('输入收件人姓名')
        rn_layout.addWidget(self.recipient_name_edit)
        recipient_layout.addLayout(rn_layout)

        re_layout = QVBoxLayout()
        re_layout.addWidget(QLabel('收件人邮箱:'))
        self.recipient_email_edit = QLineEdit()
        self.recipient_email_edit.setPlaceholderText('输入收件人邮箱')
        re_layout.addWidget(self.recipient_email_edit)
        recipient_layout.addLayout(re_layout)
        layout.addWidget(self.recipient_row_widget)

        content_row = QWidget()
        content_layout = QHBoxLayout(content_row)
        content_layout.setSpacing(10)

        body_layout = QVBoxLayout()
        body_layout.addWidget(QLabel('邮件内容:'))
        self.body_edit = QTextEdit()
        self.body_edit.setMinimumHeight(60)
        body_layout.addWidget(self.body_edit)
        content_layout.addLayout(body_layout, 2)

        att_layout = QVBoxLayout()
        att_layout.addWidget(QLabel('附件:'))
        self.attachment_list = QListWidget()
        self.attachment_list.setMinimumHeight(60)
        self.attachment_list.setSelectionMode(QListWidget.SelectionMode.MultiSelection)
        att_layout.addWidget(self.attachment_list)
        btn_layout = QHBoxLayout()
        self.add_attachment_btn = QPushButton('添加附件')
        self.remove_attachment_btn = QPushButton('删除附件')
        self.remove_attachment_btn.setEnabled(False)
        btn_layout.addWidget(self.add_attachment_btn)
        btn_layout.addWidget(self.remove_attachment_btn)
        att_layout.addLayout(btn_layout)
        content_layout.addLayout(att_layout, 1)
        layout.addWidget(content_row)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.toggle_batch_btn = QPushButton('显示批量')
        self.reset_btn = QPushButton('重置')
        self.send_btn = QPushButton('发送')
        self.cancel_btn = QPushButton('取消')
        button_layout.addWidget(self.toggle_batch_btn)
        button_layout.addWidget(self.reset_btn)
        button_layout.addWidget(self.send_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)

    def get_form_data(self):
        return {
            'sender_name': self.sender_name_edit.text().strip(),
            'sender_email': self.sender_email_edit.text().strip(),
            'subject': self.subject_edit.text().strip(),
            'recipient_name': self.recipient_name_edit.text().strip(),
            'recipient_email': self.recipient_email_edit.text().strip(),
            'body': self.body_edit.toPlainText().strip(),
            'attachments': self.get_attachments()
        }

    def clear_form(self):
        self.sender_name_edit.clear()
        self.sender_email_edit.clear()
        self.subject_edit.clear()
        self.recipient_name_edit.clear()
        self.recipient_email_edit.clear()
        self.body_edit.clear()
        self.attachment_list.clear()

    def get_attachments(self):
        attachments = []
        for i in range(self.attachment_list.count()):
            item = self.attachment_list.item(i)
            file_path = item.data(Qt.ItemDataRole.UserRole)
            attachments.append(file_path if file_path else item.text())
        return attachments

    def set_form_data(self, data):
        self.sender_name_edit.setText(data.get('sender_name', ''))
        self.subject_edit.setText(data.get('subject', ''))
        self.recipient_name_edit.setText(data.get('recipient_name', ''))
        self.recipient_email_edit.setText(data.get('recipient_email', ''))
        self.body_edit.setText(data.get('body', ''))
        self.attachment_list.clear()
        for att in data.get('attachments', []):
            item = QListWidgetItem(os.path.basename(att))
            item.setData(Qt.ItemDataRole.UserRole, att)
            self.attachment_list.addItem(item)

    def set_inputs_enabled(self, enabled: bool):
        self.subject_edit.setEnabled(enabled)
        self.recipient_name_edit.setEnabled(enabled)
        self.recipient_email_edit.setEnabled(enabled)
        self.body_edit.setEnabled(enabled)
        self.add_attachment_btn.setEnabled(enabled)
        self.remove_attachment_btn.setEnabled(enabled and len(self.attachment_list.selectedItems()) > 0)
        self.attachment_list.setEnabled(enabled)

class BatchEmailWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        layout.setContentsMargins(10, 10, 10, 10)

        self.email_table = QTableWidget()
        self.email_table.setColumnCount(5)
        self.email_table.setHorizontalHeaderLabels(['收件人姓名', '收件人邮箱', '邮件标题', '内容/文件', '状态'])
        self.email_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.email_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.email_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.email_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Stretch)
        self.email_table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Fixed)
        self.email_table.setColumnWidth(4, 80)
        self.email_table.setMinimumHeight(120)
        self.email_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.email_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.email_table.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.email_table.setStyleSheet('QTableWidget::item:selected { background-color: #3498db; color: white; }')
        layout.addWidget(self.email_table)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.import_btn = QPushButton('导入CSV')
        self.add_row_btn = QPushButton('添加行')
        self.apply_all_btn = QPushButton('应用于全部')
        self.delete_row_btn = QPushButton('删除行')
        self.batch_send_btn = QPushButton('批量发送')
        button_layout.addWidget(self.import_btn)
        button_layout.addWidget(self.add_row_btn)
        button_layout.addWidget(self.apply_all_btn)
        button_layout.addWidget(self.delete_row_btn)
        button_layout.addWidget(self.batch_send_btn)
        layout.addLayout(button_layout)

    def add_email_item(self, recipient_name='', recipient_email='', content_or_file='', attachments=None, subject=''):
        row = self.email_table.rowCount()
        self.email_table.insertRow(row)
        self.email_table.setItem(row, 0, QTableWidgetItem(recipient_name))
        self.email_table.setItem(row, 1, QTableWidgetItem(recipient_email))
        self.email_table.setItem(row, 2, QTableWidgetItem(subject))
        has_content = bool(content_or_file) or (attachments and len(attachments) > 0)
        content_item = QTableWidgetItem('有内容' if has_content else '无内容')
        content_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        content_item.setData(Qt.ItemDataRole.UserRole, {'content': content_or_file, 'attachments': attachments or []})
        self.email_table.setItem(row, 3, content_item)
        status_item = QTableWidgetItem('未发送')
        status_item.setForeground(QBrush(QColor('red')))
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.email_table.setItem(row, 4, status_item)

    def delete_selected_rows(self):
        rows = sorted(set(item.row() for item in self.email_table.selectedItems()), reverse=True)
        for row in rows:
            self.email_table.removeRow(row)

    def update_status(self, row, success):
        status_item = QTableWidgetItem('已发送' if success else '未发送')
        status_item.setForeground(QBrush(QColor('green') if success else QColor('red')))
        status_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
        self.email_table.setItem(row, 4, status_item)

    def get_email_list(self):
        result = []
        for r in range(self.email_table.rowCount()):
            content_item = self.email_table.item(r, 3)
            data = content_item.data(Qt.ItemDataRole.UserRole) if content_item else {}
            content = data.get('content', '') if isinstance(data, dict) else ''
            attachments = data.get('attachments', []) if isinstance(data, dict) else []
            result.append({
                'recipient_name': self.email_table.item(r, 0).text() if self.email_table.item(r, 0) else '',
                'recipient_email': self.email_table.item(r, 1).text() if self.email_table.item(r, 1) else '',
                'subject': self.email_table.item(r, 2).text() if self.email_table.item(r, 2) else '',
                'content': content,
                'attachments': attachments
            })
        return result

    def get_selected_row_data(self):
        rows = sorted(set(item.row() for item in self.email_table.selectedItems()))
        if not rows:
            return None
        r = rows[0]
        content_item = self.email_table.item(r, 3)
        data = content_item.data(Qt.ItemDataRole.UserRole) if content_item else {}
        content = data.get('content', '') if isinstance(data, dict) else (data or '')
        attachments = data.get('attachments', []) if isinstance(data, dict) else []
        return {
            'row': r,
            'recipient_name': self.email_table.item(r, 0).text() if self.email_table.item(r, 0) else '',
            'recipient_email': self.email_table.item(r, 1).text() if self.email_table.item(r, 1) else '',
            'subject': self.email_table.item(r, 2).text() if self.email_table.item(r, 2) else '',
            'body': content,
            'attachments': attachments
        }

    def update_selected_row(self, data):
        rows = sorted(set(item.row() for item in self.email_table.selectedItems()))
        if not rows:
            return
        r = rows[0]
        self.email_table.setItem(r, 0, QTableWidgetItem(data.get('recipient_name', '')))
        self.email_table.setItem(r, 1, QTableWidgetItem(data.get('recipient_email', '')))
        self.email_table.setItem(r, 2, QTableWidgetItem(data.get('subject', '')))
        content = data.get('body', '')
        attachments = data.get('attachments', [])
        has_content = bool(content) or (attachments and len(attachments) > 0)
        content_item = QTableWidgetItem('有内容' if has_content else '无内容')
        content_item.setData(Qt.ItemDataRole.UserRole, {'content': content, 'attachments': attachments})
        self.email_table.setItem(r, 3, content_item)

    def update_all_rows(self, data):
        row_count = self.email_table.rowCount()
        if row_count == 0:
            return
        subject = data.get('subject', '')
        content = data.get('body', '')
        attachments = data.get('attachments', [])
        has_content = bool(content) or (attachments and len(attachments) > 0)
        for r in range(row_count):
            self.email_table.setItem(r, 0, QTableWidgetItem(data.get('recipient_name', '')))
            self.email_table.setItem(r, 1, QTableWidgetItem(data.get('recipient_email', '')))
            self.email_table.setItem(r, 2, QTableWidgetItem(subject))
            content_item = QTableWidgetItem('有内容' if has_content else '无内容')
            content_item.setData(Qt.ItemDataRole.UserRole, {'content': content, 'attachments': attachments})
            self.email_table.setItem(r, 3, content_item)

    def clear_table(self):
        self.email_table.setRowCount(0)