if (typeof inventoryRows === 'undefined') {
  var inventoryRows = [];
}

  document.addEventListener("DOMContentLoaded", () => {
    const tableBody = document.getElementById("inventory-table-body");
    if (!tableBody) {
      return;
    }

    tableBody.innerHTML = inventoryRows.map((row) => `
      <tr>
        <td>${row.stt}</td>
        <td>${row.ten}</td>
        <td>${row.ton}</td>
        <td>${row.min}</td>
        <td>
          <span class="inventory-badge ${row.tt === "Thiếu nhẹ" ? "inventory-badge-mild" : "inventory-badge-critical"}">${row.tt}</span>
        </td>
      </tr>
    `).join("");
  });

