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
  if (typeof loadSubscriptions === "function") loadSubscriptions();
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

// ---------- 訂閱功能 ----------

const citySel = document.getElementById("city");
const routeQ = document.getElementById("route-q");
const routeSel = document.getElementById("route-select");
const directionSel = document.getElementById("direction");
const stopSel = document.getElementById("stop-select");
const minutesInput = document.getElementById("notify-minutes");
const subscribeBtn = document.getElementById("subscribe-btn");
const subMessage = document.getElementById("sub-message");
const subList = document.getElementById("sub-list");

let routes = []; // 搜尋到的路線，選路線時要用到 route_uid

function showSubMessage(text, ok = false) {
  subMessage.textContent = text;
  subMessage.className = ok ? "message ok" : "message";
}

// 呼叫需要登入的 API；token 失效（401）就自動登出
async function authFetch(url, options = {}) {
  const res = await fetch(url, {
    ...options,
    headers: { ...(options.headers || {}), Authorization: `Bearer ${getToken()}` },
  });
  if (res.status === 401) {
    logout();
    showMessage("登入已過期，請重新登入");
    throw new Error("unauthorized");
  }
  return res;
}

async function searchRoutes() {
  const q = routeQ.value.trim();
  if (!q) return;
  showSubMessage("搜尋中...", true);

  const res = await fetch(`/cities/${citySel.value}/routes?q=${encodeURIComponent(q)}`);
  if (!res.ok) {
    showSubMessage("搜尋失敗，請稍後再試");
    return;
  }
  routes = await res.json();
  routeSel.innerHTML = "";

  if (routes.length === 0) {
    routeSel.innerHTML = '<option value="">找不到路線</option>';
    routeSel.disabled = true;
    directionSel.disabled = true;
    stopSel.disabled = true;
    subscribeBtn.disabled = true;
    showSubMessage("找不到符合的路線");
    return;
  }

  routes.forEach((r, i) => {
    const opt = document.createElement("option");
    opt.value = i; // 用陣列索引，方便之後取回完整資料
    opt.textContent = `${r.route_name}　${r.headsign}`;
    routeSel.appendChild(opt);
  });
  routeSel.disabled = false;
  directionSel.disabled = false;
  showSubMessage("");
  loadStops();
}

async function loadStops() {
  const route = routes[routeSel.value];
  if (!route) return;

  stopSel.innerHTML = '<option value="">載入中...</option>';
  stopSel.disabled = true;
  subscribeBtn.disabled = true;

  const url = `/cities/${citySel.value}/routes/${encodeURIComponent(route.route_name)}/stops?direction=${directionSel.value}`;
  const res = await fetch(url);
  if (!res.ok) {
    stopSel.innerHTML = '<option value="">載入失敗</option>';
    return;
  }
  const stops = await res.json();
  stopSel.innerHTML = "";

  if (stops.length === 0) {
    stopSel.innerHTML = '<option value="">此方向沒有站牌資料</option>';
    return;
  }

  stops.forEach((s) => {
    const opt = document.createElement("option");
    opt.value = s.stop_uid;
    opt.textContent = `${s.sequence}. ${s.stop_name}`;
    opt.dataset.name = s.stop_name;
    stopSel.appendChild(opt);
  });
  stopSel.disabled = false;
  subscribeBtn.disabled = false;
}

async function subscribe() {
  const route = routes[routeSel.value];
  const stopOpt = stopSel.options[stopSel.selectedIndex];
  if (!route || !stopOpt || !stopOpt.value) return;

  const body = {
    city: citySel.value,
    route_name: route.route_name,
    route_uid: route.route_uid,
    direction: Number(directionSel.value),
    stop_uid: stopOpt.value,
    stop_name: stopOpt.dataset.name,
    notify_minutes: Number(minutesInput.value),
  };

  try {
    const res = await authFetch("/subscriptions", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });
    if (res.ok) {
      showSubMessage("訂閱成功", true);
      loadSubscriptions();
    } else {
      showSubMessage("訂閱失敗，請檢查欄位（通知時間需為 1～30）");
    }
  } catch (e) {
    /* 401 已在 authFetch 處理 */
  }
}

async function loadSubscriptions() {
  try {
    const res = await authFetch("/subscriptions");
    const subs = await res.json();
    subList.innerHTML = "";

    if (subs.length === 0) {
      subList.innerHTML = "<li>目前沒有訂閱</li>";
      return;
    }

    subs.forEach((s) => {
      const li = document.createElement("li");
      const dir = s.direction === 0 ? "去程" : "返程";
      // 用 textContent 而不是 innerHTML，避免資料中的特殊字元被當成 HTML 執行
      li.textContent = `${s.route_name} 路（${dir}）${s.stop_name}，提前 ${s.notify_minutes} 分鐘`;

      const del = document.createElement("button");
      del.textContent = "刪除";
      del.addEventListener("click", async () => {
        await authFetch(`/subscriptions/${s.id}`, { method: "DELETE" });
        loadSubscriptions();
      });
      li.appendChild(del);
      subList.appendChild(li);
    });
  } catch (e) {
    /* 401 已在 authFetch 處理 */
  }
}

document.getElementById("route-search-btn").addEventListener("click", searchRoutes);
routeQ.addEventListener("keydown", (e) => {
  if (e.key === "Enter") searchRoutes();
});
routeSel.addEventListener("change", loadStops);
directionSel.addEventListener("change", loadStops);
citySel.addEventListener("change", () => {
  routes = [];
  routeSel.innerHTML = '<option value="">請先搜尋路線</option>';
  routeSel.disabled = true;
  directionSel.disabled = true;
  stopSel.innerHTML = '<option value="">請先選擇路線</option>';
  stopSel.disabled = true;
  subscribeBtn.disabled = true;
});
subscribeBtn.addEventListener("click", subscribe);