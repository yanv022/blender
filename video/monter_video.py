# Montage de la video avec voix off : accroche sur l'image d'ensemble, puis la capture
# d'ecran recadree sur la camera, chaque etape ralentie ou acceleree pour durer
# exactement le temps de sa phrase. Lancer : python monter_video.py
# Les phrases sont dans voix/segNN.mp3 (texte : voix-off-texte.md).

import os, subprocess, sys

ICI = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ICI, "Aufzeichnung 2026-11-20 115432.mp4")
IMG_ACCROCHE = os.path.join(ICI, "..", "rendu-realiste-ensemble.png")
VOIX = os.path.join(ICI, "voix")
TMP = os.path.join(ICI, "montage-tmp")
SORTIE = os.path.join(ICI, "bauxite-alumine-voix-off.mp4")
POLICE = "C\\:/Windows/Fonts/segoeuib.ttf"

W, H, FPS = 1280, 720, 30
CROP = "crop=788:442:395:221"          # cadre de la camera dans la capture 1576x884
AVANT, APRES = 0.25, 0.40              # silence avant / apres chaque phrase (s)
VIT_MIN, VIT_MAX = 0.70, 2.00          # ralenti / accelere au plus ; au-dela : arret sur image ou silence
FIN_ARRET = 2.0                        # arret sur l'alumine apres la derniere phrase
CURSEUR = "x=341:y=352:w=20:h=27"      # pointeur de souris dans l'image recadree
CURSEUR_DEPUIS = 63.4                  # il y reste immobile a partir de cet instant (s)

# (numero, debut, fin) dans la capture, en secondes : changements de legende mesures
ETAPES = [
    (1, 0.45, 14.40),    # entree : bauxite + billes dans le fut
    (2, 14.40, 22.03),   # broyage
    (3, 22.03, 31.07),   # vidange au palan
    (4, 31.07, 47.40),   # chargement de R1
    (5, 47.40, 53.97),   # attaque
    (6, 53.97, 57.40),   # decantation
    (7, 57.40, 67.80),   # filtration boues rouges
    (8, 67.80, 72.53),   # transfert
    (9, 72.53, 82.33),   # precipitation
    (10, 82.33, 86.77),  # filtration hydrate
    (11, 86.77, 90.63),  # amorce + creusets
    (12, 90.63, 93.00),  # four
    (13, 93.00, 97.10),  # calcination
    (14, 97.10, 99.43),  # refroidissement
    (15, 99.43, 103.60), # alumine (la capture reboucle a 103,7 s)
]

ENC_V = ["-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p", "-r", str(FPS)]
ENC_A = ["-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2"]


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.returncode:
        print(r.stderr[-3000:])
        sys.exit("ffmpeg a echoue")


def duree(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
                          "-of", "csv=p=0", f], capture_output=True, text=True).stdout
    return float(out.strip())


def voix(n):
    f = os.path.join(VOIX, f"seg{n:02d}.mp3")
    if not os.path.exists(f):
        sys.exit(f"phrase manquante : {f}")
    return f


def audio_filtre(T):
    ms = int(AVANT * 1000)
    return f"[1:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms},apad,atrim=0:{T:.3f}[a]"


def texte(nom, contenu):
    f = os.path.join(TMP, nom)
    with open(f, "w", encoding="utf-8") as fh:
        fh.write(contenu)
    return f.replace("\\", "/").replace(":", "\\:")


