"""
Tarea 1 (Elizabeth): dataset curado -> ventanas listas para Joseph.

Entrada : zips Empatica en CARPETA + intervalos_ictales.csv (inicio y fin de cada evento,
          definidos sobre las gráficas; ya no se usa 1110.txt ni el supuesto de 60 s).
Salida  : ventanas/ventanas.npz   (acc, eda, bvp, y)
          ventanas/meta.csv       (una fila por ventana)
          ventanas/tabla_dataset.csv (tabla descriptiva)

Frecuencias nativas del E4 (estándar del proyecto): ACC 32 Hz, EDA 4 Hz, BVP 64 Hz.
Filtros (según el diagrama de flujo): ACC 0.5-15 Hz, EDA pasabajos 1 Hz, PPG 0.5-8 Hz.
Etiquetas: 1 = ictal, 0 = interictal (submuestreadas, ver SUBMUESTREO_INTERICTAL). Se descartan ventanas en márgenes pre/post ictales,
en eventos "probable" y "dudosa" (si INCLUIR_PROBABLE es False) y en zonas "excluir".
"""
import time
import zipfile
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.signal import butter, sosfiltfilt

# ---------------- parámetros ----------------
CARPETA = Path("raw/mayo/Empatica_Chronic")

if not Path("intervalos_ictales.csv").exists():
    raise SystemExit("No encuentro intervalos_ictales.csv en " + str(Path.cwd()) +
                     ". Copia el archivo a esta carpeta y vuelve a ejecutar.")
INTERVALOS = Path("intervalos_ictales.csv")
SALIDA = Path("ventanas")
SALIDA.mkdir(exist_ok=True)

FS = {"acc": 32, "eda": 4, "bvp": 64}
VENT = 10            # s por ventana
PASO = 5             # s entre ventanas (50 % de solapamiento)
MARGEN_PRE = 120     # s antes del inicio ictal que se descartan
MARGEN_POST = 120    # s después del fin ictal que se descartan (recuperación)
INCLUIR_PROBABLE = False   # True: los eventos "probable" se etiquetan como ictales
SUBMUESTREO_INTERICTAL = 12   # se guarda 1 de cada N ventanas interictales (12 = 1 por minuto). 1 = todas.
                              # Las ventanas ictales se guardan siempre todas.

iv = pd.read_csv(INTERVALOS, encoding="utf-8-sig")
ictal = iv[(iv.tipo == "ictal") | ((iv.tipo == "probable") & INCLUIR_PROBABLE)]
excluidas = iv[~iv.index.isin(ictal.index)]   # dudosa, probable y excluir


# ---------------- utilidades ----------------
def leer_csv(zf, nombre):
    with zf.open(nombre) as fh:
        t0 = float(fh.readline().decode().split(",")[0])
        fs = float(fh.readline().decode().split(",")[0])
        df = pd.read_csv(fh, header=None)
    return t0, fs, df.to_numpy(dtype=float)


def filtrar(x, fs, tipo, f):
    sos = butter(4, f, btype=tipo, fs=fs, output="sos")
    if len(x) <= 50:
        return x
    return sosfiltfilt(sos, x, axis=0)


def etiquetar(ini, fin):
    """Vectorizado. y: 1 ictal, 0 interictal, -1 descartar. Devuelve y, id_evento, usar_acc, usar_eda."""
    centro = (ini + fin) / 2
    n = len(ini)
    y = np.zeros(n, dtype=int)
    eid = np.full(n, "", dtype=object)
    ua = np.full(n, "Sí", dtype=object)
    ue = np.full(n, "Sí", dtype=object)
    for r in ictal.itertuples():            # márgenes pre/post
        y[((r.inicio_utc - MARGEN_PRE <= centro) & (centro < r.inicio_utc)) |
          ((r.fin_utc < centro) & (centro <= r.fin_utc + MARGEN_POST))] = -1
    for r in excluidas.itertuples():        # zonas dudosa / probable / excluir
        y[(r.inicio_utc <= fin) & (ini <= r.fin_utc)] = -1
    for r in ictal.itertuples():            # ictal manda sobre lo anterior
        m = (r.inicio_utc <= centro) & (centro <= r.fin_utc)
        y[m] = 1
        eid[m], ua[m], ue[m] = r.id_evento, r.usar_acc, r.usar_eda
    return y, eid, ua, ue


