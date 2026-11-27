"""
Recorta cada crisis ictal con contexto continuo a partir de los zips originales del E4.

Entrada : zips Empatica en CARPETA (cada zip trae ACC.csv, EDA.csv, BVP.csv) e
          intervalos_ictales.csv (columnas: inicio_utc, fin_utc, tipo, id_evento, usar_acc, usar_eda).
Salida  : recortes/<id_evento>.npz  (señales CRUDAS, sin filtrar, con su hora UTC de inicio)
          recortes/indice.csv       (una fila por crisis: cobertura de pre, ictal y post)

Ventana estandar: PRE = 180 s antes del inicio y POST = 900 s despues del fin (-3/+15 min).
Ventana extendida (solo para revision): --extendida usa -600/+1800 s (-10/+30 min).

Uso (desde la carpeta que contiene raw\\ e intervalos_ictales.csv):
    python recortar_crisis.py
    python recortar_crisis.py --extendida
    python recortar_crisis.py --carpeta "raw/mayo/Empatica_Chronic" --salida recortes

Solo lee los zips; no modifica nada. Si falta tramo, guarda lo que hay y lo marca en indice.csv.
"""
import argparse
import zipfile
from pathlib import Path

import numpy as np
import pandas as pd

FS_ESPERADA = {"acc": 32, "eda": 4, "bvp": 64}
ARCHIVOS = {"acc": "ACC.CSV", "eda": "EDA.CSV", "bvp": "BVP.CSV"}


def leer_csv(zf, nombre):
    """Formato E4: fila 1 = hora de inicio (UTC, s); fila 2 = frecuencia; luego los datos."""
    with zf.open(nombre) as fh:
        t0 = float(fh.readline().decode().split(",")[0])
        fs = float(fh.readline().decode().split(",")[0])
        datos = pd.read_csv(fh, header=None).to_numpy(dtype=float)
    return t0, fs, datos


def indexar_sesiones(carpeta):
    """Lee solo la primera linea de BVP.csv de cada zip: hora de inicio de la sesion."""
    sesiones = []
    for z in sorted(carpeta.glob("*.zip")):
        try:
            with zipfile.ZipFile(z) as zf:
                nombres = {n.split("/")[-1].upper(): n for n in zf.namelist()}
                if not set(ARCHIVOS.values()) <= nombres.keys():
                    continue
                with zf.open(nombres["BVP.CSV"]) as fh:
                    t0 = float(fh.readline().decode().split(",")[0])
        except (zipfile.BadZipFile, ValueError):
            continue
        sesiones.append((t0, z))
    return sorted(sesiones)


def cargar_sesion(z):
    with zipfile.ZipFile(z) as zf:
        nombres = {n.split("/")[-1].upper(): n for n in zf.namelist()}
        return {k: leer_csv(zf, nombres[v]) for k, v in ARCHIVOS.items()}


def recortar(senal, t_desde, t_hasta):
    """Devuelve (datos, t_inicio_real) para el tramo pedido, o (vacio, nan) si no hay nada."""
    t0, fs, datos = senal
    i0 = max(0, int(np.ceil((t_desde - t0) * fs)))
    i1 = min(len(datos), int(np.floor((t_hasta - t0) * fs)))
    if i1 <= i0:
        return datos[:0], float("nan")
    return datos[i0:i1], t0 + i0 / fs


