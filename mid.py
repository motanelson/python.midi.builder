#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Conversor texto → MIDI
Autor: (seu nome)
Descrição:
    Lê um ficheiro contendo dígitos 0‑9 (acordes) e letras A‑H (notas)
    e escreve um .mid tocável.
"""

from pathlib import Path
import sys
from mido import Message, MidiFile, MidiTrack, bpm2tempo

# ---------- Configurações ----------
TICKS_PER_BEAT = 480          # resolução MIDI
BPM             = 120         # tempo (pode alterar)
# Dicionário de acordes (tríades maiores / menores simples)
ACORDES = {
    '0': [60, 64, 67],   # C maior  (C‑E‑G)
    '1': [62, 65, 69],   # D menor  (D‑F‑A)
    '2': [64, 67, 71],   # E menor
    '3': [65, 69, 72],   # F maior
    '4': [67, 71, 74],   # G maior
    '5': [69, 72, 76],   # A menor
    '6': [71, 74, 77],   # B diminuto (B‑D‑F)
    '7': [72, 76, 79],   # C maior (oitava acima)
    '8': [74, 77, 81],   # D menor (oitava acima)
    '9': [76, 79, 83],   # E menor (oitava acima)
}
# Dicionário de notas individuais (escala natural A‑H)
NOTAS = {
    'A': 69,  # A4 = 440 Hz
    'B': 71,
    'C': 60,  # C4 (middle C)
    'D': 62,
    'E': 64,
    'F': 65,
    'G': 67,
    'H': 70,  # B natural (notação alemã) – opcional
}

DURACAO_NOTA = TICKS_PER_BEAT  # cada símbolo = semínima

# ---------- Funções utilitárias ----------
def toca_notas(track, notas, ticks):
    """Adiciona eventos note_on / note_off para uma lista de notas, com pausa entre eventos."""
    DURACAO_NOTA = int(ticks * 0.75)  # 75% do tempo = nota
    PAUSA = ticks - DURACAO_NOTA      # 25% = silêncio

    # Toca notas simultâneas (acorde ou nota única)
    for n in notas:
        track.append(Message('note_on', note=n, velocity=80, time=0))
    # Desliga as notas com duração definida
    for i, n in enumerate(notas):
        time = DURACAO_NOTA if i == 0 else 0  # só 1.º tem tempo
        track.append(Message('note_off', note=n, velocity=64, time=time))

    # Pausa entre notas/acordes
    if PAUSA > 0:
        # Pausa = evento 'espera' sem tocar nada
        track.append(Message('note_on', note=0, velocity=0, time=PAUSA))

def converter_txt_para_midi(ficheiro_txt: Path):
    if not ficheiro_txt.exists():
        print(f"❌  Ficheiro não encontrado: {ficheiro_txt}")
        sys.exit(1)

    texto = ficheiro_txt.read_text(encoding='utf-8').upper()
    base_name = ficheiro_txt.stem
    ficheiro_midi = ficheiro_txt.with_suffix('.mid')

    mid = MidiFile(ticks_per_beat=TICKS_PER_BEAT)
    track = MidiTrack()
    mid.tracks.append(track)

    # Meta‑evento de tempo
    track.append(Message('program_change', program=0, time=0))
    """mid.tracks[0].append(
        Message('meta', type='set_tempo',
                tempo=bpm2tempo(BPM), time=0)
    )
    """
    for ch in texto:
        if ch in ACORDES:
            toca_notas(track, ACORDES[ch], DURACAO_NOTA)
        elif ch in NOTAS:
            toca_notas(track, [NOTAS[ch]], DURACAO_NOTA)
        else:
            # ignora tudo excepto 0‑9, A‑H e '\n'
            continue

    mid.save(ficheiro_midi)
    print(f"✅  MIDI criado: {ficheiro_midi.resolve()}")
print("\033c\033[43;30m\n")
# ---------- Programa principal ----------
if __name__ == "__main__":
    try:
        nome = input("Nome do ficheiro de texto a converter: ").strip('"').strip()
        if not nome:
            raise ValueError("O nome do ficheiro não pode estar vazio.")
        converter_txt_para_midi(Path(nome))
    except KeyboardInterrupt:
        print("\nCancelado pelo utilizador.")

