# backend/app/api/v1/routes/admin_ui.py
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.core.config import settings

router = APIRouter()


@router.get("/admin", response_class=HTMLResponse)
def admin_ui():
    default_provider_acct = settings.PROVIDER_CLIENT_ID or ""

    html = """
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>API Admin UI</title>
  <style>
    body { font-family: ui-sans-serif, system-ui; margin: 20px; }
    .row { display:flex; gap:12px; flex-wrap:wrap; align-items:flex-end; }
    .card { border:1px solid #ddd; border-radius:10px; padding:14px; margin:12px 0; }
    label { display:block; font-size:12px; color:#333; margin-bottom:4px; }
    input, select, textarea, button { padding:10px; border:1px solid #ccc; border-radius:8px; }
    textarea { width:100%; min-height: 90px; }
    button { cursor:pointer; }
    .muted { color:#666; font-size:12px; }
    .mono { font-family: ui-monospace, SFMono-Regular; font-size:12px; white-space:pre-wrap; }
    table { width:100%; border-collapse:collapse; }
    td, th { border-bottom: 1px solid #eee; padding:6px; text-align:left; }

    .tabs { display:flex; gap:8px; flex-wrap:wrap; margin-bottom: 12px; }
    .tabbtn { background:#f7f7f7; }
    .tabbtn.active { background:#eaeaea; border-color:#999; }
    .page { display:none; }
    .page.active { display:block; }
  </style>
</head>
<body>
  <h2>Admin UI (HTML+JS)</h2>
  <div class="muted">Endpoints: /api/v1/of-accounts, /api/v1/audiences/*, /api/v1/provider/*</div>

  <div class="tabs">
    <button class="tabbtn active" data-page="pageAccounts" onclick="showPage('pageAccounts')">Accounts</button>
    <button class="tabbtn" data-page="pageAudiences" onclick="showPage('pageAudiences')">Audiences</button>
    <button class="tabbtn" data-page="pageSend" onclick="showPage('pageSend')">Send</button>
    <button class="tabbtn" data-page="pageQueue" onclick="showPage('pageQueue')">Queue</button>
    <button class="tabbtn" data-page="pageOverview" onclick="showPage('pageOverview')">Overview</button>
  </div>

  <!-- PAGE: ACCOUNTS -->
  <div id="pageAccounts" class="page card active">
    <h3>Accounts</h3>

    <div class="row">
      <div style="min-width:420px;">
        <label>Accounts in DB (multi-select)</label>
        <select id="accountsSelect" multiple size="8" style="width:520px"></select>
        <div class="muted">Выбери 1+ аккаунтов. Для custom audience отправка только на 1 аккаунт.</div>
      </div>
      <div>
        <button onclick="loadAccounts()">Load Accounts</button>
      </div>
      <div>
        <button onclick="deleteSelectedAccounts()">Delete Selected</button>
      </div>
    </div>

    <hr style="border:none;border-top:1px solid #eee;margin:14px 0;" />

    <h4>Create account</h4>
    <div class="row">
      <div>
        <label>Name</label>
        <input id="accName" placeholder="Main Account" style="width:260px" />
      </div>
      <div>
        <label>account_code (acct_...)</label>
        <input id="accCode" placeholder="acct_..." style="width:420px" />
      </div>
      <div>
        <label>is_active</label>
        <select id="accActive" style="width:140px">
          <option value="true" selected>true</option>
          <option value="false">false</option>
        </select>
      </div>
      <div>
        <button onclick="createAccount()">Create</button>
      </div>
    </div>

    <div id="accountsStatus" class="muted" style="margin-top:10px;"></div>
  </div>

  <!-- PAGE: AUDIENCES -->
  <div id="pageAudiences" class="page card">
    <h3>Audiences</h3>

    <div class="row">
      <div>
        <label>Internal of_account_id</label>
        <input id="ofAccountId" type="number" value="1" style="width:220px" />
        <div class="muted">Берём из первого выбранного аккаунта (если выбран).</div>
      </div>
      <div>
        <button onclick="loadAudiences()">Load Audiences</button>
      </div>
      <div id="audiencesStatus" class="muted"></div>
    </div>

    <hr style="border:none;border-top:1px solid #eee;margin:14px 0;" />

    <h4>Custom Lists</h4>

    <div class="row">
      <div>
        <label>Create new custom list</label>
        <input id="newListName" placeholder="VIP LA Fans" style="width:320px" />
      </div>
      <div>
        <button onclick="createList()">Create</button>
      </div>
    </div>

    <div class="row" style="margin-top:12px;">
      <div style="min-width:320px;">
        <label>Pick custom list</label>
        <select id="customListSelect" style="width:320px"></select>
      </div>
      <div>
        <button onclick="loadMembers()">Load Members</button>
      </div>
      <div id="membersStatus" class="muted"></div>
    </div>

    <div style="margin-top:10px;">
      <label>Add members (provider_user_id). One per line / comma / space.</label>
      <textarea id="membersInput" placeholder="123\n456\n789"></textarea>
      <div class="row" style="margin-top:10px;">
        <button onclick="addMembers()">Add</button>
      </div>
    </div>

    <div style="margin-top:12px;">
      <h4>Members</h4>
      <div id="membersTable"></div>
    </div>
  </div>

  <!-- PAGE: SEND -->
  <div id="pageSend" class="page card">
    <h3>Send Mass Message</h3>

    <div class="row">
      <div>
        <label>Provider account_id (fallback)</label>
        <input id="providerAccountId" value="__DEFAULT_PROVIDER_ACCT__" style="width:420px" />
        <div class="muted">Если выбран аккаунт из DB — используем его account_code.</div>
      </div>
      <div style="min-width:320px;">
        <label>Audience</label>
        <select id="audienceSelect" style="width:320px"></select>
      </div>
      <div id="recentBox" style="display:none;">
        <label>Recent period</label>
        <div class="row">
          <input id="recentStart" placeholder="YYYY-MM-DD HH:MM:SS" style="width:220px" />
          <input id="recentEnd" placeholder="YYYY-MM-DD HH:MM:SS" style="width:220px" />
        </div>
      </div>
    </div>

    <div style="margin-top:10px;">
      <label>Text</label>
      <textarea id="messageText" placeholder="Hello!"></textarea>
    </div>

    <div class="row" style="margin-top:10px;">
      <button onclick="sendMessage()">Send</button>
      <div id="sendStatus" class="muted"></div>
    </div>

    <div class="mono" id="sendResult" style="margin-top:10px;"></div>
  </div>

  <!-- PAGE: QUEUE -->
  <div id="pageQueue" class="page card">
    <h3>Queue (pending / recent)</h3>

    <div class="row">
      <div>
        <button onclick="loadQueue()">Load Queue for selected account</button>
      </div>
      <div class="muted" id="queueStatus"></div>
    </div>

    <div class="mono" id="queueResult" style="margin-top:10px;"></div>

    <hr style="border:none;border-top:1px solid #eee;margin:14px 0;" />

    <div class="row">
      <div>
        <label>queue_id</label>
        <input id="queueId" type="number" placeholder="123" style="width:240px" />
      </div>
      <div>
        <button onclick="loadQueueItem()">Get queue item</button>
      </div>
    </div>

    <div class="mono" id="queueItemResult" style="margin-top:10px;"></div>
  </div>

  <!-- PAGE: OVERVIEW -->
  <div id="pageOverview" class="page card">
    <h3>Overview</h3>

    <div class="row">
      <div>
        <label>start_date</label>
        <input id="ovStart" placeholder="2025-01-01 00:00:00" style="width:220px" />
      </div>
      <div>
        <label>end_date</label>
        <input id="ovEnd" placeholder="2025-03-31 23:59:59" style="width:220px" />
      </div>
      <div>
        <label>limit</label>
        <input id="ovLimit" type="number" value="10" style="width:120px" />
      </div>
      <div>
        <label>offset</label>
        <input id="ovOffset" type="number" value="0" style="width:120px" />
      </div>
      <div>
        <label>query</label>
        <input id="ovQuery" placeholder="My message text" style="width:220px" />
      </div>
      <div>
        <button onclick="loadOverview()">Load Overview</button>
      </div>
      <div class="muted" id="overviewStatus"></div>
    </div>

    <div class="mono" id="overviewResult" style="margin-top:10px;"></div>
  </div>

<script>
const API = "/api/v1";

function $(id) { return document.getElementById(id); }
function val(id) { return $(id).value; }
function setText(id, text) { $(id).textContent = text; }
function setHtml(id, html) { $(id).innerHTML = html; }

function showPage(pageId) {
  for (const el of document.querySelectorAll(".page")) el.classList.remove("active");
  $(pageId).classList.add("active");

  for (const btn of document.querySelectorAll(".tabbtn")) {
    btn.classList.toggle("active", btn.dataset.page === pageId);
  }
}

async function apiFetch(path, opts={}) {
  const res = await fetch(API + path, {
    headers: { "Content-Type": "application/json", ...(opts.headers||{}) },
    ...opts
  });
  const txt = await res.text();
  let data = null;
  try { data = JSON.parse(txt); } catch(e) { data = txt; }
  if (!res.ok) {
    throw new Error(typeof data === "string" ? data : JSON.stringify(data));
  }
  return data;
}

function parseIds(text) {
  return (text || "")
    .split(/[^0-9]+/g)
    .map(x => x.trim())
    .filter(Boolean)
    .map(x => parseInt(x, 10))
    .filter(n => Number.isFinite(n) && n > 0);
}

function getSelectedAccounts() {
  const sel = $("accountsSelect");
  return Array.from(sel.selectedOptions).map(o => ({
    id: parseInt(o.value, 10),
    account_code: o.dataset.acct || "",
    name: o.dataset.name || "",
    label: o.textContent || ""
  }));
}

function resolveProviderAccount(selectedAccount) {
  const fromDb = (selectedAccount && selectedAccount.account_code) ? selectedAccount.account_code.trim() : "";
  if (fromDb) return fromDb;

  const fallback = val("providerAccountId").trim();
  if (fallback) return fallback;

  return "__DEFAULT_PROVIDER_ACCT__";
}

async function loadAccounts() {
  setText("accountsStatus", "Loading...");
  const data = await apiFetch("/of-accounts");
  const items = data.items || [];

  const sel = $("accountsSelect");
  sel.innerHTML = "";

  for (const it of items) {
    const opt = document.createElement("option");
    opt.value = String(it.id);
    opt.dataset.acct = it.account_code || "";
    opt.dataset.name = it.name || "";
    opt.textContent = `${it.id} — ${it.name} (${it.account_code})`;
    sel.appendChild(opt);
  }

  if (sel.options.length && sel.selectedOptions.length === 0) {
    sel.options[0].selected = true;
  }

  const accs = getSelectedAccounts();
  if (accs.length) {
    $("ofAccountId").value = accs[0].id;
  }

  setText("accountsStatus", "Loaded: " + items.length);
}

async function createAccount() {
  const name = val("accName").trim();
  const account_code = val("accCode").trim();
  const is_active = val("accActive") === "true";

  if (!name || !account_code) {
    return alert("Fill name, account_code");
  }

  setText("accountsStatus", "Creating...");
  await apiFetch("/of-accounts", {
    method: "POST",
    body: JSON.stringify({ name, account_code, is_active })
  });
  await loadAccounts();
  setText("accountsStatus", "Created");
}

async function deleteSelectedAccounts() {
  const accs = getSelectedAccounts();
  if (!accs.length) return alert("No accounts selected");

  for (const a of accs) {
    // 1) пробуем обычное удаление
    try {
      await apiFetch("/of-accounts/" + a.id, { method: "DELETE" });
      continue;
    } catch (e) {
      // apiFetch кидает Error(string). Пытаемся распарсить JSON из сообщения.
      let payload = null;
      try { payload = JSON.parse(String(e)); } catch (_) {}

      // FastAPI обычно возвращает {"detail": {...}}
      const detail = payload && payload.detail ? payload.detail : null;

      if (detail && detail.will_delete) {
        const d = detail.will_delete;
        const lines = [
          `Account: ${detail.account_id} — ${detail.account_code || ""}`,
          ``,
          `We will delete related records:`,
          `- operator_account_access: ${d.operator_account_access}`,
          `- audience_lists: ${d.audience_lists}`,
          `- audience_list_members: ${d.audience_list_members}`,
          `- campaigns: ${d.campaigns}`,
          `- campaign_runs: ${d.campaign_runs}`,
          ``,
          `TOTAL: ${d.total}`,
          ``,
          `Proceed with FORCE DELETE (cleanup DB)?`
        ];

        const ok = confirm(lines.join("\n"));
        if (!ok) continue;

        // 2) подтверждено — force delete
        await apiFetch("/of-accounts/" + a.id + "?force=true", { method: "DELETE" });
        continue;
      }

      // если ошибка не про зависимости — показываем как есть и выходим
      alert("Delete failed for account_id=" + a.id + "\n\n" + String(e));
    }
  }

  await loadAccounts();
  setText("accountsStatus", "Delete finished");
}

function rebuildAudienceSelect(builtin, custom) {
  const sel = $("audienceSelect");
  sel.innerHTML = "";

  for (const b of builtin) {
    const opt = document.createElement("option");
    opt.value = "builtin:" + b.key;
    opt.textContent = "Builtin: " + b.label;
    sel.appendChild(opt);
  }

  const optDirect = document.createElement("option");
  optDirect.value = "direct";
  optDirect.textContent = "Direct: userIds (manual)";
  sel.appendChild(optDirect);

  for (const c of custom) {
    const opt = document.createElement("option");
    opt.value = "custom:" + c.id;
    opt.textContent = "Custom: " + c.name + " (" + c.count + ")";
    sel.appendChild(opt);
  }

  sel.onchange = () => {
    $("recentBox").style.display = (sel.value === "builtin:recent") ? "block" : "none";
  };
  sel.onchange();
}

function rebuildCustomLists(custom) {
  const sel = $("customListSelect");
  sel.innerHTML = "";
  for (const c of custom) {
    const opt = document.createElement("option");
    opt.value = String(c.id);
    opt.textContent = c.name + " (" + c.count + ")";
    sel.appendChild(opt);
  }
}

async function loadAudiences() {
  setText("audiencesStatus", "Loading...");

  const accs = getSelectedAccounts();
  if (accs.length) {
    $("ofAccountId").value = accs[0].id;
  }

  const ofId = parseInt(val("ofAccountId"), 10);
  if (!ofId) {
    setText("audiencesStatus", "No of_account_id");
    return;
  }

  const data = await apiFetch("/audiences/" + ofId);
  rebuildAudienceSelect(data.builtin, data.custom);
  rebuildCustomLists(data.custom);

  setText("audiencesStatus", "Loaded. Builtin: " + data.builtin.length + ", custom: " + data.custom.length);
}

async function createList() {
  const ofId = parseInt(val("ofAccountId"), 10);
  const name = val("newListName").trim();
  if (!ofId) return alert("No of_account_id");
  if (!name) return alert("List name is empty");

  setText("membersStatus", "Creating...");
  await apiFetch("/audiences/" + ofId + "/custom", {
    method: "POST",
    body: JSON.stringify({ name })
  });
  await loadAudiences();
  setText("membersStatus", "Created");
}

async function loadMembers() {
  const listId = val("customListSelect");
  if (!listId) return alert("No custom list selected");

  setText("membersStatus", "Loading members...");
  const data = await apiFetch("/audiences/custom/" + listId + "/members");
  const items = data.items || [];

  let html = "<table><tr><th>ID</th><th>provider_user_id</th><th></th></tr>";
  for (const it of items) {
    html += `<tr>
      <td>${it.id}</td>
      <td>${it.provider_user_id}</td>
      <td><button onclick="deleteMember(${listId}, ${it.id})">Delete</button></td>
    </tr>`;
  }
  html += "</table>";
  setHtml("membersTable", html);

  setText("membersStatus", "Members: " + items.length);
}
async function addMembers() {
  const listId = val("customListSelect");
  if (!listId) return alert("No custom list selected");

  const ids = parseIds(val("membersInput"));
  if (!ids.length) return alert("No IDs parsed");

  setText("membersStatus", "Adding...");

  const data = await apiFetch("/audiences/custom/" + listId + "/members", {
    method: "POST",
    body: JSON.stringify({ provider_user_ids: ids })
  });

  var created = 0;
  if (data && data.created !== undefined && data.created !== null) created = data.created;

  setText("membersStatus", "Added: " + created);
  await loadAudiences();
  await loadMembers();
}

async function deleteMember(listId, memberId) {
  if (!confirm("Delete member " + memberId + "?")) return;
  setText("membersStatus", "Deleting...");
  await apiFetch(`/audiences/custom/${listId}/members/${memberId}`, { method: "DELETE" });
  await loadAudiences();
  await loadMembers();
}

async function sendMessage() {
  const accs = getSelectedAccounts();
  if (!accs.length) return alert("No accounts selected");

  const text = val("messageText").trim();
  if (!text) return alert("Message text is empty");

  const sel = val("audienceSelect");
  let audience = null;

  if (sel === "direct") {
    const manual = prompt("Enter userIds (comma/space/newline):", "123,456");
    const ids = parseIds(manual || "");
    if (!ids.length) return alert("No userIds provided");
    audience = { type: "direct", user_ids: ids };
  } else if (sel.startsWith("builtin:")) {
    const key = sel.split(":")[1];
    audience = { type: key };
    if (key === "recent") {
      const s = val("recentStart").trim();
      const e = val("recentEnd").trim();
      if (s) audience.start_date = s;
      if (e) audience.end_date = e;
    }
  } else if (sel.startsWith("custom:")) {
    const id = parseInt(sel.split(":")[1], 10);
    audience = { type: "custom", custom_list_id: id };
  } else {
    return alert("Unknown audience selection");
  }

  if (audience.type === "custom" && accs.length > 1) {
    return alert("Custom audience можно отправлять только для 1 аккаунта.");
  }

  setText("sendStatus", "Sending...");
  setText("sendResult", "");

  try {
    const results = [];
    for (const a of accs) {
      const providerAccountId = resolveProviderAccount(a);
      if (!providerAccountId) throw new Error("provider account_id is empty");

      const data = await apiFetch("/provider/" + encodeURIComponent(providerAccountId) + "/send", {
        method: "POST",
        body: JSON.stringify({ text, audience })
      });
      results.push({ account: providerAccountId, result: data });
    }

    setText("sendStatus", "OK (" + results.length + ")");
    setText("sendResult", JSON.stringify(results, null, 2));
  } catch (e) {
    setText("sendStatus", "ERROR");
    setText("sendResult", String(e));
  }
}

async function loadQueue() {
  const accs = getSelectedAccounts();
  if (!accs.length) return alert("No accounts selected");

  const providerAccountId = resolveProviderAccount(accs[0]);
  if (!providerAccountId) return alert("provider account_id is empty");

  setText("queueStatus", "Loading...");
  setText("queueResult", "");

  try {
    const data = await apiFetch("/provider/" + encodeURIComponent(providerAccountId) + "/queue");
    setText("queueStatus", "OK");
    setText("queueResult", JSON.stringify(data, null, 2));
  } catch (e) {
    setText("queueStatus", "ERROR");
    setText("queueResult", String(e));
  }
}

async function loadQueueItem() {
  const accs = getSelectedAccounts();
  if (!accs.length) return alert("No accounts selected");

  const providerAccountId = resolveProviderAccount(accs[0]);
  const qid = parseInt(val("queueId"), 10);
  if (!qid) return alert("queue_id is empty");

  setText("queueItemResult", "");
  const data = await apiFetch("/provider/" + encodeURIComponent(providerAccountId) + "/queue/" + qid);
  setText("queueItemResult", JSON.stringify(data, null, 2));
}

async function loadOverview() {
  const accs = getSelectedAccounts();
  if (!accs.length) return alert("No accounts selected");

  const providerAccountId = resolveProviderAccount(accs[0]);
  const start_date = val("ovStart").trim() || null;
  const end_date = val("ovEnd").trim() || null;
  const limit = parseInt(val("ovLimit"), 10) || 10;
  const offset = parseInt(val("ovOffset"), 10) || 0;
  const query = val("ovQuery").trim() || null;

  const qs = new URLSearchParams();
  if (start_date) qs.set("start_date", start_date);
  if (end_date) qs.set("end_date", end_date);
  qs.set("limit", String(limit));
  qs.set("offset", String(offset));
  if (query) qs.set("query", query);

  setText("overviewStatus", "Loading...");
  setText("overviewResult", "");

  try {
    const data = await apiFetch("/provider/" + encodeURIComponent(providerAccountId) + "/overview?" + qs.toString());
    setText("overviewStatus", "OK");
    setText("overviewResult", JSON.stringify(data, null, 2));
  } catch (e) {
    setText("overviewStatus", "ERROR");
    setText("overviewResult", String(e));
  }
}

window.addEventListener("load", async () => {
  showPage("pageAccounts");
  try {
    await loadAccounts();
    await loadAudiences();
  } catch(e) {}
});
</script>
</body>
</html>
""".replace("__DEFAULT_PROVIDER_ACCT__", default_provider_acct)

    return HTMLResponse(html)