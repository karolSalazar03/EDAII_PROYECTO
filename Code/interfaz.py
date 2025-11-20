import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QFileDialog, QMessageBox, QInputDialog, QFrame, QSizePolicy
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
import math

from grafo import Grafo
from dfs import dfs
from bfs import bfs

class MainMenu(QWidget):
    """
    Clase que representa el menú principal de la aplicación.

    Permite al usuario seleccionar entre los algoritmos DFS y BFS para el sistema de evacuación en campus.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Selección de Algoritmo")
        self.setStyleSheet("""
            QWidget { background: #87CEEB; }
            QLabel { color: #000000; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14pt; }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4682B4, stop:1 #1e90ff);
                color: #ffffff;
                border: 1px solid #1e90ff;
                border-radius: 12px;
                padding: 12px 24px;
                font-size: 12pt;
                font-weight: bold;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e90ff, stop:1 #4169e1);
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        # Imagen de Evacuacion
        evacuacion_label = QLabel()
        pixmap = QPixmap("Media/Evacuacion.png")
        if not pixmap.isNull():
            evacuacion_label.setPixmap(pixmap.scaledToWidth(200, Qt.SmoothTransformation))
            evacuacion_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(evacuacion_label)

        title = QLabel("Bienvenido al Planificador de Evacuación en Campus")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        self.dfs_btn = QPushButton("Búsqueda en Profundidad (DFS)")
        self.dfs_btn.clicked.connect(self.launch_dfs)
        layout.addWidget(self.dfs_btn)

        self.bfs_btn = QPushButton("Búsqueda en Anchura (BFS)")
        self.bfs_btn.clicked.connect(self.launch_bfs)
        layout.addWidget(self.bfs_btn)

        self.showMaximized()

    def launch_dfs(self):
        """
        Lanza la aplicación de evacuación usando DFS.
        """
        self.close()
        self.evacuacion_dfs_app = EvacuacionApp()
        self.evacuacion_dfs_app.show()

    def launch_bfs(self):
        """
        Lanza la aplicación de evacuación usando BFS.
        """
        self.close()
        self.evacuacion_bfs_app = EvacuacionAppBFS()
        self.evacuacion_bfs_app.show()

class GrafoCanvas(FigureCanvas):
    """
    Clase para visualizar el grafo usando matplotlib.

    Dibuja nodos como imágenes de edificios y aristas como líneas, destacando rutas en amarillo.
    """
    def __init__(self, grafo):
        """
        Inicializa el canvas con una figura de matplotlib.

        Args:
            grafo (Grafo): El grafo a visualizar.
        """
        self.fig, self.ax = plt.subplots(figsize=(7, 6), dpi=120)
        super().__init__(self.fig)
        self.set_grafo(grafo)

    def set_grafo(self, grafo, ruta=None):
        """
        Dibuja el grafo en el canvas.

        Args:
            grafo (Grafo): El grafo a dibujar.
            ruta (list, optional): Lista de nodos que forman la ruta a destacar.
        """
        self.ax.clear()
        nodes = list(grafo.nodos.keys())
        edges = []
        for nombre, nodo in grafo.nodos.items():
            for ady in nodo.adyacentes:
                if nombre < ady.nombre:  # Evitar duplicados
                    edges.append((nombre, ady.nombre))

        # Asignar posiciones en círculo
        n = len(nodes)
        pos = {}
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / n if n > 0 else 0
            pos[node] = (math.cos(angle), math.sin(angle))

        # Dibujar todas las aristas en gris
        for edge in edges:
            x1, y1 = pos[edge[0]]
            x2, y2 = pos[edge[1]]
            self.ax.plot([x1, x2], [y1, y2], color="#B0BEC5", linewidth=1.5)

        # Dibujar aristas de la ruta en amarillo
        ruta_edges = set()
        if ruta:
            for i in range(len(ruta) - 1):
                ruta_edges.add((ruta[i], ruta[i+1]))
                ruta_edges.add((ruta[i+1], ruta[i]))  # Para grafo no dirigido

        for edge in ruta_edges:
            if edge in edges or (edge[1], edge[0]) in edges:
                x1, y1 = pos[edge[0]]
                x2, y2 = pos[edge[1]]
                self.ax.plot([x1, x2], [y1, y2], color="#FFD600", linewidth=3)

        # Cargar imagen de edificio
        try:
            img = mpimg.imread("Media/Edificio.png")
        except Exception:
            img = None
        # Coloca la imagen en cada nodo
        if img is not None:
            for p in pos.values():
                imagebox = OffsetImage(img, zoom=0.02)  # Ajusta el zoom según tamaño deseado
                ab = AnnotationBbox(imagebox, p, frameon=False)
                self.ax.add_artist(ab)

        # Etiquetas encima de la imagen
        for node, (x, y) in pos.items():
            self.ax.text(x, y + 0.09, node, fontsize=4, color="#FFFFFF", fontweight='light', ha='center', va='bottom',
                         bbox=dict(boxstyle="round,pad=0.25", fc="#23272e", ec="#B0BEC5", lw=1, alpha=0.85))
        self.ax.set_title(
            "Grafo de Edificios",
            fontsize=11,
            color="#000000",
            fontweight='light',
            pad=8
        )
        self.ax.set_facecolor("#ffffff")
        self.fig.patch.set_facecolor("#ffffff")
        self.ax.axis('off')
        self.draw()

# ...existing code...

class EvacuacionApp(QWidget):
    """
    Clase para la aplicación de evacuación usando DFS.

    Proporciona una interfaz gráfica para gestionar el grafo de edificios y buscar rutas usando DFS.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Evacuacion en Campus ")
        self.setStyleSheet("""
            QWidget { background: #87CEEB; }
            QLabel, QLineEdit, QTextEdit {
                color: #000000;
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
                font-size: 11pt;
                font-weight: 400;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4682B4, stop:1 #1e90ff);
                color: #ffffff;
                border: 1px solid #1e90ff;
                border-radius: 7px;
                padding: 7px 18px;
                font-size: 11pt;
                font-weight: 500;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e90ff, stop:1 #4169e1);
            }
            QLineEdit, QTextEdit {
                background: #ffffff;
                border: 1px solid #44475a;
                border-radius: 6px;
                font-size: 11pt;
            }
            QTextEdit#CargadosTextEdit {
                font-size: 12pt; /* Más grande para mejor visibilidad */
                background: #ffffff;
                color: #000000;
                border: 2px solid #44475a;
                border-radius: 8px;
                margin-bottom: 12px;
            }
            QTextEdit { padding: 8px; }
        """)
        self.grafo = Grafo()
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        """
        Inicializa la interfaz de usuario para la aplicación de evacuación.

        Configura el layout principal, paneles, botones, campos de entrada y canvas del grafo.
        """
        main_layout = QVBoxLayout(self)

        # --- Panel superior: controles y resultados ---
        top_panel = QHBoxLayout()
        left_panel = QVBoxLayout()
        left_panel.setSpacing(18)

        # Botón de volver al menú principal
        self.menu_btn = QPushButton("Volver al Menu Principal")
        self.menu_btn.clicked.connect(self.volver_menu)
        left_panel.addWidget(self.menu_btn)

        # Logo EPN
        logo_label = QLabel()
        pixmap = QPixmap("Media/EPNLOGO.png")
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaledToWidth(150, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            left_panel.addWidget(logo_label)

        title = QLabel("Sistema de Evacuacion en Campus")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(title)

        # Entrada de edificios
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Edificio (origen,destino)")
        left_panel.addWidget(self.entry)

        self.add_btn = QPushButton("Agregar Edificio")
        self.add_btn.clicked.connect(self.agregar_edificio)
        left_panel.addWidget(self.add_btn)

        self.csv_btn = QPushButton("Cargar CSV")
        self.csv_btn.clicked.connect(self.cargar_csv)
        left_panel.addWidget(self.csv_btn)

        self.buscar_btn = QPushButton("Buscar Ruta DFS")
        self.buscar_btn.clicked.connect(self.buscar_ruta)
        left_panel.addWidget(self.buscar_btn)

        # Botón de eliminar arista
        self.eliminar_btn = QPushButton("Eliminar Arista")
        self.eliminar_btn.clicked.connect(self.eliminar_arista)
        left_panel.addWidget(self.eliminar_btn)

        # Botón de borrar todo
        self.borrar_btn = QPushButton("Borrar Todo")
        self.borrar_btn.clicked.connect(self.borrar_todo)
        left_panel.addWidget(self.borrar_btn)

        # Texto de resultados de agregados/cargados (más alto, bien encuadrado, con barra scroll)
        self.texto = QTextEdit()
        self.texto.setObjectName("CargadosTextEdit")
        self.texto.setReadOnly(True)
        self.texto.setFixedHeight(250)
        self.texto.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.texto.setLineWrapMode(QTextEdit.WidgetWidth)
        left_panel.addWidget(self.texto)

        # Línea separadora entre cuadros
        dfs_line = QFrame()
        dfs_line.setFrameShape(QFrame.HLine)
        dfs_line.setFrameShadow(QFrame.Sunken)
        dfs_line.setStyleSheet("color: #44475a; background: #44475a; max-height: 2px; margin-bottom: 8px;")
        left_panel.addWidget(dfs_line)

        left_panel.addStretch(0)

        # --- LADO DERECHO: Grafo ---
        self.grafo_canvas = GrafoCanvas(self.grafo)
        self.grafo_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # --- Panel superior: controles (izq) y grafo (der) ---
        top_panel.addLayout(left_panel, stretch=1)
        top_panel.addWidget(self.grafo_canvas, stretch=2)

        # --- Panel inferior: resultado DFS a lo ancho ---
        self.resultado = QTextEdit()
        self.resultado.setReadOnly(True)
        self.resultado.setStyleSheet("background: #ffffff; color: #000000; font-size: 12pt; border: 2px solid #44475a; border-radius: 8px;")
        self.resultado.setLineWrapMode(QTextEdit.WidgetWidth)
        self.resultado.setFixedHeight(70)

        main_layout.addLayout(top_panel, stretch=5)
        main_layout.addWidget(self.resultado, stretch=0)

    # ...existing methods...

# ...existing code...
    def agregar_edificio(self):
        """
        Agrega una nueva arista al grafo basada en la entrada del usuario.

        Lee el texto de entrada, lo divide en origen y destino, y agrega la arista al grafo.
        Actualiza el canvas del grafo y guarda automáticamente en CSV si existe.
        """
        datos = self.entry.text().strip()
        if ',' not in datos:
            QMessageBox.critical(self, "Error", "Formato: origen,destino")
            return
        origen, destino = datos.split(',')
        self.grafo.agregar_arista(origen.strip(), destino.strip())
        self.texto.append(f"Agregado: {origen.strip()} -> {destino.strip()}")
        self.entry.clear()
        self.grafo_canvas.set_grafo(self.grafo)
        # Guardar automáticamente en CSV solo si el archivo existe
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'Archivos', 'CampusEpn.csv')
        if os.path.exists(csv_path):
            with open(csv_path, 'w', encoding='utf-8') as f:
                for nombre, nodo in self.grafo.nodos.items():
                    for adyacente in nodo.adyacentes:
                        if nombre < adyacente.nombre:
                            f.write(f"{nombre},{adyacente.nombre}\n")

    def cargar_csv(self):
        """
        Carga un archivo CSV y agrega las aristas al grafo.

        Abre un diálogo para seleccionar un archivo CSV, lee cada línea como origen,destino,
        agrega las aristas al grafo y actualiza el canvas.
        """
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir CSV", "", "CSV Files (*.csv)")
        if archivo:
            with open(archivo, 'r',encoding='utf-8') as f:
                for linea in f:
                    origen, destino = linea.strip().split(',')
                    self.grafo.agregar_arista(origen, destino)
                    self.texto.append(f"Conectado: {origen} -> {destino}")
            self.grafo_canvas.set_grafo(self.grafo)

    def guardar_csv(self):
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "", "CSV Files (*.csv)")
        if archivo:
            with open(archivo, 'w', encoding='utf-8') as f:
                for nombre, nodo in self.grafo.nodos.items():
                    for adyacente in nodo.adyacentes:
                        # Para evitar duplicados en grafo no dirigido, solo escribir si nombre < adyacente.nombre
                        if nombre < adyacente.nombre:
                            f.write(f"{nombre},{adyacente.nombre}\n")
            QMessageBox.information(self, "Guardado", "Grafo guardado en CSV exitosamente.")

    def pedir_edificio(self, titulo, mensaje):
        texto, ok = QInputDialog.getText(self, titulo, mensaje)
        return texto.strip() if ok and texto else None

    def buscar_ruta(self):
        inicio = self.pedir_edificio("Inicio", "Edificio de inicio:")
        fin = self.pedir_edificio("Fin", "Edificio de destino:")
        if inicio and fin:
            resultado_dfs = dfs(self.grafo, inicio, fin)
            texto = f"Padres: {resultado_dfs['padres']}\n"
            texto += f"Árbol DFS: {resultado_dfs['arbol_dfs']}\n"
            ruta = resultado_dfs['ruta_encontrada']
            if ruta:
                texto += f"Ruta encontrada: {' -> '.join(ruta)}\n"
                texto += f"Distancia: {len(ruta) - 1}\n"
            else:
                texto += "Ruta encontrada: No encontrada\n"
            texto += f"Camino más profundo: {' -> '.join(resultado_dfs['camino_mas_profundo'])}\n"
            texto += f"Tiempo: {resultado_dfs['tiempo']:.6f} segundos"
            self.resultado.setText(texto)
            if ruta:
                self.grafo_canvas.set_grafo(self.grafo, ruta)
            else:
                self.grafo_canvas.set_grafo(self.grafo)
            self.grafo_canvas.update()
            self.grafo_canvas.repaint()

    def eliminar_arista(self):
        origen = self.pedir_edificio("Eliminar Arista", "Edificio origen:")
        if not origen:
            return
        destino = self.pedir_edificio("Eliminar Arista", "Edificio destino:")
        if not destino:
            return
        reply = QMessageBox.question(self, "Confirmar", f"¿Eliminar arista de {origen} a {destino}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.grafo.eliminar_arista(origen, destino)
            self.texto.append(f"Eliminado: {origen} -> {destino}")
            self.grafo_canvas.set_grafo(self.grafo)

    def borrar_todo(self):
        self.grafo = Grafo()
        self.grafo_canvas.set_grafo(self.grafo)
        self.texto.clear()
        self.resultado.clear()
        self.entry.clear()

    def volver_menu(self):
        self.close()
        self.menu = MainMenu()
        self.menu.show()

class EvacuacionAppBFS(QWidget):
    """
    Clase para la aplicación de evacuación usando BFS.

    Similar a EvacuacionApp pero utiliza BFS para encontrar la ruta más corta.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Evacuacion en Campus ")
        self.setStyleSheet("""
            QWidget { background: #87CEEB; }
            QLabel, QLineEdit, QTextEdit {
                color: #000000;
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
                font-size: 11pt;
                font-weight: 400;
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #4682B4, stop:1 #1e90ff);
                color: #ffffff;
                border: 1px solid #1e90ff;
                border-radius: 7px;
                padding: 7px 18px;
                font-size: 11pt;
                font-weight: 500;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1, stop:0 #1e90ff, stop:1 #4169e1);
            }
            QLineEdit, QTextEdit {
                background: #ffffff;
                border: 1px solid #44475a;
                border-radius: 6px;
                font-size: 11pt;
            }
            QTextEdit#CargadosTextEdit {
                font-size: 12pt; /* Más grande para mejor visibilidad */
                background: #ffffff;
                color: #000000;
                border: 2px solid #44475a;
                border-radius: 8px;
                margin-bottom: 12px;
            }
            QTextEdit { padding: 8px; }
        """)
        self.grafo = Grafo()
        self.init_ui()
        self.showMaximized()

    # ...existing code...

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        # --- Panel superior: controles y resultados ---
        top_panel = QHBoxLayout()
        left_panel = QVBoxLayout()
        left_panel.setSpacing(18)

        # Botón de volver al menú principal
        self.menu_btn = QPushButton("Volver al Menu Principal")
        self.menu_btn.clicked.connect(self.volver_menu)
        left_panel.addWidget(self.menu_btn)

        # Logo EPN
        logo_label = QLabel()
        pixmap = QPixmap("Media/EPNLOGO.png")
        if not pixmap.isNull():
            logo_label.setPixmap(pixmap.scaledToWidth(150, Qt.SmoothTransformation))
            logo_label.setAlignment(Qt.AlignCenter)
            left_panel.addWidget(logo_label)

        title = QLabel("Sistema de Evacuacion en Campus")
        title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(title)

        # Entrada de edificios
        self.entry = QLineEdit()
        self.entry.setPlaceholderText("Edificio (origen,destino)")
        left_panel.addWidget(self.entry)

        self.add_btn = QPushButton("Agregar Edificio")
        self.add_btn.clicked.connect(self.agregar_edificio)
        left_panel.addWidget(self.add_btn)

        self.csv_btn = QPushButton("Cargar CSV")
        self.csv_btn.clicked.connect(self.cargar_csv)
        left_panel.addWidget(self.csv_btn)

        self.buscar_btn = QPushButton("Buscar Ruta BFS")
        self.buscar_btn.clicked.connect(self.buscar_ruta)
        left_panel.addWidget(self.buscar_btn)

        # Botón de eliminar arista
        self.eliminar_btn = QPushButton("Eliminar Arista")
        self.eliminar_btn.clicked.connect(self.eliminar_arista)
        left_panel.addWidget(self.eliminar_btn)

        # Botón de borrar todo
        self.borrar_btn = QPushButton("Borrar Todo")
        self.borrar_btn.clicked.connect(self.borrar_todo)
        left_panel.addWidget(self.borrar_btn)

        # Texto de resultados de agregados/cargados (más alto para mejor visibilidad)
        self.texto = QTextEdit()
        self.texto.setObjectName("CargadosTextEdit")
        self.texto.setReadOnly(True)
        self.texto.setFixedHeight(250)
        self.texto.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.texto.setLineWrapMode(QTextEdit.WidgetWidth)
        left_panel.addWidget(self.texto)

        # Línea separadora entre cuadros
        dfs_line = QFrame()
        dfs_line.setFrameShape(QFrame.HLine)
        dfs_line.setFrameShadow(QFrame.Sunken)
        dfs_line.setStyleSheet("color: #44475a; background: #44475a; max-height: 2px; margin-bottom: 8px;")
        left_panel.addWidget(dfs_line)

        left_panel.addStretch(0)

        # --- LADO DERECHO: Grafo ---
        self.grafo_canvas = GrafoCanvas(self.grafo)
        self.grafo_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # --- Panel superior: controles (izq) y grafo (der) ---
        top_panel.addLayout(left_panel, stretch=1)
        top_panel.addWidget(self.grafo_canvas, stretch=2)

        # --- Panel inferior: resultado DFS a lo ancho ---
        self.resultado = QTextEdit()
        self.resultado.setReadOnly(True)
        self.resultado.setStyleSheet("background: #ffffff; color: #000000; font-size: 12pt; border: 2px solid #44475a; border-radius: 8px;")
        self.resultado.setLineWrapMode(QTextEdit.WidgetWidth)
        self.resultado.setFixedHeight(70)

        main_layout.addLayout(top_panel, stretch=5)
        main_layout.addWidget(self.resultado, stretch=0)

# ...existing code...
    def agregar_edificio(self):
        datos = self.entry.text().strip()
        if ',' not in datos:
            QMessageBox.critical(self, "Error", "Formato: origen,destino")
            return
        origen, destino = datos.split(',')
        self.grafo.agregar_arista(origen.strip(), destino.strip())
        self.texto.append(f"Agregado: {origen.strip()} -> {destino.strip()}")
        self.entry.clear()
        self.grafo_canvas.set_grafo(self.grafo)
        # Guardar automáticamente en CSV solo si el archivo existe
        csv_path = os.path.join(os.path.dirname(__file__), '..', 'Archivos', 'CampusEpn.csv')
        if os.path.exists(csv_path):
            with open(csv_path, 'w', encoding='utf-8') as f:
                for nombre, nodo in self.grafo.nodos.items():
                    for adyacente in nodo.adyacentes:
                        if nombre < adyacente.nombre:
                            f.write(f"{nombre},{adyacente.nombre}\n")

    def cargar_csv(self):
        archivo, _ = QFileDialog.getOpenFileName(self, "Abrir CSV", "", "CSV Files (*.csv)")
        if archivo:
            with open(archivo, 'r',encoding='utf-8') as f:
                for linea in f:
                    origen, destino = linea.strip().split(',')
                    self.grafo.agregar_arista(origen, destino)
                    self.texto.append(f"Conectado: {origen} -> {destino}")
            self.grafo_canvas.set_grafo(self.grafo)

    def pedir_edificio(self, titulo, mensaje):
        texto, ok = QInputDialog.getText(self, titulo, mensaje)
        return texto.strip() if ok and texto else None

    def buscar_ruta(self):
        inicio = self.pedir_edificio("Inicio", "Edificio de inicio:")
        fin = self.pedir_edificio("Fin", "Edificio de destino:")
        if inicio and fin:
            resultado_bfs = bfs(self.grafo, inicio, fin)
            if fin in resultado_bfs['distancias']:
                texto = f"Distancia al destino: {resultado_bfs['distancias'][fin]}\n"
            else:
                texto = "Distancia al destino: No encontrada\n"
            texto += f"Padres: {resultado_bfs['padres']}\n"
            texto += f"Ruta más corta: {' -> '.join(resultado_bfs['ruta_mas_corta']) if resultado_bfs['ruta_mas_corta'] else 'No encontrada'}\n"
            texto += f"Árbol BFS: {resultado_bfs['arbol_bfs']}\n"
            texto += f"Tiempo: {resultado_bfs['tiempo']:.6f} segundos"
            self.resultado.setText(texto)
            ruta = resultado_bfs['ruta_mas_corta']
            if ruta:
                self.grafo_canvas.set_grafo(self.grafo, ruta)
            else:
                self.grafo_canvas.set_grafo(self.grafo)
            self.grafo_canvas.update()
            self.grafo_canvas.repaint()

    def eliminar_arista(self):
        origen = self.pedir_edificio("Eliminar Arista", "Edificio origen:")
        if not origen:
            return
        destino = self.pedir_edificio("Eliminar Arista", "Edificio destino:")
        if not destino:
            return
        reply = QMessageBox.question(self, "Confirmar", f"¿Eliminar arista de {origen} a {destino}?", QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.Yes:
            self.grafo.eliminar_arista(origen, destino)
            self.texto.append(f"Eliminado: {origen} -> {destino}")
            self.grafo_canvas.set_grafo(self.grafo)

    def borrar_todo(self):
        self.grafo = Grafo()
        self.grafo_canvas.set_grafo(self.grafo)
        self.texto.clear()
        self.resultado.clear()
        self.entry.clear()

    def volver_menu(self):
        self.close()
        self.menu = MainMenu()
        self.menu.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    menu = MainMenu()
    menu.show()
    sys.exit(app.exec_())
