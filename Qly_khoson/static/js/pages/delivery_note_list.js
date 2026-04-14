const deliveryNoteRows = [
  {
    stt: 1,
    ma: "PX0001",
    nguon: "Nguyễn Văn A",
    gia: "50.000.000",
    time: "13/11/2022 15:30",
    check: false,
    detail: {
      nguonNhan: "Nguyễn Văn A",
      maDon: "DH0001",
      soDienThoai: "0975260109",
      diaChi: "35 Tạ Hiện, Đà Nẵng",
      maPhieu: "PX0001",
      ngayXuat: "08/03/2026",
      duKienGiao: "15/3/2026",
      lyDoXuat: "Giao cho khách hàng",
      tongTien: "50.000.000 đ",
      items: [
        { tenHangHoa: "Sơn Alex - Màu ABC", maHang: "SP001", donViTinh: "Thùng", donGia: "30.000.000", soLuong: "10", thanhTien: "300.000.000" },
        { tenHangHoa: "Sơn Alex - Màu ABC", maHang: "SP002", donViTinh: "Thùng", donGia: "3.998.000", soLuong: "10", thanhTien: "39.980.000" },
        { tenHangHoa: "Sơn Alex - Màu ABC", maHang: "SP003", donViTinh: "Thùng", donGia: "40.000.000", soLuong: "5", thanhTien: "200.000.000" },
        { tenHangHoa: "Sơn Alex - Màu ABC", maHang: "SP004", donViTinh: "Thùng", donGia: "20.000.000", soLuong: "4", thanhTien: "80.000.000" },
        { tenHangHoa: "Sơn Alex - Màu ABC", maHang: "SP005", donViTinh: "Thùng", donGia: "790.000", soLuong: "55", thanhTien: "43.450.000" }
      ]
    }
  },
  { stt: 2, ma: "PX0002", nguon: "Nguyễn Văn A", gia: "50.000.000", time: "13/11/2022 11:09", check: true },
  { stt: 3, ma: "PX0003", nguon: "Nguyễn Văn A", gia: "50.000.000", time: "12/11/2022 14:30", check: false },
  { stt: 4, ma: "PX0004", nguon: "Nguyễn Văn A", gia: "50.000.000", time: "12/11/2022 12:30", check: true },
  { stt: 5, ma: "PX0005", nguon: "Nguyễn Văn A", gia: "50.000.000", time: "12/11/2022 09:30", check: false },
  { stt: 6, ma: "PX0006", nguon: "Nguyễn Văn A", gia: "50.000.000", time: "11/11/2022 15:30", check: false },
  { stt: 7, ma: "PX0007", nguon: "Nguyễn Văn A", gia: "50.000.000", time: "10/11/2022 16:08", check: false },
  { stt: 8, ma: "PX0008", nguon: "Nguyễn Văn A", gia: "50.000.000", time: "10/11/2022 15:05", check: true },
  { stt: 9, ma: "PX0009", nguon: "Nguyễn Văn A", gia: "50.000.000", time: "10/11/2022 09:55", check: false },
  { stt: 10, ma: "PX0010", nguon: "Nguyễn Văn A", gia: "50.000.000", time: "10/11/2022 08:30", check: false },
  { stt: 11, ma: "PX0011", nguon: "Nguyễn Văn A", gia: "50.000.000", time: "09/11/2022 17:27", check: true },
  { stt: 12, ma: "PX0012", nguon: "Nguyễn Văn A", gia: "50.000.000", time: "09/11/2022 07:30", check: false }
];

document.addEventListener("DOMContentLoaded", () => {
  const page = document.querySelector(".delivery-page");
  const tableBody = document.getElementById("delivery-note-table-body");
  const detailUrl = page?.dataset.detailUrl || "#";
  const editUrl = page?.dataset.editUrl || "#";

  if (!tableBody || !page) {
    return;
  }

  const deliveryOrderCreated = localStorage.getItem("deliveryOrderCreated") === "true";
  const rowsToRender = deliveryNoteRows.map((row, index) => {
    if (deliveryOrderCreated && index === 0) {
      return { ...row, check: true };
    }
    return row;
  });

  tableBody.innerHTML = rowsToRender.map((row, index) => `
    <tr class="clickable" data-index="${index}">
      <td>${row.stt}</td>
      <td><a class="delivery-link" href="${detailUrl}" data-index="${index}">${row.ma}</a></td>
      <td>${row.nguon}</td>
      <td class="delivery-td-value">${row.gia}</td>
      <td>${row.time}</td>
      <td>
        <div class="delivery-actions-cell">
          <button class="delivery-btn-edit" type="button" title="Chỉnh sửa"><i class="fa-solid fa-pen-to-square"></i></button>
          ${row.check
            ? '<span class="delivery-badge-check"><i class="fa-solid fa-check"></i></span>'
            : '<span class="delivery-badge-plus">+</span>'}
        </div>
      </td>
    </tr>
  `).join("");

  const buildFallbackDetail = (selectedRow) => ({
    nguonNhan: selectedRow.nguon,
    maDon: "XXXXX",
    soDienThoai: "0975260109",
    diaChi: "35 Tạ Hiện, Đà Nẵng",
    maPhieu: selectedRow.ma,
    ngayXuat: "08/03/2026",
    duKienGiao: "15/3/2026",
    lyDoXuat: "Giao cho khách hàng",
    tongTien: `${selectedRow.gia} đ`,
    items: [
      {
        tenHangHoa: "Sơn Alex - Màu ABC",
        maHang: "XXXXX",
        donViTinh: "Thùng",
        donGia: "5.000.000",
        soLuong: "10",
        thanhTien: selectedRow.gia
      }
    ]
  });

  const storeSelectedRow = (index) => {
    const selectedRow = rowsToRender[index];
    if (!selectedRow) {
      return null;
    }

    const detail = selectedRow.detail || buildFallbackDetail(selectedRow);
    localStorage.setItem("selectedDeliveryNote", JSON.stringify(detail));
    return detail;
  };

  const openDetail = (index) => {
    const selectedRow = rowsToRender[index];
    if (!selectedRow) {
      return;
    }

    storeSelectedRow(index);
    window.location.href = detailUrl;
  };

  tableBody.querySelectorAll("tr.clickable").forEach((row) => {
    row.addEventListener("click", (event) => {
      const interactive = event.target.closest("button, a");
      if (interactive && interactive.matches("button")) {
        return;
      }

      const index = Number(row.dataset.index);
      openDetail(index);
    });
  });

  tableBody.querySelectorAll(".delivery-link").forEach((link) => {
    link.addEventListener("click", (event) => {
      event.preventDefault();
      const index = Number(link.dataset.index);
      openDetail(index);
    });
  });

  tableBody.querySelectorAll(".delivery-btn-edit").forEach((button) => {
    button.addEventListener("click", (event) => {
      event.stopPropagation();
      const row = button.closest("tr");
      const index = Number(row?.dataset.index);
      storeSelectedRow(index);
      window.location.href = editUrl;
    });
  });

  if (deliveryOrderCreated) {
    localStorage.removeItem("deliveryOrderCreated");
  }
});
