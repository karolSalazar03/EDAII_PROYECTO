from grafo import Grafo

def dfs_ruta_mas_profunda(grafo, inicio, fin):
    start = grafo.nodos.get(inicio)
    end = grafo.nodos.get(fin)
    if not start or not end:
        return None

    rutas_mas_largas = []

    def dfs_recursivo(nodo, ruta, visitados):
        if nodo == end:
            rutas_mas_largas.append(list(ruta))
            return
        for adyacente in nodo.adyacentes:
            if adyacente.nombre not in visitados:
                visitados.add(adyacente.nombre)
                ruta.append(adyacente.nombre)
                dfs_recursivo(adyacente, ruta, visitados)
                ruta.pop()
                visitados.remove(adyacente.nombre)

    dfs_recursivo(start, [start.nombre], set([start.nombre]))

    if not rutas_mas_largas:
        return None
    # Selecciona la ruta más larga
    return max(rutas_mas_largas, key=len)