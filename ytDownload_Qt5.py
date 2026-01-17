import sys
import threading
import yt_dlp
import os

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QLineEdit,
    QPushButton, QRadioButton, QVBoxLayout,
    QProgressBar, QMessageBox, QGroupBox, QHBoxLayout,
    QFileDialog, QCheckBox
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal
from PyQt5.QtGui import QIcon  # 导入QIcon


# ==============================
# 信号类（线程安全）
# ==============================
class DownloadSignals(QObject):
    progress = pyqtSignal(int)
    status = pyqtSignal(str)
    finished = pyqtSignal()
    error = pyqtSignal(str)  # 新增错误信号


# 自定义日志处理器
class CustomLogger:
    def __init__(self, window_instance):
        self.window = window_instance

    def debug(self, msg):
        print(msg)
        # 检查停止标志
        if self.window.should_stop.is_set():
            raise KeyboardInterrupt("Download stopped by user")
        
        # 检查是否是连接超时或其他网络错误信息
        if "Connection" in msg and ("timed out" in msg or "timeout" in msg.lower()):
            self.window.signals.status.emit(f"网络连接问题: {msg}")
        elif "Retrying" in msg:
            self.window.signals.status.emit(f"正在重试... {msg.split('Retrying')[1]}")

    def warning(self, msg):
        # 检查停止标志
        if self.window.should_stop.is_set():
            raise KeyboardInterrupt("Download stopped by user")
        
        # 发出警告信息
        #print(f"Warning: {msg}")
        #self.window.signals.status.emit(f"警告: {msg}")

    def error(self, msg):
        # 检查停止标志
        if self.window.should_stop.is_set():
            raise KeyboardInterrupt("Download stopped by user")
        
        # 发出错误信息
        #print(f"ERROR: {msg}")
        self.window.signals.error.emit(f"错误: {msg}")



