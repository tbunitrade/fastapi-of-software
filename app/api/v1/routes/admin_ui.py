# backend/app/api/v1/routes/admin_ui.py
from __future__ import annotations

from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from app.core.config import settings

router = APIRouter()

@router.get("/admin", response_class=HTMLResponse)
def admin_ui():
    default_provider_acct = settings.PROVIDER_CLIENT_ID or ""

    html = r"""
<!doctype html>
<html>
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1"/>
  <title>API Admin UI</title>
  <link rel="stylesheet" href="/static/admin/admin.css" />
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
      <div><button onclick="loadAccounts()">Load Accounts</button></div>
      <div><button onclick="deleteSelectedAccounts()">Delete Selected</button></div>
    </div>

    <hr class="sep" />

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
      <div><button onclick="createAccount()">Create</button></div>
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
      <div><button onclick="loadAudiences()">Load Audiences</button></div>
      <div id="audiencesStatus" class="muted"></div>
    </div>

    <hr class="sep" />

    <h4>Custom Lists</h4>

    <div class="row">
      <div>
        <label>Create new custom list</label>
        <input id="newListName" placeholder="VIP LA Fans" style="width:320px" />
      </div>
      <div><button onclick="createList()">Create</button></div>
    </div>

    <div class="row" style="margin-top:12px;">
      <div style="min-width:320px;">
        <label>Pick custom list</label>
        <select id="customListSelect" style="width:320px"></select>
      </div>
      <div><button onclick="loadMembers()">Load Members</button></div>
      <div id="membersStatus" class="muted"></div>
    </div>

    <div style="margin-top:10px;">
      <label>Add members (provider_user_id). One per line / comma / space.</label>
      <textarea id="membersInput" placeholder="123\\n456\\n789"></textarea>
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
      <div><button onclick="loadQueue()">Load Queue for selected account</button></div>
      <div class="muted" id="queueStatus"></div>
    </div>

    <div class="mono" id="queueResult" style="margin-top:10px;"></div>

    <hr class="sep" />

    <div class="row">
      <div>
        <label>queue_id</label>
        <input id="queueId" type="number" placeholder="123" style="width:240px" />
      </div>
      <div><button onclick="loadQueueItem()">Get queue item</button></div>
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
      <div><button onclick="loadOverview()">Load Overview</button></div>
      <div class="muted" id="overviewStatus"></div>
    </div>

    <div class="mono" id="overviewResult" style="margin-top:10px;"></div>
  </div>

  <script>
    window.__DEFAULT_PROVIDER_ACCT__ = "__DEFAULT_PROVIDER_ACCT__";
  </script>

  <script src="/static/admin/api.js"></script>
  <script src="/static/admin/tabs.js"></script>
  <script src="/static/admin/accounts.js"></script>
  <script src="/static/admin/audiences.js"></script>
  <script src="/static/admin/send.js"></script>
  <script src="/static/admin/queue.js"></script>
  <script src="/static/admin/overview.js"></script>
  <script src="/static/admin/admin.js"></script>
</body>
</html>
""".replace("__DEFAULT_PROVIDER_ACCT__", default_provider_acct)

    return HTMLResponse(html)