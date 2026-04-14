document.addEventListener("DOMContentLoaded", () => {
  const createButton = document.getElementById("createTicketBtn");
  const tableBody = document.getElementById("kiemkeTableBody");
  const rowTemplate = document.getElementById("newTicketRowTemplate");

  if (!createButton || !tableBody || !rowTemplate) {
    return;
  }

  const renumberRows = () => {
    const rows = tableBody.querySelectorAll("tr[data-ticket-row], tr[data-inline-row]");
    rows.forEach((row, index) => {
      const firstCell = row.querySelector("td");
      if (firstCell) {
        firstCell.textContent = index + 1;
      }
    });
  };

  const removeEmptyRow = () => {
    const emptyRow = tableBody.querySelector("[data-empty-row]");
    if (emptyRow) {
      emptyRow.remove();
    }
  };

  const handleCancel = (row) => {
    row.remove();
    renumberRows();
  };

  createButton.addEventListener("click", () => {
    const existingInlineRow = tableBody.querySelector("[data-inline-row]");
    if (existingInlineRow) {
      const select = existingInlineRow.querySelector(".inline-select");
      if (select) {
        select.focus();
      }
      return;
    }

    removeEmptyRow();

    const rowFragment = rowTemplate.content.cloneNode(true);
    const inlineRow = rowFragment.querySelector("[data-inline-row]");
    const cancelButton = rowFragment.querySelector("[data-inline-cancel]");
    const select = rowFragment.querySelector(".inline-select");

    if (cancelButton && inlineRow) {
      cancelButton.addEventListener("click", () => handleCancel(inlineRow));
    }

    tableBody.prepend(rowFragment);
    renumberRows();

    if (select) {
      select.focus();
    }
  });
});
