import sys
import os
from qtpy.QtCore import QUrl, QSize, Qt, QTimer
from qtpy.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton,
    QHBoxLayout, QAction, QMenu, QMessageBox, QProgressDialog, QInputDialog
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

        # Connect signals
        self.back_button.clicked.connect(self.browser.back)
        self.forward_button.clicked.connect(self.browser.forward)
        self.reload_button.clicked.connect(self.browser.reload)  # Connect reload button
        self.home_button.clicked.connect(self.goHome)
        self.go_button.clicked.connect(self.navigate)
        self.browser.urlChanged.connect(self.updateUrlBar)
        self.browser.page().profile().downloadRequested.connect(self.downloadRequested)

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

    def downloadRequested(self, downloadItem):
        # Get download information
        suggested_filename = downloadItem.suggestedFileName()
        download_path = os.path.join(os.path.expanduser('~'), 'Downloads', suggested_filename)

        # Create a progress dialog
        progress_dialog = QProgressDialog("Downloading...", "Cancel", 0, 0, self)
        progress_dialog.setWindowTitle("Downloading")
        progress_dialog.setWindowModality(Qt.WindowModal)
        progress_dialog.setAutoReset(False)
        progress_dialog.setAutoClose(False)

        # Connect signals for progress dialog
        downloadItem.downloadProgress.connect(progress_dialog.setValue)
        downloadItem.finished.connect(progress_dialog.reset)
        downloadItem.finished.connect(lambda: self.showDone(progress_dialog))  # Show "Done"
        progress_dialog.canceled.connect(lambda: self.cancelDownload(downloadItem))  # Cancel download

        # Start download
        downloadItem.setPath(download_path)
        downloadItem.accept()

        # Open progress dialog
        progress_dialog.exec_()

    def showDone(self, progress_dialog):
        # Show "Done" for 1 second before closing the progress dialog
        progress_dialog.setLabelText("Done")
        QTimer.singleShot(1000, progress_dialog.close)

    def cancelDownload(self, downloadItem):
        downloadItem.cancel()


def main():
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
