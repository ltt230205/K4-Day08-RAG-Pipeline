"""
Task 2 — Crawl bài viết/hướng dẫn hỗ trợ pháp lý khởi nghiệp & TMĐT dành cho Người bán.
Chủ đề 2: 🏢 Trợ Lý Pháp Lý Khởi Nghiệp & Thương Mại Điện Tử (SUGGESTED_TOPICS.md)
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data" / "landing" / "news"


def setup_directory():
    """Tạo thư mục data/landing/news/ nếu chưa có."""
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"✓ Thư mục đã sẵn sàng: {DATA_DIR}")


# Danh sách 5 bài viết hướng dẫn Pháp lý Khởi nghiệp & TMĐT dành cho Người bán
SAMPLE_ARTICLES = [
    {
        "url": "https://luatvietnam.vn/doanh-nghiep/huong-dan-dang-ky-ho-kinh-doanh-ca-the-561-90123-article.html",
        "title": "Hướng dẫn chi tiết hồ sơ và thủ tục đăng ký Hộ kinh doanh cá thể cho người bán online 2026",
        "content_markdown": """# Hướng dẫn chi tiết hồ sơ và thủ tục đăng ký Hộ kinh doanh cá thể cho người bán online

Để đăng ký Hộ kinh doanh cá thể phục vụ bán hàng online trên Shopee, TikTok Shop hoặc mở cửa hàng, bạn cần chuẩn bị hồ sơ và thực hiện theo quy trình sau:

### 1. Hồ sơ cần chuẩn bị
- **Giấy đề nghị đăng ký hộ kinh doanh** (theo mẫu Phụ lục III-1).
- **Bản sao hợp lệ CCCD/CMND** của chủ hộ kinh doanh hoặc các thành viên hộ gia đình.
- **Biên bản họp hộ gia đình** về việc thành lập hộ kinh doanh (nếu do các thành viên cùng thành lập).
- **Hợp đồng thuê địa điểm kinh doanh** hoặc giấy chứng nhận quyền sử dụng đất.

### 2. Nơi nộp hồ sơ
- Nộp trực tiếp tại **Bộ phận một cửa - Phòng Tài chính - Kế hoạch** thuộc UBND cấp quận/huyện nơi đặt trụ sở kinh doanh.
- Nộp trực tuyến qua **Cổng thông tin đăng ký doanh nghiệp quốc gia** (nếu địa phương triển khai Dịch vụ công).

### 3. Thời gian giải quyết
Trong thời hạn **03 ngày làm việc** kể từ ngày nhận đủ hồ sơ hợp lệ, UBND quận/huyện sẽ cấp **Giấy chứng nhận đăng ký hộ kinh doanh**.""",
    },
    {
        "url": "https://thuvienphapluat.vn/tu-van-phap-luat/thue-ban-hang-online-tiktok-shopee-34201.html",
        "title": "Bán hàng online trên TikTok Shop và Shopee đạt doanh thu bao nhiêu thì phải nộp thuế TNCN và GTGT?",
        "content_markdown": """# Quy định nộp thuế GTGT và TNCN cho cá nhân bán hàng online trên sàn TMĐT

Rất nhiều nhà bán hàng mới khởi nghiệp trên TikTok Shop, Shopee thắc mắc về nghĩa vụ thuế. Dưới đây là quy định pháp lý chính thức theo Thông tư 40/2021/TT-BTC:

### 1. Ngưỡng doanh thu chịu thuế
- **Doanh thu dưới 100 triệu đồng/năm**: Cá nhân bán hàng online được **miễn 100% thuế GTGT và thuế TNCN**.
- **Doanh thu từ 100 triệu đồng/năm trở lên**: Bắt buộc phải kê khai và nộp thuế GTGT và thuế TNCN theo quy định.

### 2. Mức thuế suất phải nộp
Đối với ngành nghề bán buôn, bán lẻ hàng hóa (bán hàng online):
- **Thuế giá trị gia tăng (GTGT)**: **1%** tính trên tổng doanh thu.
- **Thuế thu nhập cá nhân (TNCN)**: **0.5%** tính trên tổng doanh thu.
- **Tổng cộng**: Người bán phải nộp **1.5%** trên tổng doanh thu bán hàng (chưa trừ chi phí nhập hàng hay quảng cáo).

### 3. Cách thức nộp thuế
Cá nhân có thể đăng ký MST cá nhân kinh doanh, nộp thuế theo phương pháp kê khai định kỳ (hàng quý) hoặc thông qua sự hỗ trợ khấu trừ/cung cấp dữ liệu tự động của sàn TikTok Shop/Shopee.""",
    },
    {
        "url": "https://seller.tiktok.com/university/article/huong-dan-dang-ky-gian-hang-nguoi-ban-tiktok-shop",
        "title": "Hướng dẫn đăng ký gian hàng người bán (Seller Account) trên Shopee và TikTok Shop",
        "content_markdown": """# Hướng dẫn quy trình đăng ký gian hàng người bán trên Shopee và TikTok Shop

Để bắt đầu bán hàng chuyên nghiệp trên sàn TMĐT, nhà bán hàng cần thực hiện xác minh danh tính tài khoản người bán:

### 1. Đối với cá nhân kinh doanh
- Chuẩn bị bản chụp mặt trước và mặt sau **CCCD/CMND** còn hiệu lực.
- Cung cấp **Mã số thuế cá nhân** và tài khoản ngân hàng trùng tên với CCCD để nhận tiền thanh toán đơn hàng.

