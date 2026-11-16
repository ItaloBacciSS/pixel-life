let last;

// Sorteia uma fala do personagem entre as do humor, do período do dia e (se houver) da sequência.
export function pick(speech, period, streak) {
  const pool = [...speech.humor, ...speech.periodos[period], ...(streak >= 3 ? speech.sequencia : [])];
  const options = pool.length > 1 ? pool.filter((text) => text !== last) : pool;
  last = options[Math.floor(Math.random() * options.length)];
  return last;
}
