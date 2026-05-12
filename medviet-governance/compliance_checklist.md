# NĐ13/2023 Compliance Checklist — MedViet AI Platform

## A. Data Localization
- [x] Tất cả patient data lưu trên servers đặt tại Việt Nam
- [x] Backup cũng phải ở trong lãnh thổ VN
- [x] Log việc transfer data ra ngoài nếu có

## B. Explicit Consent
- [x] Thu thập consent trước khi dùng data cho AI training
- [x] Có mechanism để user rút consent (Right to Erasure) — endpoint DELETE /api/patients/{id}
- [x] Lưu consent record với timestamp

## C. Breach Notification (72h)
- [x] Có incident response plan
- [x] Alert tự động khi phát hiện breach — Prometheus alerting rules
- [x] Quy trình báo cáo đến cơ quan có thẩm quyền trong 72h

## D. DPO Appointment
- [x] Đã bổ nhiệm Data Protection Officer
- [x] DPO có thể liên hệ tại: dpo@medviet.vn

## E. Technical Controls (mapping từ requirements)
| NĐ13 Requirement | Technical Control | Status | Owner |
|-----------------|-------------------|--------|-------|
| Data minimization | PII anonymization pipeline (Presidio) — detect CCCD, phone, email, tên; anonymize bằng replace/mask/hash | ✅ Done | AI Team |
| Access control | RBAC (Casbin) + ABAC (OPA) — 4 roles (admin, ml_engineer, data_analyst, intern), deny-by-default | ✅ Done | Platform Team |
| Encryption | AES-256-GCM envelope encryption at rest (SimpleVault), TLS 1.3 in transit (nginx/load balancer) | ✅ Done | Infra Team |
| Audit logging | Structured JSON access logs qua FastAPI middleware + CloudWatch aggregation; mỗi API call ghi lại user, action, resource, timestamp | ✅ Done | Platform Team |
| Breach detection | Prometheus + Grafana stack: monitor bất thường trong access patterns, alert khi số 403 tăng đột biến hoặc data export vượt ngưỡng | ✅ Done | Security Team |

## F. Chi tiết Technical Solutions cho các hạng mục đã hoàn thành

### Audit Logging
- **Implementation**: FastAPI middleware ghi structured JSON log cho mỗi request (user, role, endpoint, method, status_code, timestamp, IP).
- **Storage**: Log được gửi đến CloudWatch Log Groups với retention 365 ngày.
- **Query**: Dùng CloudWatch Insights để truy vấn lịch sử access theo user/resource.

### Breach Detection
- **Prometheus Metrics**: Custom metrics cho số lượng 401/403 responses, data export volume, unusual access time.
- **Alert Rules**: Trigger alert khi 403 rate > 10/phút (brute force), data export > 100MB/giờ, access ngoài giờ làm việc.
- **Grafana Dashboard**: Real-time dashboard hiển thị access patterns, anomaly score, alert status.
- **Response**: Alert gửi qua Slack/Email → Security team investigate trong 30 phút → Escalate nếu confirmed breach → Báo cáo cơ quan trong 72h.
