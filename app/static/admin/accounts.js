// frontend/app/static/admin/accounts.js
import { $, val, setText, apiFetch, getSelectedAccounts } from "./api.js";

export async function loadAccounts() {
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

export async function createAccount() {
    const name = val("accName").trim();
    const account_code = val("accCode").trim();
    const is_active = val("accActive") === "true";

    if (!name || !account_code) return alert("Fill name, account_code");

    setText("accountsStatus", "Creating...");
    await apiFetch("/of-accounts", {
        method: "POST",
        body: JSON.stringify({ name, account_code, is_active })
    });
    await loadAccounts();
    setText("accountsStatus", "Created");
}

export async function deleteSelectedAccounts() {
    const accs = getSelectedAccounts();
    if (!accs.length) return alert("No accounts selected");

    for (const a of accs) {
        try {
            await apiFetch("/of-accounts/" + a.id, { method: "DELETE" });
            continue;
        } catch (e) {
            // здесь ожидаем, что бэк позже начнёт отдавать detail.will_delete
            // пока — просто показываем ошибку
            alert("Delete failed for account_id=" + a.id + "\n\n" + String(e));
        }
    }

    await loadAccounts();
    setText("accountsStatus", "Delete finished");
}