def accroche():
    v = voix(0)
    T = 0.6 + v_dur(v) + 0.5
    N = round(T * FPS)
    t1 = texte("titre1.txt", "De la bauxite à l'aluminium")
    t2 = texte("titre2.txt", "Cameroun  ·  Guinée")
    vf = (f"[0:v]scale=3840:-1,zoompan=z='1+0.12*on/{N}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)'"
          f":d={N}:s={W}x{H}:fps={FPS},"
          f"drawtext=fontfile='{POLICE}':textfile='{t1}':fontsize=54:fontcolor=white:"
          f"box=1:boxcolor=black@0.55:boxborderw=18:x=(w-tw)/2:y=h-170:"
          f"alpha='min(1,max(0,(t-0.4)/0.6))',"
          f"drawtext=fontfile='{POLICE}':textfile='{t2}':fontsize=32:fontcolor=0xFFC34D:"
          f"box=1:boxcolor=black@0.55:boxborderw=12:x=(w-tw)/2:y=h-82:"
          f"alpha='min(1,max(0,(t-3.2)/0.6))',"
          f"fade=t=in:st=0:d=0.5,fade=t=out:st={T-0.35:.3f}:d=0.35,format=yuv420p[v]")
    ms = 600
    af = f"[1:a]aresample=48000,aformat=channel_layouts=stereo,adelay={ms}|{ms},apad,atrim=0:{T:.3f}[a]"
    out = os.path.join(TMP, "c00.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-i", IMG_ACCROCHE, "-i", v,
         "-filter_complex", vf + ";" + af, "-map", "[v]", "-map", "[a]", "-t", f"{T:.3f}",
         *ENC_V, *ENC_A, out])
    return out, T


def v_dur(f):
    return duree(f)


def etape(n, a, b, derniere=False):
    v = voix(n)
    L = b - a
    T = AVANT + v_dur(v) + APRES + (FIN_ARRET if derniere else 0)
    vit = max(VIT_MIN, min(VIT_MAX, L / T))
    d_video = L / vit
    T = max(T, d_video)                 # trop long meme accelere : la voix finit, l'image continue
    arret = max(0.0, T - d_video)       # trop court meme ralenti : arret sur la derniere image
    vf = f"[0:v]{CROP}"
    if b > CURSEUR_DEPUIS:              # pointeur de souris immobile dans l'image : on l'efface
        vf += f",delogo={CURSEUR}:enable='gte(t,{max(0.0, CURSEUR_DEPUIS - a):.2f})'"
    vf += f",scale={W}:{H}:flags=lanczos,setpts=(PTS-STARTPTS)/{vit:.4f},fps={FPS}"
    if arret > 0:
        vf += f",tpad=stop_mode=clone:stop_duration={arret:.3f}"
    if n == 1:
        vf += ",fade=t=in:st=0:d=0.3"
    if derniere:
        vf += f",fade=t=out:st={T-1.0:.3f}:d=1.0"
    vf += ",format=yuv420p[v]"
    af = audio_filtre(T)
    if derniere:
        af = af[:-3] + f",afade=t=out:st={T-1.0:.3f}:d=1.0[a]"
    out = os.path.join(TMP, f"c{n:02d}.mp4")
    run(["ffmpeg", "-y", "-v", "error", "-ss", f"{a:.3f}", "-t", f"{L:.3f}", "-i", SRC, "-i", v,
         "-filter_complex", vf + ";" + af, "-map", "[v]", "-map", "[a]", "-t", f"{T:.3f}",
         *ENC_V, *ENC_A, out])
    print(f"etape {n:2d} : capture {L:5.2f} s -> {T:5.2f} s  (vitesse x{vit:.2f}"
          + (f", arret {arret:.1f} s" if arret > 0.05 else "") + ")")
    return out, T


def main():
    os.makedirs(TMP, exist_ok=True)
    clips = []
    c, T = accroche()
    clips.append(c)
    print(f"accroche : {T:5.2f} s")
    total = T
    for i, (n, a, b) in enumerate(ETAPES):
        c, T = etape(n, a, b, derniere=(i == len(ETAPES) - 1))
        clips.append(c)
        total += T
    liste = os.path.join(TMP, "liste.txt")
    with open(liste, "w", encoding="utf-8") as fh:
        for c in clips:
            fh.write(f"file '{c}'\n")
    # assemblage + volume de la voix normalise (-16 LUFS, niveau habituel des reseaux sociaux)
    run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0", "-i", liste,
         "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", *ENC_A,
         "-movflags", "+faststart", SORTIE])
    print(f"VIDEO_OK {SORTIE}  ({duree(SORTIE):.1f} s, prevu {total:.1f} s)")


if __name__ == "__main__":
    main()