# ==============================
# 主窗口
# ==============================
class YtDlpWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Video 下载器")
        self.setFixedSize(520, 380)  # 增加高度以容纳新控件

        # 设置窗口图标 - 尝试使用本地图标文件，如果不存在则使用默认系统图标
        if os.path.exists('download.png'):
            self.setWindowIcon(QIcon('download.png'))
        else:
            # 如果没有找到icon.ico文件，可以使用系统内置图标或跳过
            # 在实际部署时，应放置一个名为icon.ico的图标文件在程序目录中
            pass

        self.signals = DownloadSignals()
        self.signals.progress.connect(self.update_progress)
        self.signals.status.connect(self.update_status)
        self.signals.finished.connect(self.download_finished)
        self.signals.error.connect(self.show_error)  # 连接错误信号

        # 添加线程管理相关属性
        self.download_thread = None
        self.is_downloading = False
        self.should_stop = threading.Event()

        # 默认下载目录
        self.download_dir = "downloads"
        os.makedirs(self.download_dir, exist_ok=True)

        self.init_ui()

    # ==========================
    def init_ui(self):
        layout = QVBoxLayout(self)

        # ===== URL =====
        label_url = QLabel("视频链接")
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://www.youtube.com/watch?v=...")

        layout.addWidget(label_url)
        layout.addWidget(self.url_input)

        # ===== 下载目录选择 =====
        dir_layout = QVBoxLayout()
        dir_layout2 = QHBoxLayout()
        label_dir = QLabel("下载目录:")
        self.dir_path_label = QLabel(self.download_dir)
        self.dir_path_label.setWordWrap(True)
        self.dir_path_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                border: 1px solid #ccc;
                padding: 5px;
                border-radius: 3px;
            }
        """)
        
        self.btn_select_dir = QPushButton("选择目录")
        self.btn_select_dir.clicked.connect(self.select_download_dir)
        self.btn_select_dir.setFixedSize(80, 30)  # 设置按钮大小为宽80px，高30px
        
        dir_layout2.addWidget(self.dir_path_label,1)
        dir_layout2.addWidget(self.btn_select_dir)

        dir_layout.addWidget(label_dir)
        dir_layout.addLayout(dir_layout2)
        layout.addLayout(dir_layout)

        # ===== 下载参数 =====
        group = QGroupBox("下载类型")
        group_layout = QVBoxLayout()

        self.rb_best = QRadioButton("最佳视频")
        self.rb_720 = QRadioButton("720p 视频")
        self.rb_1080 = QRadioButton("1080p 视频")

        self.rb_best.setChecked(True)

        for rb in (self.rb_best, self.rb_720, self.rb_1080):
            group_layout.addWidget(rb)

        group.setLayout(group_layout)
        layout.addWidget(group)

        # ===== 代理选项 =====
        proxy_layout = QHBoxLayout()
        self.chk_system_proxy = QCheckBox("使用代理") 
        self.chk_system_proxy.stateChanged.connect(self.toggle_proxy)
        # 使用 QCheckBox 来表示代理启用/禁用状态
        
        

        self.proxy_input = QLineEdit()
        self.proxy_input.setText("http://127.0.0.1:8080")  # 默认不使用代理
        self.proxy_input.setPlaceholderText("http://127.0.0.1:8080")
         # 默认启用输入框
        self.proxy_input.setEnabled(True)
        proxy_layout.addWidget(self.proxy_input, 1)
        proxy_layout.addWidget(self.chk_system_proxy)
        layout.addLayout(proxy_layout)

        # ===== 下载按钮 =====
        self.btn_download = QPushButton("开始下载")
        self.btn_download.setFixedHeight(38)
        self.btn_download.clicked.connect(self.toggle_download)
        layout.addWidget(self.btn_download)

        # ===== 进度条 =====
        self.progress = QProgressBar()
        self.progress.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.progress)

        # ===== 状态 =====
        self.status_label = QLabel("等待下载")
        self.status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.status_label)

        # ===== 样式 =====
        self.setStyleSheet("""
            QWidget {
                font-size: 14px;
            }
            QPushButton {
                font-size: 13px;
                background-color: #2d89ef;
                color: white;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #1b5fa7;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
            QGroupBox {
                font-weight: bold;
            }
        """)

    # ==========================
    def select_download_dir(self):
        """选择下载目录"""
        directory = QFileDialog.getExistingDirectory(
            self, 
            "选择下载目录", 
            self.download_dir
        )
        
        if directory:
            self.download_dir = directory
            self.dir_path_label.setText(directory)
    
    # ==========================
    def show_error(self, error_msg):
        """在主线程中显示错误消息"""
        QMessageBox.critical(self, "错误", error_msg)
        self.btn_download.setEnabled(True)
        self.is_downloading = False

    # ==========================
    def toggle_download(self):
        """切换下载状态：开始/暂停/继续"""
        if not self.is_downloading:
            # 开始下载
            self.start_download()
        else:
           self.stop_download()

    # ==========================
    def start_download(self):
        url = self.url_input.text().strip()
        if not url:
            QMessageBox.warning(self, "错误", "请输入视频链接")
            return

        if self.is_downloading:
            return  # 防止重复点击

        self.progress.setValue(0)
        self.btn_download.setText("停止下载")
        self.btn_download.setStyleSheet("background-color: red; color: white;")  # 设置为红色背景
        self.is_downloading = True
        self.should_stop.clear()  # 重置停止标志

        # 创建并启动下载线程
        self.download_thread = threading.Thread(target=self.download, args=(url,), daemon=False)
        self.download_thread.start()

    def stop_download(self):
        if self.is_downloading:
            self.status_label.setText("正在停止下载 ⛔")
            self.btn_download.setText("停止下载中...")
            self.btn_download.setEnabled(False)

            # 设置停止标志
            self.should_stop.set()
    def toggle_proxy(self, state):
        """切换代理状态"""
        if state == Qt.Checked:
            # 使用代理
            proxy_url = self.proxy_input.text().strip()
            if not proxy_url:
                QMessageBox.warning(self, "错误", "请输入代理地址")
                self.chk_system_proxy.setChecked(False)
                return
            self.proxy_input.setEnabled(False)
        else:
            # 不使用代理
            proxy_url = None
            self.proxy_input.setEnabled(True)

    # ==========================
    def download(self, url):
        if self.rb_720.isChecked():
            format_opt = "bestvideo[height<=720]+bestaudio/best"
        elif self.rb_1080.isChecked():
            format_opt = "bestvideo[height<=1080]+bestaudio/best"
        else:
            format_opt = "best"

        # 使用用户选择的下载目录
        # 建议：添加 HTTP 头以模拟浏览器，减少 403 风险；增加重试以应对临时网络/限流问题
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
            "Referer": "https://www.youtube.com/",
        }

        # 创建自定义日志处理器
        logger = CustomLogger(self)

        ydl_opts = {
            "outtmpl": os.path.join(self.download_dir, "%(title)s.%(ext)s"),
            "progress_hooks": [self.progress_hook],
            "http_headers": headers,
            # 减少重试次数，以便用户能更快地停止下载
            "retries": 5,
            "fragment_retries": 10,
            "extractor_retries": 5,
            "file_access_retries": 5,
            # 减少连接超时时间，以便更快地检测到连接问题
            "socket_timeout": 30,
            # 添加日志处理器
            "logger": logger,
            # 若需要使用登录 cookie，可在这里加入 "cookiefile": "path/to/cookies.txt"
        }

        if self.chk_system_proxy.isChecked():
            # 如果配置了代理（系统或自定义），传给 yt-dlp
            proxy = self.get_proxy()
            if proxy:
                ydl_opts["proxy"] = proxy
                self.signals.status.emit(f"正在使用代理：{proxy}")
    

        if format_opt == "audio":
            ydl_opts.update({
                "format": "bestaudio/best",
                "postprocessors": [{
                    "key": "FFmpegExtractAudio",
                    "preferredcodec": "mp3",
                    "preferredquality": "192",
                }],
            })
        else:
            ydl_opts["format"] = format_opt

        # 在真正开始下载前再次检查是否需要停止
        if self.should_stop.is_set():
            self.signals.status.emit("下载已取消")
            return

        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 在下载前再次检查停止标志
                if self.should_stop.is_set():
                    self.signals.status.emit("下载已取消")
                    return
                ydl.download([url])
            
            # 只有在没有被停止的情况下才发送完成信号
            if not self.should_stop.is_set():
                self.signals.finished.emit()
        except KeyboardInterrupt:
            self.signals.status.emit("下载已停止 ❌")
        except yt_dlp.DownloadError as e:
            # 特别处理下载错误，包括网络异常
            if "ERROR: " in str(e) and ("timeout" in str(e).lower() or "network" in str(e).lower() or "connection" in str(e).lower()):
                self.signals.status.emit("网络异常，下载已停止")
                if self.should_stop.is_set():
                    # 如果是用户主动停止的
                    self.signals.status.emit("下载已停止 ❌")
                else:
                    # 如果是网络错误导致的
                    self.signals.error.emit(f"网络错误: {str(e)}")
            else:
                # 其他类型的下载错误
                if not self.should_stop.is_set():
                    self.signals.error.emit(str(e))
        except Exception as e:
            # 如果不是因为停止而引发的异常，则发送错误信号
            if not self.should_stop.is_set():
                self.signals.error.emit(str(e))
        finally:
            # 确保在任何情况下都重置状态
            self.is_downloading = False
            self.should_stop.clear()

            self.signals.progress.emit(0)
            self.signals.status.emit("等待下载")
            self.btn_download.setText("开始下载")
            self.btn_download.setStyleSheet("")  # 恢复原始样式 
            self.btn_download.setEnabled(True)

    # ==========================
    def progress_hook(self, d):
        if self.should_stop.is_set():
            # 如果需要停止，则抛出异常以中断下载
            print("Stopping download...")
            raise KeyboardInterrupt()

        if d["status"] == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate")
            downloaded = d.get("downloaded_bytes", 0)
            
            # 计算百分比
            percent = 0
            if total:
                percent = int(downloaded / total * 100)
            
            # 获取下载速度 (B/s) 并转换为合适的单位
            speed = d.get("speed", 0)  # bytes per second
            speed_str = self.format_speed(speed)
            
            # 获取已下载大小和总大小
            downloaded_str = self.format_bytes(downloaded)
            total_str = self.format_bytes(total) if total else "未知"
            
            # 发送状态更新，包含百分比和速度
            self.signals.status.emit(f"正在下载... {percent}% | 速度: {speed_str} | 已下载: {downloaded_str}/{total_str}")
            self.signals.progress.emit(percent)
            
        elif d["status"] == "finished":
            self.signals.progress.emit(100)
            self.signals.status.emit("下载完成，正在处理文件...")
        elif d["status"] == "error":
            # 检查是否是网络错误
            self.signals.status.emit("发生错误，等待处理...")

    # ==========================
    def format_speed(self, speed_bytes):
        """将字节/秒转换为更易读的格式"""
        if speed_bytes is None:
            return "未知"
        
        if speed_bytes < 1024:
            return f"{speed_bytes:.0f} B/s"
        elif speed_bytes < 1024 * 1024:
            return f"{speed_bytes / 1024:.1f} KB/s"
        elif speed_bytes < 1024 * 1024 * 1024:
            return f"{speed_bytes / (1024 * 1024):.1f} MB/s"
        else:
            return f"{speed_bytes / (1024 * 1024 * 1024):.2f} GB/s"

    def format_bytes(self, bytes_value):
        """将字节数转换为更易读的格式"""
        if bytes_value is None:
            return "未知"
        
        if bytes_value < 1024:
            return f"{bytes_value:.0f} B"
        elif bytes_value < 1024 * 1024:
            return f"{bytes_value / 1024:.1f} KB"
        elif bytes_value < 1024 * 1024 * 1024:
            return f"{bytes_value / (1024 * 1024):.1f} MB"
        else:
            return f"{bytes_value / (1024 * 1024 * 1024):.2f} GB"

    # ==========================
    def update_progress(self, value):
        self.progress.setValue(value)



    def update_status(self, text):
        self.status_label.setText(text)

    def download_finished(self):
        self.status_label.setText("下载完成 ✅")
        self.btn_download.setText("开始下载")
        self.btn_download.setStyleSheet("")  # 恢复原始样式 
        self.btn_download.setEnabled(True)
        self.is_downloading = False



    def get_proxy(self):
        """返回应传递给 yt-dlp 的代理字符串，或 None。优先使用输入框内容（若不为空），否则返回 None。

        如果用户选择了“使用系统代理”（按钮处于 checked），输入框已被填充为环境代理。
        要求格式示例: http://127.0.0.1:8080
        """
        text = self.proxy_input.text().strip()
        if not text:
            return None
        return text

    # ==========================
    def closeEvent(self, event):
        """重写关闭事件，确保安全退出"""
        if self.is_downloading:
            reply = QMessageBox.question(
                self, 
                "确认退出", 
                "下载正在进行中，确定要退出吗？", 
                QMessageBox.Yes | QMessageBox.No, 
                QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                # 设置停止标志并等待线程结束
                self.should_stop.set()
                event.accept()  # 接受关闭事件
            else:
                event.ignore()  # 忽略关闭事件
        else:
            event.accept()  # 没有下载时直接接受关闭事件

    def __del__(self):
        """析构函数，确保清理资源"""
        if self.download_thread and self.download_thread.is_alive():
            self.should_stop.set()


# ==============================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = YtDlpWindow()
    win.show()
    sys.exit(app.exec_())