def cobertura(senal, t_desde, t_hasta):
    """Porcentaje del tramo [t_desde, t_hasta] que tiene datos."""
    t0, fs, datos = senal
    fin = t0 + len(datos) / fs
    solape = max(0.0, min(fin, t_hasta) - max(t0, t_desde))
    return 100.0 * solape / (t_hasta - t_desde) if t_hasta > t_desde else 0.0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--carpeta", default="raw/mayo/Empatica_Chronic")
    ap.add_argument("--intervalos", default="intervalos_ictales.csv")
    ap.add_argument("--salida", default="recortes")
    ap.add_argument("--extendida", action="store_true", help="usar -10/+30 min en lugar de -3/+15 min")
    a = ap.parse_args()

    pre, post = (600, 1800) if a.extendida else (180, 900)
    carpeta, salida = Path(a.carpeta), Path(a.salida)
    if not carpeta.exists():
        raise SystemExit(f"No encuentro la carpeta {carpeta}. Usa --carpeta con la ruta correcta.")
    if not Path(a.intervalos).exists():
        raise SystemExit(f"No encuentro {a.intervalos} en {Path.cwd()}.")
    salida.mkdir(exist_ok=True)

    iv = pd.read_csv(a.intervalos, encoding="utf-8-sig")
    ictales = iv[iv.tipo == "ictal"]
    sesiones = indexar_sesiones(carpeta)
    print(f"{len(ictales)} eventos ictales; {len(sesiones)} sesiones con ACC, EDA y BVP.")

    filas, cache = [], {}
    for r in ictales.itertuples():
        t_ini, t_fin = float(r.inicio_utc), float(r.fin_utc)
        previas = [(t0, z) for t0, z in sesiones if t0 <= t_fin]
        if not previas:
            print(f"  {r.id_evento}: sin sesion que cubra el evento")
            filas.append({"id_evento": r.id_evento, "sesion": "", "estado": "sin_sesion"})
            continue
        t0s, z = previas[-1]           # las sesiones del E4 no se solapan: la ultima que empezo antes
        if z not in cache:
            cache.clear()              # solo se guarda la sesion actual para no llenar la memoria
            cache[z] = cargar_sesion(z)
        sen = cache[z]
        for k, (_, fs, _) in sen.items():
            if fs != FS_ESPERADA[k]:
                raise SystemExit(f"Frecuencia inesperada en {z.name} ({k}: {fs} Hz)")

        d, h = t_ini - pre, t_fin + post
        out, inicios = {}, {}
        for k in ("acc", "eda", "bvp"):
            out[k], inicios[k] = recortar(sen[k], d, h)
        cob = {k: (cobertura(sen[k], d, t_ini), cobertura(sen[k], t_ini, t_fin), cobertura(sen[k], t_fin, h))
               for k in sen}
        # EDA y BVP: si no hay datos en el tramo, el archivo conserva el arreglo vacio
        np.savez_compressed(
            salida / f"{r.id_evento}.npz",
            acc=out["acc"].astype(np.int16), eda=out["eda"][:, 0].astype(np.float32),
            bvp=out["bvp"][:, 0].astype(np.float32),
            t_inicio_acc=inicios["acc"], t_inicio_eda=inicios["eda"], t_inicio_bvp=inicios["bvp"],
            fs_acc=32, fs_eda=4, fs_bvp=64,
            inicio_utc=t_ini, fin_utc=t_fin, ventana_desde_utc=d, ventana_hasta_utc=h,
            pre_s=pre, post_s=post, sesion=z.stem,
        )
        fila = {"id_evento": r.id_evento, "sesion": z.stem, "inicio_utc": t_ini, "fin_utc": t_fin,
                "duracion_ictal_s": round(t_fin - t_ini, 1), "pre_s": pre, "post_s": post,
                "usar_acc": getattr(r, "usar_acc", ""), "usar_eda": getattr(r, "usar_eda", "")}
        for k in ("acc", "eda", "bvp"):
            fila[f"{k}_pre_%"], fila[f"{k}_ictal_%"], fila[f"{k}_post_%"] = (round(c, 1) for c in cob[k])
        completo = all(c >= 99.0 for v in cob.values() for c in v)
        vacio = all(c == 0 for v in cob.values() for c in v)
        fila["estado"] = "sin_datos" if vacio else ("completo" if completo else "parcial")
        filas.append(fila)
        print(f"  {r.id_evento}: {fila['estado']}  (pre {cob['acc'][0]:.0f}% | ictal {cob['acc'][1]:.0f}% | post {cob['acc'][2]:.0f}%)")

    pd.DataFrame(filas).to_csv(salida / "indice.csv", index=False)
    print(f"Listo: {sum(f.get('estado') == 'completo' for f in filas)} completos, "
          f"{sum(f.get('estado') == 'parcial' for f in filas)} parciales, "
          f"{sum(f.get('estado') == 'sin_datos' for f in filas)} sin datos, "
          f"{sum(f.get('estado') == 'sin_sesion' for f in filas)} sin sesion. Ver {salida / 'indice.csv'}")


if __name__ == "__main__":
    main()
