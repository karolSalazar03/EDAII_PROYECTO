import sys
import os
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTextEdit, QFileDialog, QMessageBox, QInputDialog, QFrame, QSizePolicy
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.image as mpimg
from matplotlib.offsetbox import OffsetImage, AnnotationBbox
from matplotlib.patches import Circle
import math

from grafo import Grafo
from dfs import dfs
from bfs import bfs


def set_result_widget_text(widget, text, min_lines=1, max_lines=8, padding=12):
    """Setea el texto de `widget` (QTextEdit) y ajusta su altura para mostrar todas las líneas.

    - `min_lines` y `max_lines` limitan la altura mínima y máxima (en número de líneas).
    - `padding` agrega espacio extra en píxeles.
    """
    widget.setPlainText(text)
    fm = QFontMetrics(widget.font())
    line_h = fm.lineSpacing()
    lines = text.count('\n') + 1
    lines = max(min_lines, min(lines, max_lines))
    height = lines * line_h + padding
    try:
        widget.setFixedHeight(height)
        widget.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    except Exception:
        pass


class TreeCanvas(FigureCanvas):
    """Canvas simple para dibujar un árbol (node-link) usando matplotlib.

    Método público: `set_tree(padres_map)` acepta los mismos formatos que antes
    (child->parent o parent->children) y dibuja un layout jerárquico.
    """
    def __init__(self):
        self.fig, self.ax = plt.subplots(figsize=(4, 4), dpi=100)
        super().__init__(self.fig)
        try:
            self.setMinimumSize(360, 300)
        except Exception:
            pass
        self.ax.axis('off')

    def set_tree(self, padres_map, ruta=None):
        self.ax.clear()
        if not padres_map:
            self.draw()
            return

        # Normalizar a parent->children
        is_child_parent = all(not isinstance(v, (list, tuple)) for v in padres_map.values())
        children = {}
        roots = []

        if is_child_parent:
            for child, parent in padres_map.items():
                if parent is None:
                    roots.append(child)
                else:
                    children.setdefault(parent, []).append(child)
            # añadir nodos sueltos
            for k in padres_map.keys():
                children.setdefault(k, [])
        else:
            for parent, childs in padres_map.items():
                children.setdefault(parent, []).extend(list(childs))
        # detectar raíces: nodos que no son hijos
        all_children = {c for childs in children.values() for c in childs}
        potential_roots = [n for n in children.keys() if n not in all_children]
        if potential_roots:
            roots = potential_roots
        else:
            roots = list(children.keys())

        # asignar posiciones (x,y) por recorrido recursivo
        xpos = {}
        ypos = {}
        counter = [0]

        def assign(node, depth=0):
            if not children.get(node):
                xpos[node] = counter[0]
                counter[0] += 1
            else:
                for c in sorted(children.get(node, [])):
                    assign(c, depth + 1)
                xs = [xpos[c] for c in children.get(node, [])]
                xpos[node] = sum(xs) / len(xs) if xs else counter[0]
            ypos[node] = -depth

        for r in roots:
            assign(r, 0)

        # escalar x para mejor presentación
        xs = {n: xpos[n] * 1.6 for n in xpos}
        ys = ypos

        # preparar ruta (si la hay) para resaltar
        route_nodes = set(ruta) if ruta else set()
        route_edges = set()
        if ruta and len(ruta) >= 2:
            for i in range(len(ruta) - 1):
                route_edges.add((ruta[i], ruta[i+1]))
                route_edges.add((ruta[i+1], ruta[i]))

        # dibujar aristas (colorear en verde si pertenecen a la ruta)
        for parent, childs in children.items():
            for c in childs:
                x1, y1 = xs.get(parent, 0), ys.get(parent, 0)
                x2, y2 = xs.get(c, 0), ys.get(c, 0)
                if (parent, c) in route_edges:
                    self.ax.plot([x1, x2], [y1, y2], color="#2ecc71", linewidth=3.0, zorder=1)
                else:
                    self.ax.plot([x1, x2], [y1, y2], color="#8B0000", linewidth=1.6, zorder=1)

        # dibujar nodos con tamaño adaptativo para que el texto quepa
        for node in xpos.keys():
            x, y = xs[node], ys[node]
            label = str(node)
            # aproximación del ancho requerido según longitud del texto
            text_len = max(1, len(label))
            # base radius y factor por carácter
            radius = max(0.18, 0.07 * text_len)
            # si el nodo está en la ruta, color verde, si no, color navy
            face = "#2ecc71" if node in route_nodes else "#0b2545"
            edgec = "#1e7a3a" if node in route_nodes else "#8B0000"
            circ = Circle((x, y), radius, facecolor=face, edgecolor=edgec, linewidth=1.2, zorder=2)
            self.ax.add_patch(circ)
            # Ajustar tamaño de fuente ligeramente según longitud
            fsize = 9 if text_len <= 12 else max(6, int(11 - (text_len - 12) * 0.3))
            self.ax.text(x, y, label, color="#ffffff", ha='center', va='center', fontsize=fsize, zorder=3)

        self.ax.set_facecolor('#ffffff')
        self.fig.patch.set_facecolor('#ffffff')
        self.ax.axis('off')
        self.draw()

