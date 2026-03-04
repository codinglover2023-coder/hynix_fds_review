# fds_00001 — Kickoff Scope: 인가 통제 게이트웨이 API

todo_idx: fds_00001
issue_idx: 00
생성일: 2026-03-04

---

## 목적

Confluence, Jira 등 외부 서비스에 대한 인가 통제 게이트웨이를 FastAPI 기반으로 구축.
SQLite 샘플로 URI 매핑 DB 관리 구조를 검증한다.

## 현재 결정사항

1. **시스템 성격**: 단순 프록시가 아닌 **인가 통제형 API Gateway Lite**
2. **URL 구조**: `{fdsapi_base_url}/{sub_prefix_uri}/{서비스별 URI}`
3. **DB**: SQLite (샘플) — 운영 시 PostgreSQL 전환 가능 구조
4. **ORM**: SQLAlchemy (async) + aiosqlite
5. **HTTP 클라이언트**: httpx AsyncClient (lifespan에서 생성/해제)
6. **인가 방식**: 서비스별 인증 정보를 DB에 저장, 프록시 시 헤더에 주입
7. **레이어 분리**: Proxy 로직과 Admin 로직 분리 (crud/ 디렉토리)

## SQLite 스키마 (확정)

### services 테이블
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | INTEGER PK | 자동 증가 |
| name | TEXT UNIQUE | 서비스명 (예: confluence, jira) |
| sub_prefix | TEXT UNIQUE | URL 접두사 (예: conf, jira) |
| base_url | TEXT NOT NULL | 외부 서비스 기본 URL |
| auth_type | TEXT NOT NULL | 인증 방식 (bearer, basic, api_key) |
| auth_value | TEXT NOT NULL | 인증 값 (토큰, base64 등) — 암호화 저장 권장 |
| is_active | BOOLEAN DEFAULT TRUE | 활성화 여부 |
| created_at | DATETIME | 생성일시 |
| updated_at | DATETIME | 수정일시 |

### uri_mappings 테이블
| 컬럼 | 타입 | 설명 |
|---|---|---|
| id | INTEGER PK | 자동 증가 |
| service_id | INTEGER FK | services.id 참조 |
| path_pattern | TEXT NOT NULL | 허용 경로 패턴 (예: `/rest/api/*`) |
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

### 필수 적용 (MVP)
- 허용된 base_url만 호출 (DB 등록 서비스만)
- 미등록 서비스 → 404, 비활성 서비스 → 403

### 운영 전환 시
- auth_value Fernet 암호화 (평문 저장 지양)
- Host 검증 + 내부망 IP 필터링 (SSRF 방지)
- Vault 연동 (토큰 관리)

## 미확정 사항 (사용자 확인 필요)

1. **인증 주체**: FDS 단일 서비스 토큰 vs 사용자별 토큰 전달 vs SSO 위임?
2. **URI 매핑 검증**: 와일드카드(`/rest/api/*`) vs 정규식?
3. **Rate limit 정책**: per-service? per-user? 양쪽 다?

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

1. 미확정 사항 사용자 확인
2. `fds_00001_01_design_review.md` 기반 구현 착수
