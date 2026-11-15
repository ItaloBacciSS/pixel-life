import { dayLabel, toDate } from "./format.js";

const NS = "http://www.w3.org/2000/svg";
const HEIGHT = 220;

function node(tag, attrs = {}, text) {
  const element = document.createElementNS(NS, tag);
  for (const [name, value] of Object.entries(attrs)) element.setAttribute(name, value);
  if (text !== undefined) element.textContent = text;
  return element;
}

/**
 * Gráfico em degraus (o valor só muda nos dias com registro).
 * points: [{ day: "AAAA-MM-DD", y: número }] em ordem; format: número -> rótulo do eixo.
 */
export function stepChart(container, points, { color = "#2b2d42", format = String, empty = "Ainda sem dados." } = {}) {
  if (!points.length) return container.replaceChildren(Object.assign(document.createElement("p"), { className: "sub", textContent: empty }));

  const width = Math.max(container.clientWidth, 280);
  const labels = points.map((p) => p.y);
  let [low, high] = [Math.min(...labels), Math.max(...labels)];
  if (low === high) [low, high] = [low - 1, high + 1];
  const pad = { left: 12 + Math.max(...[low, high].map((v) => format(v).length)) * 6.5, right: 14, top: 12, bottom: 28 };

  const times = points.map((p) => toDate(p.day).getTime());
  const [start, end] = [times[0], times[times.length - 1]];
  const x = (t) => pad.left + (end === start ? 0.5 : (t - start) / (end - start)) * (width - pad.left - pad.right);
  const y = (v) => HEIGHT - pad.bottom - ((v - low) / (high - low)) * (HEIGHT - pad.top - pad.bottom);

  let path = `M${x(times[0])},${y(points[0].y)}`;
  points.slice(1).forEach((p, i) => { path += ` H${x(times[i + 1])} V${y(p.y)}`; });
  path += ` H${width - pad.right}`;

  const svg = node("svg", { viewBox: `0 0 ${width} ${HEIGHT}`, role: "img" });
  [low, (low + high) / 2, high].forEach((value) => svg.append(
    node("line", { class: "linha-grade", x1: pad.left, x2: width - pad.right, y1: y(value), y2: y(value) }),
    node("text", { x: pad.left - 6, y: y(value) + 3, "text-anchor": "end" }, format(Math.round(value)))));
  svg.append(
    node("text", { x: pad.left, y: HEIGHT - 8 }, dayLabel(points[0].day, { day: "2-digit", month: "2-digit", year: "2-digit" })),
    node("text", { x: width - pad.right, y: HEIGHT - 8, "text-anchor": "end" },
      dayLabel(points[points.length - 1].day, { day: "2-digit", month: "2-digit", year: "2-digit" })),
    node("path", { d: path, fill: "none", stroke: color, "stroke-width": 3 }));
  points.forEach((p, i) => {
    const dot = node("circle", { cx: x(times[i]), cy: y(p.y), r: 4, fill: color, stroke: "#fff", "stroke-width": 2 });
    dot.append(node("title", {}, `${dayLabel(p.day)}: ${format(p.y)}`));
    svg.append(dot);
  });
  container.replaceChildren(svg);
}
