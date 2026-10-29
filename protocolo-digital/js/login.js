const form = document.getElementById("login-form");
const message = document.getElementById("login-message");

form.addEventListener("submit", async event => {
  event.preventDefault();
  message.hidden = true;
  const data = new FormData(form);
  try {
    const response = await fetch("/login", {
      method: "POST",
      credentials: "same-origin",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ email: data.get("email").trim(), senha: data.get("senha") })
    });
    const result = await response.json();
    if (!response.ok) throw new Error(result.detail || "Não foi possível entrar.");
    window.location.assign("/sistema");
  } catch (error) {
    message.textContent = error.message;
    message.hidden = false;
  }
});
