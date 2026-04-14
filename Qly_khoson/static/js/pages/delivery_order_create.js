document.addEventListener("DOMContentLoaded", () => {
  const page = document.querySelector(".delivery-order-create-page");
  const listUrl = page?.dataset.listUrl || "#";
  const donGiaInput = document.getElementById("delivery-order-create-don-gia");
  const soLuongInput = document.getElementById("delivery-order-create-so-luong");
  const thanhTienInput = document.getElementById("delivery-order-create-thanh-tien");
  const totalEl = document.getElementById("delivery-order-create-total");
  const saveBtn = document.getElementById("delivery-order-create-save-btn");

  const parseNumber = (value) => {
    const normalized = String(value || "").replace(/\./g, "").replace(/,/g, "").trim();
    const parsed = Number(normalized);
    return Number.isFinite(parsed) ? parsed : 0;
  };

  const formatNumber = (value) => value.toLocaleString("vi-VN");

  const recalculate = () => {
    const donGia = parseNumber(donGiaInput?.value);
    const soLuong = parseNumber(soLuongInput?.value);
    const thanhTien = donGia * soLuong;

    if (thanhTienInput) {
      thanhTienInput.value = thanhTien > 0 ? formatNumber(thanhTien) : "";
    }

    if (totalEl) {
      totalEl.textContent = `${formatNumber(thanhTien)} đ`;
    }
  };

  donGiaInput?.addEventListener("input", recalculate);
  soLuongInput?.addEventListener("input", recalculate);
  recalculate();

  saveBtn?.addEventListener("click", () => {
    const draft = {
      nguonNhan: document.getElementById("delivery-order-create-nguon-nhan")?.value.trim() || "",
      maDon: document.getElementById("delivery-order-create-ma-don")?.value.trim() || "",
      soDienThoai: document.getElementById("delivery-order-create-so-dien-thoai")?.value.trim() || "",
      diaChi: document.getElementById("delivery-order-create-dia-chi")?.value.trim() || "",
      maPhieu: document.getElementById("delivery-order-create-ma-phieu")?.value.trim() || "",
      ngayDatHang: document.getElementById("delivery-order-create-ngay-dat-hang")?.value.trim() || "",
      ghiChu: document.getElementById("delivery-order-create-ghi-chu")?.value.trim() || "",
      tenHang: document.getElementById("delivery-order-create-ten-hang")?.value.trim() || "",
      maHang: document.getElementById("delivery-order-create-ma-hang")?.value.trim() || "",
      donViTinh: document.getElementById("delivery-order-create-don-vi-tinh")?.value.trim() || "",
      donGia: donGiaInput?.value.trim() || "",
      soLuong: soLuongInput?.value.trim() || "",
      thanhTien: thanhTienInput?.value.trim() || "",
      tongTien: totalEl?.textContent.trim() || "0 đ"
    };

    localStorage.setItem("deliveryOrderDraft", JSON.stringify(draft));
    localStorage.setItem("deliveryOrderCreated", "true");
    window.location.href = listUrl;
  });
});