# ---------------- procesamiento ----------------
T0 = time.time()
acc_w, eda_w, bvp_w, meta = [], [], [], []
resumen_sesiones = []

for z in sorted(CARPETA.glob("*.zip")):
    try:
        zf = zipfile.ZipFile(z)
    except zipfile.BadZipFile:
        continue
    with zf:
        nombres = {n.split("/")[-1].upper(): n for n in zf.namelist()}
        if not {"BVP.CSV", "ACC.CSV", "EDA.CSV"} <= nombres.keys():
            continue
        tb, fb, bvp = leer_csv(zf, nombres["BVP.CSV"])
        ta, fa, acc = leer_csv(zf, nombres["ACC.CSV"])
        te, fe, eda = leer_csv(zf, nombres["EDA.CSV"])

    assert (fa, fe, fb) == (FS["acc"], FS["eda"], FS["bvp"]), f"frecuencias distintas en {z.name}"

    acc = filtrar(acc[:, :3] / 64.0, fa, "bandpass", [0.5, 15])   # a g
    eda_raw = eda[:, 0]
    eda_f = filtrar(eda_raw, fe, "lowpass", 1.0)
    bvp = filtrar(bvp[:, 0], fb, "bandpass", [0.5, 8])

    ini = max(ta, te, tb)
    fin = min(ta + len(acc) / fa, te + len(eda_f) / fe, tb + len(bvp) / fb)
    n = int((fin - ini - VENT) // PASO) + 1
    if n <= 0:
        continue

    cont = {0: 0, 1: 0}
    ks = np.arange(n)
    t_ini_all = ini + ks * PASO
    Y, EID, UA, UE = etiquetar(t_ini_all, t_ini_all + VENT)
    mantener = (Y == 1) | ((Y == 0) & (ks % SUBMUESTREO_INTERICTAL == 0))
    for k in ks[mantener]:
        t_ini = t_ini_all[k]

        def cortar(sig, t0, fs):
            a = int(round((t_ini - t0) * fs))
            return sig[a:a + int(VENT * fs)]

        wa, we, wb = cortar(acc, ta, fa), cortar(eda_f, te, fe), cortar(bvp, tb, fb)
        if len(wa) < VENT * fa or len(we) < VENT * fe or len(wb) < VENT * fb:
            continue
        we_raw = cortar(eda_raw, te, fe)

        acc_w.append(wa.astype(np.float32))
        eda_w.append(we.astype(np.float32))
        bvp_w.append(wb.astype(np.float32))
        meta.append({
            "sesion": z.stem,
            "t_ini_utc": t_ini,
            "y": int(Y[k]),
            "id_evento": EID[k],
            "usar_acc": UA[k],
            "usar_eda": UE[k],
            "eda_cero_frac": float((we_raw < 0.05).mean()),  # posible pérdida de contacto
        })
        cont[int(Y[k])] += 1
    print(f"{z.name}: {cont[0]} interictales, {cont[1]} ictales ({time.time() - T0:.0f} s)", flush=True)

    resumen_sesiones.append({
        "sesion": z.stem,
        "duracion_h": round((fin - ini) / 3600, 2),
        "ventanas_0": cont[0],
        "ventanas_1": cont[1],
    })

meta = pd.DataFrame(meta)
np.savez_compressed(
    SALIDA / "ventanas.npz",
    acc=np.stack(acc_w), eda=np.stack(eda_w), bvp=np.stack(bvp_w),
    y=meta["y"].to_numpy(),
)
meta.to_csv(SALIDA / "meta.csv", index=False)
pd.DataFrame(resumen_sesiones).to_csv(SALIDA / "tabla_dataset.csv", index=False)

print(f"Ventanas totales: {len(meta)}")
print(meta["y"].value_counts().rename({0: "interictal", 1: "ictal"}).to_string())
print("Ventanas ictales por evento:")
print(meta[meta.y == 1].groupby("id_evento").size().to_string())
print(f"Ventanas con EDA >20 % en cero: {(meta.eda_cero_frac > 0.2).sum()}")
