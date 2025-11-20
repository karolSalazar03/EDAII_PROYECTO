# 🏫 Sistema de Evacuación en Campus — BFS y DFS
![Python](https://img.shields.io/badge/Python-3.8%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Graph Theory](https://img.shields.io/badge/Graph%20Theory-BFS%20%7C%20DFS-red)

![Portada](Media/Evacuacion.png)

Aplicación en Python que utiliza algoritmos BFS y DFS para analizar y planificar rutas de evacuación en redes de edificios de un campus universitario.

## 📌 Características Principales
- Implementación de grafos con clases `Grafo`, `Nodo` y `Arista`.
- Algoritmos BFS (ruta más corta) y DFS (ruta más profunda) aplicados a redes de edificios en campus.
- Interfaz gráfica intuitiva con PyQt5 y visualización de grafos con Matplotlib (sin librerías externas de grafos).
- Carga de datos manual o desde archivos CSV.

## 🚀 Instalación Rápida
1. Clona el repositorio y navega a la carpeta del proyecto.

   ```bash
   git clone https://github.com/tu-usuario/nombre-del-repo.git
   cd nombre-del-repo
   ```

2. Instala las dependencias:

   ```bash
   pip install -r requirements.txt
   ```

3. Ejecuta el menú principal:

   ```bash
   python main.py
   ```

## 🖥️ Uso
- Elige entre los modos DFS o BFS desde el menú principal.
- Agrega conexiones entre edificios manualmente o carga un archivo CSV.
- Busca rutas de evacuación entre dos edificios usando el algoritmo seleccionado.

## 📂 Estructura del Proyecto
- `main.py`: Menú principal para seleccionar BFS o DFS.
- `interfaz.py`: Interfaces gráficas para ambos algoritmos.
- `grafo.py`: Estructura de datos de grafo.
- `bfs.py` y `dfs.py`: Implementaciones de los algoritmos.
- `Media/`: Recursos gráficos (por ejemplo, íconos de edificios).
