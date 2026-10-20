# ============================================================
# PROTEGE ANIMAL
# Aplicacion para reportar maltrato animal
# ============================================================

import os
import webbrowser
from datetime import datetime

import tkinter as tk
from tkinter import filedialog

# ============================================================
# LIBRERIAS OPCIONALES
# ============================================================

try:
    import msvcrt
    MSVCRT_DISPONIBLE = True
except ImportError:
    MSVCRT_DISPONIBLE = False

try:
    import cv2
    CV2_DISPONIBLE = True
except ImportError:
    CV2_DISPONIBLE = False

try:
    import folium
    FOLIUM_DISPONIBLE = True
except ImportError:
    FOLIUM_DISPONIBLE = False

try:
    from plyer import notification
    PLYER_DISPONIBLE = True
except ImportError:
    PLYER_DISPONIBLE = False


# ============================================================
# VARIABLES GLOBALES
# ============================================================

denuncias = []
contador_denuncia = 1
usuario_registrado = None

CARPETA_EVIDENCIAS = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "evidencias"
)

RUTA_MAPA = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "mapa_generado.html"
)


# ============================================================
# DATOS DE REFUGIOS
# ============================================================

REFUGIOS = [
    {
        "nombre": "Refugio Patitas Felices",
        "direccion": "Colonia Centro",
        "telefono": "22221111",
        "lat": 12.8654,
        "lon": -85.2072
    },
    {
        "nombre": "Refugio Huellas de Amor",
        "direccion": "Colonia San Jose",
        "telefono": "22223333",
        "lat": 12.8700,
        "lon": -85.2100
    }
]


# ============================================================
# DATOS DE VETERINARIAS
# ============================================================

VETERINARIAS = [
    {
        "nombre": "Veterinaria San Francisco",
        "direccion": "Avenida Principal",
        "telefono": "22226666",
        "lat": 12.8680,
        "lon": -85.2050
    },
    {
        "nombre": "Clinica Vida Animal",
        "direccion": "Zona Central",
        "telefono": "22227777",
        "lat": 12.8720,
        "lon": -85.2020
    }
]


# ============================================================
# VALIDAR CORREO ELECTRONICO
# CORREGIDO: PERMITE NUMEROS EN EL CORREO
# ============================================================

def correo_valido(correo):

    correo = correo.strip()

    if not correo or any(c.isspace() for c in correo):
        return False

    if correo.count("@") != 1:
        return False

    nombre, dominio = correo.split("@")

    if not nombre or not dominio:
        return False

    # Permitir letras, numeros y caracteres habituales
    # antes del simbolo @.
    caracteres_validos = (
        "abcdefghijklmnopqrstuvwxyz"
        "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        "0123456789._+-"
    )

    if not all(c in caracteres_validos for c in nombre):
        return False

    # Validar el dominio.
    if "." not in dominio:
        return False

    if dominio.startswith(".") or dominio.endswith("."):
        return False

    if ".." in correo:
        return False

    partes_dominio = dominio.split(".")

    if any(not parte for parte in partes_dominio):
        return False

    if any(
        not all(c.isalnum() or c == "-" for c in parte)
        for parte in partes_dominio
    ):
        return False

    # La terminacion debe tener al menos dos letras.
    if (
        len(partes_dominio[-1]) < 2
        or not partes_dominio[-1].isalpha()
    ):
        return False

    return True


# ============================================================
# OCULTAR CONTRASENA
# ============================================================

def ocultar_contrasena(mensaje):

    if not MSVCRT_DISPONIBLE:
        import getpass
        return getpass.getpass(mensaje)

    print(mensaje, end="", flush=True)
    contrasena = ""

    while True:

        tecla = msvcrt.getch()

        if tecla == b"\r":
            print()
            break

        elif tecla == b"\x08":

            if contrasena:
                contrasena = contrasena[:-1]
                print("\b \b", end="", flush=True)

        elif tecla in (b"\x00", b"\xe0"):
            msvcrt.getch()

        else:

            try:
                caracter = tecla.decode("utf-8")

                if caracter.isprintable():
                    contrasena += caracter
                    print("*", end="", flush=True)

            except UnicodeDecodeError:
                pass

    return contrasena


