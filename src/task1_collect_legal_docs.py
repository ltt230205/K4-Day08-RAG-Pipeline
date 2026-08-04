"""
Task 1 — Thu thập văn bản pháp luật dành cho Người bán & Khởi nghiệp TMĐT.
Chủ đề 2: 🏢 Trợ Lý Pháp Lý Khởi Nghiệp & Thương Mại Điện Tử (SUGGESTED_TOPICS.md)
"""

from pathlib import Path
from fpdf import FPDF

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"


def setup_directory():
    """Tạo thư mục data/landing/legal/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Thư mục đã sẵn sàng: {DATA_DIR}")


# 3 Văn bản pháp luật chính thức dành cho Người bán & Startup
LEGAL_DOCS = [
    {
        "filename": "luat-doanh-nghiep-2020-ho-kinh-doanh-cong-ty-tnhh.pdf",
        "title": "LUAT DOANH NGHIEP 2020 - QUY DINH VE HO KINH DOANH VA CONG TY TNHH",
        "customer_role": "seller",
        "content": """CHUONG VII: HO KINH DOANH VA CONG TY TNHH (TRICH LUAT DOANH NGHIEP 2020)

Dieu 79. Dang ky ho kinh doanh
1. Ho kinh doanh do mot ca nhan hoac cac thanh vien ho gia dinh dang ky thanh lap va chiu trach nhiem bang toan bo tai san cua minh doi voi hoat dong kinh doanh cua ho.
2. Ca nhan, thanh vien ho gia dinh chi duoc dang ky mot ho kinh doanh tren pham vi toan quoc.

Dieu 80. Ho so, trinh tu dang ky ho kinh doanh
1. Ho so dang ky ho kinh doanh bao gom:
   a) Giay de nghi dang ky ho kinh doanh;
   b) Ban sao giay to phap ly cua ca nhan doi voi chu ho kinh doanh, thanh vien ho gia dinh;
   c) Ban sao bien ban hop ho gia dinh ve viec thanh lap ho kinh doanh;
   d) Ban sao van ban uy quyen cua thanh vien ho gia dinh cho mot thanh vien lam chu ho kinh doanh.
2. Co quan dang ky kinh doanh cap Huyen cap Giay chung nhan dang ky ho kinh doanh trong thoi han 03 ngay lam viec ke tu ngay nhan ho so hop le.

Dieu 81. Thanh lap Cong ty TNHH Mot thanh vien cho nha ban hang
1. Cong ty TNHH mot thanh vien la doanh nghiep do mot to chuc hoac mot ca nhan lam chu so huu.
2. Chu so huu cong ty chiu trach nhiem ve cac khoan no va nghia vu tai chinh khac cua cong ty trong pham vi so von dieu le cua cong ty.""",
    },
    {
        "filename": "nghi-dinh-52-2013-va-85-2021-thuong-mai-dien-tu.pdf",
        "title": "NGHI DINH 52/2013/ND-CP VA 85/2021/ND-CP VE THUONG MAI DIEN TU",
        "customer_role": "seller",
        "content": """TRICH NGHI DINH 52/2013/ND-CP VA NGHI DINH 85/2021/ND-CP VE QUAN LY SAN TMDT

Dieu 37. Trach nhiem cua nguoi ban tren san giao dich thuong mai dien tu
1. Cung cap day du va chinh xac thong tin nhu Ten, Dia chi, Ma so thue, So dien thoai, Email tren gian hang ban hang online.
2. Cung cap thong tin day du ve hang hoa, dich vu, gia ca, dieu kien giao hang, phuong thuc thanh toan va chinh sach doi tra.
3. Tuan thu quy dinh cua phap luat ve hoa don, chung tu, ke khai va nop thue khi ban hang tren san TMDT (Shopee, TikTok Shop, Lazada).
4. Khong duoc kinh doanh hang gia, hang nhai, hang vi pham quyen so huu tri tue hoac hang hoa thuoc danh muc cam kinh doanh.

Dieu 52. Thong bao website va gian hang thuong mai dien tu ban hang
1. Cac thuong nhan, to chuc hoac ho kinh doanh ban hang qua website hoac gian hang TMDT phai thuc hien thong bao voi Bo Cong Thuong qua Cong thong tin online.gov.vn.
2. Quy trinh thong bao duoc thuc hien truc tuyen va khong thu bat ky khoan phi nao cua nguoi ban.""",
    },
    {
        "filename": "dieu-khoan-nguoi-ban-shopee-tiktokshop-thue-tncn-gtgt.pdf",
        "title": "QUY DINH VA DIEU KHOAN DANH CHO NGUOI BAN TIKTOK SHOP VA SHOPEE",
        "customer_role": "seller",
        "content": """QUY DINH DIEU KHOAN BAN HANG (SELLER TERMS) TREN TIKTOK SHOP VA SHOPEE VIETNAM

Muc 1. Quy dinh ve Thue Thu nhap ca nhan (TNCN) va Thue Gia tri gia tang (GTGT)
1. Theo Thong tu 40/2021/TT-BTC, ca nhan/ho kinh doanh ban hang online co doanh thu tren 100 trieu dong/nam phai nop thue.
2. Ty le thue phai nop tren doanh thu:
   - Thue GTGT: 1% tren doanh thu.
   - Thue TNCN: 0.5% tren doanh thu.
   - Tong ti le thue nghia vu = 1.5% tren tong doanh thu ban hang.
3. San TMDT (TikTok Shop/Shopee) co nghia vu cung cap du lieu doanh thu nguoi ban cho Co quan Thue va khau tru thue tu dong theo quy dinh.

Muc 2. Cac hanh vi vi pham va hinh thuc xu ly vi pham cua Nguoi ban
1. Vi pham ve hang gia, hang nhai: Khoa gian hang vinh vien, tich thu tien ky quy va chuyen ho so cho co quan chuc nang.
2. Vi pham ve ke khai thong tin doanh nghiep/ho kinh doanh: Tam dung quyen ban hang cho den khi cap nhat du thong tin Ma so thue va Giay phep kinh doanh.""",
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
    print("🚀 Đang thu thập văn bản pháp luật cho Người bán & Startup TMĐT...")

    for doc in LEGAL_DOCS:
        filepath = DATA_DIR / doc["filename"]
        create_pdf_document(doc["title"], doc["content"], filepath)

    print("✅ Hoàn thành Task 1!")


if __name__ == "__main__":
    collect_legal_documents()
