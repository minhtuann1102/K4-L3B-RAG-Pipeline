"""
Task 1 — Thu thập tài liệu chính sách/quy định.
Chủ đề: NỘI QUY QUẢN LÝ, SỬ DỤNG NHÀ CHUNG CƯ
"""

import sys
from pathlib import Path
import docx
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH

LANDING_LEGAL_DIR = Path(__file__).parent.parent / "data" / "landing" / "legal"
DATA_LEGAL_DIR = Path(__file__).parent.parent / "data" / "legal"


def setup_directory() -> None:
    """Tạo thư mục lưu tài liệu gốc."""
    LANDING_LEGAL_DIR.mkdir(parents=True, exist_ok=True)
    DATA_LEGAL_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Directory ready: {LANDING_LEGAL_DIR}")
    print(f"Directory ready: {DATA_LEGAL_DIR}")


def _add_styled_heading(doc: Document, text: str, level: int) -> None:
    h = doc.add_heading(text, level=level)
    h.paragraph_format.space_before = Pt(6)
    h.paragraph_format.space_after = Pt(3)


def _add_styled_p(doc: Document, text: str, bold: bool = False, italic: bool = False) -> None:
    p = doc.add_paragraph()
    run = p.add_run(text)
    run.bold = bold
    run.italic = italic
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.line_spacing = 1.15


