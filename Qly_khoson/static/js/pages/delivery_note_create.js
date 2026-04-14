document.addEventListener("DOMContentLoaded", () => {
  const tbody = document.getElementById("delivery-create-table-body");
  const btnAdd = document.getElementById("delivery-create-btn-add");
  const totalEl = document.getElementById("delivery-create-total-value");
  
  const productCatalogRows = window.productsJson || [];
  const existingDetails = window.existingDetailsJson || [];
  let rowCount = 0;

  const formatNumber = (value) => value.toLocaleString("vi-VN");

  const calculateTotal = () => {
    let grandTotal = 0;
    tbody.querySelectorAll("tr").forEach(tr => {
      const priceStr = tr.querySelector(".product-price").value.replace(/\./g, '').replace(/,/g, '');
      const price = Number(priceStr) || 0;
      const qty = Number(tr.querySelector(".product-qty").value) || 0;
      const lineTotal = price * qty;
      
      const lineTotalInput = tr.querySelector(".line-total");
      if (lineTotalInput) {
        lineTotalInput.value = lineTotal > 0 ? formatNumber(lineTotal) : "0";
      }
      grandTotal += lineTotal;
    });

    if (totalEl) {
      totalEl.textContent = grandTotal > 0 ? `${formatNumber(grandTotal)} đ` : "0 đ";
    }
  };

  const addRow = (initialProductId = "", initialQty = 0) => {
    rowCount++;
    const tr = document.createElement("tr");
    
    let options = productCatalogRows.map(p => {
      const selected = parseInt(p.id) === parseInt(initialProductId) ? "selected" : "";
      return `<option value="${p.id}" data-ma="${p.ma || ''}" data-dvt="${p.dvt || ''}" data-gia="${p.gia || 0}" data-ton="${p.ton || 0}" ${selected}> ${p.ten}</option>`;
    }).join("");

    tr.innerHTML = `
      <td style="text-align: center; color: #4b5563;">${rowCount}</td>
      <td>
        <input type="hidden" name="product_id" class="product-id-hidden" value="${initialProductId}">
        <select class="delivery-create-row-input text-left product-select" style="width: 100%;">
          <option value="">Chọn hàng hóa...</option>
          ${options}
        </select>
      </td>
      <td><input type="text" class="delivery-create-row-input product-code" readonly></td>
      <td><input type="text" class="delivery-create-row-input product-unit" readonly></td>
      <td><input type="text" class="delivery-create-row-input product-stock" readonly></td>
      <td><input type="text" class="delivery-create-row-input product-price unit-price readonly" readonly></td>
      <td><input type="number" class="delivery-create-row-input quantity product-qty" min="0" value="${initialQty}" ${!initialProductId ? 'disabled' : ''}></td>
      <td><input type="text" class="delivery-create-row-input line-total readonly" value="0" readonly></td>
      <td style="text-align: center;">
        <button class="delivery-create-delete-btn" type="button" style="background:none; border:none; color:#e53c2b; cursor:pointer; padding: 4px 8px;">
          <i class="fa-solid fa-trash-can"></i>
        </button>
      </td>
    `;
    tbody.appendChild(tr);

    const select = tr.querySelector(".product-select");
    const qtyInput = tr.querySelector(".product-qty");
    const idInput = tr.querySelector(".product-id-hidden");

    const updateRowFromSelect = () => {
      const option = select.options[select.selectedIndex];
      if(option && option.value) {
        tr.querySelector(".product-code").value = option.dataset.ma || "";
        tr.querySelector(".product-unit").value = option.dataset.dvt || "";
        tr.querySelector(".product-stock").value = option.dataset.ton || "0";
        tr.querySelector(".product-price").value = option.dataset.gia ? formatNumber(Number(option.dataset.gia)) : "0";
        
        idInput.value = option.value;
        qtyInput.name = `quantity_${option.value}`;
        qtyInput.removeAttribute("disabled");
        qtyInput.max = option.dataset.ton || "0";
      } else {
        tr.querySelector(".product-code").value = "";
        tr.querySelector(".product-unit").value = "";
        tr.querySelector(".product-stock").value = "";
        tr.querySelector(".product-price").value = "";
        
        idInput.value = "";
        qtyInput.name = "";
        qtyInput.setAttribute("disabled", "disabled");
      }
      calculateTotal();
    };

    select.addEventListener("change", updateRowFromSelect);
    qtyInput.addEventListener("input", calculateTotal);

    tr.querySelector(".delivery-create-delete-btn").addEventListener("click", () => {
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

  if (existingDetails.length > 0) {
    existingDetails.forEach(detail => {
      addRow(detail.product_id, detail.so_luong);
    });
  } else {
    // Start with one empty row for convenience if manual
    addRow();
  }

  btnAdd?.addEventListener("click", () => addRow());
});
