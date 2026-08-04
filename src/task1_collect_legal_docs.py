"""
Task 1 — Thu thập văn bản chính sách thương mại điện tử / hỗ trợ khách hàng.
"""

from pathlib import Path
import urllib.request
from fpdf import FPDF

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


def setup_directory():
    """Tạo thư mục data/landing/legal/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Thư mục đã sẵn sàng: {DATA_DIR}")


# Danh sách 3 chính sách mẫu TMĐT (Shopee Vietnam) - Định dạng chuẩn không lỗi phông
LEGAL_DOCS = [
    {
        "filename": "returns-refund-policy-shopee.pdf",
        "title": "CHINH SACH TRA HANG VA HOAN TIEN SHOPEE",
        "customer_role": "buyer",
        "content": """1. DIEU KIEN AP DUNG TRA HANG / HOAN TIEN
Shopee quy dinh Nguoi mua co the yeu cau tra hang va hoan tien trong cac truong hop sau:
- Nguoi mua da thanh toan nhung khong nhan duoc san pham, hoac san pham bi mat trong qua trinh van chuyen.
- San pham bi loi hoac bi hu hai trong qua trinh van chuyen.
- Nguoi ban giao sai san pham cho Nguoi mua (vi du: sai kich co, sai mau sac, v.v.).
- San pham Nguoi mua nhan duoc khac biet mot cach ro ret so voi thong tin ma Nguoi ban cung cap trong muc mo ta san pham.

2. THOI GIAN GUI YEU CAU HOAN TIEN
Nguoi mua me can gui yeu cau tra hang/hoan tien trong vong 03-07 ngay ke tu khi don hang cap nhat trang thai "Giao hang thanh cong".

3. BANG CHUNG CAN CUNG CAP
- Hinh anh/Video mo hop san pham (unboxing video).
- Hinh anh phieu giao hang co ma van don.
- Hinh anh chi tiet loi/hu hong cua san pham.""",
    },
    {
        "filename": "payment-methods-shopee.pdf",
        "title": "QUY DINH VE PHUONG THUC THANH TOAN SHOPEE",
        "customer_role": "both",
        "content": """1. CAC PHUONG THUC THANH TOAN DUOC CHAP NHAN
Shopee ho tro cac phuong thuc thanh toan an toan sau:
- Vi ShopeePay (Thanh toan truc tiep qua lien ket ngan hang).
- The Tin dung / Ghi no (Visa, Mastercard, JCB).
- Thanh toan khi nhan hang (COD - Cash on Delivery).
- Chuyen khoan ngan hang (QR Code / Bank Transfer).
- SPayLater (Thanh toan sau / Tra gop).

2. QUY DINH HOAN TIEN THEO PHUONG THUC THANH TOAN
- COD / Chuyen khoan: Hoan tien ve So du Tai khoan Shopee / Vi ShopeePay trong 24h.
- The tin dung/ghi no: Hoan tien truc tiep vao the trong 7-14 ngay lam viec tuy ngan hang phat hanh.
- SPayLater: Hoan han muc kha dung ngay khi don hang hoan tat thu tuc huy/tra hang.""",
    },
    {
        "filename": "privacy-policy-shopee.pdf",
        "title": "CHINH SACH BAO MAT THONG TIN NGUOI DUNG",
        "customer_role": "both",
        "content": """1. MUC DICH THU THAP DU LIEU
Shopee thu thap thong tin ca nhan cua nguoi dung de:
- Xu ly don hang va giao hang dung dia chi.
- Cung cap dich vu cham soc khach hang va giai quyet tranh chap.
- Xac thuc danh tinh nguoi dung va ngan ngua hanh vi gian luan.

2. BAO VE THONG TIN CA NHAN
Chung toi ap dung cac bien phap bao mat ky thuat va to chuc phu hop de bao ve du lieu ca nhan cua nguoi dung khong bi truy cap, thu thap, su dung, tiet lo hoac huy hoai trai phep.

3. QUYEN CUA NGUOI DUNG
Nguoi dung co quyen kiem tra, cap nhat, dieu chinh hoac yeu cau xoa bo thong tin ca nhan cua minh bang cach dang nhap vao tai khoan ca nhan tren ung dung Shopee.""",
    },
]


def create_pdf_document(title: str, content: str, filepath: Path):
    """Tạo file PDF hợp lệ có dung lượng > 1KB."""
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 14)
    encoded_title = title.encode("latin-1", "replace").decode("latin-1")
    pdf.cell(pdf.epw, 10, encoded_title, new_x="LMARGIN", new_y="NEXT", align="C")
    pdf.ln(5)

    pdf.set_font("Helvetica", size=10)
    for line in content.split("\n"):
        line_str = line.strip()
        if not line_str:
            pdf.ln(4)
            continue
        encoded_line = line_str.encode("latin-1", "replace").decode("latin-1")
        pdf.multi_cell(pdf.epw, 6, encoded_line)

    pdf.output(str(filepath))
    print(f"  ✓ Đã tạo PDF: {filepath} ({filepath.stat().st_size} bytes)")


def collect_legal_documents():
    setup_directory()
    print("🚀 Đang thu thập/tạo văn bản pháp luật TMĐT...")

    for doc in LEGAL_DOCS:
        filepath = DATA_DIR / doc["filename"]
        create_pdf_document(doc["title"], doc["content"], filepath)

    print("✅ Hoàn thành Task 1!")


if __name__ == "__main__":
    collect_legal_documents()
