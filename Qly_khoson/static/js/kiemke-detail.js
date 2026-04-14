document.addEventListener("DOMContentLoaded", () => {
  const rows = document.querySelectorAll(".detail-row");
  const isReadonly = Boolean(window.kiemKeDetailReadonly);

  const formatDifference = (value) => {
    if (value > 0) {
      return `+${value}`;
    }
    return `${value}`;
  };

  const updateRow = (row) => {
    const systemStock = Number(row.dataset.systemStock || 0);
    const actualInput = row.querySelector(".detail-number-input");
    const reasonInput = row.querySelector(".detail-reason-input");
    const differenceBadge = row.querySelector(".difference-badge");

    if (!actualInput || !reasonInput || !differenceBadge) {
      return;
    }

    const rawValue = actualInput.value.trim();
    differenceBadge.classList.remove("is-negative", "is-positive", "is-zero", "is-visible");

    if (!rawValue) {
      differenceBadge.textContent = "";
      if (!isReadonly) {
        reasonInput.value = "";
        reasonInput.required = false;
        reasonInput.disabled = true;
      }
      return;
    }

    const actualValue = Number(rawValue);
    if (Number.isNaN(actualValue)) {
      differenceBadge.textContent = "";
      return;
    }

    const difference = actualValue - systemStock;
    differenceBadge.textContent = formatDifference(difference);
    differenceBadge.classList.add("is-visible");

    if (difference < 0) {
      differenceBadge.classList.add("is-negative");
      if (!isReadonly) {
        reasonInput.disabled = false;
        reasonInput.required = true;
      }
    } else if (difference > 0) {
      differenceBadge.classList.add("is-positive");
      if (!isReadonly) {
        reasonInput.disabled = true;
        reasonInput.required = false;
        reasonInput.value = "";
      }
    } else {
      differenceBadge.classList.add("is-zero");
      if (!isReadonly) {
        reasonInput.disabled = true;
        reasonInput.required = false;
        reasonInput.value = "";
      }
    }
  };

  rows.forEach((row) => {
    const actualInput = row.querySelector(".detail-number-input");
    if (actualInput && !isReadonly) {
      actualInput.addEventListener("input", () => updateRow(row));
    }
    updateRow(row);
  });
});
