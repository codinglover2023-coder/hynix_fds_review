# fds_00001 — Validation & Output: 인가 통제 게이트웨이 API

todo_idx: fds_00001
issue_idx: 02
생성일: 2026-03-04
최종 갱신일: 2026-03-04

---

## 목적

구현 결과 검증 체크리스트 및 산출물 정의.
MVP 범위: 인가 통제형 단일 토큰 프록시 게이트웨이 (화이트리스트 기반)

## 검증 체크리스트 (2026-03-04 통합 테스트 28/28 PASS)

### DB 계층
- [x] SQLite DB 파일 생성 정상
- [x] services 테이블 CRUD 동작
- [x] uri_mappings 테이블 CRUD 동작
- [x] FK 제약 조건 정상 동작
- [x] updated_at 자동 갱신 확인

### 관리 API (`/api/admin/`) — X-ADMIN-KEY 보호
- [x] `X-ADMIN-KEY` 헤더 누락 시 401 응답
- [x] `X-ADMIN-KEY` 헤더 불일치 시 403 응답
- [x] `POST /services` — 서비스 등록 (201, 중복 409)
- [x] `GET /services` — 서비스 목록 조회
- [x] `GET /services/{id}` — 서비스 상세 조회 (삭제 후 404)
- [x] `PUT /services/{id}` — 서비스 수정
- [x] `DELETE /services/{id}` — 서비스 삭제 (204)
- [x] `POST /services/{id}/mappings` — URI 매핑 등록
- [x] `GET /services/{id}/mappings` — URI 매핑 조회
- [x] `DELETE /mappings/{id}` — URI 매핑 삭제

### 프록시 (`/{sub_prefix}/{path:path}`) — 루트 레벨, 단일 토큰
- [x] 등록된 서비스로 프록시 요청 정상 전달 (Conf→401, Jira→403 = upstream 도달)
- [x] FDS 단일 서비스 토큰으로 인가 헤더 주입 (bearer)
- [x] 인가 헤더 자동 주입 (basic) — 코드 구현 확인
- [x] 인가 헤더 자동 주입 (api_key) — 코드 구현 확인
- [x] Query params 유지 전달 (upstream 도달 확인)
- [x] Request body 유지 전달 (POST upstream 도달 확인)
- [x] Response status code 유지 반환
- [x] httpx timeout 30초 설정 확인
- [x] 미등록 서비스 요청 시 404 응답
- [x] 비활성 서비스 요청 시 403 응답
- [x] 외부 서비스 오류 시 적절한 에러 응답

### 보안 (MVP 범위)
- [x] DB 등록 서비스만 호출 가능 (오픈 프록시 아님)
- [x] is_active=False 서비스 차단
- [x] uri_mappings 화이트리스트 prefix 매칭 (미등록 경로 → 403)
- [x] Admin API: X-ADMIN-KEY 없으면 접근 불가

### Swagger UI
- [x] `/docs` 에서 전체 API 확인 가능
- [x] Admin/Proxy 라우터 태그 분리 표시 (admin, proxy, health, sample)
- [x] 각 엔드포인트 설명·예시 표시

## 검증 시나리오

### 0단계: Admin API 인증 확인
```bash
# X-ADMIN-KEY 없이 → 401
curl http://localhost:8000/api/admin/services

# X-ADMIN-KEY 불일치 → 403
curl -H "X-ADMIN-KEY: wrong_key" http://localhost:8000/api/admin/services
```

### 1단계: Admin API (X-ADMIN-KEY 포함)
```bash
# 서비스 등록
curl -X POST http://localhost:8000/api/admin/services \
  -H "Content-Type: application/json" \
  -H "X-ADMIN-KEY: {설정된_키}" \
  -d '{"name":"confluence","sub_prefix":"conf","base_url":"https://company.atlassian.net","auth_type":"bearer","auth_value":"sample_token"}'

# 서비스 목록 확인
curl -H "X-ADMIN-KEY: {설정된_키}" http://localhost:8000/api/admin/services

# URI 매핑 등록 (화이트리스트 prefix)
curl -X POST http://localhost:8000/api/admin/services/1/mappings \
  -H "Content-Type: application/json" \
  -H "X-ADMIN-KEY: {설정된_키}" \
  -d '{"path_pattern":"/wiki/rest/api","description":"Confluence REST API"}'
```

### 2단계: 프록시 호출
```bash
# Confluence API 프록시 (화이트리스트 경로)
curl http://localhost:8000/conf/wiki/rest/api/content

# 미등록 서비스 → 404
curl http://localhost:8000/unknown/some/path

# 화이트리스트 미등록 경로 → 403
curl http://localhost:8000/conf/some/blocked/path

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
| `app/__init__.py` | create_app() 팩토리 + lifespan (httpx client + DB init) |
| `app/db.py` | async engine + session (SQLite) |
| `app/models.py` | SQLAlchemy 모델 (services, uri_mappings) |
| `app/schemas.py` | Pydantic 요청/응답 스키마 |
| `app/deps.py` | 의존성 (DB 세션, Admin API Key 검증) |
| `app/routes.py` | 라우터 등록 (admin, proxy, sample) |
| `app/crud/__init__.py` | CRUD 패키지 |
| `app/crud/service.py` | services CRUD |
| `app/crud/mapping.py` | uri_mappings CRUD |
| `app/routers/admin.py` | 관리 API 라우터 (X-ADMIN-KEY 보호) |
| `app/routers/proxy.py` | 프록시 라우터 (단일 토큰, 화이트리스트) |
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

## 추가 검증 사항 (Rule 102 실행 중 발견)

- [x] proxy `filter_request_headers`: `accept-encoding` 제거 (이중 압축 방지)
- [x] proxy `filter_response_headers`: `content-encoding` 제거 (httpx 디코딩 후 전달)

## 다음 액션

1. ~~구현 완료 후 체크리스트 순차 검증~~ → 28/28 PASS (2026-03-04)
2. `fds rule105 00001`로 done 판정 진행
