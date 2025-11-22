import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton # type: ignore
from PyQt5.QtGui import QFont, QPixmap # pyright: ignore[reportMissingImports]
from PyQt5.QtCore import Qt

from interfaz import EvacuacionApp, EvacuacionAppBFS

class MenuPrincipal(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Menú de Evacuación en Campus")
        self.setStyleSheet("""
            QWidget { background: #0b2545; }
            QLabel { color: #ffffff; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14pt; }
            QPushButton {
                background-color: #8B0000;
                color: #ffffff;
                border: 1px solid #8B0000;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6b0000;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setSpacing(30)

        # Imagen de Evacuacion
        evacuacion_label = QLabel()
        pixmap = QPixmap("Media/Evacuacion.png")
        if not pixmap.isNull():
            evacuacion_label.setPixmap(pixmap.scaledToWidth(200, Qt.SmoothTransformation))
            evacuacion_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(evacuacion_label)

        titulo = QLabel("Bienvenido al Planificador de Evacuación en Campus")
        titulo.setFont(QFont("Segoe UI", 16, QFont.Bold))
        titulo.setAlignment(Qt.AlignCenter)
        layout.addWidget(titulo)

        layout.addStretch()

        btn_dfs = QPushButton("DFS (Cobertura de Accesos)")
        btn_dfs.clicked.connect(self.abrir_dfs)
        layout.addWidget(btn_dfs)

        btn_bfs = QPushButton("BFS (Ruta Más Corta de Evacuación)")
        btn_bfs.clicked.connect(self.abrir_bfs)
        layout.addWidget(btn_bfs)

        layout.addStretch()

        self.showMaximized()

    def abrir_dfs(self):
        self.hide()
        self.ventana_dfs = EvacuacionApp()
        self.ventana_dfs.showMaximized()
        self.ventana_dfs.show()

    def abrir_bfs(self):
        self.hide()
        self.ventana_bfs = EvacuacionAppBFS()
        self.ventana_bfs.showMaximized()
        self.ventana_bfs.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    menu = MenuPrincipal()
    menu.show()
    sys.exit(app.exec_())

