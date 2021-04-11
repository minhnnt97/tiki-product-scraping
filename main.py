from tiki_scraper import *

### MAIN CATEGORIES ###
MAIN_CATS = [
    {'Name': 'Điện Thoại - Máy Tính Bảng', 'URL': 'https://tiki.vn/dien-thoai-may-tinh-bang/c1789?src=c.1789.hamburger_menu_fly_out_banner'},
    {'Name': 'Điện Tử - Điện Lạnh', 'URL': 'https://tiki.vn/tivi-thiet-bi-nghe-nhin/c4221?src=c.4221.hamburger_menu_fly_out_banner'},
    {'Name': 'Phụ Kiện - Thiết Bị Số', 'URL': 'https://tiki.vn/thiet-bi-kts-phu-kien-so/c1815?src=c.1815.hamburger_menu_fly_out_banner'},
    {'Name': 'Laptop - Thiết bị IT', 'URL': 'https://tiki.vn/laptop-may-vi-tinh/c1846?src=c.1846.hamburger_menu_fly_out_banner'},
    {'Name': 'Máy Ảnh - Quay Phim', 'URL': 'https://tiki.vn/may-anh/c1801?src=c.1801.hamburger_menu_fly_out_banner'},
    {'Name': 'Điện Gia Dụng', 'URL': 'https://tiki.vn/dien-gia-dung/c1882?src=c.1882.hamburger_menu_fly_out_banner'},
    {'Name': 'Nhà Cửa Đời Sống', 'URL': 'https://tiki.vn/nha-cua-doi-song/c1883?src=c.1883.hamburger_menu_fly_out_banner'},
    {'Name': 'Hàng Tiêu Dùng - Thực Phẩm', 'URL': 'https://tiki.vn/bach-hoa-online/c4384?src=c.4384.hamburger_menu_fly_out_banner'},
    {'Name': 'Đồ chơi, Mẹ & Bé', 'URL': 'https://tiki.vn/me-va-be/c2549?src=c.2549.hamburger_menu_fly_out_banner'},
    {'Name': 'Làm Đẹp - Sức Khỏe', 'URL': 'https://tiki.vn/lam-dep-suc-khoe/c1520?src=c.1520.hamburger_menu_fly_out_banner'},
    {'Name': 'Thể Thao - Dã Ngoại', 'URL': 'https://tiki.vn/the-thao/c1975?src=c.1975.hamburger_menu_fly_out_banner'},
    {'Name': 'Xe Máy, Ô tô, Xe Đạp', 'URL': 'https://tiki.vn/o-to-xe-may-xe-dap/c8594?src=c.8594.hamburger_menu_fly_out_banner'},
    {'Name': 'Hàng quốc tế', 'URL': 'https://tiki.vn/hang-quoc-te/c17166?src=c.17166.hamburger_menu_fly_out_banner'},
    {'Name': 'Sách, VPP & Quà Tặng', 'URL': 'https://tiki.vn/nha-sach-tiki/c8322?src=c.8322.hamburger_menu_fly_out_banner'},
    {'Name': 'Voucher - Dịch Vụ - Thẻ Cào', 'URL': 'https://tiki.vn/voucher-dich-vu/c11312?src=c.11312.hamburger_menu_fly_out_banner'}]

CAT_LIMIT = 3
MAIN_CATS = MAIN_CATS[:CAT_LIMIT]


### GLOBALS ###
SAVE_FLAG   = False
RESET_FLAG  = False
RUN_FLAG    = False

DB_PATH     = './tiki_data.db'
MAX_PAGE    = 2

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()



######################
### BEGIN SCRAPING ###
######################

if RUN_FLAG:
    # Create database:
    if RESET_FLAG:
        drop_table('categories', conn, cur)
        drop_table('products', conn, cur)
    
        create_categories_table(conn,cur)
        create_products_table(conn, cur)

    # Add main categories to CATEGORY_SET
    Category.get_main_categories(MAIN_CATEGORIES, conn, cur, save=save_to_db)
    
    # Get all categories from CATEGORY_SET and their sub-categories
    Category.get_all_categories(conn, cur, save=save_to_db)
    
    # Get lowest sub-categories from the (sub-)categories we have
    lowest_sub_cats = [Category(*sub_cat_info) for sub_cat_info in get_lowest_subcat(conn).to_numpy()]

    # Scrape all products from all categories we just got above
    Category.scrape_all_categories(lowest_sub_cats, conn, cur, save=save_to_db, max_page=num_max_page)

    print('Script finished.')

else:
    print('RUN_FLAG was set to False.')

conn.close()
