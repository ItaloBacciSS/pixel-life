import { $ } from "./dom.js";

// [hora em que começa, céu da janela, período do dia para as falas]
const STAGES = [
  [0, "madrugada", "madrugada"],
  [5, "amanhecer", "manha"],
  [7, "dia", "manha"],
  [12, "dia", "tarde"],
  [17, "entardecer", "tarde"],
  [18, "entardecer", "noite"],
  [19, "noite", "noite"],
];
const WEATHER = { feliz: "sol", normal: "nuvens", triste: "chuva" };

// `?hora=22` e `?clima=chuva` na URL deixam ver como o quarto fica em outros momentos.
const preview = new URLSearchParams(location.search);

export function momento(date = new Date()) {
  const hour = Number(preview.get("hora") ?? date.getHours());
  const [, sky, period] = STAGES.filter(([start]) => start <= hour).pop() ?? STAGES[0];
  return { sky, period };
}

// Pinta a janela e a luz do quarto com a hora do jogador e o humor (sol, nuvens ou chuva).
export function paint(humor) {
  const now = momento();
  const scene = $("cena");
  scene.dataset.ceu = now.sky;
  scene.dataset.clima = preview.get("clima") ?? WEATHER[humor];
  return now;
}
