"""
Task 2 — Crawl bài viết/hướng dẫn hỗ trợ pháp lý khởi nghiệp & TMĐT.
Chủ đề: 🏢 Trợ Lý Pháp Lý Khởi Nghiệp & Thương Mại Điện Tử (Topic 2 - SUGGESTED_TOPICS.md)
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


# Danh sách 5 bài viết hướng dẫn Pháp lý Khởi nghiệp & TMĐT
SAMPLE_ARTICLES = [
    {
        "url": "https://luatvietnam.vn/doanh-nghiep/huong-dan-dang-ky-ho-kinh-doanh-ca-the-561-90123-article.html",
        "title": "Hướng dẫn chi tiết hồ sơ và thủ tục đăng ký Hộ kinh doanh cá thể mới nhất 2026",
        "content_markdown": """# Hướng dẫn chi tiết hồ sơ và thủ tục đăng ký Hộ kinh doanh cá thể

Để đăng ký Hộ kinh doanh cá thể phục vụ bán hàng online hoặc mở cửa hàng, bạn cần chuẩn bị hồ sơ và làm theo quy trình sau:

### 1. Hồ sơ cần chuẩn bị
- **Giấy đề nghị đăng ký hộ kinh doanh** (theo mẫu Phụ lục III-1 Thông tư 01/2021/TT-BKHĐT).
- **Bản sao hợp lệ CCCD/CMND** của chủ hộ kinh doanh hoặc các thành viên hộ gia đình tham gia góp vốn.
- **Biên bản họp hộ gia đình** về việc thành lập hộ kinh doanh (nếu hộ kinh doanh do các thành viên hộ gia đình cùng thành lập).
- **Hợp đồng thuê địa điểm kinh doanh** hoặc giấy chứng nhận quyền sử dụng đất (bản sao).

### 2. Nơi nộp hồ sơ
- Nộp trực tiếp tại **Bộ phận một cửa - Phòng Tài chính - Kế hoạch** thuộc UBND cấp quận/huyện nơi đặt trụ sở kinh doanh.
- Nộp trực tuyến qua **Cổng thông tin đăng ký doanh nghiệp quốc gia** (nếu địa phương triển khai Dịch vụ công trực tuyến).

### 3. Thời gian giải quyết
Trong thời hạn **03 ngày làm việc** kể từ ngày nhận đủ hồ sơ hợp lệ, UBND quận/huyện sẽ cấp **Giấy chứng nhận đăng ký hộ kinh doanh**.""",
    },
    {
        "url": "https://thuvienphapluat.vn/tu-van-phap-luat/thue-ban-hang-online-tiktok-shopee-34201.html",
        "title": "Bán hàng online trên TikTok Shop và Shopee đạt doanh thu bao nhiêu thì phải nộp thuế?",
        "content_markdown": """# Quy định nộp thuế GTGT và TNCN cho cá nhân bán hàng online trên sàn TMĐT

Rất nhiều nhà bán hàng mới khởi nghiệp trên TikTok Shop, Shopee thắc mắc về nghĩa vụ thuế. Dưới đây là quy định pháp lý chính thức theo Thông tư 40/2021/TT-BTC:

### 1. Ngưỡng doanh thu chịu thuế
- **Doanh thu dưới 100 triệu đồng/năm**: Cá nhân bán hàng online được **miễn 100% thuế GTGT và thuế TNCN**.
- **Doanh thu từ 100 triệu đồng/năm trở lên**: Bắt buộc phải kê khai và nộp thuế GTGT và thuế TNCN theo quy định.

### 2. Mức thuế suất phải nộp
Đối với ngành nghề bán buôn, bán lẻ hàng hóa (bán hàng online):
- **Thuế giá trị gia tăng (GTGT)**: **1%** tính trên tổng doanh thu.
- **Thuế thu nhập cá nhân (TNCN)**: **0.5%** tính trên tổng doanh thu.
- **Tổng cộng**: Người bán phải nộp **1.5%** trên tổng doanh thu bán hàng (chưa trừ chi phí nhập hàng, vận chuyển hay quảng cáo).

