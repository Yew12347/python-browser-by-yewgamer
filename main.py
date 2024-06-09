import sys
import os
from qtpy.QtCore import QUrl, QSize, Qt
from qtpy.QtWidgets import (
    QApplication, QMainWindow, QVBoxLayout, QWidget, QLineEdit, QPushButton,
    QHBoxLayout, QAction, QMenu, QMessageBox
)
from qtpy.QtGui import QIcon
from qtpy.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile


class BrowserWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Yewgamer Browser")
        self.setWindowIcon(QIcon('icon/icon.png'))  # Updated path
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
        self.add_bookmark_action.triggered.connect(self.toggleBookmark)
        self.bookmark_menu.addAction(self.add_bookmark_action)

        # Cookie settings
        self.cookie_settings_menu = QMenu("Cookie Settings", self)
        self.delete_cookie_action = QAction("Delete Cookies", self)
        self.delete_cookie_action.triggered.connect(self.deleteCookies)
        self.cookie_settings_menu.addAction(self.delete_cookie_action)
        self.menuBar().addMenu(self.cookie_settings_menu)

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

        # Enable cookie storage
        profile = QWebEngineProfile.defaultProfile()
        profile.setPersistentCookiesPolicy(QWebEngineProfile.ForcePersistentCookies)
        self.cookie_store = profile.cookieStore()

        # Set initial URL
        self.browser.load(QUrl("https://www.google.com"))

        # Connect signals
        self.back_button.clicked.connect(self.browser.back)
        self.forward_button.clicked.connect(self.browser.forward)
        self.reload_button.clicked.connect(self.browser.reload)  # Connect reload button
        self.home_button.clicked.connect(self.goHome)
        self.go_button.clicked.connect(self.navigate)
        self.browser.urlChanged.connect(self.updateUrlBar)
        self.cookie_store.cookieAdded.connect(self.cookieAdded)

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

        # Bookmarks
        self.bookmarks = []
        self.loadBookmarks()

    def goHome(self):
        self.browser.load(QUrl("https://www.google.com"))

    def toggleBookmark(self):
        current_url = self.browser.url().toString()
        if current_url in self.bookmarks:
            self.bookmarks.remove(current_url)
            for action in self.bookmark_menu.actions():
                if action.text() == current_url:
                    self.bookmark_menu.removeAction(action)
                    break
        else:
            self.bookmarks.append(current_url)
            bookmark_action = QAction(current_url, self)
            bookmark_action.triggered.connect(self.loadBookmark)
            self.bookmark_menu.addAction(bookmark_action)

        self.saveBookmarks()
        self.updateBookmarkButton()

    def loadBookmark(self):
        action = self.sender()
        if action:
            url = action.text()
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

    def saveBookmarks(self):
        with open("bookmarks.txt", "w") as f:
            for bookmark in self.bookmarks:
                f.write(bookmark + "\n")

    def loadBookmarks(self):
        if os.path.exists("bookmarks.txt"):
            with open("bookmarks.txt", "r") as f:
                for line in f:
                    self.bookmarks.append(line.strip())

            # Populate bookmark menu
            for bookmark in self.bookmarks:
                bookmark_action = QAction(bookmark, self)
                bookmark_action.triggered.connect(self.loadBookmark)
                self.bookmark_menu.addAction(bookmark_action)

        # Check if the default home page is bookmarked
        default_home_page = "https://www.google.com"  # Change this to your desired home page URL
        if default_home_page in self.bookmarks:
            self.add_bookmark_action.setText("Remove Bookmark")
        else:
            self.add_bookmark_action.setText("Add Bookmark")

        self.updateBookmarkButton()

    def updateBookmarkButton(self):
        current_url = self.browser.url().toString()
        if current_url in self.bookmarks:
            self.add_bookmark_action.setText("Remove Bookmark")
        else:
            self.add_bookmark_action.setText("Add Bookmark")

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Save Bookmarks?',
                                     "Do you want to save your bookmarks before closing?",
                                     QMessageBox.Yes | QMessageBox.No,
                                     QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            self.saveBookmarks()
            event.accept()
        else:
            event.ignore()

    def cookieAdded(self, cookie):
        print("Cookie added:", cookie.name().data().decode(), cookie.value().data().decode())

    def deleteCookies(self):
        self.cookie_store.deleteAllCookies()

    def printCookies(self, cookies):
        for cookie in cookies:
            print(f"Name: {cookie.name().data().decode()}, Value: {cookie.value().data().decode()}, Domain: {cookie.domain().data().decode()}")


def main():
    app = QApplication(sys.argv)
    window = BrowserWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