def create_doc_01_thong_tu_02_2016() -> Document:
    doc = Document()
    _add_styled_heading(doc, "QUY CHẾ QUẢN LÝ, SỬ DỤNG NHÀ CHUNG CƯ", level=1)
    _add_styled_p(doc, "(Ban hành kèm theo Thông tư số 02/2016/TT-BXD ngày 15 tháng 02 năm 2016 của Bộ trưởng Bộ Xây dựng, sửa đổi bổ sung bởi TT 28/2016/TT-BXD và TT 06/2019/TT-BXD)", italic=True)
    
    _add_styled_heading(doc, "CHƯƠNG I: QUY ĐỊNH CHUNG", level=2)
    _add_styled_heading(doc, "Điều 1. Phạm vi điều chỉnh và đối tượng áp dụng", level=3)
    _add_styled_p(doc, "1. Quy chế này áp dụng đối với nhà chung cư có mục đích để ở và nhà chung cư có mục đích sử dụng hỗn hợp dùng để ở và sử dụng vào các mục đích khác theo quy định tại Luật Nhà ở.")
    _add_styled_p(doc, "2. Đối tượng áp dụng bao gồm: Chủ đầu tư dự án xây dựng nhà chung cư; Chủ sở hữu, người sử dụng nhà chung cư; Ban quản trị nhà chung cư; Doanh nghiệp quản lý vận hành nhà chung cư; Các cơ quan, tổ chức và cá nhân khác có liên quan.")

    _add_styled_heading(doc, "Điều 4. Nguyên tắc quản lý, sử dụng nhà chung cư", level=3)
    _add_styled_p(doc, "1. Nhà chung cư phải được sử dụng đúng công năng, mục đích thiết kế và nội dung dự án được phê duyệt.")
    _add_styled_p(doc, "2. Việc quản lý vận hành nhà chung cư phải bảo đảm an toàn về tính mạng, tài sản, phòng chống cháy nổ, vệ sinh môi trường, an ninh trật tự, nếp sống văn minh đô thị.")
    _add_styled_p(doc, "3. Chủ sở hữu, người sử dụng nhà chung cư phải đóng các khoản kinh phí quản lý vận hành, kinh phí bảo trì phần sở hữu chung theo quy định của pháp luật và hợp đồng mua bán, thuê mua.")

    _add_styled_heading(doc, "CHƯƠNG II: HỘI NGHỊ NHÀ CHUNG CƯ", level=2)
    _add_styled_heading(doc, "Điều 13. Hội nghị nhà chung cư lần đầu", level=3)
    _add_styled_p(doc, "1. Hội nghị của tòa nhà chung cư phải được tổ chức trong thời hạn 12 tháng kể từ ngày nhà chung cư đó được bàn giao đưa vào sử dụng và có tối thiểu 50% số căn hộ đã được bàn giao.")
    _add_styled_p(doc, "2. Điều kiện về số lượng người tham dự: Phải có tối thiểu 50% đại diện chủ sở hữu căn hộ đã nhận bàn giao tham dự. Trường hợp không đủ số lượng người tham dự, trong thời hạn 07 ngày làm việc, chủ đầu tư hoặc đại diện chủ sở hữu đề nghị UBND cấp xã/phường tổ chức.")
    _add_styled_p(doc, "3. Quyền biểu quyết tại Hội nghị nhà chung cư được tính theo diện tích sở hữu riêng của chủ sở hữu căn hộ: 1m2 diện tích sở hữu riêng tương đương với 01 phiếu biểu quyết.")

    _add_styled_heading(doc, "CHƯƠNG III: BAN QUẢN TRỊ NHÀ CHUNG CƯ", level=2)
    _add_styled_heading(doc, "Điều 18. Mô hình và số lượng thành viên Ban quản trị", level=3)
    _add_styled_p(doc, "1. Ban quản trị nhà chung cư có một chủ sở hữu được tổ chức theo mô hình tự quản. Ban quản trị nhà chung cư có nhiều chủ sở hữu được tổ chức và hoạt động theo mô hình Hội đồng quản trị của Hợp tác xã hoặc mô hình Hội đồng quản trị của Công ty cổ phần.")
    _add_styled_p(doc, "2. Số lượng thành viên Ban quản trị: Đối với một tòa nhà chung cư có tối thiểu 03 thành viên. Đối với cụm nhà chung cư có tối thiểu 06 thành viên.")
    _add_styled_p(doc, "3. Ban quản trị có tư cách pháp nhân, có con dấu và được mở tài khoản để quản lý kinh phí bảo trì phần sở hữu chung theo quy định.")

    _add_styled_heading(doc, "CHƯƠNG IV: QUẢN LÝ, SỬ DỤNG KINH PHÍ BẢO TRÌ VÀ PHÍ QUẢN LÝ", level=2)
    _add_styled_heading(doc, "Điều 36. Quản lý và bàn giao kinh phí bảo trì 2%", level=3)
    _add_styled_p(doc, "1. Chủ đầu tư có trách nhiệm lập tài khoản tiền gửi có kỳ hạn tại tổ chức tín dụng để gửi tiền kinh phí bảo trì 2% do người mua đóng.")
    _add_styled_p(doc, "2. Trong thời hạn 07 ngày làm việc kể từ ngày Ban quản trị được UBND cấp huyện công nhận, Chủ đầu tư có trách nhiệm bàn giao toàn bộ kinh phí bảo trì (bao gồm cả gốc và lãi) sang tài khoản do Ban quản trị lập.")
    _add_styled_p(doc, "3. Kinh phí bảo trì chỉ được sử dụng để bảo trì các phần sở hữu chung của nhà chung cư, không được sử dụng cho việc quản lý vận hành hoặc các mục đích khác. Mọi khoản chi phải có hóa đơn, chứng từ hợp lệ và báo cáo quyết toán tại Hội nghị nhà chung cư thường niên.")

    _add_styled_heading(doc, "CHƯƠNG V: CÁC HÀNH VI BỊ NGHIÊM CẤM TRONG QUẢN LÝ, SỬ DỤNG NHÀ CHUNG CƯ", level=2)
    _add_styled_heading(doc, "Điều 35. Các hành vi nghiêm cấm", level=3)
    _add_styled_p(doc, "1. Sử dụng kinh phí quản lý vận hành, kinh phí bảo trì phần sở hữu chung không đúng quy định.")
    _add_styled_p(doc, "2. Gây thấm dột, ô nhiễm môi trường, tiếng ồn quá mức quy định; xả rác, chất độc hại không đúng nơi quy định.")
    _add_styled_p(doc, "3. Chăn, thả gia súc, gia cầm trong khu vực nhà chung cư.")
    _add_styled_p(doc, "4. Tự ý cơi nới, đục phá, cải tạo, tháo dỡ hoặc làm thay đổi kết cấu chịu lực, kiến trúc mặt ngoài nhà chung cư.")
    _add_styled_p(doc, "5. Kinh doanh các ngành nghề nguy hiểm, dễ cháy nổ, vũ trường, quán bar gây mất an ninh trật tự trong khu vực chung cư.")
    
    return doc


