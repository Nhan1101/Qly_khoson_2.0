document.addEventListener("DOMContentLoaded", () => {
  const page = document.querySelector(".order-edit-page");
  const listUrl = page?.dataset.listUrl || "#";
  const tbody = document.getElementById("order-edit-table-body");
  const btnAdd = document.querySelector(".order-edit-btn-add");
  const totalEl = document.getElementById("order-edit-total");
  const saveBtn = document.querySelector(".order-edit-save-btn");
  const closeBtn = document.querySelector(".order-edit-close");
  let rowCount = 0;

  const productCatalogRows = window.productsJson || [];
  const existingDetails = window.existingDetailsJson || [];

  const formatNumber = (value) => value.toLocaleString("vi-VN");

  const calculateTotal = () => {
    let grandTotal = 0;
    tbody.querySelectorAll("tr").forEach(tr => {
      const priceStr = tr.querySelector(".product-price").value.replace(/\./g, '').replace(/,/g, '');
      const price = Number(priceStr) || 0;
      const qty = Number(tr.querySelector(".product-qty").value) || 0;
      const lineTotal = price * qty;
      
      const lineTotalInput = tr.querySelector(".product-total");
      if (lineTotalInput) {
        lineTotalInput.value = lineTotal > 0 ? formatNumber(lineTotal) : "0";
      }
      grandTotal += lineTotal;
    });

    if (totalEl) {
      totalEl.textContent = grandTotal > 0 ? `${formatNumber(grandTotal)} đ` : "0 đ";
    }
  };

  const addRow = (initialProductId = "", initialQty = 1) => {
    rowCount++;
    const tr = document.createElement("tr");
    
    let options = productCatalogRows.map(p => {
      const selected = parseInt(p.id) === parseInt(initialProductId) ? "selected" : "";
      return `<option value="${p.id}" data-ma="${p.ma || ''}" data-dvt="${p.dvt || ''}" data-gia="${p.gia || 0}" ${selected}>${p.ten}</option>`;
    }).join("");

    tr.innerHTML = `
      <td style="text-align: center; color: #4b5563;">${rowCount}</td>
      <td>
        <select name="product_ids" class="order-edit-row-input text-left product-select">
          <option value="">Chọn hàng hóa...</option>
          ${options}
        </select>
      </td>
      <td><input type="text" class="order-edit-row-input product-code" readonly></td>
      <td><input type="text" class="order-edit-row-input product-unit" readonly></td>
      <td><input type="text" class="order-edit-row-input product-price" readonly></td>
      <td><input name="quantities" type="number" class="order-edit-row-input product-qty" min="1" value="${initialQty}"></td>
      <td><input type="text" class="order-edit-row-input product-total" placeholder="Thành tiền" readonly></td>
      <td style="text-align: center;">
        <button class="order-edit-delete-btn" type="button">
          <i class="fa-solid fa-trash-can"></i>
        </button>
      </td>
    `;
    tbody.appendChild(tr);

    const select = tr.querySelector(".product-select");
    const updateRowFromSelect = () => {
      const option = select.options[select.selectedIndex];
      if(option && option.value) {
        tr.querySelector(".product-code").value = option.dataset.ma || "";
        tr.querySelector(".product-unit").value = option.dataset.dvt || "";
        tr.querySelector(".product-price").value = option.dataset.gia ? formatNumber(Number(option.dataset.gia)) : "0";
      } else {
        tr.querySelector(".product-code").value = "";
        tr.querySelector(".product-unit").value = "";
        tr.querySelector(".product-price").value = "";
      }
      calculateTotal();
    };

    select.addEventListener("change", updateRowFromSelect);

    tr.querySelector(".product-qty").addEventListener("input", calculateTotal);

    tr.querySelector(".order-edit-delete-btn").addEventListener("click", () => {
      tr.remove();
      updateRowNumbers();
      calculateTotal();
    });

    if(initialProductId) {
      updateRowFromSelect();
    }
  };

  const updateRowNumbers = () => {
    rowCount = 0;
    tbody.querySelectorAll("tr").forEach(tr => {
      rowCount++;
      tr.querySelector("td").textContent = rowCount;
    });
  };

  // Populate initial rows
  if (existingDetails.length > 0) {
    existingDetails.forEach(detail => {
      addRow(detail.product_id, detail.so_luong);
    });
  }

  btnAdd?.addEventListener("click", () => addRow());
  
  // Removed `saveBtn.addEventListener("click")`, let the form submit natively.
});
