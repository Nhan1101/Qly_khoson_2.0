document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("createAccountModal");
  const accountForm = document.getElementById("accountModalForm");
  const formTitle = document.getElementById("modalTitle");
  const fullNameInput = document.getElementById("modalFullName");
  const usernameInput = document.getElementById("modalUsername");
  const passwordInput = document.getElementById("modalPassword");
  const roleInput = document.getElementById("modalRole");
  const closeBtn = document.getElementById("closeModal");
  const createBtn = document.getElementById("openModal");
  const nextInput = accountForm ? accountForm.querySelector('[name="next"]') : null;
  const createUrl = accountForm ? accountForm.dataset.createUrl : "";
  const editUrlTemplate = accountForm ? accountForm.dataset.editUrlTemplate : "";

  if (!modal || !accountForm) {
    return;
  }

  const currentLocation = () => `${window.location.pathname}${window.location.search}`;

  const openModal = () => {
    if (nextInput) {
      nextInput.value = currentLocation();
    }
    modal.classList.remove("hidden");
    modal.classList.add("flex");
    modal.style.display = "flex";
  };

  const closeModal = () => {
    modal.classList.remove("flex");
    modal.classList.add("hidden");
    modal.style.display = "none";
  };

  const resetForm = () => {
    fullNameInput.value = "";
    usernameInput.value = "";
    passwordInput.value = "";
    roleInput.value = "Admin";
  };

  closeModal();

  if (createBtn) {
    createBtn.addEventListener("click", () => {
      formTitle.textContent = "Tạo tài khoản";
      accountForm.action = createUrl || accountForm.action;
      resetForm();
      openModal();
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener("click", closeModal);
  }

  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      closeModal();
    }
  });

  document.querySelectorAll(".editBtn").forEach((button) => {
    button.addEventListener("click", (event) => {
      const row = event.currentTarget.closest("tr");
      if (!row) {
        return;
      }
      const accountId = row.dataset.accountId;
      formTitle.textContent = "Chỉnh sửa tài khoản";
      accountForm.action = editUrlTemplate
        ? editUrlTemplate.replace("{id}", accountId)
        : accountForm.action;
      fullNameInput.value =
        row.dataset.fullName || row.querySelector("td:nth-child(2)")?.innerText.trim() || "";
      usernameInput.value = row.dataset.username || "";
      passwordInput.value = "";
      roleInput.value = row.dataset.role || "Admin";
      openModal();
    });
  });
});
