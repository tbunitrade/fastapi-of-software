// frontend/app/static/admin/overview.js
import { val, setText, apiFetch, getSelectedAccounts, resolveProviderAccount } from "./api.js";

export async function loadOverview() {
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
        setText("overviewResult", JSON.stringify(e.data || e, null, 2));
    }
}