class MainMenu(QWidget):
    """
    Clase que representa el menú principal de la aplicación.

    Permite al usuario seleccionar entre los algoritmos DFS y BFS para el sistema de evacuación en campus.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Selección de Algoritmo")
        self.setStyleSheet("""
            QWidget { background: #0b2545; }
            QLabel { color: #ffffff; font-family: 'Segoe UI', Arial, sans-serif; font-size: 14pt; }
            QPushButton {
                background-color: #8B0000;
                color: #ffffff;
                border: none;
                border-radius: 12px;
                padding: 10px 20px;
                font-size: 12pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #6b0000;
            }
        """)
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignCenter)

        
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
        
        self.fig, self.ax = plt.subplots(figsize=(8, 6), dpi=120)
        super().__init__(self.fig)
        
        try:
            self.setMinimumSize(720, 540)
        except Exception:
            pass
        self.set_grafo(grafo)

    def set_grafo(self, grafo, ruta=None):
        self.ax.clear()
        nodes = list(grafo.nodos.keys())
        edges = []
        for nombre, nodo in grafo.nodos.items():
            for ady in nodo.adyacentes:
                if nombre < ady.nombre:  # Evitar duplicados
                    edges.append((nombre, ady.nombre))

        
        n = len(nodes)
        pos = {}
        
        radius = 1.2 + min(3.0, max(0.0, (n - 6) * 0.08)) if n > 0 else 1.0
        for i, node in enumerate(nodes):
            angle = 2 * math.pi * i / n if n > 0 else 0
            pos[node] = (math.cos(angle) * radius, math.sin(angle) * radius)

        
        for edge in edges:
            x1, y1 = pos[edge[0]]
            x2, y2 = pos[edge[1]]
            self.ax.plot([x1, x2], [y1, y2], color="#9EA7AA", linewidth=2)

        
        ruta_edges = set()
        if ruta:
            for i in range(len(ruta) - 1):
                ruta_edges.add((ruta[i], ruta[i+1]))
                ruta_edges.add((ruta[i+1], ruta[i]))  # Para grafo no dirigido

        for edge in ruta_edges:
            if edge in edges or (edge[1], edge[0]) in edges:
                x1, y1 = pos[edge[0]]
                x2, y2 = pos[edge[1]]
                self.ax.plot([x1, x2], [y1, y2], color="#FFD600", linewidth=4, zorder=1)

        
        try:
            img = mpimg.imread("Media/Edificio.png")
        except Exception:
            img = None

        
        if img is not None:
            if n <= 8:
                img_zoom = 0.08
            elif n <= 20:
                img_zoom = 0.06
            else:
                img_zoom = 0.035
        else:
            img_zoom = None

        
        for node, (x, y) in pos.items():
            
            self.ax.scatter([x], [y], s=240 if n <= 8 else 120, color="#0b2545", edgecolors="#8B0000", linewidths=1.2, zorder=2)
            if img is not None:
                try:
                    imagebox = OffsetImage(img, zoom=img_zoom)
                    ab = AnnotationBbox(imagebox, (x, y), frameon=False, zorder=3)
                    self.ax.add_artist(ab)
                except Exception:
                    pass

        
        for node, (x, y) in pos.items():
            self.ax.text(x, y + (0.12 if n <= 8 else 0.09), node, fontsize=11 if n <= 12 else 9, color="#FFFFFF",
                         fontweight='600', ha='center', va='bottom',
                         bbox=dict(boxstyle="round,pad=0.25", fc="#0b2545", ec="#8B0000", lw=0.8, alpha=0.98), zorder=4)
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


class EvacuacionApp(QWidget):
    """
    Clase para la aplicación de evacuación usando DFS.

    Proporciona una interfaz gráfica para gestionar el grafo de edificios y buscar rutas usando DFS.
    """
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema de Evacuacion en Campus ")
        self.setStyleSheet("""
            QWidget { background: #0b2545; }
            QLabel, QLineEdit, QTextEdit {
                color: #ffffff;
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
                font-size: 11pt;
                font-weight: 400;
            }
            QPushButton {
                background-color: #8B0000;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 9px 16px;
                font-size: 11pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #6b0000;
            }
            QLineEdit, QTextEdit {
                background: #ffffff;
                color: #000000;
                border: 1px solid #0b2545;
                border-radius: 8px;
                font-size: 11pt;
            }
            QTextEdit#CargadosTextEdit {
                font-size: 12pt; /* Más grande para mejor visibilidad */
                background: #ffffff;
                color: #000000;
                border: 2px solid #0b2545;
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

        
        top_panel = QHBoxLayout()
        left_panel = QVBoxLayout()
        left_panel.setSpacing(18)

        
        self.menu_btn = QPushButton("Volver al Menu Principal")
        self.menu_btn.clicked.connect(self.volver_menu)
        left_panel.addWidget(self.menu_btn)

        
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

        

        
        self.tree = TreeCanvas()
        # Small fixed height to keep layout compact; TreeCanvas handles its own drawing
        left_panel.addWidget(self.tree)

        
        dfs_line = QFrame()
        dfs_line.setFrameShape(QFrame.HLine)
        dfs_line.setFrameShadow(QFrame.Sunken)
        dfs_line.setStyleSheet("color: #44475a; background: #44475a; max-height: 2px; margin-bottom: 8px;")
        left_panel.addWidget(dfs_line)

        left_panel.addStretch(0)

        
        self.grafo_canvas = GrafoCanvas(self.grafo)
        self.grafo_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        
        top_panel.addLayout(left_panel, stretch=1)
        top_panel.addWidget(self.grafo_canvas, stretch=2)

        
        self.resultado = QTextEdit()
        self.resultado.setReadOnly(True)
        self.resultado.setStyleSheet("background: #ffffff; color: #000000; font-size: 12pt; border: 2px solid #0b2545; border-radius: 8px;")
        self.resultado.setLineWrapMode(QTextEdit.WidgetWidth)
        # start with a reasonable small height; will auto-resize when setting text
        self.resultado.setFixedHeight(90)

        main_layout.addLayout(top_panel, stretch=5)
        main_layout.addWidget(self.resultado, stretch=0)

    
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
        
        # actualizar visualmente (no mostrar mensajes de conexión en el área de resultados)
        # (conexiones se añaden al grafo y se visualizan en el canvas)
        self.entry.clear()
        self.grafo_canvas.set_grafo(self.grafo)
        
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
                    # no registrar en el área del árbol ni en el área de resultados
            self.grafo_canvas.set_grafo(self.grafo)

    def guardar_csv(self):
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "", "CSV Files (*.csv)")
        if archivo:
            with open(archivo, 'w', encoding='utf-8') as f:
                for nombre, nodo in self.grafo.nodos.items():
                    for adyacente in nodo.adyacentes:
                        
                        if nombre < adyacente.nombre:
                            f.write(f"{nombre},{adyacente.nombre}\n")
            QMessageBox.information(self, "Guardado", "Grafo guardado en CSV exitosamente.")

    def pedir_edificio(self, titulo, mensaje):
        texto, ok = QInputDialog.getText(self, titulo, mensaje)
        return texto.strip() if ok and texto else None

    pass

    def buscar_ruta(self):
        inicio = self.pedir_edificio("Inicio", "Edificio de inicio:")
        fin = self.pedir_edificio("Fin", "Edificio de destino:")
        if inicio and fin:
            resultado_dfs = dfs(self.grafo, inicio, fin)
            ruta = resultado_dfs.get('ruta_encontrada')
            # preparar texto: Distancia, Ruta encontrada, Tiempo, Padres, Camino más profundo
            if ruta:
                distancia = len(ruta) - 1
                ruta_text = ' -> '.join(ruta)
            else:
                distancia = 'No encontrada'
                ruta_text = 'No encontrada'
            camino_profundo = resultado_dfs.get('camino_mas_profundo') or []
            camino_profundo_text = ' -> '.join(camino_profundo) if camino_profundo else 'N/A'
            texto = f"Distancia: {distancia}\n"
            texto += f"Ruta encontrada: {ruta_text}\n"
            texto += f"Tiempo: {resultado_dfs['tiempo']:.6f} segundos\n"
            texto += f"Padres: {resultado_dfs.get('padres', {})}\n"
            texto += f"Camino más profundo: {camino_profundo_text}\n"
            # mostrar mensaje popup si no hay ruta encontrada
            if not ruta:
                QMessageBox.information(self, "Resultado", "La ruta no existe")
            set_result_widget_text(self.resultado, texto, min_lines=4, max_lines=8)
            # actualizar grafo principal
            if ruta:
                self.grafo_canvas.set_grafo(self.grafo, ruta)
            else:
                self.grafo_canvas.set_grafo(self.grafo)
            self.grafo_canvas.update()
            self.grafo_canvas.repaint()
            padres = resultado_dfs.get('arbol_dfs') or resultado_dfs.get('padres') or {}
            try:
                self.tree.set_tree(padres, ruta)
            except Exception:
                pass

    

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
            QWidget { background: #0b2545; }
            QLabel, QLineEdit, QTextEdit {
                color: #ffffff;
                font-family: 'Segoe UI', 'Roboto', Arial, sans-serif;
                font-size: 11pt;
                font-weight: 400;
            }
            QPushButton {
                background-color: #8B0000;
                color: #ffffff;
                border: none;
                border-radius: 10px;
                padding: 9px 16px;
                font-size: 11pt;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #6b0000;
            }
            QLineEdit, QTextEdit {
                background: #ffffff;
                color: #000000;
                border: 1px solid #0b2545;
                border-radius: 8px;
                font-size: 11pt;
            }
            QTextEdit#CargadosTextEdit {
                font-size: 12pt; /* Más grande para mejor visibilidad */
                background: #ffffff;
                color: #000000;
                border: 2px solid #0b2545;
                border-radius: 8px;
                margin-bottom: 12px;
            }
            QTextEdit { padding: 8px; }
        """)
        self.grafo = Grafo()
        self.init_ui()
        self.showMaximized()

    def init_ui(self):
        main_layout = QVBoxLayout(self)

        
        top_panel = QHBoxLayout()
        left_panel = QVBoxLayout()
        left_panel.setSpacing(18)

        
        self.menu_btn = QPushButton("Volver al Menu Principal")
        self.menu_btn.clicked.connect(self.volver_menu)
        left_panel.addWidget(self.menu_btn)

        
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

        
        
        self.tree = TreeCanvas()
        left_panel.addWidget(self.tree)

        
        dfs_line = QFrame()
        dfs_line.setFrameShape(QFrame.HLine)
        dfs_line.setFrameShadow(QFrame.Sunken)
        dfs_line.setStyleSheet("color: #44475a; background: #44475a; max-height: 2px; margin-bottom: 8px;")
        left_panel.addWidget(dfs_line)

        left_panel.addStretch(0)

        
        self.grafo_canvas = GrafoCanvas(self.grafo)
        self.grafo_canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        
        top_panel.addLayout(left_panel, stretch=1)
        top_panel.addWidget(self.grafo_canvas, stretch=2)

        
        self.resultado = QTextEdit()
        self.resultado.setReadOnly(True)
        self.resultado.setStyleSheet("background: #ffffff; color: #000000; font-size: 12pt; border: 2px solid #4b0000; border-radius: 8px;")
        self.resultado.setLineWrapMode(QTextEdit.WidgetWidth)
        self.resultado.setFixedHeight(90)

        main_layout.addLayout(top_panel, stretch=5)
        main_layout.addWidget(self.resultado, stretch=0)

    def agregar_edificio(self):
        datos = self.entry.text().strip()
        if ',' not in datos:
            QMessageBox.critical(self, "Error", "Formato: origen,destino")
            return
        origen, destino = datos.split(',')
        self.grafo.agregar_arista(origen.strip(), destino.strip())
        self.entry.clear()
        self.grafo_canvas.set_grafo(self.grafo)
        
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
            with open(archivo, 'r', encoding='utf-8') as f:
                for linea in f:
                    origen, destino = linea.strip().split(',')
                    self.grafo.agregar_arista(origen, destino)
            self.grafo_canvas.set_grafo(self.grafo)

    def guardar_csv(self):
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar CSV", "", "CSV Files (*.csv)")
        if archivo:
            with open(archivo, 'w', encoding='utf-8') as f:
                for nombre, nodo in self.grafo.nodos.items():
                    for adyacente in nodo.adyacentes:
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
            resultado_bfs = bfs(self.grafo, inicio, fin)
            ruta = resultado_bfs.get('ruta_mas_corta')
            if ruta:
                distancia = resultado_bfs['distancias'].get(fin, 'No encontrada')
                ruta_text = ' -> '.join(ruta)
            else:
                distancia = 'No encontrada'
                ruta_text = 'No encontrada'
            texto = f"Distancia: {distancia}\n"
            texto += f"Ruta encontrada: {ruta_text}\n"
            texto += f"Tiempo: {resultado_bfs['tiempo']:.6f} segundos\n"
            texto += f"Padres: {resultado_bfs.get('padres', {})}\n"
            set_result_widget_text(self.resultado, texto, min_lines=3, max_lines=6)
            ruta = resultado_bfs.get('ruta_mas_corta')
            # popup si no existe la ruta
            if not ruta:
                QMessageBox.information(self, "Resultado", "La ruta no existe")
            if ruta:
                self.grafo_canvas.set_grafo(self.grafo, ruta)
            else:
                self.grafo_canvas.set_grafo(self.grafo)
            self.grafo_canvas.update()
            self.grafo_canvas.repaint()
            # Mostrar árbol BFS en vista visual (QTreeWidget)
            padres = resultado_bfs.get('arbol_bfs') or resultado_bfs.get('padres') or {}
            try:
                self.tree.set_tree(padres, ruta)
            except Exception:
                pass
            

    def volver_menu(self):
        self.close()
        self.menu = MainMenu()
        self.menu.show()

    



    

