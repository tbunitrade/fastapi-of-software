// frontend/app/static/admin/send.js
import { val, setText, apiFetch, getSelectedAccounts, resolveProviderAccount } from "./api.js";

export async function loadQueue() {
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

export async function loadQueueItem() {
    const accs = getSelectedAccounts();
    if (!accs.length) return alert("No accounts selected");

    const providerAccountId = resolveProviderAccount(accs[0]);
    const qid = parseInt(val("queueId"), 10);
    if (!qid) return alert("queue_id is empty");

    setText("queueItemResult", "");
    const data = await apiFetch("/provider/" + encodeURIComponent(providerAccountId) + "/queue/" + qid);
    setText("queueItemResult", JSON.stringify(data, null, 2));
}