# AutoSkill Hominhtuan95 – Lộ trình 7 tọa độ, 5 phút/điểm

Chế độ **Đi tuần tự nhiều tọa độ (lặp vòng)** được bật mặc định.

1. Mở game, nhấn Alt+D mở bản đồ. Trong AutoSkill chọn đúng HWND.
2. Nhấn lần lượt **Lấy ô X**, **Lấy ô Y**, **Lấy Dò tìm**; mỗi lần có 4 giây để di chuột tới đúng ô/nút trên bản đồ.
3. Đóng bản đồ bằng Alt+D. Bật **Auto Train** và **Đi tuần tự nhiều tọa độ**.
4. Danh sách mặc định: 265,122 → 215,075 → 121,086 → 093,141 → 130,182 → 177,204 → 245,146 → lặp lại.
5. Chu kỳ mặc định **5 phút**: đi điểm đầu ngay khi nhấn Chạy/F1, sau 5 phút gửi lệnh đến điểm kế tiếp. Mỗi vòng 35 phút (tính theo lịch chuyển điểm, chưa bao gồm thời gian gửi thao tác).
6. Bấm Chạy hoặc F1 khi cửa sổ AutoSkill được chọn. F1 chỉ điều khiển phiên AutoSkill đang được chọn.

**Giới hạn:** Bản này không đọc tọa độ nhân vật hay kiểm tra đã đến đích. Thời gian tính từ lúc lệnh Dò tìm được gửi, không phải lúc nhân vật tới nơi. Các phím gửi nền bằng PostMessage có thể bị game bỏ qua; phải thử thực tế. Tọa độ chuột hiệu chỉnh dùng theo cửa sổ game và có thể cần hiệu chỉnh lại nếu đổi kích thước game.

**Bảo mật:** Không đưa PRIVATE_LICENSE_KEY.pem lên GitHub. Cần sử dụng mã nguồn đã chứa đúng khóa công khai khớp với khóa bí mật của bạn. Nếu thay mã nguồn bằng bản chưa cấu hình khóa công khai, hãy sao lưu và chuyển đúng PUBLIC_KEY_HEX từ bản hiện tại hoặc chạy lại bước cấu hình với khóa hiện có; không tự tạo bộ khóa mới.
