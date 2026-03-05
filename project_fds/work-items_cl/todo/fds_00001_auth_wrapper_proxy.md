# TODO: 인가 통제 게이트웨이 API (Confluence, Jira 등)

todo_idx: fds_00001
상태: 통합 검증 완료 (28/28 PASS) — done 판정 대기
생성일: 2026-03-04
최종 갱신일: 2026-03-04
관련: 고객 요구사항 — 외부 서비스 인가 래퍼 구축

---

## 목적

고객이 Confluence, Jira 등 외부 서비스에 대한 **인가(Authorization) 통제 게이트웨이**를 요청.
단순 프록시가 아니라 **인가 정책 + 서비스 매핑을 DB 기반으로 통제하는 레이어**.

## 시스템 성격

> **인가 통제형 Keycloak 기반 프록시 게이트웨이 (화이트리스트 기반)**
> - 사용자 인증: Keycloak Access Token (JWT/OIDC)
> - DB 기반 서비스·URI 매핑 관리
> - 서비스별 인가 헤더 자동 주입 (외부 서비스 토큰은 별도)
> - uri_mappings = 허용 경로 화이트리스트 (경로 변환 없음)
> - 서비스/매핑 관리: DB 직접 CRUD (Admin API 엔드포인트 제거)

향후 확장 (Phase 2): pkey 교집합 강제, Fernet 암호화, Rate limit, proxy_logs

## 전체 아키텍처

```
Client
   ↓
FDS API (FastAPI)
   ├── 인증: Keycloak JWT 검증 (OIDC)
   ├── Proxy Router (/{sub_prefix}/{path:path}) — 동적 프록시
   ├── DB (SQLite → 향후 PostgreSQL) — 서비스/매핑 직접 관리
   └── httpx AsyncClient (외부 호출)
         ↓
   Confluence / Jira / ...
```

## 요구사항

### URL 패턴
```
{fdsapi_base_url}/{sub_prefix_uri}/{서비스별 URI}
```

- `fdsapi_base_url`: FDS API 서버 주소 (예: `http://localhost:8000`)
- `sub_prefix_uri`: 서비스 구분 접두사 (예: `conf`, `jira`)
- `서비스별 URI`: 실제 외부 서비스 엔드포인트 경로

### 예시
| 요청 URI | 프록시 대상 |
|---|---|
| `/conf/wiki/rest/api/content` | Confluence REST API |
| `/jira/rest/api/2/issue` | Jira REST API |

### DB 관리
- 서비스별 URI 매핑 정보를 **DB에서 관리**
- 샘플 구현: **SQLite** (운영 시 PostgreSQL 전환 가능 구조)

## 핵심 결정사항 (2026-03-04 확정)

| 항목 | 결정 | 비고 |
|---|---|---|
| 인증 주체 | Keycloak Access Token (JWT/OIDC) | X-ADMIN-KEY 대체 |
| 프록시 경로 | `/{sub_prefix}/{path:path}` 루트 레벨 | `/proxy/` prefix 불필요 |
| uri_mappings 역할 | 화이트리스트 (허용 경로만 통과) | 경로 변환 없음 |
| URI 매핑 검증 | prefix 매칭 | 와일드카드/정규식은 Phase 2 |
| 토큰 저장 | 평문 (MVP 샘플용) | Fernet 암호화는 Phase 2 |
| httpx timeout | 30초 고정 | 서비스별 설정은 Phase 2 |
| Rate limit | MVP 제외 | Phase 2 |
| 서비스/매핑 관리 | DB 직접 CRUD (Admin API 제거) | DBeaver/스크립트 등 |

## 작업 항목 (구현 순서)

1. [x] DB 모델 + 세션 초기화 (SQLAlchemy + aiosqlite)
2. [x] ~~Admin API 완성~~ → DB 직접 CRUD로 대체 (Admin 라우터 제거 예정)
3. [x] Proxy 구현 (sub_prefix → DB 조회 → 화이트리스트 확인 → httpx 전달)
4. [x] 인가 헤더 주입 (bearer, basic, api_key)
5. [x] 샘플 데이터 시딩 (Confluence, Jira 초기 데이터)
6. [x] 동작 검증 (통합 테스트 28/28 PASS)

