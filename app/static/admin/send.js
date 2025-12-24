// frontend/app/static/admin/send.js
import { val, setText, apiFetch, parseIds, getSelectedAccounts, resolveProviderAccount } from "./api.js";

export async function sendMessage() {
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