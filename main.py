import sys
import os
from qtpy.QtCore import QUrl, QSize, Qt, QTimer
from qtpy.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton,
    QHBoxLayout, QAction, QMenu, QMessageBox, QInputDialog
)
from qtpy.QtGui import QIcon
from qtpy.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yewgamer Browser")
        self.setWindowIcon(QIcon('icon.ico'))  # Updated path
        self.setWindowFlags(Qt.Window)  # Allow the window to go fullscreen

        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()
        central_widget.setLayout(layout)

        # Navigation buttons layout
        nav_layout = QHBoxLayout()
        layout.addLayout(nav_layout)

        # Back button
        self.back_button = QPushButton("<")
        self.back_button.setIconSize(QSize(32, 32))
        nav_layout.addWidget(self.back_button)

        # Forward button
        self.forward_button = QPushButton(">")
        self.forward_button.setIconSize(QSize(32, 32))
        nav_layout.addWidget(self.forward_button)

        # Reload button (now named "Reload")
        self.reload_button = QPushButton("Reload")
        self.reload_button.setIconSize(QSize(32, 32))
        nav_layout.addWidget(self.reload_button)

        # Home button
        self.home_button = QPushButton("Home")
        self.home_button.setIconSize(QSize(32, 32))
        nav_layout.addWidget(self.home_button)

        # Bookmark button
        self.bookmark_button = QPushButton("Bookmark")
        self.bookmark_button.setIconSize(QSize(32, 32))
        nav_layout.addWidget(self.bookmark_button)

        # Bookmark menu
        self.bookmark_menu = QMenu("Bookmarks", self)
        self.bookmark_button.setMenu(self.bookmark_menu)

        # Add Bookmark action
        self.add_bookmark_action = QAction("Add Bookmark", self)
        self.add_bookmark_action.triggered.connect(self.addBookmark)
        self.bookmark_menu.addAction(self.add_bookmark_action)

        # Search bar layout
        search_layout = QHBoxLayout()
        layout.addLayout(search_layout)

        self.url_input = QLineEdit()
        self.url_input.setMinimumHeight(30)
        search_layout.addWidget(self.url_input)

        self.go_button = QPushButton("Go")
        self.go_button.setIconSize(QSize(32, 32))
        search_layout.addWidget(self.go_button)

        # Browser widget
        self.browser = QWebEngineView()
        layout.addWidget(self.browser)

        # Set initial URL
        self.browser.load(QUrl("https://www.google.com"))

        # Connect signals after window is shown
        self.showEvent = self.connect_after_show(self.showEvent, self.connect_signals)

        # Track downloaded files
        self.downloaded_files = {}

        # Apply styles
        self.setStyleSheet("""
            QMainWindow {
                background-color: #FFFFFF;
            }
            QLineEdit {
                padding: 8px 10px;
                border-radius: 5px;
                border: 1px solid #CCCCCC;
                background-color: #FFFFFF;
                font-size: 14px;
            }
            QPushButton {
                padding: 8px 10px;
                border-radius: 5px;
                border: 1px solid #CCCCCC;
                background-color: #FFFFFF;
                font-size: 14px;
            }
            QPushButton::hover {
                background-color: #F7F7F7;
            }
            QPushButton:pressed {
                background-color: #EFEFEF;
            }
        """)

    def goHome(self):
        self.browser.load(QUrl("https://www.google.com"))

    def addBookmark(self):
        current_url = self.browser.url().toString()
        bookmark_name, ok = QInputDialog.getText(self, "Add Bookmark", "Bookmark Name:")
        if ok and bookmark_name:
            action = QAction(bookmark_name, self)
            action.triggered.connect(lambda: self.loadBookmark(current_url))
            self.bookmark_menu.addAction(action)

    def loadBookmark(self, url):
        self.browser.load(QUrl(url))

    def navigate(self):
        input_text = self.url_input.text()
        if input_text.endswith('.com'):
            url = f"https://{input_text}"
        elif input_text.startswith('http://') or input_text.startswith('https://'):
            url = input_text
        else:
            search_query = input_text.replace(' ', '+')
            url = f"https://www.google.com/search?q={search_query}"
        self.browser.load(QUrl(url))

    def updateUrlBar(self, url):
        self.url_input.setText(url.toString())

    def connect_signals(self):
        self.back_button.clicked.connect(self.browser.back)
        self.forward_button.clicked.connect(self.browser.forward)
        self.reload_button.clicked.connect(self.browser.reload)  # Connect reload button
        self.home_button.clicked.connect(self.goHome)
        self.go_button.clicked.connect(self.navigate)
        self.browser.urlChanged.connect(self.updateUrlBar)

        # Connect downloadRequested signal
        self.browser.page().profile().downloadRequested.connect(self.downloadRequested)

    def connect_after_show(self, event, func):
        def wrapper(*args, **kwargs):
            res = event(*args, **kwargs)
            QTimer.singleShot(0, func)
            return res
        return wrapper

    def downloadRequested(self, downloadItem):
        # Get download information
        suggested_filename = downloadItem.suggestedFileName()
        download_path = os.path.join(os.path.expanduser('~'), 'Downloads', suggested_filename)

        # Store original download path and the new path without ".download" extension
        self.downloaded_files[suggested_filename] = download_path

        # Start download
        downloadItem.setPath(download_path)
        downloadItem.accept()

        # Connect signal for finished download
        downloadItem.finished.connect(lambda: self.showDownloadDialog(suggested_filename))

    def cancelDownload(self, downloadItem):
        downloadItem.cancel()

    def showDownloadDialog(self, filename):
        QMessageBox.information(self, "Download Complete", f"Downloaded file: {filename}")

    # Remove closeEvent method to prevent downloaded files from being deleted when the browser is closed


def main():
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
