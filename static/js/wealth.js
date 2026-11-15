import * as api from "./api.js";
import { $, attempt, el, toast } from "./dom.js";
import { stepChart } from "./chart.js";
import { brl, dayLabel } from "./format.js";

let data;

const toCents = (value) => Math.round(Number(value) * 100);

function moveRow(move) {
  return el("li", {},
    el("span", {}, move.nota || (move.centavos > 0 ? "Entrada" : "Saída"), el("small", {}, dayLabel(move.dia, { day: "numeric", month: "short", year: "numeric" }))),
    el("b", { className: move.centavos > 0 ? "entrada" : "saida" }, `${move.centavos > 0 ? "+" : ""}${brl(move.centavos)}`),
    el("button", { type: "button", className: "btn btn-ghost", title: "Excluir movimento", "aria-label": "Excluir movimento",
      onclick: () => act(() => api.removeMove(move.id)) }, "✕"));
}

const drawChart = () => stepChart($("grafico"), data.serie.map((p) => ({ day: p.dia, y: p.saldo })),
  { color: "#f4a100", format: brl, empty: "Registre um movimento para ver a evolução." });

function render() {
  $("saldo").textContent = brl(data.saldo);
  $("saldo").classList.toggle("negativo", data.saldo < 0);
  for (const form of [$("form-movimento"), $("form-saldo")]) form.dia.defaultValue = form.dia.max = data.hoje;
  $("movimentos").replaceChildren(...(data.movimentos.length ? data.movimentos.map(moveRow) : [el("li", {}, "Nenhum movimento ainda.")]));
  drawChart();
}

const act = (request) => attempt(async () => {
  data = await request();
  render();
});

$("form-movimento").onsubmit = async (event) => {
  event.preventDefault();
  const form = event.target;
  const sign = Number(event.submitter.value);
  if (await act(() => api.addMove(sign * toCents(form.valor.value), form.nota.value, form.dia.value))) {
    form.reset();
    toast("Movimento registrado!");
  }
};

$("form-saldo").onsubmit = async (event) => {
  event.preventDefault();
  const form = event.target;
  if (await act(() => api.setBalance(toCents(form.saldo.value), form.dia.value))) {
    form.reset();
    toast("Saldo atualizado!");
  }
};

act(api.getWealth);
window.addEventListener("resize", () => data && drawChart());
