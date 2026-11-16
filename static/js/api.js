async function request(method, url, body) {
  const response = await fetch(url, {
    method,
    headers: body ? { "Content-Type": "application/json" } : {},
    body: body && JSON.stringify(body),
  });
  const data = await response.json().catch(() => ({}));
  if (response.status === 401) location.href = "/login";
  if (!response.ok) throw new Error(data.erro || "Algo deu errado.");
  return data;
}

export const getState = (day) => request("GET", `/api/estado${day ? `?dia=${day}` : ""}`);
export const addEntry = (actionKey, day) => request("POST", "/api/registros", { action_key: actionKey, dia: day });
export const removeEntry = (id) => request("DELETE", `/api/registros/${id}`);
export const createAction = (action) => request("POST", "/api/acoes", action);
export const getCharacter = () => request("GET", "/api/personagem");
export const saveCharacter = (look) => request("PUT", "/api/personagem", look);
export const getHome = () => request("GET", "/api/quarto");
export const saveHome = (choice) => request("PUT", "/api/quarto", choice);
export const getSummary = () => request("GET", "/api/progresso");
export const getGoals = () => request("GET", "/api/metas");
export const addGoal = (actionKey, times) => request("POST", "/api/metas", { action_key: actionKey, vezes: times });
export const removeGoal = (id) => request("DELETE", `/api/metas/${id}`);
export const getWealth = () => request("GET", "/api/riqueza");
export const addMove = (cents, note, day) => request("POST", "/api/riqueza", { centavos: cents, nota: note, dia: day });
export const setBalance = (cents, day) => request("POST", "/api/riqueza/saldo", { saldo: cents, dia: day });
export const removeMove = (id) => request("DELETE", `/api/riqueza/${id}`);
export const changePassword = (current, next) => request("POST", "/api/senha", { atual: current, nova: next });
export const newRecoveryCode = (password) => request("POST", "/api/recuperacao", { senha: password });
export const saveStyle = (id) => request("PUT", "/api/estilo", { estilo: id });
export const deleteAccount = (password) => request("DELETE", "/api/conta", { senha: password });
