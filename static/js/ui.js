import * as api from "./api.js";
import { $, el, meter, toast } from "./dom.js";
import * as cenario from "./cenario.js";
import * as effects from "./effects.js";
import * as speech from "./fala.js";
import { brl, signed } from "./format.js";
import * as sound from "./sound.js";

const SHELF_SLOTS = 4;
const roomUrl = $("quarto").getAttribute("src");

let state;
let leveledUp = [];
let unlocked = []; // conquistas ganhas na última ação, para animar na estante
const shownPercent = {}; // porcentagem exibida em cada barra, para animar a mudança

const attributeNames = () => Object.fromEntries(state.atributos.map((a) => [a.id, a.nome]));

function describe(effects) {
  const names = attributeNames();
  return Object.entries(effects).map(([id, xp]) => `${signed(xp)} ${names[id]}`).join(", ");
}

function actionButton(action) {
  const done = action.registro_id !== null;
  return el("button", {
    type: "button",
    className: `acao${done ? " feita" : ""}`,
    title: done ? "Clique para desfazer" : "",
    onclick: (event) => (done
      ? run(() => api.removeEntry(action.registro_id)).then((result) => result && sound.play("undo"))
      : addEntry(action, event.currentTarget.getBoundingClientRect())),
  }, done ? `✓ ${action.nome}` : action.nome, el("small", {}, describe(action.efeitos)));
}

function renderAttribute(attr) {
  const actions = state.acoes.filter((a) => !a.tropeco && attr.id in a.efeitos);
  const percent = (attr.xp / attr.custo) * 100;
  const start = leveledUp.includes(attr.id) ? 0 : shownPercent[attr.id] ?? percent;
  const fill = el("div", { style: `width: ${start}%` });
  requestAnimationFrame(() => requestAnimationFrame(() => { fill.style.width = `${percent}%`; }));
  shownPercent[attr.id] = percent;

  const card = el("article", { className: `atributo card${leveledUp.includes(attr.id) ? " subiu" : ""}`, dataset: { id: attr.id } },
    el("header", {}, el("h3", {}, `${attr.icone} ${attr.nome}`), el("span", {}, `NV ${attr.nivel}`)),
    el("div", { className: "barra" }, fill),
    el("span", { className: "xp" }, `${attr.xp} / ${attr.custo} XP`),
    ...(attr.id === "riqueza" ? [el("a", { className: "saldo", href: "/riqueza" }, `Saldo: ${brl(state.saldo)}`)] : []),
    el("div", { className: "acoes" }, ...actions.map(actionButton)));
  card.style.setProperty("--accent", attr.cor);
  return card;
}

function renderStreak(label, streak) {
  return el("div", { className: "streak" },
    el("strong", {}, `${streak.atual > 0 ? "🔥" : "💤"} ${streak.atual} dias`), `${label} · recorde ${streak.recorde}`);
}

function renderShelf() {
  const earned = state.conquistas.filter((c) => c.liberado).slice(-SHELF_SLOTS);
  $("estante").replaceChildren(...Array.from({ length: SHELF_SLOTS }, (_, i) => earned[i]
    ? el("span", { className: `selo${unlocked.includes(earned[i].id) ? " novo" : ""}`, title: earned[i].nome }, earned[i].icone)
    : el("span", { className: "selo vazio" })));
}

function renderGoals() {
  $("metas").hidden = !state.metas.length;
  $("metas").replaceChildren(
    el("header", { className: "linha" }, el("h3", {}, "Metas da semana"), el("a", { href: "/metas" }, "Gerenciar")),
    ...state.metas.map((meta) => el("div", { className: `meta${meta.cumprida ? " cumprida" : ""}` },
      el("span", {}, `${meta.cumprida ? "✓ " : ""}${meta.nome}`), el("small", {}, `${Math.min(meta.feitas, meta.vezes)}/${meta.vezes}`),
      meter(meta.feitas, meta.vezes))));
}

function renderDay() {
  const date = new Date(`${state.dia}T12:00:00`);
  $("dia-label").textContent = date.toLocaleDateString("pt-BR", { weekday: "long", day: "numeric", month: "long" });
  $("dia-proximo").disabled = state.dia === state.hoje;
  $("dia-hoje").hidden = state.dia === state.hoje;
}

