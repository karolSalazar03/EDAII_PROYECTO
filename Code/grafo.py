
class Nodo:
    def __init__(self, nombre):
        self.nombre = nombre
        self.visitado = False
        self.adyacentes = []  # Lista de nodos conectados

    def agregar_adyacente(self, nodo):
        self.adyacentes.append(nodo)

class Arista:
    def __init__(self, origen, destino):
        self.origen = origen
        self.destino = destino

class Grafo:
    def __init__(self):
        self.nodos = {}  # Diccionario: {nombre_nodo: objeto_nodo}

    def agregar_nodo(self, nombre):
        if nombre not in self.nodos:
            self.nodos[nombre] = Nodo(nombre)

    def agregar_arista(self, origen, destino):
        self.agregar_nodo(origen)
        self.agregar_nodo(destino)
        self.nodos[origen].agregar_adyacente(self.nodos[destino])
        # Para grafo no dirigido, agregar también la conexión inversa
        self.nodos[destino].agregar_adyacente(self.nodos[origen])

    def eliminar_arista(self, origen, destino):
        if origen in self.nodos and destino in self.nodos:
            # Remover la conexión de origen a destino
            if self.nodos[destino] in self.nodos[origen].adyacentes:
                self.nodos[origen].adyacentes.remove(self.nodos[destino])
            # Remover la conexión inversa de destino a origen
            if self.nodos[origen] in self.nodos[destino].adyacentes:
                self.nodos[destino].adyacentes.remove(self.nodos[origen])
