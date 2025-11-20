from grafo import Grafo
import time

def dfs(grafo, inicio, fin):
    """
    DFS para explorar el grafo desde inicio hasta fin.
    Retorna un diccionario con:
    - padres: dict de padres en el árbol DFS
    - arbol_dfs: dict (igual a padres)
    - ruta_encontrada: lista de la ruta encontrada por DFS a fin si existe, None si no
    - camino_mas_profundo: lista del camino más profundo (más largo) desde inicio a fin
    - tiempo: tiempo de ejecución en segundos
    """
    start_time = time.time()

    start = grafo.nodos.get(inicio)
    end = grafo.nodos.get(fin)
    if not start or not end:
        return {
            'padres': {},
            'arbol_dfs': {},
            'ruta_encontrada': None,
            'camino_mas_profundo': [],
            'tiempo': time.time() - start_time
        }

    rutas_todas = []

    def dfs_recursivo(nodo, ruta, visitados):
        if nodo == end:
            rutas_todas.append(list(ruta))
            return
        for adyacente in nodo.adyacentes:
            if adyacente.nombre not in visitados:
                visitados.add(adyacente.nombre)
                ruta.append(adyacente.nombre)
                dfs_recursivo(adyacente, ruta, visitados)
                ruta.pop()
                visitados.remove(adyacente.nombre)

    dfs_recursivo(start, [start.nombre], set([start.nombre]))

    if not rutas_todas:
        return {
            'padres': {},
            'arbol_dfs': {},
            'ruta_encontrada': None,
            'camino_mas_profundo': [],
            'tiempo': time.time() - start_time
        }

    # Primera ruta encontrada (simulando DFS)
    ruta_encontrada = rutas_todas[0] if rutas_todas else None

    # Ruta más larga (más profunda)
    camino_mas_profundo = max(rutas_todas, key=len) if rutas_todas else []

    # Construir árbol DFS estándar para padres
    visitados = set()
    padres = {}

    def construir_arbol_dfs(nodo):
        visitados.add(nodo.nombre)
        for adyacente in nodo.adyacentes:
            if adyacente.nombre not in visitados:
                padres[adyacente.nombre] = nodo.nombre
                construir_arbol_dfs(adyacente)

    padres[start.nombre] = None
    construir_arbol_dfs(start)

    return {
        'padres': padres,
        'arbol_dfs': padres,
        'ruta_encontrada': ruta_encontrada,
        'camino_mas_profundo': camino_mas_profundo,
        'tiempo': time.time() - start_time
    }
