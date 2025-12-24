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
    if (accs.length) $("ofAccountId").value = accs[0].id;

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

function _buildForceDeleteConfirm(detail) {
    const d = detail.will_delete || {};
    const lines = [
        `Account: ${detail.account_id} — ${detail.account_code || ""}`,
        ``,
        `We will delete related records in OUR DB:`,
        `- operator_account_access: ${d.operator_account_access ?? 0}`,
        `- audience_lists: ${d.audience_lists ?? 0}`,
        `- audience_list_members: ${d.audience_list_members ?? 0}`,
        `- campaigns: ${d.campaigns ?? 0}`,
        `- campaign_runs: ${d.campaign_runs ?? 0}`,
        ``,
        `TOTAL: ${d.total ?? 0}`,
        ``,
        `Proceed with FORCE DELETE (cleanup DB)?`
    ];
    return lines.join("\n");
}

export async function deleteSelectedAccounts() {
    const accs = getSelectedAccounts();
    if (!accs.length) return alert("No accounts selected");

    const msg =
        "Delete selected accounts?\n\n" +
        accs.map(a => `${a.id} — ${a.account_code || ""}`).join("\n");

    if (!confirm(msg)) return;

    setText("accountsStatus", "Deleting...");

    let okCount = 0;
    let errCount = 0;

    for (const a of accs) {
        try {
            await apiFetch("/of-accounts/" + a.id, { method: "DELETE" });
            okCount++;
            continue;
        } catch (e) {
            const data = e && e.data ? e.data : null;
            const detail = data && data.detail ? data.detail : null;

            if (e.status === 409 && detail && detail.will_delete) {
                const ok = confirm(_buildForceDeleteConfirm(detail));
                if (!ok) continue;

                try {
                    await apiFetch("/of-accounts/" + a.id + "?force=true", { method: "DELETE" });
                    okCount++;
                    continue;
                } catch (e2) {
                    errCount++;
                    alert("Force delete failed for account_id=" + a.id + "\n\n" + JSON.stringify(e2.data || e2, null, 2));
                    continue;
                }
            }

            errCount++;
            alert("Delete failed for account_id=" + a.id + "\n\n" + JSON.stringify(data || e, null, 2));
        }
    }

    await loadAccounts();
    setText("accountsStatus", `Delete done. OK: ${okCount}, ERR: ${errCount}`);
}