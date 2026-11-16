import * as api from "./api.js";
import { $, el, toast } from "./dom.js";

const firstTime = $("salvar").dataset.primeiro === "1";
let data;
let items; // id -> item
let look; // cópia de trabalho: corpo, cores, modelos e itens (inclusive bloqueados, que só servem para provar)
let dirty = false;

const previewUrl = (itemIds) => `/personagem.svg?${new URLSearchParams({ ...look, itens: itemIds.join(",") })}`;
const capitalize = (text) => text[0].toUpperCase() + text.slice(1);

const choice = (value, text) => ({ value, text });
const color = (value) => ({ value, color: value });

// Cada seletor: { label, options: [{ value, text?, color?, hint?, locked? }], current, choose }.
function basics() {
  const { opcoes } = data;
  const fromBody = (list) => opcoes[list][look.corpo].map((style) => choice(style.id, style.nome));
  const field = (key) => ({ current: () => look[key], choose: (value) => { look[key] = value; } });
  return [
    { label: "Corpo", options: opcoes.corpos.map((body) => choice(body, capitalize(body))), ...field("corpo") },
    { label: "Pele", options: opcoes.peles.map(color), ...field("pele") },
    { label: "Penteado", options: fromBody("penteados"), ...field("penteado") },
    { label: "Cor do cabelo", options: opcoes.cabelos.map(color), ...field("cabelo") },
    { label: "Modelo de roupa", options: fromBody("trajes"), ...field("traje") },
    { label: "Cor da roupa", options: opcoes.roupas.map(color), ...field("roupa") },
  ];
}

// Um seletor por lugar do corpo: "Nenhum" e depois todos os itens dele, também os bloqueados.
function itemSlots() {
  return Object.entries(data.opcoes.slots).map(([slot, label]) => ({
    label,
    options: [choice("", "Nenhum"), ...data.itens.filter((item) => item.slot === slot).map((item) => ({
      ...choice(item.id, item.nome),
      locked: !item.liberado,
      hint: item.liberado ? "Liberado" : `🔒 ${item.requisito} (${item.atual}/${item.meta})`,
    }))],
    current: () => look.itens.find((id) => items[id].slot === slot) ?? "",
    choose: (value) => {
      look.itens = look.itens.filter((id) => items[id].slot !== slot);
      if (value) look.itens.push(value);
    },
  }));
}

function selector(spec) {
  const index = Math.max(0, spec.options.findIndex((option) => option.value === spec.current()));
  const option = spec.options[index];
  const step = (delta) => () => {
    spec.choose(spec.options[(index + delta + spec.options.length) % spec.options.length].value);
    dirty = true;
    render();
  };
  const arrow = (symbol, delta, name) => el("button", { type: "button", className: "seta", title: `${spec.label}: ${name}`, onclick: step(delta) }, symbol);
  return el("div", { className: `seletor${option.locked ? " bloqueado" : ""}` },
    el("span", { className: "rotulo" }, spec.label),
    el("div", { className: "linha" }, arrow("‹", -1, "anterior"),
      el("div", { className: "valor" }, ...(option.color ? [el("i", { className: "amostra", style: `background: ${option.color}` })] : []), option.text ?? ""),
      arrow("›", 1, "próximo")),
    el("small", { className: "dica" }, option.hint ?? ""));
}

function render() {
  const styles = [["penteado", "penteados"], ["traje", "trajes"]]; // a lista depende do corpo escolhido
  styles.forEach(([key, list]) => {
    const ids = data.opcoes[list][look.corpo].map((style) => style.id);
    if (!ids.includes(look[key])) look[key] = ids[0];
  });
  $("basico").replaceChildren(...basics().map(selector));
  if (!firstTime) $("itens").replaceChildren(...itemSlots().map(selector));
  $("preview").src = previewUrl(look.itens);
  $("aviso").hidden = look.itens.every((id) => items[id].liberado);
  $("estado").textContent = !firstTime && dirty ? "Alterações não salvas: clique em Salvar." : "";
}

$("salvar").onclick = async () => {
  try {
    data = await api.saveCharacter({ ...look, itens: look.itens.filter((id) => items[id].liberado) });
    dirty = false;
    render();
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
