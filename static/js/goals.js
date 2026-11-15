import * as api from "./api.js";
import { $, attempt, el, meter, toast } from "./dom.js";
import { dayLabel } from "./format.js";

let data;

function goalRow(meta) {
  return el("div", { className: `meta-linha${meta.cumprida ? " cumprida" : ""}` },
    el("strong", {}, `${meta.cumprida ? "✓ " : ""}${meta.nome}`),
    el("span", {}, `${Math.min(meta.feitas, meta.vezes)}/${meta.vezes} por semana`),
    el("button", { type: "button", className: "btn btn-ghost", title: "Excluir meta", "aria-label": `Excluir meta ${meta.nome}`,
      onclick: () => act(() => api.removeGoal(meta.id)) }, "✕"),
    meter(meta.feitas, meta.vezes));
}

function render() {
  $("semana-datas").textContent = `${dayLabel(data.inicio)} a ${dayLabel(data.fim)}`;
  $("lista").replaceChildren(...(data.metas.length ? data.metas.map(goalRow)
    : [el("p", { className: "sub" }, "Nenhuma meta ainda. Crie a primeira abaixo!")]));
  const groups = new Map();
  data.acoes.forEach((a) => groups.set(a.atributo, [...(groups.get(a.atributo) || []), a]));
  const current = $("acao-meta").value;
  $("acao-meta").replaceChildren(...[...groups].map(([attr, list]) =>
    el("optgroup", { label: attr }, ...list.map((a) => el("option", { value: a.key }, a.nome)))));
  if (current) $("acao-meta").value = current;
}

const act = (request) => attempt(async () => {
  data = await request();
  render();
});

$("form-meta").onsubmit = async (event) => {
  event.preventDefault();
  const form = event.target;
  if (await act(() => api.addGoal(form.action_key.value, Number(form.vezes.value)))) toast("Meta criada!");
};

act(api.getGoals);