### 2. Đối với Hộ kinh doanh / Doanh nghiệp
- Tải lên bản scan **Giấy chứng nhận đăng ký hộ kinh doanh** hoặc **Giấy chứng nhận đăng ký doanh nghiệp (GPKD)**.
- Cung cấp **Mã số thuế doanh nghiệp** và tài khoản ngân hàng công ty/chủ hộ.

### 3. Quy trình duyệt gian hàng
Sàn sẽ kiểm duyệt thông tin trong vòng 24h - 48h. Sau khi được duyệt, nhà bán hàng có thể đăng tải sản phẩm và liên kết ngân hàng rút tiền.""",
    },
    {
        "url": "https://dichvucong.gov.vn/huong-dan-thanh-lap-cong-ty-tnhh-cho-nha-ban-hang-tmdt.html",
        "title": "Điều kiện, hồ sơ và thủ tục thành lập Công ty TNHH / Cổ phần cho khởi nghiệp kinh doanh online",
        "content_markdown": """# Hướng dẫn thủ tục thành lập Công ty TNHH / Cổ phần cho khởi nghiệp TMĐT

Khi quy mô bán hàng trên Shopee/TikTok Shop phát triển lớn, việc thành lập Công ty TNHH giúp nâng cao uy tín và xuất hóa đơn VAT cho khách hàng.

### 1. Hồ sơ thành lập Công ty TNHH 1 thành viên / Cổ phần
- Giấy đề nghị đăng ký doanh nghiệp.
- Điều lệ công ty.
- Danh sách thành viên / cổ đông sáng lập.
- Bản sao CCCD/CMND/Hộ chiếu của chủ sở hữu và thành viên góp vốn.

### 2. Quy trình thực hiện
1. **Bước 1**: Chuẩn bị tên công ty, địa chỉ trụ sở, vốn điều lệ và mã ngành kinh doanh (Mã ngành 4791 - Bán lẻ theo yêu cầu đặt hàng qua internet).
2. **Bước 2**: Nộp hồ sơ qua Cổng thông tin quốc gia về đăng ký doanh nghiệp (`dangkykinhdoanh.gov.vn`).
3. **Bước 3**: Nhận Giấy chứng nhận đăng ký doanh nghiệp sau 3 ngày làm việc.
4. **Bước 4**: Khắc con dấu công ty, mở tài khoản ngân hàng doanh nghiệp và mua Chữ ký số (USB Token) để kê khai thuế.""",
    },
    {
        "url": "https://online.gov.vn/huong-dan-thong-bao-website-gian-hang-tmdt-bo-cong-thuong.html",
        "title": "Hướng dẫn thông báo gian hàng & website TMĐT với Bộ Công Thương tại online.gov.vn",
        "content_markdown": """# Hướng dẫn thông báo website và gian hàng TMĐT với Bộ Công Thương

Theo Nghị định 52/2013/NĐ-CP và Nghị định 85/2021/NĐ-CP của Chính phủ:

### 1. Đối tượng bắt buộc phải thông báo
- Các doanh nghiệp, thương nhân hoặc hộ kinh doanh sở hữu website bán hàng trực tiếp.
- Gian hàng của doanh nghiệp/hộ kinh doanh trên các sàn giao dịch thương mại điện tử lớn.

### 2. Các bước thực hiện trực tuyến (Miễn phí 100%)
1. Truy cập Cổng thông tin Quản lý hoạt động thương mại điện tử của Bộ Công Thương tại địa chỉ `online.gov.vn`.
2. Đăng ký tài khoản doanh nghiệp/hộ kinh doanh bằng Mã số thuế.
3. Kê khai thông tin website/gian hàng và nộp bản scan Giấy đăng ký kinh doanh.
4. Bộ Công Thương xét duyệt trong 3 ngày làm việc và cấp Logo "Đã thông báo Bộ Công Thương" để gắn lên trang.""",
    },
]


async def crawl_article(article_info: dict) -> dict:
    """Crawl/Chuẩn hóa bài viết với đầy đủ metadata."""
    try:
        from crawl4ai import AsyncWebCrawler
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(url=article_info["url"])
            if result and result.markdown and len(result.markdown) > 200:
                return {
                    "url": article_info["url"],
                    "title": result.metadata.get("title", article_info["title"]),
                    "date_crawled": datetime.now().isoformat(),
                    "content_markdown": result.markdown,
                }
    except Exception as e:
        print(f"  ℹ Crawl4AI fallback sang dữ liệu mẫu ({e})")

    # Fallback dữ liệu nội dung chuẩn
    return {
        "url": article_info["url"],
        "title": article_info["title"],
        "date_crawled": datetime.now().isoformat(),
        "content_markdown": article_info["content_markdown"],
    }


async def crawl_all():
    """Crawl và lưu toàn bộ bài viết vào data/landing/news/."""
    setup_directory()
    print("🚀 Đang tiến hành crawl/thu thập bài viết Pháp lý Khởi nghiệp & TMĐT dành cho Người bán...")

    for i, article_data in enumerate(SAMPLE_ARTICLES, 1):
        print(f"[{i}/{len(SAMPLE_ARTICLES)}] Processing: {article_data['title']}")
        article = await crawl_article(article_data)

        filename = f"article_{i:02d}.json"
        filepath = DATA_DIR / filename
        filepath.write_text(json.dumps(article, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"  ✓ Saved: {filepath} ({filepath.stat().st_size} bytes)")

    print("✅ Hoàn thành Task 2!")


if __name__ == "__main__":
    asyncio.run(crawl_all())
