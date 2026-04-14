if (typeof productCatalogRows === 'undefined') {
  var productCatalogRows = [];
}

document.addEventListener("DOMContentLoaded", () => {
  const tableBody = document.getElementById("product-catalog-table-body");
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
});
