// frontend/app/static/admin/audiences.js
import { $, val, setText, setHtml, apiFetch, parseIds, getSelectedAccounts } from "./api.js";

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

export async function loadAudiences() {
    setText("audiencesStatus", "Loading...");

    const accs = getSelectedAccounts();
    if (accs.length) $("ofAccountId").value = accs[0].id;

    const ofId = parseInt(val("ofAccountId"), 10);
    if (!ofId) { setText("audiencesStatus", "No of_account_id"); return; }

    const data = await apiFetch("/audiences/" + ofId);
    rebuildAudienceSelect(data.builtin, data.custom);
    rebuildCustomLists(data.custom);

    setText("audiencesStatus", "Loaded. Builtin: " + data.builtin.length + ", custom: " + data.custom.length);
}

export async function createList() {
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

export async function loadMembers() {
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

export async function addMembers() {
    const listId = val("customListSelect");
    if (!listId) return alert("No custom list selected");

    const ids = parseIds(val("membersInput"));
    if (!ids.length) return alert("No IDs parsed");

    setText("membersStatus", "Adding...");
    const data = await apiFetch("/audiences/custom/" + listId + "/members", {
        method: "POST",
        body: JSON.stringify({ provider_user_ids: ids })
    });

    const created = (data && data.created != null) ? data.created : 0;
    setText("membersStatus", "Added: " + created);

    await loadAudiences();
    await loadMembers();
}

export async function deleteMember(listId, memberId) {
    if (!confirm("Delete member " + memberId + "?")) return;
    setText("membersStatus", "Deleting...");
    await apiFetch(`/audiences/custom/${listId}/members/${memberId}`, { method: "DELETE" });
    await loadAudiences();
    await loadMembers();
}