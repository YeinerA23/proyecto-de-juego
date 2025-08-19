# -*- coding: utf-8 -*-
# Diseño estilo "¿Quién quiere ser millonario?"
# - Sonido al acertar, fallar y terminar
# - Botón "Volver a jugar" después de perder/ganar
# - Lee preguntas desde preguntas.json (respuesta: "A","B","C","D")

import tkinter as tk
from tkinter import messagebox
import json, random, os

# -------- Sonido con pygame (opcional pero recomendado) --------
try:
    import pygame
    pygame.mixer.init()
except Exception as e:
    pygame = None
    print("⚠️ Sonido deshabilitado (pygame no disponible):", e)

def cargar_sonido(nombre):
    """Intenta cargar un sonido si pygame está disponible; retorna None si no existe."""
    if pygame is None:
        return None
    if os.path.exists(nombre):
        try:
            return pygame.mixer.Sound(nombre)
        except Exception as e:
            print(f"⚠️ No se pudo cargar {nombre}: {e}")
            return None
    else:
        print(f"ℹ️ Sonido no encontrado: {nombre}")
        return None

snd_correcto  = cargar_sonido("correcto.mp3")
snd_incorrecto= cargar_sonido("incorrecto.mp3")
snd_fin       = cargar_sonido("fin_juego.mp3")

def play(sound):
    if sound:
        try:
            sound.play()
        except Exception as e:
            print("⚠️ Error al reproducir sonido:", e)

# -------- Cargar preguntas --------
def cargar_preguntas():
    try:
        with open("preguntas.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            # Validación simple
            val = []
            for q in data:
                if {"pregunta","opciones","respuesta"} <= set(q.keys()):
                    val.append(q)
            return val if val else []
    except Exception as e:
        print("⚠️ No se pudo leer preguntas.json:", e)
        return []

preguntas = cargar_preguntas()
if not preguntas:
    preguntas = [
        {
            "pregunta": "¿Capital de Colombia?",
            "opciones": ["A) Bogotá","B) Lima","C) Quito","D) Caracas"],
            "respuesta": "A"
        }
    ]

# -------- Lógica del juego --------
puntaje = 0
indice_pregunta = 0

def mostrar_pregunta():
    global indice_pregunta
    if indice_pregunta >= len(preguntas):
        finalizar_juego(ganador=True)
        return

    p = preguntas[indice_pregunta]
    pregunta_lbl.config(text=p["pregunta"])
    for i, opcion in enumerate(p["opciones"]):
        botones[i].config(text=opcion, state="normal")
    resultado_lbl.config(text="")
    marcador_lbl.config(text=f"Puntos: {puntaje}")

def verificar_respuesta(letra):
    global puntaje, indice_pregunta
    correcta = preguntas[indice_pregunta]["respuesta"].strip().upper()
    if letra == correcta:
        puntaje += 100
        play(snd_correcto)
        resultado_lbl.config(text="✅ ¡Correcto! +100", fg="#00d084")
        indice_pregunta += 1
        ventana.after(900, mostrar_pregunta)
    else:
        play(snd_incorrecto)
        resultado_lbl.config(text=f"❌ Incorrecto. Era {correcta}", fg="#ff6868")
        for b in botones: b.config(state="disabled")
        ventana.after(900, lambda: finalizar_juego(ganador=False))

def finalizar_juego(ganador):
    for b in botones: b.config(state="disabled")
    play(snd_fin if ganador else snd_incorrecto)
    titulo = "🎉 ¡Ganaste!" if ganador else "Juego terminado"
    messagebox.showinfo(titulo, f"Puntaje final: {puntaje}")
    reiniciar_btn.pack(pady=18)

def reiniciar_juego():
    global puntaje, indice_pregunta, preguntas
    puntaje = 0
    indice_pregunta = 0
    random.shuffle(preguntas)
    reiniciar_btn.pack_forget()
    mostrar_pregunta()

# -------- Interfaz (Tkinter) --------
ventana = tk.Tk()
ventana.title("¿Quién quiere ser millonario?")
ventana.geometry("900x620")
ventana.configure(bg="black")

fuente_titulo    = ("Arial Black", 24, "bold")
fuente_pregunta  = ("Arial", 20, "bold")
fuente_opcion    = ("Arial", 16, "bold")
fuente_marcador  = ("Arial", 14, "bold")

titulo_lbl = tk.Label(ventana, text="¿QUIÉN QUIERE SER MILLONARIO?",
                      font=fuente_titulo, bg="black", fg="gold")
titulo_lbl.pack(pady=16)

pregunta_lbl = tk.Label(ventana, text="", font=fuente_pregunta, wraplength=820,
                        bg="black", fg="white", justify="center")
pregunta_lbl.pack(pady=28)

frame_opciones = tk.Frame(ventana, bg="black")
frame_opciones.pack()

botones = []
letras = ["A","B","C","D"]
for i in range(4):
    b = tk.Button(frame_opciones, text="", width=35, height=2, font=fuente_opcion,
                  bg="#0b1d5b", fg="white", activebackground="#153b9b",
                  command=lambda x=letras[i]: verificar_respuesta(x))
    b.grid(row=i//2, column=i%2, padx=18, pady=18)
    botones.append(b)

resultado_lbl = tk.Label(ventana, text="", font=("Arial", 16, "bold"),
                         bg="black", fg="white")
resultado_lbl.pack(pady=8)

marcador_lbl = tk.Label(ventana, text="Puntos: 0", font=fuente_marcador,
                        bg="black", fg="gold")
marcador_lbl.pack(pady=4)

reiniciar_btn = tk.Button(ventana, text="🔄 Volver a jugar", font=fuente_opcion,
                          bg="green", fg="white", command=reiniciar_juego)

# Atajos de teclado (opcional)
def on_key(e):
    k = e.keysym.upper()
    if k in ("A","B","C","D"):
        verificar_respuesta(k)
    elif k == "R" and reiniciar_btn.winfo_ismapped():
        reiniciar_juego()

ventana.bind("<KeyPress>", on_key)

# Iniciar
random.shuffle(preguntas)
mostrar_pregunta()
ventana.mainloop()