# ============================================================
# 1. CREAR CUENTA
# CORREGIDO: VALIDAR EL CORREO CON CORREO_VALIDO()
# ============================================================

def crear_una_cuenta():

    print("\n===== CREAR CUENTA =====")

    try:

        nombre = input("Ingrese su nombre: ").strip()

        if not nombre:
            print("El nombre es obligatorio.")
            return None

        if not nombre.replace(" ", "").isalpha():
            print("El nombre solo debe contener letras.")
            return None

        # Solicitar el correo despues de validar el nombre.
        correo = input(
            "Ingrese su correo electronico: "
        ).strip()

        # Esta validacion permite numeros en el correo.
        if not correo_valido(correo):
            print("Correo no valido.")
            print("Ejemplo: usuario123@gmail.com")
            return None

        contrasena = ocultar_contrasena(
            "Ingrese su contrasena: "
        )

        if not contrasena:
            print("La contrasena no puede estar vacia.")
            return None

        confirmar = ocultar_contrasena(
            "Confirme su contrasena: "
        )

        if contrasena != confirmar:
            print("Las contrasenas no coinciden.")
            return None

        usuario = {
            "nombre": nombre,
            "correo": correo,
            "contrasena": contrasena
        }

        print("\nCuenta creada correctamente.")

        return usuario

    except (ValueError, EOFError, KeyboardInterrupt) as error:
        print("No se pudo crear la cuenta:", error)
        return None


# ============================================================
# 2. INICIAR SESION
# ============================================================

def iniciar_sesion(usuario):

    print("\n===== INICIAR SESION =====")

    if usuario is None:
        print("Primero debe crear una cuenta.")
        return False

    try:

        correo = input("Ingrese su correo: ").strip()

        if not correo_valido(correo):
            print("El correo no es valido.")
            return False

        contrasena = ocultar_contrasena(
            "Ingrese su contrasena: "
        )

        if (
            correo.lower() == usuario["correo"].lower()
            and contrasena == usuario["contrasena"]
        ):

            print("\nBienvenido", usuario["nombre"])
            print("Inicio de sesion exitoso.")

            return True

        print("Correo o contrasena incorrectos.")
        return False

    except (ValueError, EOFError, KeyboardInterrupt) as error:
        print("Error al iniciar sesion:", error)
        return False


# ============================================================
# CLASE DENUNCIA
# ============================================================

class Denuncia:

    def __init__(
        self,
        numero,
        tipo_maltrato,
        descripcion,
        ubicacion,
        fecha
    ):

        self.numero = numero
        self.tipo_maltrato = tipo_maltrato
        self.descripcion = descripcion
        self.ubicacion = ubicacion
        self.fecha = fecha
        self.fotografia = None

    def mostrar_denuncia(self):

        print("\n------------------------------")
        print("Numero:", self.numero)
        print("Tipo de maltrato:", self.tipo_maltrato)
        print("Descripcion:", self.descripcion)
        print("Ubicacion:", self.ubicacion)
        print("Fecha:", self.fecha)

        if self.fotografia:
            print("Fotografia:", self.fotografia)
        else:
            print("Fotografia: Sin fotografia")

        print("------------------------------")


# ============================================================
# 3. REGISTRAR DENUNCIA
# ============================================================

def registrar_denuncia():

    global contador_denuncia

    print("\n===== REGISTRAR DENUNCIA =====")

    try:

        tipo = input(
            "Tipo de maltrato animal: "
        ).strip()

        if not tipo or not any(c.isalpha() for c in tipo):
            print("Ingrese un tipo de maltrato valido.")
            return None

        descripcion = input(
            "Descripcion del caso: "
        ).strip()

        if not descripcion:
            print("La descripcion es obligatoria.")
            return None

        ubicacion = input(
            "Ubicacion del animal: "
        ).strip()

        if not ubicacion:
            print("La ubicacion es obligatoria.")
            return None

        fecha = input(
            "Fecha (DD/MM/AAAA): "
        ).strip()

        fecha_correcta = datetime.strptime(
            fecha,
            "%d/%m/%Y"
        )

        denuncia = Denuncia(
            contador_denuncia,
            tipo,
            descripcion,
            ubicacion,
            fecha_correcta.strftime("%d/%m/%Y")
        )

        denuncias.append(denuncia)
        contador_denuncia += 1

        print("\nDenuncia registrada correctamente.")
        print("Numero de denuncia:", denuncia.numero)

        return denuncia

    except ValueError:
        print("Error: revise los datos y la fecha.")
        print("Use el formato DD/MM/AAAA.")
        return None

    except (EOFError, KeyboardInterrupt):
        print("\nRegistro cancelado.")
        return None