## Rule 102 실행 결과 (2026-03-04)

- [x] DB 모델 + 세션 초기화 구현
  - `app/db.py`, `app/models.py`, `app/schemas.py`
- [x] Admin API 구현 + API Key 보호
  - `app/routers/admin.py`, `app/deps.py`, `app/crud/service.py`, `app/crud/mapping.py`
- [x] Proxy 구현 + 화이트리스트 검사 + 업스트림 전달
  - `app/routers/proxy.py`
- [x] 인가 헤더 주입 분기 구현
  - `bearer`, `basic`, `api_key`
- [x] 샘플 데이터 시딩 구현
  - `app/bootstrap.py` (startup 시 conf/jira 기본 데이터 주입)
- [x] 동작 검증 (통합 테스트 `test_verify.py`)
  - 28/28 PASS (2026-03-04)
  - 0단계: Admin API 인증 (no key→401, wrong key→403) ✓
  - 1단계: Admin CRUD 전체 (services+mappings CRUD, 중복409, 삭제후404) ✓
  - 2단계: 프록시 (미등록→404, 차단경로→403, 비활성→403, 화이트리스트→upstream 도달) ✓
  - 3단계: healthz→200, Swagger→200, OpenAPI tags(admin,proxy) ✓
- [x] 프록시 버그 수정: accept-encoding/content-encoding 이중 처리 방지

## 구현 방식 비교 검토 (FastAPI vs Nginx)

- 상세 문서: `todo_issues/fds_00001_03_fastapi_vs_nginx_review.md`
- 결론: MVP는 FastAPI 단독 적합, 운영 전환 시 Nginx(Edge) + FastAPI(Gateway) 하이브리드 권장
- Nginx 단독은 DB 기반 동적 인가 제어 요구사항에 부적합

## 외부 서비스 API 미지정 문제 분석

- 상세 문서: `todo_issues/fds_00001_04_unknown_api_design_limits.md`
- 문제: 서비스마다 API 구조가 달라 화이트리스트 사전 등록에 한계
- 접근 방법: 5가지 비교 (대분류 prefix / 전체 허용 / 정규식 / 거부 목록 / 하이브리드)
- MVP: 현재 방식(대분류 prefix) 유지, Phase 2에서 서비스별 access_mode 선택 구조 권장

## 경로 파라미터 패턴 매칭 검토

- 상세 문서: `todo_issues/fds_00001_05_path_parameter_pattern.md`
- 문제: 고객 지정 패턴(`/page/{page_id}/{action}`)을 prefix 매칭으로 정확히 표현 불가
- 해결: `match_type: segment` 추가 — `{param}`을 세그먼트 단위로 매칭
- 구현 규모: ~20줄 (models/schemas/crud 소규모 변경)
- 판단: 고객 패턴 중 B·C·D 유형 존재 시 즉시 구현, 없으면 Phase 2

## 외부 서비스 응답 통합 포맷 검토

- 상세 문서: `todo_issues/fds_00001_06_unified_response_format.md`
- 문제: 서비스마다 응답 구조가 달라 클라이언트가 서비스별 파싱 로직 필요
- 통합 수준: Level 1(엔벨로프) ~ Level 4(필드 매핑) 단계적 접근
- 권장: Phase 1에서 엔벨로프 래핑 + 에러 포맷 통합 (~30줄), 어댑터는 필요 시 점진 추가

## 인가 교집합 설계 (pkey 권한 × 외부 토큰 권한)

