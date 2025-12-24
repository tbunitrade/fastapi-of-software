// frontend/app/static/admin/api.js
export const API = "/api/v1";

export function $(id) { return document.getElementById(id); }
export function val(id) { return $(id).value; }
export function setText(id, text) { $(id).textContent = text; }
export function setHtml(id, html) { $(id).innerHTML = html; }

export async function apiFetch(path, opts = {}) {
    const res = await fetch(API + path, {
        headers: { "Content-Type": "application/json", ...(opts.headers || {}) },
        ...opts
    });

    const txt = await res.text();
    let data = null;
    try { data = JSON.parse(txt); } catch (_) { data = txt; }

    if (!res.ok) {
        const err = new Error("API_ERROR");
        err.status = res.status;
        err.data = data;
        throw err;
    }
    return data;
}

export function parseIds(text) {
    return (text || "")
        .split(/[^0-9]+/g)
        .map(x => x.trim())
        .filter(Boolean)
        .map(x => parseInt(x, 10))
        .filter(n => Number.isFinite(n) && n > 0);
}

export function getSelectedAccounts() {
    const sel = $("accountsSelect");
    const o = sel && sel.selectedOptions && sel.selectedOptions[0] ? sel.selectedOptions[0] : null;
    if (!o) return [];
    return [{
        id: parseInt(o.value, 10),
        account_code: o.dataset.acct || "",
        name: o.dataset.name || "",
        label: o.textContent || ""
    }];
}
export function resolveProviderAccount(selectedAccount) {
    const fromDb = (selectedAccount && selectedAccount.account_code) ? selectedAccount.account_code.trim() : "";
    if (fromDb) return fromDb;

    const fallback = (document.getElementById("providerAccountId")?.value || "").trim();
    if (fallback) return fallback;

    return (window.__DEFAULT_PROVIDER_ACCT__ || "").trim();
}