# ============================================================
# 4. VER DENUNCIAS
# ============================================================

def ver_denuncias():

    print("\n===== DENUNCIAS REGISTRADAS =====")

    if len(denuncias) == 0:
        print("No hay denuncias registradas.")
        return

    for denuncia in denuncias:
        denuncia.mostrar_denuncia()


# ============================================================
# 5. BUSCAR DENUNCIA
# ============================================================

def buscar_denuncia():

    print("\n===== BUSCAR DENUNCIA =====")

    if not denuncias:
        print("No hay denuncias registradas.")
        return

    try:

        numero = int(
            input("Ingrese el numero de denuncia: ")
        )

        for denuncia in denuncias:

            if denuncia.numero == numero:
                print("Denuncia encontrada.")
                denuncia.mostrar_denuncia()
                return

        print("No se encontro esa denuncia.")

    except ValueError:
        print("Debe ingresar un numero entero.")


# ============================================================
# 6. DESCRIPCION DEL REPORTE
# ============================================================

def descripcion_reporte():

    print("\n===== DESCRIPCION DEL REPORTE =====")

    try:

        ocurrido = input(
            "Que ocurrio?: "
        ).strip()

        animal = input(
            "Que animal fue afectado?: "
        ).strip()

        informacion = input(
            "Informacion adicional: "
        ).strip()

        if not ocurrido or not animal or not informacion:
            print("Todos los campos son obligatorios.")
            return

        print("\nDescripcion del reporte:")
        print("Lo ocurrido:", ocurrido)
        print("Animal afectado:", animal)
        print("Informacion adicional:", informacion)

    except (ValueError, EOFError, KeyboardInterrupt) as error:
        print("Error:", error)


# ============================================================
# SELECCIONAR FOTOGRAFIA DE LA GALERIA
# ============================================================

def seleccionar_fotografia():

    ventana = None

    try:

        ventana = tk.Tk()
        ventana.withdraw()

        ruta = filedialog.askopenfilename(
            title="Seleccionar fotografia",
            filetypes=[
                ("Imagenes", "*.jpg *.jpeg *.png *.bmp"),
                ("Todos los archivos", "*.*")
            ]
        )

        return ruta if ruta else None

    except Exception as error:
        print("Error al abrir la galeria:", error)
        return None

    finally:

        if ventana is not None:
            ventana.destroy()


# ============================================================
# TOMAR FOTOGRAFIA CON LA CAMARA
# ============================================================

def tomar_fotografia():

    if not CV2_DISPONIBLE:
        print("La camara requiere opencv-python.")
        print("Instale con: pip install opencv-python")
        return None

    camara = None

    try:

        os.makedirs(
            CARPETA_EVIDENCIAS,
            exist_ok=True
        )

        camara = cv2.VideoCapture(0)

        if not camara.isOpened():
            print("No se pudo abrir la camara.")
            return None

        fotografia = None

        print("Presione ESPACIO para capturar.")
        print("Presione ESC para cancelar.")

        while True:

            correcto, imagen = camara.read()

            if not correcto:
                print("No se pudo obtener la imagen.")
                break

            cv2.imshow("PROTEGE ANIMAL", imagen)

            tecla = cv2.waitKey(1) & 0xFF

            if tecla == 27:
                break

            if tecla == 32:

                nombre = datetime.now().strftime(
                    "evidencia_%Y%m%d_%H%M%S.png"
                )

                fotografia = os.path.join(
                    CARPETA_EVIDENCIAS,
                    nombre
                )

                if cv2.imwrite(fotografia, imagen):
                    print("Fotografia guardada:", fotografia)
                else:
                    print("No se pudo guardar la fotografia.")
                    fotografia = None

                break

        return fotografia

    except Exception as error:
        print("Error con la camara:", error)
        return None

    finally:

        if camara is not None:
            camara.release()

        if CV2_DISPONIBLE:
            cv2.destroyAllWindows()


