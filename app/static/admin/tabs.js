// frontend/app/static/admin/tabs.js
import { $ } from "./api.js";

export function showPage(pageId) {
    for (const el of document.querySelectorAll(".page")) el.classList.remove("active");
    $(pageId).classList.add("active");

    for (const btn of document.querySelectorAll(".tabbtn")) {
        btn.classList.toggle("active", btn.dataset.page === pageId);
    }
}