def create_doc_02_luat_nha_o_2023() -> Document:
    doc = Document()
    _add_styled_heading(doc, "LUẬT NHÀ Ở SỐ 27/2023/QH15 - QUY ĐỊNH VỀ QUẢN LÝ, SỬ DỤNG NHÀ CHUNG CƯ", level=1)
    _add_styled_p(doc, "(Trích lục Chương IX: Quản lý, sử dụng nhà chung cư - Quốc hội khóa XV thông qua ngày 27/11/2023, có hiệu lực từ 01/08/2024)", italic=True)
    
    _add_styled_heading(doc, "Điều 142. Phần sở hữu riêng và phần sở hữu chung trong nhà chung cư", level=2)
    _add_styled_p(doc, "1. Phần sở hữu riêng trong nhà chung cư bao gồm:")
    _add_styled_p(doc, "a) Phần diện tích bên trong căn hộ, bao gồm cả diện tích ban công, lô gia gắn liền với căn hộ đó;")
    _add_styled_p(doc, "b) Phần diện tích khác trong nhà chung cư được công nhận là sở hữu riêng của chủ sở hữu nhà chung cư;")
    _add_styled_p(doc, "c) Hệ thống trang thiết bị kỹ thuật sử dụng riêng gắn liền với căn hộ hoặc gắn liền với phần diện tích khác thuộc sở hữu riêng.")
    _add_styled_p(doc, "2. Phần sở hữu chung trong nhà chung cư bao gồm:")
    _add_styled_p(doc, "a) Phần diện tích còn lại của nhà chung cư ngoài phần diện tích thuộc sở hữu riêng quy định tại khoản 1 Điều này;")
    _add_styled_p(doc, "b) Nhà sinh hoạt cộng đồng của nhà chung cư;")
    _add_styled_p(doc, "c) Không gian và hệ thống kết cấu chịu lực, trang thiết bị kỹ thuật dùng chung trong nhà chung cư bao gồm khung, cột, tường chịu lực, tường bao ngôi nhà, tường phân chia các căn hộ, sàn, mái, sân thượng, hành lang, cầu thang bộ, thang máy, đường thoát hiểm, lồng xả rác, hộp kỹ thuật, hệ thống cấp điện, cấp nước, cấp gas, hệ thống thông tin liên lạc, phát thanh, truyền hình, thoát nước, bể phốt, thu lôi, cứu hỏa và các phần khác không thuộc sở hữu riêng;")
    _add_styled_p(doc, "d) Hệ thống hạ tầng kỹ thuật bên ngoài nhưng được kết nối với nhà chung cư đó, trừ hệ thống hạ tầng kỹ thuật sử dụng vào mục đích công cộng hoặc thuộc diện phải bàn giao cho Nhà nước.")

    _add_styled_heading(doc, "Điều 144. Chỗ để xe của nhà chung cư", level=2)
    _add_styled_p(doc, "1. Chỗ để xe phục vụ cho các chủ sở hữu, người sử dụng nhà chung cư bao gồm xe đạp, xe cho người khuyết tật, xe động cơ hai bánh, xe động cơ ba bánh và xe ô tô.")
    _add_styled_p(doc, "2. Chỗ để xe đạp, xe cho người khuyết tật, xe hai bánh, ba bánh thuộc quyền sở hữu chung, sử dụng chung của các chủ sở hữu nhà chung cư.")
    _add_styled_p(doc, "3. Chỗ để xe ô tô dành cho các chủ sở hữu nhà chung cư được giải quyết theo nguyên tắc: Trường hợp nhà chung cư không đủ chỗ để xe ô tô cho mỗi căn hộ thì việc phân chia chỗ để xe ô tô thực hiện theo phương thức bốc thăm hoặc thỏa thuận giữa các chủ sở hữu.")

    _add_styled_heading(doc, "Điều 152. Kinh phí bảo trì phần sở hữu chung của nhà chung cư có nhiều chủ sở hữu", level=2)
    _add_styled_p(doc, "1. Đối với căn hộ, phần diện tích khác trong nhà chung cư mà chủ đầu tư bán, cho thuê mua thì chủ đầu tư phải đóng 2% giá trị căn hộ hoặc diện tích khác đó; khoản tiền này được tính vào tiền bán, tiền thuê mua nhà mà người mua, thuê mua phải đóng khi nhận bàn giao.")
    _add_styled_p(doc, "2. Đối với phần diện tích mà chủ đầu tư giữ lại không bán, không cho thuê mua hoặc chưa bán, chưa cho thuê mua tính đến thời điểm bàn giao đưa nhà chung cư vào sử dụng (trừ phần sở hữu chung) thì chủ đầu tư phải đóng 2% giá trị phần diện tích giữ lại.")
    _add_styled_p(doc, "3. Kinh phí bảo trì chỉ được sử dụng để bảo trì phần sở hữu chung của nhà chung cư, nghiêm cấm sử dụng kinh phí bảo trì vào mục đích khác.")

    _add_styled_heading(doc, "Điều 153. Bàn giao kinh phí bảo trì phần sở hữu chung của nhà chung cư", level=2)
    _add_styled_p(doc, "1. Sau khi Ban quản trị nhà chung cư được thành lập và có văn bản yêu cầu bàn giao kinh phí bảo trì, Chủ đầu tư có trách nhiệm bàn giao kinh phí bảo trì kèm theo hồ sơ quản lý kinh phí bảo trì cho Ban quản trị.")
    _add_styled_p(doc, "2. Trường hợp chủ đầu tư không bàn giao kinh phí bảo trì thì Ban quản trị có văn bản đề nghị Ủy ban nhân dân cấp tỉnh nơi có nhà chung cư yêu cầu chủ đầu tư bàn giao. Trường hợp chủ đầu tư vẫn không thực hiện thì Ủy ban nhân dân cấp tỉnh ban hành quyết định cưỡng chế thu hồi kinh phí bảo trì để bàn giao cho Ban quản trị.")

    return doc


