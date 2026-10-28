export const FILM = {
  fig: "Fig 1",
  title: "Pórtico de hamacas",
  radius: 2300,
  label: "Pórtico de hamacas en rollizos de madera, armado.",
  bounds: [
    [-2050, 2050],
    [-1250, 1250],
    [-1120, 1250],
  ],
};

export const FIGURE = {
  title: "Pórtico de hamacas · croquis armado",
  start: { yaw: -30, pitch: 16 },
  label: "Pórtico de hamacas en rollizos: travesaño Ø20 cm × 3,70 m con el eje a 2,10 m, apoyado en la horqueta de dos A de patas Ø17 cm (33° lateral, 14° frontal), tirantes a 1,10 m, cartelas y abrazaderas de cuelgue. {parts} piezas.",
  keys: [
    { mark: "raised", label: "Rollizos: travesaño Ø20, patas Ø17, tirantes Ø15, cartelas Ø12" },
    { mark: "lit", label: "Varilla roscada 16 mm y 6 abrazaderas de cuelgue (sin perforar el travesaño)" },
    { mark: "edge", label: "Accesorios intercambiables en 3 puestos estándar" },
  ],
  caption: "Croquis armado. Eje del travesaño a 2,10 m; patas cruzadas a 1,76 m; base 2,30 m por A; pies a 4,30 m por fuera; asientos a 0,50 m.",
};

export const FEATURE_DEFAULTS = {};
export const FEATURE_KEYS = [];
export function featureValues(s, values) {
  return { ...values };
}
export function featureTravel() {
  return 0;
}
