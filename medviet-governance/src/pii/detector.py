# src/pii/detector.py
from presidio_analyzer import AnalyzerEngine, PatternRecognizer, Pattern
from presidio_analyzer.nlp_engine import NlpEngineProvider

_VN_NAMES = (
    "Nguyễn|Trần|Lê|Phạm|Hoàng|Huỳnh|Phan|Vũ|Võ|Đặng|Bùi|Đỗ|Hồ|Ngô|"
    "Dương|Lý|Đinh|Trịnh|Đào|Mai|Tô|Lâm|Tạ|Lương|Hà|Thái|Cao|Chu|Quách|"
    "Đoàn|Từ|Kiều|Tăng|Nghiêm|Văn|Anh|Hương|Phúc|Quang|Bảo|Huy|Thị|Thanh|"
    "Minh|Tuấn|Hưng|Phong|Long|Khánh|Trung|Dũng|Tùng|Sơn|Hải|Nam|Đức|Thắng|"
    "Tâm|Hiếu|Khoa|Linh|Trang|Lan|Hạnh|Yến|Nhung|Thảo|Ngọc|Phương|Hồng|"
    "Giang|Thương|Vy|Nhi|My|Chi|Thy|Uyên|Trâm|Trinh|Xuân|Như|Quyên|Diệu|"
    "Bích|Cúc|Hoa|Lệ|Ánh|Tuyết|Chị|Cô|Ông|Bà|Vinh|Khải|Kiên|Toàn|Cường|"
    "Tín|Thiện|Trí|Nhân|Bình|Lợi|Tài|Phát|Đạt|An|Hùng|Mạnh|Thành|Quân|"
    "Thịnh|Duy|Hiền|Hằng|Tú|Phượng|Vân|Loan|Nga|Thúy|Huệ|Dung|Hảo|Kim|"
    "Ngân|Thu|Hương|Mai|Đông|Tây|Bắc|Quý|Thuận|Tuệ|Lộc|Thọ|Phú|Quốc"
)


def build_vietnamese_analyzer() -> AnalyzerEngine:
    """Xây dựng AnalyzerEngine với các recognizer tùy chỉnh cho VN."""

    # --- TASK 2.2.1: CCCD recognizer (đúng 12 chữ số) ---
    cccd_recognizer = PatternRecognizer(
        supported_entity="VN_CCCD",
        supported_language="vi",
        patterns=[Pattern(
            name="cccd_pattern",
            regex=r"\b\d{12}\b",
            score=0.9
        )],
        context=["cccd", "căn cước", "chứng minh", "cmnd"]
    )

    # --- TASK 2.2.2: Phone recognizer (0[3|5|7|8|9]xxxxxxxx) ---
    phone_recognizer = PatternRecognizer(
        supported_entity="VN_PHONE",
        supported_language="vi",
        patterns=[Pattern(
            name="vn_phone",
            regex=r"\b0[35789]\d{8}\b",
            score=0.85
        )],
        context=["điện thoại", "sdt", "phone", "liên hệ"]
    )

    # Email recognizer cho tiếng Việt
    email_recognizer = PatternRecognizer(
        supported_entity="EMAIL_ADDRESS",
        supported_language="vi",
        patterns=[Pattern(
            name="email_pattern",
            regex=r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+",
            score=0.9
        )],
    )

    # Vietnamese name recognizer
    vn_name_recognizer = PatternRecognizer(
        supported_entity="PERSON",
        supported_language="vi",
        patterns=[Pattern(
            name="vn_name_word",
            regex=rf"\b(?:{_VN_NAMES})\b",
            score=0.6
        )],
        context=["tên", "bệnh nhân", "bác sĩ", "name", "họ tên",
                  "ho_ten", "patient"]
    )

    # --- TASK 2.2.3: NLP engine (multilingual model) ---
    provider = NlpEngineProvider(nlp_configuration={
        "nlp_engine_name": "spacy",
        "models": [{"lang_code": "vi",
                    "model_name": "xx_ent_wiki_sm"}]
    })
    nlp_engine = provider.create_engine()

    # --- TASK 2.2.4: Khởi tạo AnalyzerEngine và add recognizers ---
    analyzer = AnalyzerEngine(
        nlp_engine=nlp_engine,
        supported_languages=["vi"]
    )
    analyzer.registry.add_recognizer(cccd_recognizer)
    analyzer.registry.add_recognizer(phone_recognizer)
    analyzer.registry.add_recognizer(email_recognizer)
    analyzer.registry.add_recognizer(vn_name_recognizer)

    return analyzer


def detect_pii(text: str, analyzer: AnalyzerEngine) -> list:
    """
    Detect PII trong text tiếng Việt.
    Trả về list các RecognizerResult.
    """
    results = analyzer.analyze(
        text=text,
        language="vi",
        entities=["PERSON", "EMAIL_ADDRESS", "VN_CCCD", "VN_PHONE"],
        score_threshold=0.3,
    )
    return results
