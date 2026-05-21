import tkinter as tk
from PIL import Image, ImageTk
import math
import heapq
import os
import time
import SGrdd as SG

class Ruta:
    def __init__(self, origen, destino, gui_id):
        self.origen = origen
        self.destino = destino
        self.gui_id = gui_id

        self.peso = self.calcularPeso()
    
    def calcularPeso(self):
        x1, y1 = self.origen.center
        x2, y2 = self.destino.center
        self.peso = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
        return self.peso

class Ubicacion:
    def __init__(self, nombre, gui_id, canvas):
        self.nombre = nombre
        self.gui_id = gui_id
        self.canvas = canvas

        self.rutas = []

    @property
    def center(self):
        x1, y1, x2, y2 = self.canvas.coords(self.gui_id)
        return (x1 + x2) / 2, (y1 + y2) / 2

class MapApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Mapa IUPB")
        self.geometry("1000x750")

        #Creamos un canvas
        self.canvas = tk.Canvas(self, bg="black")
        self.canvas.pack(fill="both", expand=True)

        #Imagen del mapa
        self.imagen = Image.open("mapa.png")
        self.img_tk = ImageTk.PhotoImage(self.imagen)
        self.img_id = self.canvas.create_image( 0, 0, anchor = "nw", image=self.img_tk)

        #Variables de arrastre
        self.dragData = {"x": 0, "y": 0}

        #listas para ubicaciones, rutas y datos borrables.
        self.ubicaciones = []
        self.rutas = []

        self.GuiDlt = []

        #Estado de rutas
        self.modoRuta = False
        self.rutaOrigen = None

        #variables de busqueda
        self.modoBusqueda = False
        self.busquedaOrigen = None

        #Eventos
        self.canvas.bind("<ButtonPress-1>", self.StrDrag)
        self.canvas.bind("<ButtonRelease-1>", self.EdClk)
        self.canvas.bind("<B1-Motion>", self.Drag)
        self.canvas.bind("<ButtonPress-3>", self.Menu)

        #encargar evento de carga
        self.ubicaciones, self.rutas = SG.cargar_mapa(self.canvas, Ubicacion, Ruta)


        #Encargar envento de cierre
        SG.prepararFile()
        self.protocol("WM_DELETE_WINDOW", self.onClose)

    #------------------------------------------------------------->>> Eventos para mover e mapa<<    
        
    def StrDrag(self, event):
        self.dragData["x"] = event.x
        self.dragData["y"] = event.y

        
    def Drag(self, event):
        dragx = event.x - self.dragData["x"]
        dragy = event.y - self.dragData["y"]

        self.canvas.move("all", dragx, dragy)

        self.dragData["x"] = event.x
        self.dragData["y"] = event.y

    def StpDrag(self, event):
        self.dragData["x"] = 0
        self.dragData["y"] = 0

    enMenu = False
    def EdClk(self, event):
        self.StpDrag(event)
        if not self.enMenu:
            self.dltGUI()

    def dltGUI(self):
        for item in self.GuiDlt:
            self.canvas.delete(item)
        self.GuiDlt.clear()
    #------------------------------------------------------------->>> Menu contextual <<
    def Menu(self, event):
        x, y = event.x, event.y
        size = 110


        self.menuID = self.canvas.create_rectangle(x, y, x+size, y+size, fill  = "#6E6B6B")
        self.GuiDlt.append(self.menuID)

        btnUbi = tk.Button(self.canvas, text = "Agregar Ubicación",
                            bg = "white", command = lambda: self.AgUb(x, y))
        
        Ubtt_id = self.canvas.create_window(x+size/2, y+20, window = btnUbi)
        self.GuiDlt.append(Ubtt_id)

    def AgUb(self, x, y):
        circleID = self.canvas.create_oval(x-10, y-10, x+10, y+10, fill = "Black")

        #Crear nombre
        entry = tk.Entry(self.canvas)
        entry.insert(0, "")
        entry_id = self.canvas.create_window(x, y+20, window=entry)

        def saveName(event, cid= circleID, ent= entry):
            nombre = ent.get()
            nueva = Ubicacion(nombre, cid, self.canvas)
            self.ubicaciones.append(nueva)
            self.canvas.delete(entry_id)
        
        entry.bind("<Return>", saveName)


        self.canvas.tag_bind(circleID, "<Enter>", lambda e, cid=circleID: self.MsSobre(cid))
        self.canvas.tag_bind(circleID, "<Leave>", lambda e, cid=circleID: self.MsSalir(cid))
        self.canvas.tag_bind(circleID, "<Button-1>", lambda e, cid=circleID: self.MsClick(cid))

    def MsSobre(self, cid):
        self.canvas.itemconfig(cid, fill = "Yellow")
        self.enMenu = True
        

    def MsSalir(self, cid):
        self.canvas.itemconfig(cid, fill = "Black")
        self.enMenu = False
        
        
    def MsClick(self, cid):
        ubi = (next((u for u in self.ubicaciones if u.gui_id == cid), None))
        if not ubi:
            print("Ubicación no encontrada")
            return
        
        if self.modoBusqueda:
            destino = ubi

            camino, distancia = self.buscarRuta(self.busquedaOrigen, destino)

            for ruta in self.rutas:
                self.canvas.itemconfig(ruta.gui_id, fill = "#1A1E1C", width = 6)
            
            if camino is None:
                print("No se encontró ruta")
                
                mensaje = f"No se encontró ruta de {self.busquedaOrigen.nombre} a {destino.nombre}"

                mensaje_id = self.canvas.create_text(400, 50, text=mensaje, fill="red", font=("Arial", 22))
                self.after(3000, lambda: self.canvas.delete(mensaje_id))
            
            else:
                #pontar camino
                for i in range(len(camino)-1):
                    a = camino[i]
                    b = camino[i+1]

                    for ruta in self.rutas:
                        if (ruta.origen == a and ruta.destino == b) or (ruta.origen == b and ruta.destino == a):
                            self.canvas.itemconfig(ruta.gui_id, fill = "Blue", width = 6)
            
                nombres = " --> ".join([u.nombre for u in camino])

                mensaje = self.canvas.create_text(400,40,text=f"Ruta: {nombres} | Distancia: {distancia}", fill="green", font=("Arial", 22))
                self.after(5000, lambda: self.canvas.delete(mensaje))

                self.modoBusqueda = False; self.busquedaOrigen = None; self.canvas.config(cursor="arrow")
            
            return

        if self.modoRuta:

            destino = ubi
            if destino != self.rutaOrigen:
                xo, yo = self.rutaOrigen.center
                xd, yd = destino.center

                lineID = self.canvas.create_line(xo, yo, xd, yd, fill = "#1A1E1C", width = 6)
                self.canvas.tag_raise(lineID,self.img_id)
                for ubi in self.ubicaciones:
                    self.canvas.tag_lower(lineID, ubi.gui_id)
                
                NwRuta = Ruta(self.rutaOrigen, destino, lineID)
                self.rutas.append(NwRuta)
                self.rutaOrigen.rutas.append(NwRuta)
                destino.rutas.append(NwRuta)

                self.canvas.itemconfig(self.rutaOrigen.gui_id, fill="Black")
                self.canvas.itemconfig(destino.gui_id, fill="Black")

                self.modoRuta = False; self.rutaOrigen = None; self.canvas.config(cursor="arrow")
        else:
            self.canvas.itemconfig(cid, fill="green")
            x, y = ubi.center
            self.menuBID = self.canvas.create_rectangle(x+20, y, x+120, y+80, fill="#6E6B6B")

            self.name = self.canvas.create_text(x+70, y+20, text=ubi.nombre, fill="white", font=("Arial", 14))
            
            bttRuta = tk.Button(self.canvas, text= "Crear Ruta", bg="white", command=lambda: self.IniciarRuta(ubi))
            self.rutaWin = self.canvas.create_window(x+70, y+50, window=bttRuta)

            bttBusq = tk.Button(self.canvas, text= "Buscar Ruta", bg="white", command=lambda: self.IniciarBusqueda(ubi))
            self.busqWin = self.canvas.create_window(x+70, y+80, window=bttBusq)
            
            
            self.GuiDlt.append(self.menuBID); self.GuiDlt.append(self.name); 
            self.GuiDlt.append(self.rutaWin); self.GuiDlt.append(self.busqWin)
    
    def IniciarRuta(self, ubi):
        self.modoRuta = True
        self.rutaOrigen = ubi
        self.canvas.config(cursor="crosshair")
    
    def IniciarBusqueda(self, ubi):
        self.modoBusqueda = True
        self.busquedaOrigen = ubi
        self.canvas.config(cursor="crosshair")
    
    def buscarRuta(self, origen, destino):
        distancias = { u: float('inf') for u in self.ubicaciones }

        anteriores = {}

        distancias[origen] = 0

        cola = [(0, id(origen), origen)]

        while cola:
            disstanciaActual, _, actual = heapq.heappop(cola)

            if actual == destino:
                break

            for ruta in actual.rutas:

                vecino = (ruta.destino if ruta.origen == actual else ruta.origen)

                nuevaDistancia = (disstanciaActual + ruta.peso)

                if nuevaDistancia < distancias[vecino]:
                    distancias[vecino] = nuevaDistancia
                    anteriores[vecino] = actual
                    heapq.heappush(cola, (nuevaDistancia, id(vecino), vecino))
        if distancias[destino] == float('inf'):
            return None, None

        camino = []
        actual = destino

        while actual != origen:
            
            camino.append(actual)

            actual = anteriores[actual]
        
        camino.append(origen)
        camino.reverse()

        return camino, distancias[destino]
    
    def onClose(self):
        try:
            SG.guardar_mapa(self.ubicaciones, self.rutas, "MapSave.txt")
        except Exception as e:
            print(f"❌ Error guardando: {e}")
        finally:
            self.destroy()   # cerrar ventana sí o sí


app = MapApp()
app.mainloop()