- 설계 문서: `todo_issues/fds_00001_07_pkey_auth_intersection_design.md`
- 해결 방법: `todo_issues/fds_00001_08_pkey_intersection_solution.md`
- 문제: 외부 서비스 토큰(서비스 계정)이 사용자 인가 범위보다 넓어 권한 초과 접근 가능
- 원칙: 사용자 접근 범위 = 사용자 인가 pkey ∩ 외부 토큰 pkey (교집합)
- 해결: 사전 검증(경로 pkey 추출→차단) + 응답 필터링(목록 pkey 제거) 이중 방어
- 관리 라우터: DB CRUD로 대체 (admin API 엔드포인트 제거)

## 다음 실행 액션

1. `fds rule105 00001`로 done 판정 진행

## 보안 (MVP 범위)

- DB 등록 서비스만 프록시 허용 (미등록 → 404, 비활성 → 403)
- uri_mappings 화이트리스트 매칭 (미등록 경로 차단)
- 사용자 인증: Keycloak JWT 검증 (OIDC)
- ~~Admin API는 `X-ADMIN-KEY` 헤더 필수~~ → 제거 (DB 직접 관리)

### Phase 2 보안 (MVP 제외)
- auth_value Fernet 암호화 + Vault 연동
- SSRF 방지: 내부 IP 대역 차단
- Rate limit (per-service)
- proxy_logs 감사 추적

## 완료 판정 기준

| 기준 | 검증 방법 |
|---|---|
| DB 저장/조회 | DB 직접 조작으로 서비스·URI CRUD 확인 |
| 프록시 정상 동작 | httpx 호출 성공 (외부 서비스 응답 반환) |
| 인가 헤더 자동 주입 | 외부 서비스에서 401 없이 응답 |
| CRUD 가능 | DB 직접 조작 (DBeaver/SQLite CLI) |
| Swagger 전체 노출 | `/docs`에서 전체 API 확인 |

## 산출물

### 앱 코드
| 파일 | 설명 |
|---|---|
| `app/db.py` | DB 엔진·세션 관리 |
| `app/models.py` | SQLAlchemy 모델 (services, uri_mappings) |
| `app/schemas.py` | Pydantic 요청/응답 스키마 |
| `app/crud/` | service layer 분리 (CRUD 로직) |
| `app/routers/proxy.py` | 프록시 라우터 |
| `app/auth/keycloak.py` | Keycloak JWT 검증 (신규) |
| ~~`app/routers/admin.py`~~ | ~~관리 API 라우터~~ → 제거 (DB 직접 CRUD) |

### 기타
| 파일 | 설명 |
|---|---|
| `requirements.txt` | 의존성 (sqlalchemy, aiosqlite, httpx 추가) |
| `fds.db` | SQLite 샘플 DB |

## MVP 범위

| 기능 | 포함 | 비고 |
|---|---|---|
| services CRUD | O | DB 직접 관리 (Admin API 제거) |
| uri_mappings CRUD | O | DB 직접 관리 (Admin API 제거) |
| 프록시 호출 + 인가 주입 | O | 핵심 기능 |
| 미등록 서비스 404 / 비활성 403 | O | 보안 최소선 |
| 화이트리스트 경로 확인 | O | uri_mappings 기반 |
| Keycloak JWT 인증 | O | OIDC Access Token 검증 |
| 샘플 시딩 | O | conf, jira |
| 토큰 암호화 (Fernet) | X | Phase 2 |
| SSRF IP 필터링 | X | Phase 2 |
| Rate limit | X | Phase 2 |
| proxy_logs 로깅 | X | Phase 2 |

## 후속 작업 (Phase 2)

- pkey 교집합 강제 (사용자 인가 pkey ∩ 외부 토큰 pkey)
- 실제 Confluence/Jira 연동 테스트
- auth_value Fernet 암호화 + Vault 연동
- PostgreSQL 전환 + Redis 캐시 (service lookup)
- 요청/응답 로깅 + 감사 추적 (proxy_logs 테이블)
- Rate limit + Circuit breaker (tenacity)
- 서비스별 Timeout 설정 + Async connection pool 튜닝