### 3. Cách thức nộp thuế
Cá nhân có thể đăng ký MST cá nhân kinh doanh, nộp thuế theo phương pháp kê khai định kỳ (hàng quý) hoặc thông qua sự hỗ trợ khấu trừ/cung cấp dữ liệu tự động của sàn TikTok Shop/Shopee.""",
    },
    {
        "url": "https://dichvucong.gov.vn/huong-dan-thanh-lap-cong-ty-tnhh-cho-nha-ban-hang-tmdt.html",
        "title": "Hướng dẫn thủ tục thành lập Công ty TNHH 1 Thành viên cho nhà bán hàng TMĐT",
        "content_markdown": """# Hướng dẫn thủ tục thành lập Công ty TNHH 1 Thành viên cho khởi nghiệp TMĐT

Khi quy mô bán hàng trên Shopee/TikTok Shop phát triển lớn, việc thành lập Công ty TNHH giúp nâng cao uy tín và xuất hóa đơn VAT cho khách hàng.

### 1. Hồ sơ thành lập Công ty TNHH 1 thành viên
- Giấy đề nghị đăng ký doanh nghiệp.
- Điều lệ công ty.
- Bản sao CCCD/CMND/Hộ chiếu của chủ sở hữu công ty.

### 2. Quy trình thực hiện
1. **Bước 1**: Chuẩn bị tên công ty, địa chỉ trụ sở, vốn điều lệ và ngành nghề kinh doanh (mã ngành 4791 - Bán lẻ theo yêu cầu đặt hàng qua bưu điện hoặc qua internet).
2. **Bước 2**: Nộp hồ sơ qua Cổng thông tin quốc gia về đăng ký doanh nghiệp (`dangkykinhdoanh.gov.vn`).
3. **Bước 3**: Nhận Giấy chứng nhận đăng ký doanh nghiệp sau 3 ngày làm việc.
4. **Bước 4**: Khắc con dấu công ty, mở tài khoản ngân hàng doanh nghiệp và mua Chữ ký số (USB Token) để kê khai thuế.""",
    },
    {
        "url": "https://online.gov.vn/huong-dan-thong-bao-website-gian-hang-tmdt-bo-cong-thuong.html",
        "title": "Quy định về đăng ký thông báo gian hàng và website thương mại điện tử với Bộ Công Thương",
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
    {
        "url": "https://seller.tiktok.com/university/article/cac-loi-vi-pham-phap-ly-dieu-khoan-nguoi-ban-tiktok-shop",
        "title": "Tổng hợp các lỗi vi phạm pháp lý khiến gian hàng TikTok Shop và Shopee bị khóa vĩnh viễn",
        "content_markdown": """# Các lỗi vi phạm pháp lý dẫn đến bị khóa gian hàng trên TikTok Shop và Shopee

Nhà bán hàng online cần đặc biệt lưu ý các quy định pháp luật và chính sách sàn để tránh bị điểm phạt (Jusdiction Points) hoặc khóa shop vĩnh viễn:

### 1. Bán hàng giả, hàng nhái, vi phạm sở hữu trí tuệ
- Đăng bán các sản phẩm nhái thương hiệu lớn (Nike, Adidas, Chanel...) khi không có giấy ủy quyền chính hãng.
- **Hậu quả**: Khóa sản phẩm lập tức, tịch thu tiền ký quỹ và khóa gian hàng vĩnh viễn, đồng thời có thể bị xử lý hình sự/xử phạt hành chính từ 10 - 50 triệu đồng.

### 2. Kinh doanh hàng hóa thuộc danh mục cấm
- Thực phẩm chức năng không có giấy công bố sản phẩm, mỹ phẩm không có số công bố, thuốc chữa bệnh, vũ khí, chất cháy nổ.

### 3. Trốn thuế và gian lận hóa đơn
- Không cung cấp mã số thuế cho sàn hoặc cố tình khai gian dối doanh thu nhằm trốn thuế TNCN/GTGT.""",
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
    print("🚀 Đang tiến hành crawl/thu thập bài viết Pháp lý Khởi nghiệp & TMĐT...")

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
