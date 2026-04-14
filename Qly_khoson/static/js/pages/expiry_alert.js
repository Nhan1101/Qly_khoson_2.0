if (typeof expiryRows === 'undefined') {
  var expiryRows = [];
}

document.addEventListener("DOMContentLoaded", () => {
  const tableBody = document.getElementById("expiry-table-body");

  tableBody.innerHTML = expiryRows.map(row => `
    <tr>
      <td>${row.stt}</td>
      <td title="${row.ten}">${row.ten}</td>
      <td>${row.han}</td>
      <td>${row.muc}</td>
      <td>
        <span class="expiry-badge ${row.tt === "Còn hạn" ? "expiry-badge-ok" : "expiry-badge-warn"}">
          ${row.tt}
        </span>
      </td>
    </tr>
  `).join("");
});

