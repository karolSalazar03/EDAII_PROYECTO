from grafo import Grafo
from collections import deque
import time

def bfs(grafo, inicio, fin):
    """
    BFS para encontrar la ruta más corta entre dos nodos en un grafo no dirigido.
    Retorna un diccionario con:
    - distancias: dict de distancias desde inicio a cada nodo alcanzable
    - padres: dict de padres en el árbol BFS
    - ruta_mas_corta: lista de la ruta más corta desde inicio a fin si existe, None si no
    - arbol_bfs: dict (igual a padres)
    - tiempo: tiempo de ejecución en segundos
    """
    start_time = time.time()

    start = grafo.nodos.get(inicio)
    end = grafo.nodos.get(fin)
    if not start or not end:
        return {
            'distancias': {},
            'padres': {},
            'ruta_mas_corta': None,
            'arbol_bfs': {},
            'tiempo': time.time() - start_time
        }

    visitados = set()
    cola = deque()
    padres = {}
    distancias = {}

    cola.append(start)
    visitados.add(start.nombre)
    padres[start.nombre] = None
    distancias[start.nombre] = 0

    while cola:
        actual = cola.popleft()
        if actual == end:
            # Reconstruir la ruta desde el final hasta el inicio
            ruta = []
            while actual:
                ruta.append(actual.nombre)
                actual = grafo.nodos.get(padres[actual.nombre]) if padres[actual.nombre] else None
            ruta_mas_corta = list(reversed(ruta))
            return {
                'distancias': distancias,
                'padres': padres,
                'ruta_mas_corta': ruta_mas_corta,
                'arbol_bfs': padres,
                'tiempo': time.time() - start_time
            }
        for adyacente in actual.adyacentes:
            if adyacente.nombre not in visitados:
                visitados.add(adyacente.nombre)
                padres[adyacente.nombre] = actual.nombre
                distancias[adyacente.nombre] = distancias[actual.nombre] + 1
                cola.append(adyacente)

    # Si no se encontró el fin, devolver lo que se encontró
    return {
        'distancias': distancias,
        'padres': padres,
        'ruta_mas_corta': None,
        'arbol_bfs': padres,
        'tiempo': time.time() - start_time
    }


