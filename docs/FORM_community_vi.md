# The community Google Form — what respondents were shown

The pre-protocol community batch (PROTOCOL amendment 2026-10-04) took part of its messages
through a Google Form. This file is the form's text as respondents saw it, verbatim, because it is
the only record of what they agreed to; an English gloss and a comparison with the consent form
the protocol will use follow. Dates the form was open: **[FILL: from – to]**.

## Nguyên văn (as shown)

> **PHIẾU THU THẬP TIN NHẮN SMS (SPAM/PHISHING)**
>
> **Bối cảnh dự án:**
> Dù các bộ lọc tin nhắn rác hiện nay rất phát triển, nhưng do đặc trưng ngôn ngữ tiếng Việt vô
> cùng phức tạp, các công cụ này vẫn chưa đạt độ chính xác cao vì thiếu hụt dữ liệu thực tế. Vì
> vậy, chúng em mở Form này nhằm thu thập các tin nhắn SMS (cả tin nhắn bình thường và tin nhắn
> rác/lừa đảo) để xây dựng một bộ dữ liệu chuẩn xác nhất.
>
> **Cam kết bảo mật (Quan trọng):**
> - Dự án này hoàn toàn vì mục đích nghiên cứu phi lợi nhuận và sẽ đóng góp miễn phí cho cộng
>   đồng Khoa học máy tính, học máy ở Việt Nam.
> - Mọi thông tin cá nhân (Tên, số điện thoại, số tài khoản, OTP...) xuất hiện trong tin nhắn sẽ
>   được chúng em mã hóa và ẩn danh HOÀN TOÀN. Chúng em cam kết không lưu trữ bất kỳ thông tin nào
>   có thể định danh người gửi.
>
> Sự đóng góp (dù chỉ là 1-2 tin nhắn) của Cô/Chú, Anh/Chị và các bạn là mảnh ghép vô cùng quý
> giá cho nghiên cứu này.
> Nhóm chúng em xin chân thành cảm ơn!
>
> Việc cung cấp tin nhắn từ quý anh chị cô chú đồng nghĩa là anh chị cô chú đồng ý cung cấp các
> tin nhắn phục vụ cho mục đích học thuật

## English gloss

*SMS collection form (spam/phishing).* Spam filters still do poorly on Vietnamese for lack of
real data; this form collects SMS, both ordinary and spam/scam, to build an accurate dataset.
*Confidentiality:* the project is non-profit research and will be contributed free to the
Vietnamese computer-science and machine-learning community; every personal detail in a message
(name, phone number, account number, OTP…) will be encoded and fully anonymised; nothing that
could identify the sender will be stored. Even one or two messages help. *By providing messages
you agree to their use for academic purposes.*

## What it covers, and what it does not

Measured against `CONSENT_vi.md`, the form the protocol will use:

| the consent form says | the community form | consequence |
|---|---|---|
| purpose: a research dataset | yes, in the same words | covered |
| the dataset will be **published, permanently** | implied ("đóng góp miễn phí cho cộng đồng"), not stated as publication, not stated as permanent | the paper says respondents were told the data would be contributed to the community for research, and **not** that they were told it would be published permanently |
| withdrawal possible until deposit, impossible after | not mentioned | no withdrawal was offered; none can be performed, since submissions are unattributed |
| personal data redacted; **links kept** | "mã hóa và ẩn danh HOÀN TOÀN"; links not mentioned | the promise is wider than what is done: the pipeline redacts, it does not encrypt, and it keeps links. The paper states what was actually done |
| nothing identifying the contributor is stored | same promise, kept: no name, contact or device detail was recorded | covered |
| only machine-sent messages; **never a personal number, never person-to-person** | asks for "tin nhắn bình thường" too, no sender rule | ordinary messages submitted through the form may include person-to-person texts, which the protocol excludes; the batch so far holds none, and any legitimate batch from the form must be screened for them before ingest |
| recruitment by someone with no assessment role; anonymous; nothing attached | the form was anonymous; who was invited and by whom is **[FILL]** | state it |

The form is a record of purpose and anonymity, not of informed consent to permanent publication.
That is the gap the ethics application has to rule on, and the data article says so in those words.
