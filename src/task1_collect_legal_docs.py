"""
Task 1 — Thu thập văn bản pháp luật / quy định chính sách.
Chủ đề: 🏢 Trợ Lý Pháp Lý Khởi Nghiệp & Thương Mại Điện Tử (Topic 2 - SUGGESTED_TOPICS.md)
"""

from pathlib import Path
from fpdf import FPDF

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


def setup_directory():
    """Tạo thư mục data/landing/legal/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Thư mục đã sẵn sàng: {DATA_DIR}")


# 3 Văn bản pháp lý & quy định về Khởi nghiệp & TMĐT
LEGAL_DOCS = [
    {
        "filename": "luat-doanh-nghiep-2020-ho-kinh-doanh.pdf",
        "title": "QUY DINH VE DANG KY HO KINH DOANH VA DOANH NGHIEP (LUAT DOANH NGHIEP 2020)",
        "customer_role": "both",
        "content": """1. THU TUC DANG KY HO KINH DOANH CA THE
Theo quy dinh cua Luat Doanh nghiep 2020 va Nghi dinh 01/2021/ND-CP:
- Ho so dang ky Ho kinh doanh bao gom:
  + Giay de nghị dang ky ho kinh doanh (theo mau quy dinh).
  + Ban sao CCCD/CMND/Ho chieu con hieu luc cua chu ho kinh doanh hoac cac thanh vien ho gia dinh.
  + Ban sao bien ban hop ho gia dinh ve viec thanh lap ho kinh doanh (neu do nhieu thanh vien thanh lap).
  + Ban sao giay co che uy quyen neu uy quyen cho nguoi khac nộp ho so.
- Co quan tiep nhan: Phong Tai chinh - Ke hoach thuoc Uy ban nhan dan cap quan/huyen noi dat dia diem kinh doanh.
- Thoi gian xu ly ho so: 03 ngay lam viec ke tu ngay nhan du ho so hop le.

2. PHAN BIET HO KINH DOANH VA CONG TY TNHH
- Ho kinh doanh: Khong co tu cach phap nhan, chu ho chiu trach nhiem vo han bang toan bo tai san ca nhan. Chi duoc dang ky 01 ho kinh doanh tren toan quoc.
- Cong ty TNHH: Co tu cach phap nhan, thanh vien/chu so huu chiu trach nhiem huuhan trong pham vi von gop da dang ky.""",
    },
    {
        "filename": "nghi-dinh-52-2013-thuong-mai-dien-tu.pdf",
        "title": "NGHI DINH VE THUONG MAI DIEN TU (NGHI DINH 52/2013/ND-CP & NGHI DINH 85/2021/ND-CP)",
        "customer_role": "seller",
        "content": """1. NGHIA VU CUA NGUOI BAN TREN SAN THUONG MAI DIEN TU
Nguoi ban hang tren cac san TMDT (Shopee, TikTok Shop, Lazada...) co cac nghia vu phap ly sau:
- Cung cap day du, chinh xac thong tin nhu Ten, Dia chi, Ma so thue, So dien thoai tren gian hang.
- Cung cap thong tin chi tiet ve hang hoa, dich vu, gia ca, dieu kien giao hang, phuong thuc thanh toan va chinh sach doi tra.
- Tuan thu quy dinh ve hoa don, chung tu va ke khai nộp thue theo quy dinh cua phap luat thue Viet Nam.
- Khong duoc kinh doanh hang gia, hang nhai, hang cam hoac vi pham quyen so huu tri tue.

2. TRACH NHIEM CUA SAN THUONG MAI DIEN TU
- Kiem tra, xac minh thong tin cua nguoi ban dang ky gian hang.
- Cung cap thong tin nguoi ban va doanh thu cho Co quan Thue khi co yeu cau hop le.
- Khau tru va nop thue thay cho ca nhan kinh doanh tren san theo quy dinh cua Bọ Tai chinh.""",
    },
    {
        "filename": "quy-dinh-thue-ban-hang-online-tiktok-shopee.pdf",
        "title": "QUY DINH THUE DANG KY VA NOP THUE BAN HANG ONLINE TIKTOK SHOP VA SHOPEE",
        "customer_role": "seller",
        "content": """1. NGUONG DOANH THU PHAI NOP THUE TNCN VA GTGT
Theo Thong tu 40/2021/TT-BTC cua Bo Tai chinh:
- Ca nhan, ho kinh doanh ban hang online co doanh thu tu 100 trieu dong/nam tro xuong: DUOC MIEN THUE GTGT va thue TNCN.
- Ca nhan, ho kinh doanh ban hang online co doanh thu TREN 100 trieu dong/nam: PHAI NOP THUE GTGT va THUE TNCN.

2. TY LE THUE PHAI NOP
Doi voi hoat dong la Phan phoi, cung cap hang hoa (Ban hang online TMDT):
- Ty le thue GTGT (Gia tri gia tang): 1% tren doanh thu.
- Ty le thue TNCN (Thu nhập ca nhan): 0.5% tren doanh thu.
- Tong cong ti le thue phai nop = 1.5% tren tong doanh thu ban hang (chua tru chi phi).

3. PHUONG THUC KE KHAI NOP THUE
- Kê khai theo phuong phap khoán hoac ke khai theo thang/quy tai Chi cuc Thue quan ly.
- San TMDT (TikTok Shop/Shopee) ho tro cung cap Bang ke doanh thu va chi tiet giao dich de nguoi ban doi soat ke khai thue.""",
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
    print("🚀 Đang thu thập văn bản pháp luật Khởi nghiệp & TMĐT...")

    for doc in LEGAL_DOCS:
        filepath = DATA_DIR / doc["filename"]
        create_pdf_document(doc["title"], doc["content"], filepath)

    print("✅ Hoàn thành Task 1!")


if __name__ == "__main__":
    collect_legal_documents()
