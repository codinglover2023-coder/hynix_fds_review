# fds_00001 — Validation & Output: 인가 통제 게이트웨이 API

todo_idx: fds_00001
issue_idx: 02
생성일: 2026-03-04

---

## 목적

구현 결과 검증 체크리스트 및 산출물 정의.

## 검증 체크리스트

### DB 계층
- [ ] SQLite DB 파일 생성 정상
- [ ] services 테이블 CRUD 동작
- [ ] uri_mappings 테이블 CRUD 동작
- [ ] FK 제약 조건 정상 동작
- [ ] updated_at 자동 갱신 확인

### 관리 API (`/api/admin/`)
- [ ] `POST /services` — 서비스 등록
- [ ] `GET /services` — 서비스 목록 조회
- [ ] `GET /services/{id}` — 서비스 상세 조회
- [ ] `PUT /services/{id}` — 서비스 수정
- [ ] `DELETE /services/{id}` — 서비스 삭제
- [ ] `POST /services/{id}/mappings` — URI 매핑 등록
- [ ] `GET /services/{id}/mappings` — URI 매핑 조회
- [ ] `DELETE /mappings/{id}` — URI 매핑 삭제

### 프록시 (`/{sub_prefix}/{path:path}`)
- [ ] 등록된 서비스로 프록시 요청 정상 전달
- [ ] 인가 헤더 자동 주입 (bearer)
- [ ] 인가 헤더 자동 주입 (basic)
- [ ] 인가 헤더 자동 주입 (api_key)
- [ ] Query params 유지 전달
- [ ] Request body 유지 전달
- [ ] Response status code 유지 반환
- [ ] 미등록 서비스 요청 시 404 응답
- [ ] 비활성 서비스 요청 시 403 응답
- [ ] 외부 서비스 오류 시 적절한 에러 응답

### 보안
- [ ] DB 등록 서비스만 호출 가능 (오픈 프록시 아님)
- [ ] is_active=False 서비스 차단
- [ ] uri_mappings 미등록 경로 차단

### Swagger UI
- [ ] `/docs` 에서 전체 API 확인 가능
- [ ] Admin/Proxy 라우터 태그 분리 표시
- [ ] 각 엔드포인트 설명·예시 표시

## 검증 시나리오

### 1단계: Admin API
```bash
# 서비스 등록
curl -X POST http://localhost:8000/api/admin/services \
  -H "Content-Type: application/json" \
  -d '{"name":"confluence","sub_prefix":"conf","base_url":"https://company.atlassian.net","auth_type":"bearer","auth_value":"sample_token"}'

# 서비스 목록 확인
curl http://localhost:8000/api/admin/services

# URI 매핑 등록
curl -X POST http://localhost:8000/api/admin/services/1/mappings \
  -H "Content-Type: application/json" \
  -d '{"path_pattern":"/wiki/rest/api/*","description":"Confluence REST API"}'
```

### 2단계: 프록시 호출
```bash
# Confluence API 프록시
curl http://localhost:8000/conf/wiki/rest/api/content

# 미등록 서비스 → 404
curl http://localhost:8000/unknown/some/path

# 비활성 서비스 → 403 (서비스 비활성화 후)
curl http://localhost:8000/conf/wiki/rest/api/content
```

### 3단계: Swagger UI
- `http://localhost:8000/docs` 접속
- Admin/Proxy 태그별 엔드포인트 확인
- Try it out으로 직접 테스트

## 산출물

### 앱 코드
| 파일 | 설명 |
|---|---|
| `app/__init__.py` | create_app() 팩토리 + lifespan (httpx client 관리) |
| `app/db.py` | async engine + session (SQLite) |
| `app/models.py` | SQLAlchemy 모델 (services, uri_mappings) |
| `app/schemas.py` | Pydantic 요청/응답 스키마 |
| `app/routes.py` | 라우터 등록 (admin, proxy, sample) |
| `app/crud/__init__.py` | CRUD 패키지 |
| `app/crud/service.py` | services CRUD |
| `app/crud/mapping.py` | uri_mappings CRUD |
| `app/routers/admin.py` | 관리 API 라우터 |
| `app/routers/proxy.py` | 프록시 라우터 |
| `app/routers/sample.py` | 기존 샘플 라우터 (유지) |

### 기타
| 파일 | 설명 |
|---|---|
| `requirements.txt` | 의존성 (fastapi, uvicorn, sqlalchemy, aiosqlite, httpx) |
| `fds.db` | SQLite 샘플 DB (런타임 생성) |
| `main.py` | uvicorn 진입점 |

## 후속 산출물 (운영 확장 시)

| 파일 | 설명 |
|---|---|
| `app/security.py` | Fernet 암호화 + SSRF 필터 |
| `app/models.py` (확장) | proxy_logs 테이블 추가 |
| `app/middleware/rate_limit.py` | Rate limit 미들웨어 |
| `alembic/` | DB 마이그레이션 (PostgreSQL 전환 시) |

## 다음 액션

1. 구현 완료 후 체크리스트 순차 검증
2. 전체 통과 시 상태 → `완료`로 변경