# ============================================================
# 7. SUBIR FOTOGRAFIA A UNA DENUNCIA
# ============================================================

def subir_fotografias():

    print("\n===== SUBIR FOTOGRAFIA =====")

    if not denuncias:
        print("Primero debe registrar una denuncia.")
        return

    try:

        numero = int(
            input("Numero de la denuncia: ")
        )

    except ValueError:
        print("Ingrese un numero valido.")
        return

    denuncia_encontrada = None

    for denuncia in denuncias:

        if denuncia.numero == numero:
            denuncia_encontrada = denuncia
            break

    if denuncia_encontrada is None:
        print("No se encontro esa denuncia.")
        return

    print("\n1. Seleccionar desde galeria")
    print("2. Tomar fotografia con camara")

    opcion = input("Seleccione una opcion: ").strip()

    if opcion == "1":
        fotografia = seleccionar_fotografia()

    elif opcion == "2":
        fotografia = tomar_fotografia()

    else:
        print("Opcion no valida.")
        return

    if fotografia:

        denuncia_encontrada.fotografia = fotografia

        print("Fotografia asociada correctamente.")
        print("Archivo:", fotografia)

    else:
        print("No se selecciono ninguna fotografia.")


# ============================================================
# MOSTRAR REFUGIOS
# ============================================================

def mostrar_refugios():

    print("\n===== REFUGIOS =====")

    for refugio in REFUGIOS:

        print("\nNombre:", refugio["nombre"])
        print("Direccion:", refugio["direccion"])
        print("Telefono:", refugio["telefono"])


# ============================================================
# MOSTRAR VETERINARIAS
# ============================================================

def mostrar_veterinarias():

    print("\n===== VETERINARIAS =====")

    for veterinaria in VETERINARIAS:

        print("\nNombre:", veterinaria["nombre"])
        print("Direccion:", veterinaria["direccion"])
        print("Telefono:", veterinaria["telefono"])


# ============================================================
# MOSTRAR MAPA
# ============================================================

def mostrar_mapa():

    if not FOLIUM_DISPONIBLE:
        print("Instale folium con: pip install folium")
        return

    try:

        mapa = folium.Map(
            location=[12.8654, -85.2072],
            zoom_start=13
        )

        for refugio in REFUGIOS:

            folium.Marker(
                [refugio["lat"], refugio["lon"]],
                popup=refugio["nombre"]
            ).add_to(mapa)

        for veterinaria in VETERINARIAS:

            folium.Marker(
                [veterinaria["lat"], veterinaria["lon"]],
                popup=veterinaria["nombre"]
            ).add_to(mapa)

        mapa.save(RUTA_MAPA)

        webbrowser.open(
            "file://" + os.path.abspath(RUTA_MAPA)
        )

        print("Mapa abierto correctamente.")

    except Exception as error:
        print("Error al generar el mapa:", error)


# ============================================================
# ENVIAR NOTIFICACION
# ============================================================

def enviar_notificacion():

    mensaje = input(
        "Escriba el mensaje de alerta: "
    ).strip()

    if not mensaje:
        print("El mensaje no puede estar vacio.")
        return

    if PLYER_DISPONIBLE:

        try:

            notification.notify(
                title="PROTEGE ANIMAL",
                message=mensaje,
                timeout=5
            )

            print("Notificacion enviada.")

        except Exception as error:
            print("No se pudo enviar la notificacion:", error)

    else:

        print("\n===== ALERTA =====")
        print(mensaje)
        print("Para notificaciones del sistema instale plyer.")


# ============================================================
# LLAMAR A UN SERVICIO
# ============================================================