function render() {
  const names = attributeNames();
  $("nivel-geral").textContent = state.nivel_geral;
  $("sequencias").replaceChildren(...Object.entries(state.sequencias).map(
    ([id, streak]) => renderStreak(id === "geral" ? "sem tropeçar" : `sem tropeçar na ${names[id]}`, streak)));
  renderDay();
  renderShelf();
  renderGoals();
  const now = cenario.paint(state.mascote.humor);
  $("balao").textContent = speech.pick(state.mascote.falas, now.period, state.sequencias.geral.atual);
  $("atributos").replaceChildren(...state.atributos.map(renderAttribute));
  $("tropecos").replaceChildren(
    el("h3", {}, "Tropeços"),
    el("div", { className: "acoes" }, ...state.acoes.filter((a) => a.tropeco).map(actionButton)));
  $("atributo-acao").replaceChildren(...state.atributos.map((a) => el("option", { value: a.id }, `${a.icone} ${a.nome}`)));
}

// Itens que passaram a ter `flag` verdadeiro entre as duas listas.
const newly = (before, after, flag) => after.filter((item) => item[flag] && !before.find((old) => old.id === item.id)?.[flag]);

async function run(request) {
  try {
    const before = state;
    state = await request();
    leveledUp = before ? state.atributos.filter((a, i) => a.nivel > before.atributos[i].nivel).map((a) => a.id) : [];
    const badges = before ? newly(before.conquistas, state.conquistas, "liberado") : [];
    unlocked = badges.map((c) => c.id);
    render();
    if (before) $("quarto").src = `${roomUrl}?${Date.now()}`;
    return {
      leveled: state.atributos.filter((a) => leveledUp.includes(a.id)),
      badges,
      goals: before ? newly(before.metas, state.metas, "cumprida") : [],
    };
  } catch (error) {
    toast(error.message);
  }
}

async function addEntry(action, rect) {
  const result = await run(() => api.addEntry(action.key, state.dia));
  if (!result) return;
  effects.floatText(describe(action.efeitos), rect, action.tropeco);
  const accent = getComputedStyle(document.querySelector(`[data-id="${Object.keys(action.efeitos)[0]}"]`) ?? document.body)
    .getPropertyValue("--accent").trim() || "#ffd23f";
  const messages = [
    ...result.leveled.map((a) => `LEVEL UP! ${a.nome} ${a.nivel}`),
    ...result.badges.map((c) => `CONQUISTA! ${c.icone} ${c.nome}`),
    ...result.goals.map((m) => `META CUMPRIDA! ${m.nome}`),
  ];
  if (action.tropeco) {
    effects.animateCharacter("tremer");
    effects.sparkles(rect, "#ff6b6b", 6);
    sound.play("slip");
    return;
  }
  Object.keys(action.efeitos).forEach(effects.glow);
  effects.sparkles(rect, accent);
  if (!messages.length) {
    effects.animateCharacter("pulo");
    sound.play("done");
    return;
  }
  effects.animateCharacter("pulao");
  effects.confetti();
  effects.impact();
  effects.banner(...messages);
  sound.play(result.leveled.length ? "level" : result.badges.length ? "badge" : "goal");
}

function shiftDay(days) {
  const date = new Date(`${state.dia}T12:00:00Z`);
  date.setUTCDate(date.getUTCDate() + days);
  return run(() => api.getState(date.toISOString().slice(0, 10)));
}

$("dia-anterior").onclick = () => shiftDay(-1);
$("dia-proximo").onclick = () => shiftDay(1);
$("dia-hoje").onclick = () => sound.bindToggle($("som"));
run(() => api.getState());

const dialog = $("dialogo-acao");
$("nova-acao").onclick = () => dialog.showModal();
$("cancelar-acao").onclick = () => dialog.close();
$("form-acao").onsubmit = async (event) => {
  const form = event.target;
  const data = Object.fromEntries(new FormData(form));
  const created = await run(() => api.createAction({ ...data, tropeco: Boolean(data.tropeco) }));
  if (created) {
    form.reset();
    toast("Ação criada!");
  }
};

sound.bindToggle($("som"));
run(() => api.getState());
