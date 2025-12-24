// frontend/app/static/admin/tabs.js
export function showPage(pageId) {
    for (const el of document.querySelectorAll(".page")) el.classList.remove("active");
    const page = document.getElementById(pageId);
    if (page) page.classList.add("active");

    for (const btn of document.querySelectorAll(".tabbtn")) {
        btn.classList.toggle("active", btn.dataset.page === pageId);
    }
}