def llamar_directamente():

    print("\n===== LLAMAR DIRECTAMENTE =====")
    print("1. Refugio")
    print("2. Veterinaria")
    print("3. Introducir otro numero")

    opcion = input("Seleccione una opcion: ").strip()

    if opcion == "1":

        mostrar_refugios()

        nombre = input(
            "Escriba el nombre del refugio: "
        ).strip().lower()

        for refugio in REFUGIOS:

            if refugio["nombre"].lower() == nombre:
                webbrowser.open(
                    "tel:" + refugio["telefono"]
                )
                print("Solicitud de llamada abierta.")
                return

        print("No se encontro el refugio.")

    elif opcion == "2":

        mostrar_veterinarias()

        nombre = input(
            "Escriba el nombre de la veterinaria: "
        ).strip().lower()

        for veterinaria in VETERINARIAS:

            if veterinaria["nombre"].lower() == nombre:
                webbrowser.open(
                    "tel:" + veterinaria["telefono"]
                )
                print("Solicitud de llamada abierta.")
                return

        print("No se encontro la veterinaria.")

    elif opcion == "3":

        telefono = input(
            "Ingrese el numero telefonico: "
        ).strip()

        if telefono:
            webbrowser.open("tel:" + telefono)
            print("Solicitud de llamada abierta.")
        else:
            print("Debe ingresar un numero.")

    else:
        print("Opcion no valida.")


# ============================================================
# SERVICIOS ADICIONALES
# ============================================================

def servicios_adicionales():

    while True:

        print("\n===== SERVICIOS DE AYUDA =====")
        print("1. Ver refugios")
        print("2. Ver veterinarias")
        print("3. Mostrar mapa")
        print("4. Enviar notificacion")
        print("5. Llamar directamente")
        print("6. Volver")

        opcion = input("Seleccione una opcion: ").strip()

        if opcion == "1":
            mostrar_refugios()

        elif opcion == "2":
            mostrar_veterinarias()

        elif opcion == "3":
            mostrar_mapa()

        elif opcion == "4":
            enviar_notificacion()

        elif opcion == "5":
            llamar_directamente()

        elif opcion == "6":
            break

        else:
            print("Opcion no valida.")


# ============================================================
# MENU PRINCIPAL
# ============================================================

def menu():

    usuario = None
    sesion_iniciada = False

    while True:

        print("\n================================")
        print("        PROTEGE ANIMAL")
        print("================================")
        print("1. Crear cuenta")
        print("2. Iniciar sesion")
        print("3. Registrar denuncia")
        print("4. Ver denuncias")
        print("5. Buscar denuncia")
        print("6. Descripcion del reporte")
        print("7. Subir fotografia")
        print("8. Servicios y salir")

        opcion = input(
            "Seleccione una opcion: "
        ).strip()

        if opcion == "1":

            nuevo_usuario = crear_una_cuenta()

            if nuevo_usuario is not None:
                usuario = nuevo_usuario
                sesion_iniciada = False

        elif opcion == "2":

            if usuario is None:
                print("Primero debe crear una cuenta.")

            else:
                sesion_iniciada = iniciar_sesion(usuario)

        elif opcion == "3":

            if not sesion_iniciada:
                print("Primero debe iniciar sesion.")

            else:
                registrar_denuncia()

        # OPCION 4: NO REQUIERE INICIAR SESION
        elif opcion == "4":
            ver_denuncias()

        elif opcion == "5":

            if not sesion_iniciada:
                print("Primero debe iniciar sesion.")

            else:
                buscar_denuncia()

        elif opcion == "6":

            if not sesion_iniciada:
                print("Primero debe iniciar sesion.")

            else:
                descripcion_reporte()

        elif opcion == "7":

            if not sesion_iniciada:
                print("Primero debe iniciar sesion.")

            else:
                subir_fotografias()

        elif opcion == "8":

            print("\n1. Servicios de ayuda")
            print("2. Cerrar sesion")
            print("3. Salir del programa")

            subopcion = input(
                "Seleccione una opcion: "
            ).strip()

            if subopcion == "1":
                servicios_adicionales()

            elif subopcion == "2":

                if sesion_iniciada:
                    sesion_iniciada = False
                    print("Sesion cerrada correctamente.")
                else:
                    print("No hay una sesion iniciada.")

            elif subopcion == "3":
                print("Gracias por utilizar PROTEGE ANIMAL.")
                break

            else:
                print("Opcion no valida.")

        else:
            print("Opcion no valida. Elija del 1 al 8.")


# ============================================================
# EJECUTAR PROGRAMA
# ============================================================

if __name__ == "__main__":
    try:
        menu()
    except KeyboardInterrupt:
        print("\nPrograma finalizado.")
        