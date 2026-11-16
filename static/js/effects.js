const $ = (id) => document.getElementById(id);
const calm = () => matchMedia("(prefers-reduced-motion: reduce)").matches;

// Reinicia uma animação CSS: tira a classe, força o recálculo e põe de volta.
function restart(node, name) {
  node.classList.remove(name);
  void node.offsetWidth;
  node.classList.add(name);
  node.addEventListener("animationend", () => node.classList.remove(name), { once: true });
}

// Faíscas saindo do ponto clicado, na cor do atributo.
export function sparkles(rect, color = "#ffd23f", total = 10) {
  if (calm()) return;
  for (let i = 0; i < total; i++) {
    const angle = (i / total) * 2 * Math.PI;
    const distance = 28 + Math.random() * 34;
    const piece = document.createElement("i");
    piece.className = "faisca";
    piece.style.cssText = `left: ${rect.left + rect.width / 2}px; top: ${rect.top + rect.height / 2}px; background: ${color}; --dx: ${Math.cos(angle) * distance}px; --dy: ${Math.sin(angle) * distance}px`;
    document.body.append(piece);
    setTimeout(() => piece.remove(), 700);
  }
}

// Clarão e tremor da cena inteira, para os grandes momentos.
export function impact() {
  if (calm()) return;
  restart($("clarao"), "ativo");
  restart($("cena"), "tremor");
}

// Dá um brilho na barra do atributo que acabou de ganhar XP.
export function glow(attributeId) {
  const card = document.querySelector(`[data-id="${attributeId}"]`);
  if (card && !calm()) restart(card, "ganhou");
}

export function floatText(text, rect, negative = false) {
  const node = Object.assign(document.createElement("span"), {
    className: `flutuante${negative ? " negativo" : ""}`,
    textContent: text,
  });
  node.style.left = `${rect.left + rect.width / 2}px`;
  node.style.top = `${rect.top}px`;
  document.body.append(node);
  setTimeout(() => node.remove(), 1100);
}

// name: "pulo" | "pulao" | "tremer"
export function animateCharacter(name) {
  const character = $("personagem");
  character.classList.remove("pulo", "pulao", "tremer");
  void character.offsetWidth;
  character.classList.add(name);
  character.addEventListener("animationend", () => character.classList.remove(name), { once: true });
}

export function confetti() {
  const colors = ["#ffd23f", "#ff7a59", "#3a86ff", "#5fb85f", "#e63946", "#8338ec"];
  const total = 28;
  for (let i = 0; i < total; i++) {
    const angle = (i / total) * 2 * Math.PI;
    const distance = 70 + Math.random() * 90;
    const piece = document.createElement("i");
    piece.style.cssText = `background: ${colors[i % colors.length]}; --dx: ${Math.cos(angle) * distance}px; --dy: ${Math.sin(angle) * distance - 40}px`;
    $("confete").append(piece);
    setTimeout(() => piece.remove(), 1300);
  }
}

const BANNER_MS = 1900;

// Mostra os avisos um depois do outro.
export function banner(...texts) {
  texts.forEach((text, i) => setTimeout(() => {
    const node = $("banner");
    node.textContent = text;
    node.classList.remove("visivel");
    void node.offsetWidth;
    node.classList.add("visivel");
  }, i * BANNER_MS));
}
