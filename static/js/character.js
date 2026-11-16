import * as api from "./api.js";
import { $, el, toast } from "./dom.js";

const firstTime = $("salvar").dataset.primeiro === "1";
let data;
let items; // id -> item
let look; // cópia de trabalho: corpo, cores e itens (inclusive os bloqueados que estão só sendo provados)

const previewUrl = (itemIds) => `/personagem.svg?${new URLSearchParams({ ...look, itens: itemIds.join(",") })}`;
const capitalize = (text) => text[0].toUpperCase() + text.slice(1);

function renderChoices(containerId, field, options, build) {
  $(containerId).replaceChildren(...options.map((option) => build(option, look[field] === option, () => {
    look[field] = option;
    render();
  })));
}

// Penteado e modelo de roupa: a lista depende do corpo escolhido.
function renderStyles(containerId, field) {
  const options = data.opcoes[containerId][look.corpo];
  if (!options.some((option) => option.id === look[field])) look[field] = options[0].id;
  $(containerId).replaceChildren(...options.map((option) => el("button", {
    type: "button",
    className: `btn btn-ghost${look[field] === option.id ? " ativo" : ""}`,
    onclick: () => {
      look[field] = option.id;
      render();
    },
  }, option.nome)));
}

const swatch = (color, active, onclick) =>
  el("button", { type: "button", className: `swatch${active ? " ativo" : ""}`, style: `background: ${color}`, title: color, onclick });

const chip = (option, active, onclick) =>
  el("button", { type: "button", className: `btn btn-ghost${active ? " ativo" : ""}`, onclick }, capitalize(option));

function itemCard(item) {
  const status = item.liberado ? "Liberado" : `🔒 ${item.requisito} (${item.atual}/${item.meta})`;
  return el("button", { type: "button", className: `item${item.liberado ? "" : " bloqueado"}`, dataset: { id: item.id }, onclick: () => toggle(item) },
    el("img", { src: previewUrl([item.id]), alt: "" }), el("strong", {}, item.nome), el("small", {}, status));
}

function renderItems() {
  $("itens").replaceChildren(...Object.entries(data.opcoes.slots).map(([slot, label]) => el("section", {},
    el("h4", { className: "slot" }, label),
    el("div", { className: "itens" }, ...data.itens.filter((i) => i.slot === slot).map(itemCard)))));
}

function refresh() {
  $("preview").src = previewUrl(look.itens);
  document.querySelectorAll(".item").forEach((card) => {
    const item = items[card.dataset.id];
    const worn = look.itens.includes(item.id);
    card.classList.toggle("equipado", worn && item.liberado);
    card.classList.toggle("provando", worn && !item.liberado);
  });
  $("aviso").hidden = look.itens.every((id) => items[id].liberado);
}

function render() {
  renderChoices("corpos", "corpo", data.opcoes.corpos, chip);
  renderChoices("peles", "pele", data.opcoes.peles, swatch);
  renderStyles("penteados", "penteado");
  renderStyles("trajes", "traje");
  renderChoices("cabelos", "cabelo", data.opcoes.cabelos, swatch);
  renderChoices("roupas", "roupa", data.opcoes.roupas, swatch);
  if (!firstTime) renderItems(); // na criação da conta só se monta o personagem
  refresh();
}

function toggle(item) {
  const wearing = look.itens.includes(item.id);
  look.itens = look.itens.filter((id) => items[id].slot !== item.slot);
  if (!wearing) look.itens.push(item.id);
  refresh();
}

$("salvar").onclick = async () => {
  try {
    data = await api.saveCharacter({ ...look, itens: look.itens.filter((id) => items[id].liberado) });
    if (firstTime) location.href = "/";
    else toast("Personagem salvo!");
  } catch (error) {
    toast(error.message);
  }
};

(async () => {
  data = await api.getCharacter();
  items = Object.fromEntries(data.itens.map((item) => [item.id, item]));
  look = { ...data.personagem };
  render();
})();
