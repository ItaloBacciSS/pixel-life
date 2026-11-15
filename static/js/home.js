import * as api from "./api.js";
import { $, attempt, el, toast } from "./dom.js";

const MOODS = { normal: "Normal", feliz: "Feliz", triste: "Triste" };

let data;
let choice; // cópia de trabalho: tema, espécie e pelagem
let mood = "";

const query = () => new URLSearchParams(choice);
const species = () => data.opcoes.especies.find((item) => item.id === choice.especie);

function chip(label, active, onclick) {
  return el("button", { type: "button", className: `btn btn-ghost${active ? " ativo" : ""}`, onclick }, label);
}

function render() {
  $("fundo").src = `/cenario.svg?${query()}`;
  $("previa-quarto").src = `/quarto.svg?${new URLSearchParams({ ...choice, ...(mood && { humor: mood }) })}`;

  $("especies").replaceChildren(...data.opcoes.especies.map((item) => chip(item.nome, item.id === choice.especie, () => {
    choice.especie = item.id;
    if (!item.pelagens.some((coat) => coat.id === choice.pelagem)) choice.pelagem = item.pelagens[0].id;
    render();
  })));
  $("pelagens").replaceChildren(...species().pelagens.map((coat) => el("button", {
    type: "button", className: `swatch${coat.id === choice.pelagem ? " ativo" : ""}`, title: coat.nome,
    style: `background: ${coat.cor}`, onclick: () => { choice.pelagem = coat.id; render(); },
  })));
  $("humores").replaceChildren(...Object.entries(MOODS).map(([id, label]) =>
    chip(label, id === mood, () => { mood = mood === id ? "" : id; render(); })));
  $("temas").replaceChildren(...data.opcoes.temas.map((theme) => el("button", {
    type: "button", className: `tema${theme.id === choice.tema ? " ativo" : ""}`,
    onclick: () => { choice.tema = theme.id; render(); },
  }, el("img", { src: `/cenario.svg?${new URLSearchParams({ tema: theme.id })}`, alt: "" }), theme.nome)));
}

$("salvar").onclick = () => attempt(async () => {
  data = await api.saveHome(choice);
  toast("Quarto salvo!");
});

attempt(async () => {
  data = await api.getHome();
  choice = { ...data.atual };
  render();
});
