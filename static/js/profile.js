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
