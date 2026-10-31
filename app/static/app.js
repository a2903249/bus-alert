const TOKEN_KEY = "bus_alert_token";

const authSection = document.getElementById("auth-section");
const appSection = document.getElementById("app-section");
const authMessage = document.getElementById("auth-message");

function showMessage(text, ok = false) {
  authMessage.textContent = text;
  authMessage.className = ok ? "message ok" : "message";
}

function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

function showApp(email) {
  authSection.hidden = true;
  appSection.hidden = false;
  document.getElementById("user-email").textContent = email;
}

function showAuth() {
  authSection.hidden = false;
  appSection.hidden = true;
}

async function register() {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  const res = await fetch("/auth/register", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ email, password }),
  });

  if (res.ok) {
    showMessage("註冊成功，請按「登入」", true);
  } else {
    const err = await res.json().catch(() => ({}));
    showMessage(typeof err.detail === "string" ? err.detail : "註冊失敗，請檢查 Email 格式與密碼長度");
  }
}

async function login() {
  const email = document.getElementById("email").value.trim();
  const password = document.getElementById("password").value;

  // 登入 API 要求表單格式，欄位名稱是 username
  const form = new URLSearchParams({ username: email, password });

  const res = await fetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/x-www-form-urlencoded" },
    body: form,
  });

  if (res.ok) {
    const data = await res.json();
    localStorage.setItem(TOKEN_KEY, data.access_token);
    localStorage.setItem("bus_alert_email", email);
    showMessage("");
    showApp(email);
  } else {
    const err = await res.json().catch(() => ({}));
    showMessage(typeof err.detail === "string" ? err.detail : "登入失敗");
  }
}

function logout() {
  localStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem("bus_alert_email");
  showAuth();
}

document.getElementById("login-btn").addEventListener("click", login);
document.getElementById("register-btn").addEventListener("click", register);
document.getElementById("logout-btn").addEventListener("click", logout);

// 重新整理頁面時，如果已經有 token，直接進入登入後畫面
if (getToken()) {
  showApp(localStorage.getItem("bus_alert_email") || "");
} else {
  showAuth();
}