if (typeof customerOrderRows === 'undefined') {
  var customerOrderRows = [];
}

function customerOrderBadgeClass(status) {
  if (status === "Chờ xử lý") {
    return "order-badge-waiting";
  }
  if (status === "Đã xuất 1 phần") {
    return "order-badge-partial";
  }
  if (status === "Đã hủy") {
    return "order-badge-cancelled";
  }
  if (status === "Đã xuất") {
    return "order-badge-exported";
  }
  return "order-badge-waiting";
}

document.addEventListener("DOMContentLoaded", () => {
  const page = document.querySelector(".order-page");
  const tableBody = document.getElementById("customer-order-table-body");
  const exportModal = document.getElementById("order-export-modal");
  const exportClose = document.getElementById("order-export-close");
  const exportCancel = document.getElementById("order-export-cancel");
  const deleteModal = document.getElementById("order-delete-modal");
  const deleteConfirm = document.getElementById("order-delete-confirm");
  const deleteCancel = document.getElementById("order-delete-cancel");
  const detailUrl = page?.dataset.detailUrl || "#";
  const editUrl = page?.dataset.editUrl || "#";
  const deliveryCreateUrl = page?.dataset.deliveryCreateUrl || "#";
  let selectedOrder = null;
  let pendingDeleteIndex = null;

  if (!tableBody || !page) {
    return;
  }

  const closeExportModal = () => {
    exportModal?.classList.remove("show");
    selectedOrder = null;
  };

  const closeDeleteModal = () => {
    deleteModal?.classList.remove("show");
    pendingDeleteIndex = null;
  };

  const renderTable = () => {
    if (customerOrderRows.length === 0) {
      tableBody.innerHTML = `<tr><td colspan="7" style="text-align: center; padding: 20px; color: #888;">Chưa có đơn đặt hàng</td></tr>`;
      return;
    }

    tableBody.innerHTML = customerOrderRows.map((row, index) => `
      <tr>
        <td>${row.stt}</td>
        <td>${row.ma}</td>
        <td>${row.ten}</td>
        <td class="order-td-value">${row.gia}</td>
        <td>${row.time}</td>
        <td><span class="order-badge ${customerOrderBadgeClass(row.st)}">${row.st}</span></td>
        <td>
          <div class="order-actions">
            <a class="order-act-icon" href="/don-dat-hang-khach-hang/${row.id}/"><i class="fa-regular fa-eye" style="color: #555;"></i></a>
            <a class="order-act-icon" href="/don-dat-hang-khach-hang/${row.id}/sua/"><i class="fa-solid fa-pen" style="color: #555;"></i></a>
            <button class="order-act-icon order-open-delete" type="button" data-index="${index}">
              <i class="fa-solid fa-trash-can" style="color: #e53c2b;"></i>
            </button>
            <button class="order-act-icon order-open-export" type="button" data-index="${index}">
              <i class="fa-regular fa-square-plus" style="color: #27ae60;"></i>
            </button>
          </div>
        </td>
      </tr>
    `).join("");

    tableBody.querySelectorAll(".order-open-export").forEach((button) => {
      button.addEventListener("click", () => {
        const index = Number(button.dataset.index);
        selectedOrder = customerOrderRows[index] || null;
        exportModal?.classList.add("show");
      });
    });

    tableBody.querySelectorAll(".order-open-delete").forEach((button) => {
      button.addEventListener("click", () => {
        pendingDeleteIndex = Number(button.dataset.index);
        deleteModal?.classList.add("show");
      });
    });
  };

  renderTable();

  exportClose?.addEventListener("click", closeExportModal);
  exportCancel?.addEventListener("click", closeExportModal);

  exportModal?.addEventListener("click", (event) => {
    if (event.target === exportModal) {
      closeExportModal();
    }
  });

  document.querySelectorAll("[data-export-type]").forEach((button) => {
    button.addEventListener("click", () => {
      if (!selectedOrder) {
        return;
      }

      const exportType = button.dataset.exportType;
      const payload = selectedOrder.detail || {
        tenKhachHang: selectedOrder.ten,
        maDon: selectedOrder.ma,
        soDienThoai: "0975260109",
        diaChi: "35 Tạ Hiện, Đà Nẵng",
        maPhieu: "",
        ngayDatHang: "13-11-2022",
        ghiChu: "",
        tongTien: `${selectedOrder.gia} đ`,
        items: [
          {
            tenHangHoa: "Sơn Alex - Màu ABC",
            maHang: "XXXXX",
            donViTinh: "Thùng",
            donGia: "5.000.000",
            soLuong: "10",
            thanhTien: selectedOrder.gia
          }
        ]
      };

      const params = new URLSearchParams({
        recipient_name: selectedOrder.ten || "",
        order_code: selectedOrder.ma || "",
        phone: payload.soDienThoai || "",
        address: payload.diaChi || "",
        reason: exportType === "partial" ? "Xuất kho một phần cho khách hàng" : "Xuất kho toàn phần cho khách hàng",
        order_id: selectedOrder.id,
        export_type: exportType
      });

      window.location.href = `${deliveryCreateUrl}?${params.toString()}`;
    });
  });

  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
  }

  deleteConfirm?.addEventListener("click", () => {
    if (pendingDeleteIndex === null) {
      return;
    }

    const orderId = customerOrderRows[pendingDeleteIndex].id;
    
    fetch(`/don-dat-hang-khach-hang/${orderId}/xoa/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    }).then(res => res.json()).then(data => {
        if(data.success) {
            window.location.reload();
        }
    });
  });

  deleteCancel?.addEventListener("click", closeDeleteModal);

  deleteModal?.addEventListener("click", (event) => {
    if (event.target === deleteModal) {
      closeDeleteModal();
    }
  });
});
