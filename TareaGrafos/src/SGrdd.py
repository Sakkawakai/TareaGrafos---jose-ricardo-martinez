from pathlib import Path
import math

def prepararFile():
    carpeta = Path(__file__).parent
    archivo = carpeta / "MapSave.txt"

    intentos = 0
    while intentos < 3:
        try:
            # Intentar abrir en modo lectura/escritura
            with open(archivo, "r+"):
                pass
            # Si existe, lo limpiamos
            open(archivo, "w").close()
            print("✅ Archivo MapSave.txt listo para autoguardado")
            return archivo
        except FileNotFoundError:
            # Si no existe, lo creamos en modo escritura
            try:
                open(archivo, "w").close()
                print("📄 Archivo MapSave.txt creado")
            except Exception as e:
                print(f"❌ Error creando archivo: {e}")
        intentos += 1

    print("⚠️ Error: no se pudo acceder a MapSave.txt tras 3 intentos")
    return None


def guardar_mapa(ubicaciones, rutas, nombre_archivo="MapSave.txt"):
    carpeta = Path(__file__).parent
    archivo = carpeta / nombre_archivo

    with open(archivo, "w", encoding="utf-8") as f:
        # Guardar ubicaciones
        f.write("===Ubicaciones===\n")
        for u in ubicaciones:
            x, y = u.center  # posición calculada desde el canvas
            f.write(f"{u.nombre} | Posición: ({x:.2f}, {y:.2f})\n")

        f.write("\n===Rutas===\n")
        for r in rutas:
            f.write(f"{r.origen.nombre} -> {r.destino.nombre} | Distancia: {r.peso:.2f}\n")

    print(f"✅ Datos guardados en: {archivo}")


def cargar_mapa(canvas, UbicacionClass, RutaClass, nombre_archivo="MapSave.txt"):
    carpeta = Path(__file__).parent
    archivo = carpeta / nombre_archivo

    ubicaciones = []
    rutas = []

    if not archivo.exists():
        print("⚠️ No se encontró archivo de guardado")
        return ubicaciones, rutas

    with open(archivo, "r", encoding="utf-8") as f:
        lineas = f.readlines()

    modo = None
    nombre_to_obj = {}

    for linea in lineas:
        linea = linea.strip()
        if not linea:
            continue

        if linea == "===Ubicaciones===":
            modo = "ubi"
            continue
        elif linea == "===Rutas===":
            modo = "ruta"
            continue

        if modo == "ubi":
            # Ejemplo: "A | Posición: (100.00, 200.00)"
            partes = linea.split("|")
            nombre = partes[0].strip()
            coords = partes[1].replace("Posición:", "").strip()
            x, y = map(float, coords.strip("()").split(","))

            # recrear oval en canvas
            cid = canvas.create_oval(x-10, y-10, x+10, y+10, fill="black")
            ubi = UbicacionClass(nombre, cid, canvas)
            ubicaciones.append(ubi)
            nombre_to_obj[nombre] = ubi

        elif modo == "ruta":
            # Ejemplo: "A -> B | Distancia: 223.61"
            partes = linea.split("|")
            nodos = partes[0].split("->")
            origen = nombre_to_obj[nodos[0].strip()]
            destino = nombre_to_obj[nodos[1].strip()]

            # dibujar línea en canvas
            xo, yo = origen.center
            xd, yd = destino.center
            lineID = canvas.create_line(xo, yo, xd, yd, fill="#1A1E1C", width=6)

            ruta = RutaClass(origen, destino, lineID)
            rutas.append(ruta)
            origen.rutas.append(ruta)
            destino.rutas.append(ruta)

    print("✅ Datos cargados desde:", archivo)
    return ubicaciones, rutas
