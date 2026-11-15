export const $ = (id) => document.getElementById(id);

export function el(tag, { dataset, ...props } = {}, ...children) {
  const node = Object.assign(document.createElement(tag), props);
  Object.assign(node.dataset, dataset);
  node.append(...children);
  return node;
}

// Barra de progresso compacta; `value` e `goal` na mesma unidade.
export const meter = (value, goal, color) => el("div", { className: "trilho", style: color ? `--accent: ${color}` : "" },
  el("div", { style: `width: ${Math.min(100, Math.max(0, (value / goal) * 100))}%` }));

let toastTimer;

export function toast(message) {
  const box = $("toast");
  box.textContent = message;
  box.classList.add("visible");
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => box.classList.remove("visible"), 3000);
}

// Executa `action`; em caso de erro mostra a mensagem e devolve false.
export async function attempt(action) {
  try {
    await action();
    return true;
  } catch (error) {
    toast(error.message);
    return false;
  }
}
