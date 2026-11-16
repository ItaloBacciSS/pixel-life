// Sons de 8 bits gerados no navegador (sem arquivos de áudio). Começa ligado; a escolha fica salva.
const KEY = "pixel-life-som";

const NOTES = {
  done: [[660, 0, 0.08], [880, 0.08, 0.12]],
  undo: [[440, 0, 0.06], [330, 0.06, 0.1]],
  slip: [[196, 0, 0.12, "sawtooth"], [147, 0.12, 0.22, "sawtooth"]],
  level: [[523, 0, 0.1], [659, 0.1, 0.1], [784, 0.2, 0.1], [1047, 0.3, 0.3]],
  badge: [[784, 0, 0.1], [988, 0.1, 0.1], [1175, 0.2, 0.1], [1568, 0.3, 0.3]],
  goal: [[587, 0, 0.1], [740, 0.1, 0.1], [880, 0.2, 0.1], [1175, 0.3, 0.3]],
};

let context;
let muted = (() => {
  try { return localStorage.getItem(KEY) === "off"; } catch { return false; }
})();

function tone(frequency, start, length, type = "square") {
  const oscillator = context.createOscillator();
  const gain = context.createGain();
  const begin = context.currentTime + start;
  oscillator.type = type;
  oscillator.frequency.value = frequency;
  gain.gain.setValueAtTime(0.05, begin);
  gain.gain.exponentialRampToValueAtTime(0.0001, begin + length);
  oscillator.connect(gain).connect(context.destination);
  oscillator.start(begin);
  oscillator.stop(begin + length + 0.02);
}

export function play(name) {
  const Audio = window.AudioContext || window.webkitAudioContext;
  if (muted || !Audio) return;
  try {
    context ??= new Audio();
    if (context.state === "suspended") context.resume();
    NOTES[name].forEach((note) => tone(...note));
  } catch {
    // sem áudio disponível: o jogo segue em silêncio
  }
}

export function bindToggle(button) {
  const paint = () => {
    button.textContent = muted ? "🔇" : "🔊";
    button.setAttribute("aria-pressed", String(!muted));
    button.title = muted ? "Ligar o som" : "Desligar o som";
  };
  button.onclick = () => {
    muted = !muted;
    try { localStorage.setItem(KEY, muted ? "off" : "on"); } catch { /* sem armazenamento */ }
    paint();
    play("done");
  };
  paint();
}
