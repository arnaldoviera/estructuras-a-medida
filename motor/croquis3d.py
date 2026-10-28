"""Croquis 3D: escena (cilindros, cajas, sogas) en JSON para el visor Three.js de la propuesta.
Siempre ARMADO: no existe vista desarmada."""


def escena(ficha, M):
    piezas = [{"n": p["nombre"], "a": [round(v) for v in p["a"]], "b": [round(v) for v in p["b"]], "r": round(p["r"], 1), "m": p["mat"]}
              for p in M["piezas"]]
    legs = [v[0] for v in M["legs"].values()]
    esp = ficha["requisitos"]["espacio"]
    return {
        "piezas": piezas,
        "configs": {k: [{kk: ([round(x) for x in vv] if isinstance(vv, list) and vv and isinstance(vv[0], (int, float)) else vv)
                         for kk, vv in c.items()} for c in lst] for k, lst in M["configs"].items()},
        "pozos": [[round(f[0]), round(f[1])] for f in legs],
        "area": [esp["largo_eje_travesano_m"] * 1000, esp["largo_vaiven_m"] * 1000],
    }
