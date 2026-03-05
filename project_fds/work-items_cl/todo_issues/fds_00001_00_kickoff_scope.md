# fds_00001 — Kickoff Scope: 인가 통제 게이트웨이 API

todo_idx: fds_00001
issue_idx: 00
생성일: 2026-03-04
최종 갱신일: 2026-03-04

---

## 목적

Confluence, Jira 등 외부 서비스에 대한 인가 통제 게이트웨이를 FastAPI 기반으로 구축.
SQLite 샘플로 URI 매핑 DB 관리 구조를 검증한다.

## 현재 결정사항

1. **시스템 성격**: **인가 통제형 Keycloak 기반 프록시 게이트웨이 (화이트리스트 기반)**
2. **인증 주체**: Keycloak Access Token (JWT/OIDC)
3. **URL 구조**: `{fdsapi_base_url}/{sub_prefix_uri}/{서비스별 URI}` — 루트 레벨
4. **DB**: SQLite (샘플) — 운영 시 PostgreSQL 전환 가능 구조
5. **ORM**: SQLAlchemy (async) + aiosqlite
6. **HTTP 클라이언트**: httpx AsyncClient (lifespan에서 생성/해제, 30초 timeout)
7. **인가 방식**: 서비스별 인증 정보를 DB에 저장(MVP: 평문), 프록시 시 헤더에 주입
8. **uri_mappings 역할**: 허용 경로 화이트리스트 (경로 변환 없음, prefix 매칭)
9. **레이어 분리**: Proxy 로직과 Admin 로직 분리 (crud/ 디렉토리)
10. **서비스/매핑 관리**: DB 직접 CRUD (Admin API 엔드포인트 제거, DBeaver/스크립트 사용)

## SQLite 스키마 (확정)

### services 테이블
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | INTEGER PK | 자동 증가 |
| name | TEXT UNIQUE | 서비스명 (예: confluence, jira) |
| sub_prefix | TEXT UNIQUE | URL 접두사 (예: conf, jira) |
| base_url | TEXT NOT NULL | 외부 서비스 기본 URL |
| auth_type | TEXT NOT NULL | 인증 방식 (bearer, basic, api_key) |
| auth_value | TEXT NOT NULL | 인증 값 (MVP: 평문, Phase 2: Fernet 암호화) |
| is_active | BOOLEAN DEFAULT TRUE | 활성화 여부 |
| created_at | DATETIME | 생성일시 |
| updated_at | DATETIME | 수정일시 |

### uri_mappings 테이블
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | INTEGER PK | 자동 증가 |
| service_id | INTEGER FK | services.id 참조 |
| path_pattern | TEXT NOT NULL | 허용 경로 prefix (화이트리스트, 예: `/rest/api/2`) |
| description | TEXT | 설명 |
| is_active | BOOLEAN DEFAULT TRUE | 활성화 여부 |
| created_at | DATETIME | 생성일시 |

> prefix 기반 매핑만 하면 확장성 부족.
> URI 패턴 확장을 고려해 uri_mappings 테이블로 분리.

## 인가 헤더 주입 방식

| auth_type | 헤더 형식 |
|---|---|
| `bearer` | `Authorization: Bearer {auth_value}` |
| `basic` | `Authorization: Basic {auth_value}` |
| `api_key` | `X-API-Key: {auth_value}` |

## 보안 설계

### MVP 적용
- DB 등록 서비스만 프록시 허용 (미등록 → 404, 비활성 → 403)
- uri_mappings 화이트리스트 매칭 (미등록 경로 차단)
- 사용자 인증: Keycloak JWT 검증 (OIDC)
- ~~Admin API: `X-ADMIN-KEY` 헤더 필수~~ → 제거 (DB 직접 관리)

### Phase 2
- auth_value Fernet 암호화 + Vault 연동
- Host 검증 + 내부망 IP 필터링 (SSRF 방지)
- Rate limit (per-service)
- proxy_logs 감사 추적

## 확정된 미결 사항 (2026-03-04)

| 항목 | 결정 | 비고 |
|---|---|---|
| ~~인증 주체~~ | Keycloak Access Token (JWT/OIDC) | X-ADMIN-KEY 대체 |
| ~~URI 매핑 검증~~ | prefix 매칭 | 와일드카드/정규식은 Phase 2 |
| ~~Rate limit~~ | MVP 제외 | Phase 2 |

## 샘플 시딩 데이터

```
# services
confluence: sub_prefix=conf, base_url=https://company.atlassian.net, auth_type=bearer
jira:       sub_prefix=jira, base_url=https://company.atlassian.net, auth_type=bearer

# uri_mappings
conf → /wiki/rest/api/*
jira → /rest/api/2/*
```

## 다음 액션

1. ~~미확정 사항 사용자 확인~~ → 전건 확정 완료
2. `fds_00001_01_design_review.md` 기반 구현 착수

## Rule 101 실행 메모 (2026-03-04)

- 호출: `fds cl rule 101 00001`
- 판정: kickoff bundle 문서(00/01/02) 기존 생성 확인, 최신 상태로 재검토 완료
- 즉시 수행 가능한 작업(우선순위):
  1. `project_fds/app/models.py`, `project_fds/app/db.py` 기준 DB 모델/세션 초기화
  2. `project_fds/app/routers/admin.py`와 `project_fds/app/crud/*` 기준 서비스/매핑 CRUD 구현
  3. `project_fds/app/routers/proxy.py` 기준 `sub_prefix` 프록시 라우팅 + auth header 주입
