import csv
import os
import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image, ImageTk

ETIQUETAS = [
    "circulo",
    "triangulo",
    "cuadrado"
]

EXTENSION_VALIDA = (".png")

class EtiquetadorImagenes:

    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Programa A — Revisión y Corrección de Etiquetado")
        self.ventana.geometry("900x750")

        self.archivos = []
        self.indice_actual = 0
        self.carpeta = None
        self.imagen_tk = None
        self.etiquetas_guardadas = {}

        titulo = tk.Label(
            ventana,
            text="Programa A: Revisión y Corrección del Etiquetado",
            font=("Arial", 18, "bold")
        )
        titulo.pack(pady=10)

        self.boton_carpeta = tk.Button(
            ventana,
            text="Seleccionar carpeta de imágenes",
            font=("Arial", 12, "bold"),
            bg="#2196F3",
            fg="white",
            padx=10,
            pady=5,
            command=self.seleccionar_carpeta
        )
        self.boton_carpeta.pack(pady=10)

        self.label_archivo = tk.Label(
            ventana,
            text="No se ha seleccionado una carpeta",
            font=("Arial", 12)
        )
        self.label_archivo.pack(pady=5)

        self.label_etiqueta_actual = tk.Label(
            ventana,
            text="",
            font=("Arial", 12, "italic"),
            fg="#D32F2F"
        )
        self.label_etiqueta_actual.pack(pady=2)

        self.label_progreso = tk.Label(
            ventana,
            text="",
            font=("Arial", 11)
        )
        self.label_progreso.pack(pady=5)

        self.panel_imagen = tk.Label(ventana)
        self.panel_imagen.pack(pady=10)

        instruccion = tk.Label(
            ventana,
            text="Observe la figura e indique/corrija la etiqueta correcta:",
            font=("Arial", 12, "bold")
        )
        instruccion.pack(pady=10)

        marco_botones = tk.Frame(ventana)
        marco_botones.pack(pady=5)

        for etiqueta in ETIQUETAS:
            boton = tk.Button(
                marco_botones,
                text=etiqueta.capitalize(),
                width=12,
                font=("Arial", 12, "bold"),
                bg="#4CAF50",
                fg="white",
                command=lambda e=etiqueta: self.guardar_etiqueta(e)
            )
            boton.pack(side=tk.LEFT, padx=10)

        marco_nav = tk.Frame(ventana)
        marco_nav.pack(pady=10)

        self.boton_anterior = tk.Button(
            marco_nav,
            text="← Anterior",
            font=("Arial", 11),
            command=self.imagen_anterior
        )
        self.boton_anterior.pack(side=tk.LEFT, padx=5)

        self.boton_omitir = tk.Button(
            marco_nav,
            text="Omitir / Siguiente →",
            font=("Arial", 11),
            command=self.omitir_imagen
        )
        self.boton_omitir.pack(side=tk.LEFT, padx=5)

        self.label_estado = tk.Label(
            ventana,
            text="",
            font=("Arial", 11)
        )
        self.label_estado.pack(pady=10)

    def seleccionar_carpeta(self):
        carpeta = filedialog.askdirectory(
            title="Seleccione la carpeta que contiene las imágenes"
        )

        if not carpeta:
            return

        self.carpeta = carpeta

        self.archivos = [
            nombre
            for nombre in os.listdir(carpeta)
            if nombre.lower().endswith(EXTENSION_VALIDA)
        ]

        self.archivos.sort()
        self.indice_actual = 0

        if len(self.archivos) == 0:
            messagebox.showwarning(
                "Sin imágenes",
                "La carpeta seleccionada no contiene imágenes compatibles."
            )
            return

        self.cargar_etiquetas_existentes()

        self.label_estado.config(
            text=f"Se encontraron {len(self.archivos)} imágenes."
        )

        self.mostrar_imagen_actual()

    def cargar_etiquetas_existentes(self):
        """Carga las etiquetas ya registradas en etiquetas.csv para permitir su edición."""
        ruta_csv = os.path.join(self.carpeta, "etiquetas.csv")
        self.etiquetas_guardadas = {}

        if os.path.exists(ruta_csv):
            try:
                with open(ruta_csv, "r", encoding="utf-8") as archivo:
                    lector = csv.reader(archivo)
                    encabezado = next(lector, None)
                    for fila in lector:
                        if len(fila) >= 2:
                            self.etiquetas_guardadas[fila[0]] = fila[1]
            except Exception as e:
                print(f"Error al leer etiquetas.csv: {e}")

    def mostrar_imagen_actual(self):
        if self.indice_actual >= len(self.archivos):
            self.finalizar()
            return

        nombre_archivo = self.archivos[self.indice_actual]
        ruta = os.path.join(self.carpeta, nombre_archivo)

        try:
            imagen = Image.open(ruta)
            imagen = imagen.resize((280, 280), Image.NEAREST)
            self.imagen_tk = ImageTk.PhotoImage(imagen)

            self.panel_imagen.config(image=self.imagen_tk)
            self.label_archivo.config(text=f"Archivo: {nombre_archivo}")

            etq_actual = self.etiquetas_guardadas.get(nombre_archivo, "Sin etiqueta / No registrada")
            self.label_etiqueta_actual.config(
                text=f"Etiqueta actual registrada: {etq_actual}"
            )

            self.label_progreso.config(
                text=f"Imagen {self.indice_actual + 1} de {len(self.archivos)}"
            )

        except Exception as error:
            messagebox.showerror(
                "Error",
                f"No fue posible abrir la imagen:\n{nombre_archivo}\n\n{error}"
            )
            self.indice_actual += 1
            self.mostrar_imagen_actual()

    def guardar_etiqueta(self, etiqueta):
        if not self.archivos:
            return

        nombre_archivo = self.archivos[self.indice_actual]
        self.etiquetas_guardadas[nombre_archivo] = etiqueta

        self.reescribir_csv()

        self.label_estado.config(
            text=f"✓ Etiqueta guardada: {nombre_archivo} -> {etiqueta}"
        )

        self.indice_actual += 1
        self.mostrar_imagen_actual()

    def reescribir_csv(self):
        """Guarda de forma limpia todas las etiquetas acumuladas en etiquetas.csv."""
        ruta_csv = os.path.join(self.carpeta, "etiquetas.csv")
        with open(ruta_csv, "w", newline="", encoding="utf-8") as archivo:
            escritor = csv.writer(archivo)
            escritor.writerow(["archivo", "etiqueta"])
            for arq in sorted(self.etiquetas_guardadas.keys()):
                escritor.writerow([arq, self.etiquetas_guardadas[arq]])

    def omitir_imagen(self):
        if not self.archivos:
            return

        self.indice_actual += 1
        self.mostrar_imagen_actual()

    def imagen_anterior(self):
        if not self.archivos or self.indice_actual <= 0:
            return

        self.indice_actual -= 1
        self.mostrar_imagen_actual()

    def finalizar(self):
        self.panel_imagen.config(image="")
        self.label_archivo.config(text="Proceso de revisión y etiquetado finalizado.")
        self.label_etiqueta_actual.config(text="")
        self.label_progreso.config(text="")
        self.label_estado.config(
            text="Todas las correcciones fueron guardadas en etiquetas.csv"
        )

        messagebox.showinfo(
            "Proceso terminado",
            "Has llegado al final de las imágenes.\n\n"
            "El archivo etiquetas.csv se actualizó correctamente con todas las correcciones."
        )


if __name__ == "__main__":
    ventana = tk.Tk()
    app = EtiquetadorImagenes(ventana)
    ventana.mainloop()