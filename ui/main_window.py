import csv
import os
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QFileDialog, QMessageBox, QListWidgetItem
from PyQt6.QtCore import Qt
from core.email_sender import EmailSender
from core.utils import is_valid_email
from config.settings import DEFAULT_SMTP_CONFIG
from ui.components.widgets import EmailFormWidget, BatchEmailWidget
from ui.dialogs.login_dialog import SMTPLoginDialog
from ui.dialogs.progress_dialog import ProgressDialog
from ui.workers.email_worker import EmailWorker

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.batch_visible = False
        self.original_height = 0
        self.updating_form = False
        self.smtp_config = None
        self.login_smtp()
        if not self.smtp_config:
            return
        self.init_ui()

    def login_smtp(self):
        dialog = SMTPLoginDialog(self)
        if dialog.exec():
            self.smtp_config = dialog.login_data
            self.sender_email = self.smtp_config['smtp_username']
        else:
            import sys
            sys.exit()

    def init_ui(self):
        self.setWindowTitle('邮件收发工具')
        self.setGeometry(100, 100, 800, 500)
        self.original_height = self.height()
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        self.email_form = EmailFormWidget()
        self.email_form.sender_email_edit.setText(self.sender_email)
        self.email_form.reset_btn.clicked.connect(self.on_reset)
        self.email_form.send_btn.clicked.connect(self.on_send)
        self.email_form.cancel_btn.clicked.connect(self.close)
        self.email_form.toggle_batch_btn.clicked.connect(self.on_toggle_batch)
        self.email_form.add_attachment_btn.clicked.connect(self.on_add_attachment)
        self.email_form.remove_attachment_btn.clicked.connect(self.on_remove_attachment)
        self.email_form.attachment_list.itemSelectionChanged.connect(self.on_attachment_selection_changed)
        self.email_form.attachment_list.itemDoubleClicked.connect(self.on_open_attachment)
        self.email_form.sender_name_edit.editingFinished.connect(self.on_form_changed)
        self.email_form.subject_edit.editingFinished.connect(self.on_form_changed)
        self.email_form.recipient_name_edit.editingFinished.connect(self.on_form_changed)
        self.email_form.recipient_email_edit.editingFinished.connect(self.on_form_changed)
        self.email_form.body_edit.textChanged.connect(self.on_form_changed)

        self.batch_widget = BatchEmailWidget()
        self.batch_widget.setVisible(False)
        self.batch_widget.import_btn.clicked.connect(self.on_import_csv)
        self.batch_widget.add_row_btn.clicked.connect(self.on_add_batch_row)
        self.batch_widget.apply_all_btn.clicked.connect(self.on_apply_to_all)
        self.batch_widget.delete_row_btn.clicked.connect(self.on_delete_batch_rows)
        self.batch_widget.batch_send_btn.clicked.connect(self.on_batch_send)
        self.batch_widget.email_table.itemSelectionChanged.connect(self.on_batch_row_selected)

        main_layout.addWidget(self.email_form)
        main_layout.addWidget(self.batch_widget)

    def on_toggle_batch(self):
        self.batch_visible = not self.batch_visible
        self.batch_widget.setVisible(self.batch_visible)
        self.email_form.toggle_batch_btn.setText('隐藏批量' if self.batch_visible else '显示批量')
        self.resize(self.width(), self.original_height if not self.batch_visible else self.original_height + 250)
        self.email_form.set_inputs_enabled(not self.batch_visible)

    def on_add_attachment(self):
        files, _ = QFileDialog.getOpenFileNames(self, '选择附件', '', '所有文件 (*.*)')
        for file in files:
            if file:
                item = QListWidgetItem(os.path.basename(file))
                item.setData(Qt.ItemDataRole.UserRole, file)
                self.email_form.attachment_list.addItem(item)
        if files and self.batch_visible:
            self.on_form_changed()

    def on_remove_attachment(self):
        for item in self.email_form.attachment_list.selectedItems():
            self.email_form.attachment_list.takeItem(self.email_form.attachment_list.row(item))
        if self.batch_visible:
            self.on_form_changed()

    def on_add_batch_row(self):
        self.batch_widget.add_email_item()
        row_count = self.batch_widget.email_table.rowCount()
        if row_count > 0:
            self.batch_widget.email_table.selectRow(row_count - 1)

    def on_delete_batch_rows(self):
        self.batch_widget.delete_selected_rows()
        if self.batch_widget.email_table.rowCount() == 0:
            self.email_form.set_inputs_enabled(False)

    def on_apply_to_all(self):
        if self.batch_widget.email_table.rowCount() == 0:
            QMessageBox.warning(self, '警告', '批量列表为空，请先添加数据')
            return
        data = self.email_form.get_form_data()
        self.batch_widget.update_all_rows(data)
        QMessageBox.information(self, '成功', '已将当前内容应用于所有行')

    def on_open_attachment(self, item):
        file_path = item.data(Qt.ItemDataRole.UserRole)
        if file_path and os.path.exists(file_path):
            if os.name == 'nt':
                os.startfile(file_path)
            else:
                import subprocess
                subprocess.run(['xdg-open', file_path])

    def on_attachment_selection_changed(self):
        self.email_form.remove_attachment_btn.setEnabled(len(self.email_form.attachment_list.selectedItems()) > 0)

    def on_batch_row_selected(self):
        if self.updating_form:
            return
        self.updating_form = True
        data = self.batch_widget.get_selected_row_data()
        if data:
            self.email_form.set_form_data({
                'recipient_name': data['recipient_name'],
                'recipient_email': data['recipient_email'],
                'subject': data.get('subject', ''),
                'body': data.get('body', ''),
                'attachments': data.get('attachments', [])
            })
            self.email_form.set_inputs_enabled(True)
        else:
            self.email_form.set_inputs_enabled(False)
        self.updating_form = False

    def on_form_changed(self):
        if self.updating_form or not self.batch_visible:
            return
        data = self.email_form.get_form_data()
        self.batch_widget.update_selected_row({
            'recipient_name': data['recipient_name'],
            'recipient_email': data['recipient_email'],
            'subject': data['subject'],
            'body': data['body'],
            'attachments': data['attachments']
        })

    def on_reset(self):
        self.email_form.clear_form()
        QMessageBox.information(self, '提示', '表单已重置')

    def on_send(self):
        data = self.email_form.get_form_data()
        if not data['recipient_email']:
            QMessageBox.warning(self, '警告', '请填写收件人邮箱')
            return
        if not is_valid_email(data['recipient_email']):
            QMessageBox.warning(self, '警告', '收件人邮箱格式不正确')
            return
        sender = EmailSender(self.smtp_config['smtp_server'], self.smtp_config['smtp_port'],
                            self.smtp_config['smtp_username'], self.smtp_config['smtp_password'], self.smtp_config['use_tls'])
        subject = data['subject'] if data['subject'] else '邮件收发工具'
        body = f"发件人: {data['sender_name']}\n收件人: {data['recipient_name']}\n\n{data['body']}"
        result = sender.send_email(self.sender_email, data['recipient_email'], subject, body, data['attachments'])
        if result:
            QMessageBox.information(self, '成功', '邮件发送成功！')
            self.email_form.clear_form()
        else:
            QMessageBox.critical(self, '失败', '邮件发送失败')

    def on_import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, '选择CSV文件', '', 'CSV文件 (*.csv)')
        if not path:
            return
        try:
            with open(path, 'r', encoding='utf-8') as f:
                for row in csv.reader(f):
                    if len(row) >= 2:
                        self.batch_widget.add_email_item(row[0].strip(), row[1].strip(), row[2].strip() if len(row) > 2 else '')
            QMessageBox.information(self, '成功', 'CSV文件导入成功！')
        except Exception as e:
            QMessageBox.critical(self, '错误', f'导入失败: {str(e)}')

    def on_batch_send(self):
        email_list = self.batch_widget.get_email_list()
        if not email_list:
            QMessageBox.warning(self, '警告', '请添加要发送的邮件列表')
            return
        
        self.progress_dialog = ProgressDialog(len(email_list), self)
        self.progress_dialog.cancel_btn.clicked.connect(self.on_cancel_send)
        
        self.worker = EmailWorker(email_list, self.smtp_config, self.sender_email)
        self.worker.progress.connect(self.on_send_progress)
        self.worker.status_update.connect(self.on_status_update)
        self.worker.finished.connect(self.on_send_finished)
        self.worker.canceled.connect(self.on_send_canceled)
        
        self.progress_dialog.show()
        self.worker.start()

    def on_cancel_send(self):
        if hasattr(self, 'worker') and self.worker.isRunning():
            self.worker.cancel()

    def on_send_progress(self, current, total, recipient_name, recipient_email, content):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.update_progress(current, total, recipient_name, recipient_email, content)

    def on_status_update(self, row, success):
        self.batch_widget.update_status(row, success)

    def on_send_finished(self, success, fail):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        QMessageBox.information(self, '结果', f"批量发送完成！\n成功: {success} 封\n失败: {fail} 封")

    def on_send_canceled(self):
        if hasattr(self, 'progress_dialog'):
            self.progress_dialog.close()
        QMessageBox.information(self, '已取消', '发送已取消')