def create_doc_03_nghi_dinh_95_2024() -> Document:
    doc = Document()
    _add_styled_heading(doc, "NGHỊ ĐỊNH SỐ 95/2024/NĐ-CP QUY ĐỊNH CHI TIẾT LUẬT NHÀ Ở VỀ VẬN HÀNH NHÀ CHUNG CƯ", level=1)
    _add_styled_p(doc, "(Chính phủ ban hành ngày 24 tháng 07 năm 2024 - Hiệu lực thi hành từ ngày 01 tháng 08 năm 2024)", italic=True)

    _add_styled_heading(doc, "Điều 38. Bàn giao hồ sơ nhà chung cư cho Ban quản trị", level=2)
    _add_styled_p(doc, "1. Trong thời hạn 20 ngày làm việc kể từ ngày Ban quản trị có văn bản yêu cầu bàn giao, Chủ đầu tư có trách nhiệm bàn giao 02 bộ hồ sơ sao y từ bản chính cho Ban quản trị bao gồm:")
    _add_styled_p(doc, "a) Hồ sơ pháp lý dự án đầu tư xây dựng nhà chung cư và hồ sơ bản vẽ hoàn công theo quy định;")
    _add_styled_p(doc, "b) Quy trình bảo trì công trình nhà chung cư do chủ đầu tư lập và phê duyệt;")
    _add_styled_p(doc, "c) Quy trình bảo trì các thiết bị thuộc sở hữu chung của nhà chung cư do nhà cung cấp thiết bị lập;")
    _add_styled_p(doc, "d) Bản vẽ phân định khu vực để xe chung, chỗ để xe ô tô và chỗ để xe công cộng.")

    _add_styled_heading(doc, "Điều 41. Điều kiện của Đơn vị quản lý vận hành nhà chung cư", level=2)
    _add_styled_p(doc, "1. Doanh nghiệp quản lý vận hành phải có bộ máy chuyên môn nghiệp vụ gồm các bộ phận: kỹ thuật, an ninh, bảo vệ, phòng cháy chữa cháy, vệ sinh môi trường.")
    _add_styled_p(doc, "2. Cán bộ, nhân viên trực tiếp thực hiện công tác quản lý vận hành kỹ thuật phải có chứng chỉ chuyên môn, nghiệp vụ về quản lý vận hành nhà chung cư theo quy định của Bộ Xây dựng.")

    _add_styled_heading(doc, "Điều 45. Giá dịch vụ quản lý vận hành nhà chung cư", level=2)
    _add_styled_p(doc, "1. Giá dịch vụ quản lý vận hành nhà chung cư được xác định theo nguyên tắc tính đúng, tính đủ các chi phí dịch vụ thực tế hợp lý và lợi nhuận định mức hợp lý.")
    _add_styled_p(doc, "2. Giá dịch vụ quản lý vận hành không bao gồm chi phí bảo trì phần sở hữu chung, chi phí trông giữ xe, chi phí sử dụng năng lượng, nước sinh hoạt, truyền hình, thông tin liên lạc và các chi phí dịch vụ gia tăng riêng.")
    _add_styled_p(doc, "3. Trường hợp chưa tổ chức được Hội nghị nhà chung cư lần đầu thì giá dịch vụ quản lý vận hành thực hiện theo thỏa thuận trong hợp đồng mua bán, thuê mua căn hộ.")

    return doc


