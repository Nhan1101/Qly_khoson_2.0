document.addEventListener("DOMContentLoaded", () => {
  const page = document.querySelector(".order-create-page");
  const listUrl = page?.dataset.listUrl || "#";
  const tbody = document.getElementById("order-create-table-body");
  const btnAdd = document.querySelector(".order-create-btn-add");
  const totalEl = document.getElementById("order-create-total");
  const saveBtn = document.getElementById("order-create-save-btn");
  let rowCount = 0;

  const productCatalogRows = window.productsJson || [];

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

  const addRow = () => {
    rowCount++;
    const tr = document.createElement("tr");
    
    let options = productCatalogRows.map(p => 
      `<option value="${p.id}" data-ma="${p.ma || ''}" data-dvt="${p.dvt || ''}" data-gia="${p.gia || 0}">${p.ten}</option>`
    ).join("");

    tr.innerHTML = `
      <td style="text-align: center; color: #4b5563;">${rowCount}</td>
      <td>
        <select name="product_ids" class="order-create-row-input text-left product-select">
          <option value="">Chọn hàng hóa...</option>
          ${options}
        </select>
      </td>
      <td><input type="text" class="order-create-row-input product-code" readonly></td>
      <td><input type="text" class="order-create-row-input product-unit" readonly></td>
      <td><input type="text" class="order-create-row-input product-price" readonly></td>
      <td><input name="quantities" type="number" class="order-create-row-input product-qty" min="1" value="0"></td>
      <td><input type="text" class="order-create-row-input product-total" placeholder="Thành tiền" readonly></td>
      <td style="text-align: center;">
        <button class="order-create-delete-btn" type="button">
          <i class="fa-solid fa-trash-can"></i>
        </button>
      </td>
    `;
    tbody.appendChild(tr);

    const select = tr.querySelector(".product-select");
    select.addEventListener("change", (e) => {
      const option = e.target.options[e.target.selectedIndex];
      tr.querySelector(".product-code").value = option.dataset.ma || "";
      tr.querySelector(".product-unit").value = option.dataset.dvt || "";
      tr.querySelector(".product-price").value = option.dataset.gia ? formatNumber(Number(option.dataset.gia)) : "0";
      calculateTotal();
    });

    tr.querySelector(".product-qty").addEventListener("input", calculateTotal);

    tr.querySelector(".order-create-delete-btn").addEventListener("click", () => {
      tr.remove();
      updateRowNumbers();
      calculateTotal();
    });
  };

  const updateRowNumbers = () => {
    rowCount = 0;
    tbody.querySelectorAll("tr").forEach(tr => {
      rowCount++;
      tr.querySelector("td").textContent = rowCount;
    });
  };

  btnAdd?.addEventListener("click", addRow);
  
  // Remove JS intercept of saveBtn to let form submit naturally
});
