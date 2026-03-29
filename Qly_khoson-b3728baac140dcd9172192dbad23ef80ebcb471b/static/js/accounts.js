document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("createAccountModal");
  const accountForm = document.getElementById("accountModalForm");
  const formTitle = document.getElementById("modalTitle");
  const fullNameInput = document.getElementById("modalFullName");
  const usernameInput = document.getElementById("modalUsername");
  const passwordInput = document.getElementById("modalPassword");
  const roleInput = document.getElementById("modalRole");
  const closeBtn = document.getElementById("closeModal");
  const nextInput = accountForm?.querySelector('[name="next"]');
  const createBtn = document.getElementById("openModal");
  const createUrl = accountForm?.dataset.createUrl;
  const editUrlTemplate = accountForm?.dataset.editUrlTemplate;

  if (!modal || !accountForm) {
    return;
  }

  const currentLocation = () => window.location.pathname + window.location.search;

  const showModal = () => {
    if (nextInput) {
      nextInput.value = currentLocation();
    }
    modal.classList.remove("hidden");
    modal.classList.add("flex");
  };

  const hideModal = () => {
    modal.classList.remove("flex");
    modal.classList.add("hidden");
  };

  const resetForm = () => {
    fullNameInput.value = "";
    usernameInput.value = "";
    passwordInput.value = "";
    roleInput.value = "Admin";
  };

  if (createBtn) {
    createBtn.addEventListener("click", () => {
      formTitle.innerText = "Tạo tài khoản";
      accountForm.action = createUrl || accountForm.action;
      resetForm();
      showModal();
    });
  }

  if (closeBtn) {
    closeBtn.addEventListener("click", hideModal);
  }

  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      hideModal();
    }
  });

  document.querySelectorAll(".editBtn").forEach((button) => {
    button.addEventListener("click", (event) => {
      const row = event.currentTarget.closest("tr");
      if (!row) {
        return;
      }
      const accountId = row.dataset.accountId;
      const editUrl = editUrlTemplate ? editUrlTemplate.replace("{id}", accountId) : accountForm.action;
      formTitle.innerText = "Chỉnh sửa tài khoản";
      accountForm.action = editUrl;
      fullNameInput.value =
        row.dataset.fullName || row.querySelector("td:nth-child(2)")?.innerText.trim() || "";
      usernameInput.value = row.dataset.username || "";
      passwordInput.value = "";
      roleInput.value = row.dataset.role || "Admin";
      showModal();
    });
  });

  document.querySelectorAll(".account-delete-form").forEach((form) => {
    form.addEventListener("submit", (event) => {
      const accountName = form.dataset.accountName || "tài khoản";
      const shouldDelete = window.confirm(`Bạn có chắc chắn muốn xóa ${accountName}?`);
      if (!shouldDelete) {
        event.preventDefault();
      }
    });
  });
});
