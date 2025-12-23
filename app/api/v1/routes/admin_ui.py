#form UI
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.core.config import settings

router = APIRouter()

@router.get("/admin", response_class=HTMLResponse)
def admin_ui():
    default_provider_acct = settings.PROVIDER_CLIENT_ID or ""
    html = f"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>OF API Admin UI</title>
  <style>
    body {{ font-family: ui-sans-serif, system-ui; margin: 20px; }}
    .row {{ display:flex; gap:12px; flex-wrap:wrap; }}
    .card {{ border:1px solid #ddd; border-radius:10px; padding:14px; margin:12px 0; }}
    label {{ display:block; font-size:12px; color:#333; margin-bottom:4px; }}
    input, select, textarea, button {{ padding:10px; border:1px solid #ccc; border-radius:8px; }}
    textarea {{ width:100%; min-height: 90px; }}
    button {{ cursor:pointer; }}
    .muted {{ color:#666; font-size:12px; }}
    .mono {{ font-family: ui-monospace, SFMono-Regular; font-size:12px; white-space:pre-wrap; }}
    .danger {{ color:#a00; }}
    .ok {{ color:#0a0; }}
    table {{ width:100%; border-collapse:collapse; }}
    td, th {{ border-bottom: 1px solid #eee; padding:6px; text-align:left; }}
  </style>
</head>
<body>
  <h2>Admin UI (HTML+JS)</h2>
  <p class="muted">Эта страница работает на твоих эндпоинтах: /api/v1/audiences/* и /api/v1/provider/*</p>

  <div class="card">
    <h3>1) Context</h3>
    <div class="row">
      <div>
        <label>Internal of_account_id (int)</label>
        <input id="ofAccountId" type="number" value="1" style="width:220px" />
        <div class="muted">ID в твоей БД (таблица of_accounts). Пока вводим вручную.</div>
      </div>
      <div>
        <label>Provider account_id (acct_...)</label>
        <input id="providerAccountId" value="{default_provider_acct}" style="width:420px" />
        <div class="muted">Если пусто — берётся из .env (PROVIDER_CLIENT_ID) в бекенде.</div>
      </div>
      <div style="align-self:end;">
        <button onclick="loadAudiences()">Load Audiences</button>
      </div>
    </div>
    <div id="audiencesStatus" class="muted" style="margin-top:10px;"></div>
  </div>

  <div class="card">
    <h3>2) Send Mass Message</h3>
    <div class="row">
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

  <div class="card">
    <h3>3) Custom Lists</h3>

    <div class="row">
      <div>
        <label>Create new custom list</label>
        <input id="newListName" placeholder="VIP LA Fans" style="width:320px" />
      </div>
      <div style="align-self:end;">
        <button onclick="createList()">Create</button>
      </div>
    </div>

    <hr style="border:none;border-top:1px solid #eee;margin:14px 0;" />

    <div class="row">
      <div style="min-width:320px;">
        <label>Pick custom list</label>
        <select id="customListSelect" style="width:320px"></select>
      </div>
      <div style="align-self:end;">
        <button onclick="loadMembers()">Load Members</button>
      </div>
    </div>

    <div style="margin-top:10px;">
      <label>Add members (provider_user_id). One per line / comma / space.</label>
      <textarea id="membersInput" placeholder="123\\n456\\n789"></textarea>
      <div class="row" style="margin-top:10px;">
        <button onclick="addMembers()">Add</button>
        <div id="membersStatus" class="muted"></div>
      </div>
    </div>

    <div style="margin-top:12px;">
      <h4>Members</h4>
      <div id="membersTable"></div>
    </div>
  </div>

<script>
const API = "/api/v1";

function val(id) {{ return document.getElementById(id).value; }}
function setHtml(id, html) {{ document.getElementById(id).innerHTML = html; }}
function setText(id, text) {{ document.getElementById(id).textContent = text; }}

function parseIds(text) {{
  return text
    .split(/[^0-9]+/g)
    .map(x => x.trim())
    .filter(Boolean)
    .map(x => parseInt(x, 10))
    .filter(n => Number.isFinite(n));
}}

async function apiFetch(path, opts={{}}) {{
  const res = await fetch(API + path, {{
    headers: {{ "Content-Type": "application/json", ...(opts.headers||{{}}) }},
    ...opts
  }});
  const txt = await res.text();
  let data = null;
  try {{ data = JSON.parse(txt); }} catch(e) {{ data = txt; }}
  if (!res.ok) {{
    throw new Error(typeof data === "string" ? data : JSON.stringify(data));
  }}
  return data;
}}

function rebuildAudienceSelect(builtin, custom) {{
  const sel = document.getElementById("audienceSelect");
  sel.innerHTML = "";

  // builtin
  for (const b of builtin) {{
    const opt = document.createElement("option");
    opt.value = "builtin:" + b.key;
    opt.textContent = "Builtin: " + b.label;
    sel.appendChild(opt);
  }}

  // direct (optional)
  {{
    const opt = document.createElement("option");
    opt.value = "direct";
    opt.textContent = "Direct: userIds (manual)";
    sel.appendChild(opt);
  }}

  // custom
  for (const c of custom) {{
    const opt = document.createElement("option");
    opt.value = "custom:" + c.id;
    opt.textContent = "Custom: " + c.name + " (" + c.count + ")";
    sel.appendChild(opt);
  }}

  sel.onchange = () => {{
    const v = sel.value;
    document.getElementById("recentBox").style.display =
      v === "builtin:recent" ? "block" : "none";
  }};
  sel.onchange();
}}

function rebuildCustomLists(custom) {{
  const sel = document.getElementById("customListSelect");
  sel.innerHTML = "";
  for (const c of custom) {{
    const opt = document.createElement("option");
    opt.value = String(c.id);
    opt.textContent = c.name + " (" + c.count + ")";
    sel.appendChild(opt);
  }}
}}

async function loadAudiences() {{
  setText("audiencesStatus", "Loading...");
  const ofId = parseInt(val("ofAccountId"), 10);
  const data = await apiFetch("/audiences/" + ofId);
  rebuildAudienceSelect(data.builtin, data.custom);
  rebuildCustomLists(data.custom);
  setText("audiencesStatus", "Loaded. Builtin: " + data.builtin.length + ", custom: " + data.custom.length);
}}

async function createList() {{
  const ofId = parseInt(val("ofAccountId"), 10);
  const name = val("newListName").trim();
  if (!name) return alert("List name is empty");

  setText("membersStatus", "Creating...");
  await apiFetch("/audiences/" + ofId + "/custom", {{
    method: "POST",
    body: JSON.stringify({{ name }})
  }});

  await loadAudiences();
  setText("membersStatus", "Created");
}}

async function loadMembers() {{
  const listId = val("customListSelect");
  if (!listId) return alert("No custom list selected");
  setText("membersStatus", "Loading members...");

  const data = await apiFetch("/audiences/custom/" + listId + "/members");
  const items = data.items || [];

  let html = "<table><tr><th>ID</th><th>provider_user_id</th><th></th></tr>";
  for (const it of items) {{
    html += `<tr>
      <td>${{it.id}}</td>
      <td>${{it.provider_user_id}}</td>
      <td><button onclick="deleteMember(${{listId}}, ${{it.id}})">Delete</button></td>
    </tr>`;
  }}
  html += "</table>";
  setHtml("membersTable", html);

  setText("membersStatus", "Members: " + items.length);
}}

async function addMembers() {{
  const listId = val("customListSelect");
  if (!listId) return alert("No custom list selected");

  const ids = parseIds(val("membersInput"));
  if (!ids.length) return alert("No IDs parsed");

  setText("membersStatus", "Adding...");
  const data = await apiFetch("/audiences/custom/" + listId + "/members", {{
    method: "POST",
    body: JSON.stringify({{ provider_user_ids: ids }})
  }});
  setText("membersStatus", "Added: " + (data.created ?? 0));
  await loadAudiences();
  await loadMembers();
}}

async function deleteMember(listId, memberId) {{
  if (!confirm("Delete member " + memberId + "?")) return;
  setText("membersStatus", "Deleting...");
  await apiFetch(`/audiences/custom/${{listId}}/members/${{memberId}}`, {{ method: "DELETE" }});
  await loadAudiences();
  await loadMembers();
}}

async function sendMessage() {{
  const providerAccountId = val("providerAccountId").trim() || "{default_provider_acct}";
  if (!providerAccountId) return alert("provider account_id is empty");

  const text = val("messageText").trim();
  if (!text) return alert("Message text is empty");

  const sel = val("audienceSelect");
  let audience = null;

  if (sel === "direct") {{
    const manual = prompt("Enter userIds (comma/space/newline):", "123,456");
    const ids = parseIds(manual || "");
    if (!ids.length) return alert("No userIds provided");
    audience = {{ type: "direct", user_ids: ids }};
  }} else if (sel.startsWith("builtin:")) {{
    const key = sel.split(":")[1];
    audience = {{ type: key }};
    if (key === "recent") {{
      const s = val("recentStart").trim();
      const e = val("recentEnd").trim();
      if (s) audience.start_date = s;
      if (e) audience.end_date = e;
    }}
  }} else if (sel.startsWith("custom:")) {{
    const id = parseInt(sel.split(":")[1], 10);
    audience = {{ type: "custom", custom_list_id: id }};
  }} else {{
    return alert("Unknown audience selection");
  }}

  setText("sendStatus", "Sending...");
  setText("sendResult", "");

  try {{
    const data = await apiFetch("/provider/" + encodeURIComponent(providerAccountId) + "/send", {{
      method: "POST",
      body: JSON.stringify({{ text, audience }})
    }});
    setText("sendStatus", "OK");
    setText("sendResult", JSON.stringify(data, null, 2));
  }} catch (e) {{
    setText("sendStatus", "ERROR");
    setText("sendResult", String(e));
  }}
}}

window.addEventListener("load", () => {{
  // автозагрузка, если вбиты ID
  loadAudiences().catch(()=>{{}});
}});
</script>
</body>
</html>
"""
    return HTMLResponse(html)