// frontend/app/static/admin/accounts.js
import { $, val, setText, apiFetch, getSelectedAccounts } from "./api.js";

export function syncSelectedAccountFields() {
    const sel = $("accountsSelect");
    const opt = sel && sel.selectedOptions && sel.selectedOptions[0] ? sel.selectedOptions[0] : null;
    if (!opt) return;

    const id = parseInt(opt.value, 10);
    const acct = (opt.dataset.acct || "").trim();

    const ofId = $("ofAccountId");
    if (ofId) ofId.value = String(id);

    const prov = $("providerAccountId");
    if (prov) prov.value = acct;
}

export async function loadAccounts() {
    setText("accountsStatus", "Loading...");
    const data = await apiFetch("/of-accounts");
    const items = data.items || [];

    const sel = $("accountsSelect");
    const prev = sel && sel.value ? String(sel.value) : "";

    sel.innerHTML = "";

    for (const it of items) {
        const opt = document.createElement("option");
        opt.value = String(it.id);
        opt.dataset.acct = it.account_code || "";
        opt.dataset.name = it.name || "";
        opt.dataset.active = String(!!it.is_active);

        // ✅ to see activity
        opt.disabled = !it.is_active;

        const activeSuffix = it.is_active ? "" : " (inactive)";
        opt.textContent = `${it.id} — ${it.name} (${it.account_code})${activeSuffix}`;

        sel.appendChild(opt);
    }

    // ✅ Восстановить предыдущий выбор если он ещё есть,
    // иначе выбрать первый active, иначе первый
    if (sel.options.length) {
        let idx = -1;

        if (prev) {
            for (let i = 0; i < sel.options.length; i++) {
                if (String(sel.options[i].value) === prev) { idx = i; break; }
            }
        }

        if (idx < 0) {
            for (let i = 0; i < sel.options.length; i++) {
                if (sel.options[i].dataset.active === "true") { idx = i; break; }
            }
        }

        if (idx < 0) idx = 0;
        sel.selectedIndex = idx;
    }

    syncSelectedAccountFields();
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
    const accs = getSelectedAccounts(); // теперь вернёт 1 выбранный
    if (!accs.length) return alert("No account selected");

    const a = accs[0];

    const msg =
        "Delete account?\n\n" +
        `${a.id} — ${a.account_code || ""}`;

    if (!confirm(msg)) return;

    setText("accountsStatus", "Deleting...");

    try {
        await apiFetch("/of-accounts/" + a.id, { method: "DELETE" });
        await loadAccounts();
        setText("accountsStatus", "Deleted");
        return;
    } catch (e) {
        const data = e && e.data ? e.data : null;
        const detail = data && data.detail ? data.detail : null;

        if (e.status === 409 && detail && detail.will_delete) {
            const ok = confirm(_buildForceDeleteConfirm(detail));
            if (!ok) return;

            try {
                await apiFetch("/of-accounts/" + a.id + "?force=true", { method: "DELETE" });
                await loadAccounts();
                setText("accountsStatus", "Force deleted");
                return;
            } catch (e2) {
                alert("Force delete failed\n\n" + JSON.stringify(e2.data || e2, null, 2));
                setText("accountsStatus", "Force delete failed");
                return;
            }
        }

        alert("Delete failed\n\n" + JSON.stringify(data || e, null, 2));
        setText("accountsStatus", "Delete failed");
    }
}