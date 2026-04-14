document.addEventListener("DOMContentLoaded", () => {
    const fallbackData = {
      nguonNhan: "Nguyễn Văn A",
      maDon: "XXXXX",
      soDienThoai: "0975260109",
      diaChi: "35 Tạ Hiện, Đà Nẵng",
      maPhieu: "XXXXXX",
      ngayXuat: "08/03/2026",
      duKienGiao: "15/3/2026",
      lyDoXuat: "Giao cho khách hàng",
      tongTien: "50.000.000 đ",
      items: [
        { tenHangHoa: "Sơn Alex - Màu ABC", maHang: "XXXXX", donViTinh: "Thùng", donGia: "30.000.000", soLuong: "10", thanhTien: "300.000.000" },
        { tenHangHoa: "Sơn Alex - Màu ABC", maHang: "XXXXX", donViTinh: "Thùng", donGia: "3.998.000", soLuong: "10", thanhTien: "39.980.000" },
        { tenHangHoa: "Sơn Alex - Màu ABC", maHang: "XXXXX", donViTinh: "Thùng", donGia: "40.000.000", soLuong: "5", thanhTien: "200.000.000" },
        { tenHangHoa: "Sơn Alex - Màu ABC", maHang: "XXXXX", donViTinh: "Thùng", donGia: "20.000.000", soLuong: "4", thanhTien: "80.000.000" },
        { tenHangHoa: "Sơn Alex - Màu ABC", maHang: "XXXXX", donViTinh: "Thùng", donGia: "790.000", soLuong: "55", thanhTien: "43.450.000" }
      ]
    };

    const selectedData = JSON.parse(localStorage.getItem("selectedDeliveryNote") || "null");
    const draftData = JSON.parse(localStorage.getItem("deliveryNoteDraft") || "null");
    const data = selectedData || draftData || fallbackData;

    const setText = (id, value) => {
      const element = document.getElementById(id);
      if (element) {
        element.textContent = value || "";
      }
    };

    setText("delivery-view-nguon-nhan", data.nguonNhan);
    setText("delivery-view-ma-don", data.maDon);
    setText("delivery-view-so-dien-thoai", data.soDienThoai);
    setText("delivery-view-dia-chi", data.diaChi);
    setText("delivery-view-ma-phieu", data.maPhieu);
    setText("delivery-view-ngay-xuat", data.ngayXuat);
    setText("delivery-view-du-kien-giao", data.duKienGiao);
    setText("delivery-view-ly-do-xuat", data.lyDoXuat);
    setText("delivery-view-tong-tien", data.tongTien || "0 đ");

    const tbody = document.getElementById("delivery-view-items");
    if (!tbody) {
      return;
    }

    const items = Array.isArray(data.items) ? data.items : [];
    if (!items.length) {
      tbody.innerHTML = `
        <tr>
          <td colspan="7" style="padding: 14px; color: #6b7280;">Chưa có hàng hóa</td>
        </tr>
      `;
      return;
    }

    tbody.innerHTML = items.map((item, index) => `
      <tr>
        <td>${index + 1}</td>
        <td class="text-left">${item.tenHangHoa || ""}</td>
        <td>${item.maHang || ""}</td>
        <td>${item.donViTinh || ""}</td>
        <td>${item.donGia || ""}</td>
        <td>${item.soLuong || ""}</td>
        <td>${item.thanhTien || ""}</td>
      </tr>
    `).join("");
  });

