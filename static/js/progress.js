import * as api from "./api.js";
import { $, attempt, el, meter } from "./dom.js";
import { stepChart } from "./chart.js";
import { dayLabel, signed } from "./format.js";

let data;

const stat = (value, label, note = "") => el("div", { className: "stat" }, el("strong", {}, String(value)), label, note && el("small", {}, ` ${note}`));

function renderWeek({ semana: week }) {
  $("semana-datas").textContent = `${dayLabel(week.inicio)} a ${dayLabel(week.fim)}`;
  const diff = week.acoes - week.acoes_anterior;
  $("semana").replaceChildren(
    stat(week.acoes, "ações", `(${signed(diff)} vs. semana passada)`),
    stat(week.tropecos, "tropeços"),
    stat(week.metas.total ? `${week.metas.cumpridas}/${week.metas.total}` : "—", "metas cumpridas"),
    stat(week.sequencia, "dias sem tropeçar"));

  const biggest = Math.max(...week.xp.map((a) => Math.abs(a.xp)), 1);
  $("semana-detalhes").replaceChildren(
    ...(week.xp.length ? [] : [el("p", { className: "sub" }, "Nada registrado nesta semana ainda.")]),
    ...(week.melhor_dia ? [el("p", {}, `Melhor dia: ${dayLabel(week.melhor_dia.dia, { weekday: "long" })} (${week.melhor_dia.acoes} ações)`)] : []),
    ...(week.subiu.length ? [el("h4", {}, "Subiu de nível"),
      el("ul", { className: "subiu-lista" }, ...week.subiu.map((a) => el("li", {}, `${a.nome}: ${a.de} → ${a.para}`)))] : []),
    ...(week.xp.length ? [el("h4", {}, "XP da semana"), ...week.xp.map((a) => el("div", { className: "xp-linha" },
      el("span", {}, `${a.icone} ${a.nome}`), meter(Math.abs(a.xp), biggest, a.xp < 0 ? "var(--danger)" : a.cor), el("b", {}, signed(a.xp))))] : []));
}

function drawChart() {
  const { datas, series, rotulos } = data.evolucao;
  const label = rotulos.find((r) => r.id === $("evolucao-atributo").value);
  stepChart($("grafico"), datas.map((day, i) => ({ day, y: series[label.id][i] })), { color: label.cor });
}

function renderAchievements({ conquistas: list }) {
  $("conquistas-titulo").textContent = `Conquistas (${list.filter((c) => c.liberado).length}/${list.length})`;
  $("conquistas").replaceChildren(...list.map((c) => el("div", { className: `conquista ${c.liberado ? "liberada" : "bloqueada"}` },
    el("span", { className: "icone" }, c.icone), el("strong", {}, c.nome), el("small", {}, c.requisito),
    ...(c.liberado ? [] : [meter(c.atual, c.meta), el("small", {}, `${c.atual}/${c.meta}`)]))));
}

attempt(async () => {
  data = await api.getSummary();
  renderWeek(data);
  renderAchievements(data);
  $("evolucao-atributo").replaceChildren(...data.evolucao.rotulos.map((r) => el("option", { value: r.id }, r.nome)));
  $("evolucao-atributo").onchange = drawChart;
  drawChart();
  window.addEventListener("resize", drawChart);
});
