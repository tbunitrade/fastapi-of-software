// frontend/app/static/admin/admin.js
import { showPage } from "./tabs.js";
import { loadAccounts, createAccount, deleteSelectedAccounts } from "./accounts.js";
import { loadAudiences, createList, loadMembers, addMembers, deleteMember } from "./audiences.js";
import { sendMessage } from "./send.js";
import { loadQueue, loadQueueItem } from "./queue.js";
import { loadOverview } from "./overview.js";
import { $ } from "./api.js";

// делаем функции доступными для onclick=""
window.showPage = showPage;

window.loadAccounts = loadAccounts;
window.createAccount = createAccount;
window.deleteSelectedAccounts = deleteSelectedAccounts;

window.loadAudiences = loadAudiences;
window.createList = createList;
window.loadMembers = loadMembers;
window.addMembers = addMembers;
window.deleteMember = deleteMember;

window.sendMessage = sendMessage;

window.loadQueue = loadQueue;
window.loadQueueItem = loadQueueItem;

window.loadOverview = loadOverview;

window.addEventListener("load", async () => {
    // заполним fallback providerAccountId
    const def = (window.__DEFAULT_PROVIDER_ACCT__ || "").trim();
    if (def && $("providerAccountId") && !$("providerAccountId").value) {
        $("providerAccountId").value = def;
    }

    showPage("pageAccounts");
    try {
        await loadAccounts();
        await loadAudiences();
    } catch (e) {
        // не валим UI если нет данных/авторизации
    }
});