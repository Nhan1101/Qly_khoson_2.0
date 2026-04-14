document.addEventListener("DOMContentLoaded", () => {
  const groups = document.querySelectorAll("[data-collapsible]");

  groups.forEach((group) => {
    const title = group.querySelector(".menu-title");
    if (!title) {
      return;
    }

    title.addEventListener("click", () => {
      group.classList.toggle("is-open");
    });
  });
});
