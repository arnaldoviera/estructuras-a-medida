// Pórtico de hamacas en rollizos — croquis 3D (medidas en mm).
// x: a lo largo del travesaño (muro -> césped), y: dirección del vaivén, z: arriba.
import * as G from "../kit/lathe.mjs";
const unit = G.unit3;
const add = G.add3;
const mul = G.mul3;
const sub = G.sub3;
const dot = G.dot3;
const cross = G.cross3;
export const frame = (o, a, u) => {
  const A = unit(a);
  const U = unit(sub(u, mul(A, dot(u, A))));
  return { o, a: A, u: U, v: cross(A, U) };
};
const CONFIG = (typeof process !== "undefined" && process.env && process.env.CONFIG) || "hamacas";

// Medidas de la ficha (v3: centro del travesaño a 2,10 m)
export const D = {
  beamR: 100, beamZ: 2100, beamHalf: 1850, // travesaño Ø200 × 3,70 m; centro a 2,10 m
  legR: 85, footX: 2065, crossX: 1635, foot: 1150, ext: 560, // patas Ø170
  tieZ: 1100, tieR: 75, braceR: 60, braceTopX: 1350,
  rodR: 8, ropeR: 7, seatZ: 500, pivotZ: 1940,
};
export const SLOTS = [-940, 0, 940];
export const HANGERS = SLOTS.flatMap((c) => [c - 250, c + 250]);

