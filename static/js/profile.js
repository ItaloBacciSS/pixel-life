import * as api from "./api.js";
import { $, toast } from "./dom.js";

$("form-senha").onsubmit = async (event) => {
  event.preventDefault();
  const form = event.target;
  try {
    await api.changePassword(form.atual.value, form.nova.value);
    form.reset();
    toast("Senha alterada!");
  } catch (error) {
    toast(error.message);
  }
};

$("form-codigo").onsubmit = async (event) => {
  event.preventDefault();
  const form = event.target;
  try {
    const { codigo } = await api.newRecoveryCode(form.senha.value);
    form.reset();
    $("codigo").hidden = false;
    $("codigo").textContent = codigo;
    toast("Guarde este código: ele não aparece de novo.");
  } catch (error) {
    toast(error.message);
  }
};

$("form-excluir").onsubmit = async (event) => {
  event.preventDefault();
  try {
    await api.deleteAccount(event.target.senha.value);
    location.href = "/login";
  } catch (error) {
    toast(error.message);
  }
};

// Aparência: aplica na hora e salva na conta; se falhar, volta ao estilo anterior.
$("estilos").onclick = async (event) => {
  const botao = event.target.closest(".amostra");
  if (!botao) return;
  const anterior = document.documentElement.dataset.estilo;
  const novo = botao.dataset.id;
  if (novo === anterior) return;
  marcar(novo);
  try {
    await api.saveStyle(novo);
  } catch (error) {
    marcar(anterior);
    toast(error.message);
  }
};

function marcar(id) {
  document.documentElement.dataset.estilo = id;
  for (const botao of $("estilos").children) {
    const ativo = botao.dataset.id === id;
    botao.classList.toggle("ativa", ativo);
    botao.setAttribute("aria-pressed", ativo);
  }
}
