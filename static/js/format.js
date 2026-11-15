const money = new Intl.NumberFormat("pt-BR", { style: "currency", currency: "BRL" });

export const brl = (cents) => money.format(cents / 100);
export const signed = (n) => (n > 0 ? `+${n}` : n < 0 ? `−${-n}` : "0");
export const toDate = (iso) => new Date(`${iso}T12:00:00`);
export const dayLabel = (iso, options = { day: "numeric", month: "short" }) => toDate(iso).toLocaleDateString("pt-BR", options);