export function buildObject(T, { layer }) {
  const parts = {};
  const groups = {};
  const explode = [];
  const anchors = {};
  const root = T.group("root", { free: { origin: [0, 0, 0] } });
  groups.root = root;
  const core = T.group("core", { parent: root, slide: { direction: [0, 0, 1], travel: 0 } });
  groups.core = core;
  explode.push({ name: "core", travel: 0, delay: 0 });
  const part = (p) => (parts[p.name] = p);
  // cilindro entre dos puntos
  const Z0 = -1120;
  const log = (name, a0, b0, r, material = "coffee") => {
    const a = [a0[0], a0[1], a0[2] + Z0];
    const b = [b0[0], b0[1], b0[2] + Z0];
    const dir = sub(b, a);
    const len = Math.hypot(...dir);
    const ax = unit(dir);
    const ref = Math.abs(ax[2]) > 0.9 ? [1, 0, 0] : [0, 0, 1];
    return part(T.round({ name, group: core, layer, F: frame(a, ax, ref), s0: 0, s1: len, r, tone: "hi", crease: "lo", material }));
  };
  const boxP = (name, [x0, x1], [y0, y1], [z0, z1], material) =>
    part(
      T.prism({
        name,
        group: core,
        layer,
        F: frame([0, 0, 0], [0, 0, 1], [1, 0, 0]),
        polygon: [
          [x0, y0],
          [x1, y0],
          [x1, y1],
          [x0, y1],
        ],
        s0: z0 + Z0,
        s1: z1 + Z0,
        steps: 5,
        tone: "hi",
        crease: "lo",
        bevel: 2,
        material,
      }),
    );

  const { beamR, beamZ, beamHalf, legR, footX, crossX, foot, ext, tieZ, tieR, braceR, braceTopX, rodR, ropeR, seatZ, pivotZ } = D;
  let cz = 1760;
  for (let k = 0; k < 40; k++) cz = beamZ - (beamR + legR) / Math.sin(Math.atan(foot / cz));
  D.cross = cz;
  const lean = (footX - crossX) / cz; // inclinación en vista frontal
  const axisX = (z) => footX - lean * z;
  const lap = 30; // media madera: patas desfasadas ±30 mm en el cruce

  log("travesano", [-beamHalf, 0, beamZ], [beamHalf, 0, beamZ], beamR);

  for (const [i, sx] of [-1, 1].entries()) {
    const side = i ? "cesped" : "muro";
    for (const s of [-1, 1]) {
      const off = s * lap;
      const footP = [sx * footX + off, s * foot, 0];
      const crossP = [sx * crossX + off, 0, cz];
      const end = add(crossP, mul(unit(sub(crossP, footP)), ext));
      log(`pata.${side}.${s > 0 ? "frente" : "atras"}`, footP, end, legR);
    }
    // Varilla del cruce (a lo largo de x, atraviesa las dos patas)
    log(`varilla.cruce.${side}`, [sx * crossX - 150, 0, cz], [sx * crossX + 150, 0, cz], rodR, "steel");
    // Varilla de la horqueta: pata – travesaño – pata (a lo largo de y, a la altura del eje del travesaño)
    const yTop = foot * (beamZ / cz - 1);
    const xTop = sx * axisX(beamZ);
    log(`varilla.cabeza.${side}`, [xTop, -(yTop + 130), beamZ], [xTop, yTop + 130, beamZ], rodR, "steel");
    for (const s of [-1, 1]) log(`tuerca.cabeza.${side}.${s}`, [xTop, s * (yTop + 130), beamZ], [xTop, s * (yTop + 150), beamZ], 16, "gunmetal");
    // Tirante: sobre la cara interior de las patas
    const yT = foot * (1 - tieZ / cz);
    const tx = sx * (axisX(tieZ) - legR - tieR + 50);
    log(`tirante.${side}`, [tx, -(yT + 130), tieZ], [tx, yT + 130, tieZ], tieR);
    for (const s of [-1, 1]) log(`varilla.tirante.${side}.${s}`, [tx - sx * 110, s * yT, tieZ], [sx * (axisX(tieZ) + legR + 25), s * yT, tieZ], rodR, "steel");
    // Cartela: apoya arriba del tirante y abajo del travesaño, varillas verticales
    log(`cartela.${side}`, [tx, 0, tieZ + tieR - 15], [sx * braceTopX, 0, beamZ - beamR + 15], braceR);
    log(`varilla.cartela.inf.${side}`, [tx, 0, tieZ - tieR - 25], [tx, 0, tieZ + tieR + 110], 6, "steel");
    log(`varilla.cartela.sup.${side}`, [sx * braceTopX, 0, beamZ - beamR - 110], [sx * braceTopX, 0, beamZ + beamR + 25], 6, "steel");
  }

  // Abrazaderas de cuelgue (rodean el travesaño, sin agujerearlo)
  for (const [j, hx] of HANGERS.entries()) {
    log(`abrazadera.${j}`, [hx - 20, 0, beamZ], [hx + 20, 0, beamZ], beamR + 7, "steel");
    boxP(`abrazadera.orejas.${j}`, [hx - 20, hx + 20], [-22, 22], [beamZ - beamR - 45, beamZ - beamR + 10], "steel");
    log(`abrazadera.grillete.${j}`, [hx, 0, beamZ - beamR - 45], [hx, 0, pivotZ], 12, "gunmetal");
  }
  const hookZ = pivotZ;

  const swing = (name, c) => {
    boxP(`${name}.asiento`, [c - 215, c + 215], [-90, 90], [seatZ - 30, seatZ], "bean");
    for (const s of [-1, 1]) log(`${name}.soga.${s}`, [c + s * 235, 0, seatZ], [c + s * 250, 0, hookZ], ropeR, "porcelain");
  };
  const trapeze = (name, c) => {
    const barZ = 1300;
    log(`${name}.barra`, [c - 230, 0, barZ], [c + 230, 0, barZ], 16, "steel");
    for (const s of [-1, 1]) log(`${name}.soga.${s}`, [c + s * 240, 0, barZ + 16], [c + s * 250, 0, hookZ], ropeR, "porcelain");
  };

  if (CONFIG === "cama") {
    const bz = 450;
    boxP("cama.base", [-1000, 1000], [-700, 700], [bz - 60, bz], "bean");
    boxP("cama.colchon", [-975, 975], [-675, 675], [bz + 2, bz + 120], "knit");
    for (const sx of [-1, 1]) for (const sy of [-1, 1]) log(`cama.soga.${sx}.${sy}`, [sx * 990, sy * 690, bz + 2], [sx * 1190, 0, hookZ], ropeR, "porcelain");
  } else {
    swing("hamaca1", SLOTS[0]);
    trapeze("trapecio", SLOTS[1]);
    swing("hamaca2", SLOTS[2]);
  }

  anchors.body = [0, 0, 0];
  return { parts, groups, explode, root, anchors, features: [], counts: {} };
}
export function explodeValues(explode) {
  const out = {};
  for (const { name } of explode) out[name] = 0;
  return out;
}