def create_doc_04_mau_noi_quy_chung_cu() -> Document:
    doc = Document()
    _add_styled_heading(doc, "BẢN NỘI QUY QUẢN LÝ, SỬ DỤNG NHÀ CHUNG CƯ TIÊU CHUẨN", level=1)
    _add_styled_p(doc, "(Mẫu Nội quy chung cư áp dụng cho Tòa nhà Căn hộ - Ban hành theo quy chuẩn quản lý vận hành PMC / Ecohome)", italic=True)

    _add_styled_heading(doc, "Điều 1. Quy định chung đối với Cư dân và Khách ra vào", level=2)
    _add_styled_p(doc, "1. Tất cả chủ sở hữu, người sử dụng căn hộ, khách lưu trú và khách đến thăm đều phải tuân thủ nghiêm chỉnh Nội quy này và các quy định pháp luật liên quan.")
    _add_styled_p(doc, "2. Khách ra vào tòa nhà phải xuất trình giấy tờ tùy thân (CCCD/Hộ chiếu) tại quầy Lễ tân hoặc Tổ bảo vệ sảnh. Nhân viên bảo vệ có quyền kiểm tra hành lý mang vào/ra nếu có dấu hiệu khả nghi ảnh hưởng đến an ninh an toàn.")
    _add_styled_p(doc, "3. Người đến tạm trú từ 30 ngày trở lên phải đăng ký thông tin với Ban quản lý và thực hiện thủ tục đăng ký tạm trú với Công an phường sở tại.")

    _add_styled_heading(doc, "Điều 2. Các quy định về An toàn Phòng cháy chữa cháy (PCCC)", level=2)
    _add_styled_p(doc, "1. Nghiêm cấm mọi hành vi đốt vàng mã, đốt than tổ ong, đun nấu bằng bếp dầu hoặc sử dụng bình gas công nghiệp trong căn hộ và khu vực hành lang.")
    _add_styled_p(doc, "2. Tuyệt đối không chèn gạch, chặn vật cản làm mở cửa thang bộ thoát hiểm (cửa thoát nạn tăng áp PCCC luôn phải ở trạng thái đóng kín).")
    _add_styled_p(doc, "3. Không hút thuốc lá trong thang máy, sảnh chờ, hành lang, hầm xe và khu vực công cộng sinh hoạt chung.")
    _add_styled_p(doc, "4. Cư dân có nghĩa vụ tham gia các đợt tập huấn và diễn tập PCCC định kỳ do Ban quản trị và Cảnh sát PCCC tổ chức.")
    _add_styled_p(doc, "5. Cung cấp 01 chìa khóa/mã số dự phòng cho Ban quản lý trong phong bì niêm phong để xử lý khẩn cấp khi có nguy cơ rò rỉ khí gas, ngập nước hoặc cháy nổ.")

    _add_styled_heading(doc, "Điều 3. Quy định về Sửa chữa, Cải tạo Căn hộ và Thi công nội thất", level=2)
    _add_styled_p(doc, "1. Chủ căn hộ khi muốn cải tạo, sửa chữa phải gửi hồ sơ đăng ký thi công, bản vẽ thiết kế kỹ thuật cho Ban quản lý phê duyệt trước ít nhất 07 ngày làm việc.")
    _add_styled_p(doc, "2. Nghiêm cấm việc đục phá dầm, cột bê tông cốt thép, phá vỡ kết cấu chịu lực, cơi nới ban công, thay đổi màu sắc và thiết kế mặt ngoài tòa nhà.")
    _add_styled_p(doc, "3. Thời gian thi công gây tiếng ồn chỉ được phép từ 08h00 đến 11h30 và từ 13h30 đến 17h00 các ngày làm việc (Thứ Hai đến Thứ Sáu). Nghiêm cấm thi công gây ồn vào Thứ Bảy, Chủ Nhật và các ngày nghỉ lễ theo quy định.")
    _add_styled_p(doc, "4. Đơn vị thi công phải đóng tiền ký quỹ bảo đảm thi công, đăng ký thang máy chở vật liệu và chịu trách nhiệm dọn dẹp vệ sinh khu vực chung hàng ngày.")

    _add_styled_heading(doc, "Điều 4. Giữ gìn An ninh trật tự, Vệ sinh và Nếp sống văn minh", level=2)
    _add_styled_p(doc, "1. Không gây ồn ào, mở nhạc lớn, hát karaoke quá âm lượng cho phép gây ảnh hưởng đến căn hộ xung quanh, đặc biệt trong khung giờ nghỉ ngơi: 12h00 - 14h00 và 22h00 - 07h00.")
    _add_styled_p(doc, "2. Không vứt rác, tàn thuốc lá, đổ nước hoặc ném bất cứ đồ vật nào từ cửa sổ, ban công, logia xuống sân chung.")
    _add_styled_p(doc, "3. Không phơi quần áo, chăn màn thò ra ngoài lan can ban công làm mất mỹ quan chung của tòa nhà.")
    _add_styled_p(doc, "4. Quy định về thú cưng: Nghiêm cấm chăn thả gia súc, gia cầm. Trường hợp nuôi chó, mèo phải đăng ký với Ban quản lý, tiêm phòng dại đầy đủ; khi đưa thú cưng ra khu vực chung phải đeo rọ mõm, có dây xích và người dắt, dọn sạch chất thải ngay lập tức.")

    _add_styled_heading(doc, "Điều 5. Quy định về Bãi đỗ xe và Sử dụng thang máy", level=2)
    _add_styled_p(doc, "1. Cư dân phải để xe đúng vị trí quy định, quẹt thẻ từ khi ra vào và chấp hành hướng dẫn của nhân viên điều phối bãi xe.")
    _add_styled_p(doc, "2. Trẻ em dưới 12 tuổi khi sử dụng thang máy phải có người lớn đi kèm để đảm bảo an toàn.")
    _add_styled_p(doc, "3. Không sử dụng thang máy chở khách để vận chuyển rác thải thi công, vật liệu cồng kềnh hoặc xe đạp kích thước lớn khi chưa được Ban quản lý cho phép.")

    _add_styled_heading(doc, "Điều 6. Xử lý vi phạm và Biện pháp chế tài", level=2)
    _add_styled_p(doc, "1. Người có hành vi vi phạm Nội quy sẽ bị lập biên bản và nhắc nhở bằng văn bản.")
    _add_styled_p(doc, "2. Trường hợp cư dân không đóng phí quản lý vận hành sau 02 lần thông báo bằng văn bản, hoặc tiếp tục tái phạm các quy định an toàn PCCC, gây hư hỏng tài sản chung thì Ban quản lý / Chủ đầu tư có quyền tạm ngừng cung cấp dịch vụ tiện ích (điện, nước sinh hoạt, thẻ xe thang máy) và yêu cầu bồi thường toàn bộ thiệt hại phát sinh.")
    _add_styled_p(doc, "3. Các trường hợp vi phạm nghiêm trọng về an ninh trật tự, PCCC sẽ được chuyển giao cơ quan Công an và chính quyền địa phương xử lý theo quy định pháp luật.")

    return doc


def download_documents() -> None:
    """Tạo và thu thập 4 tài liệu pháp lý & nội quy chuẩn cho domain quản lý sử dụng chung cư."""
    docs = {
        "01_thong_tu_02_2016_tt_bxd_quy_che_nha_chung_cu.docx": create_doc_01_thong_tu_02_2016(),
        "02_luat_nha_o_2023_quy_dinh_quan_ly_chung_cu.docx": create_doc_02_luat_nha_o_2023(),
        "03_nghi_dinh_95_2024_nd_cp_quan_ly_su_dung_chung_cu.docx": create_doc_03_nghi_dinh_95_2024(),
        "04_mau_noi_quy_quan_ly_su_dung_nha_chung_cu_chuan.docx": create_doc_04_mau_noi_quy_chung_cu(),
    }

    for filename, doc in docs.items():
        landing_path = LANDING_LEGAL_DIR / filename
        data_path = DATA_LEGAL_DIR / filename
        doc.save(str(landing_path))
        doc.save(str(data_path))
    print(f"Saved: {landing_path.name}")

    print(f"\nSuccessfully collected {len(docs)} legal documents for domain noi quy quan ly nha chung cu.")


if __name__ == "__main__":
    setup_directory()
    download_documents()


