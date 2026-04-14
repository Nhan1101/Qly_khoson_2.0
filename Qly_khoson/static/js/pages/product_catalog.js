if (typeof productCatalogRows === 'undefined') {
  var productCatalogRows = [];
}

document.addEventListener("DOMContentLoaded", () => {
  const tableBody = document.getElementById("product-catalog-table-body");
  const openCreateBtn = document.querySelector(".product-actions .product-create-btn");
  const productModal = document.getElementById("productModal");
  const closeProductBtn = document.querySelector(".product-modal-close");
  const productForm = document.getElementById("productCreateForm");

  if (!tableBody) {
    return;
  }

  tableBody.innerHTML = productCatalogRows.map((row) => `
    <tr>
      <td>${row.stt}</td>
      <td class="product-name-cell">${row.ten}</td>
      <td>${row.ma}</td>
      <td>${row.loai}</td>
      <td>${row.dvt}</td>
      <td>${row.ton}</td>
      <td class="product-money-cell">${row.giaBan}</td>
      <td class="product-money-cell">${row.giaVon}</td>
      <td>
        <div class="product-actions-cell">
          <button class="product-icon-btn edit" type="button" title="Chỉnh sửa" aria-label="Chỉnh sửa">
            <i class="fa-solid fa-pen"></i>
          </button>
          <button class="product-icon-btn delete" type="button" title="Xóa" aria-label="Xóa">
            <i class="fa-solid fa-trash"></i>
          </button>
        </div>
      </td>
    </tr>
  `).join("");

  if (openCreateBtn) {
    openCreateBtn.addEventListener("click", () => {
      openProductModal();
    });
  }

  if (closeProductBtn) {
    closeProductBtn.addEventListener("click", () => {
      closeProductModal();
    });
  }

  if (productModal) {
    productModal.addEventListener("click", (event) => {
      if (event.target === productModal) {
        closeProductModal();
      }
    });
  }

  if (productForm) {
    productForm.addEventListener("submit", (event) => {
      event.preventDefault();
      productForm.submit();
    });
  }
});

function openProductModal() {
  const productModal = document.getElementById("productModal");
  if (!productModal) {
    return;
  }
  const productModalTitle = document.getElementById("productModalTitle");
  const productForm = document.getElementById("productCreateForm");

  productModalTitle.textContent = "Tạo sản phẩm mới";
  productForm.reset();
  productForm.action = window.location.pathname;
  productModal.style.display = "flex";
  productModal.setAttribute("aria-hidden", "false");
}

function closeProductModal() {
  const productModal = document.getElementById("productModal");
  if (!productModal) {
    return;
  }
  productModal.style.display = "none";
  productModal.setAttribute("aria-hidden", "true");
}
