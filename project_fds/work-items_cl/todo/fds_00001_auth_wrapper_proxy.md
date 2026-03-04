# TODO: 인가 통제 게이트웨이 API (Confluence, Jira 등)

todo_idx: fds_00001
상태: kickoff
생성일: 2026-03-04
관련: 고객 요구사항 — 외부 서비스 인가 래퍼 구축

---

## 목적

고객이 Confluence, Jira 등 외부 서비스에 대한 **인가(Authorization) 통제 게이트웨이**를 요청.
단순 프록시가 아니라 **인가 정책 + 서비스 매핑을 DB 기반으로 통제하는 레이어**.

## 시스템 성격

> **인가 통제형 API Gateway Lite**
> - DB 기반 서비스·URI 매핑 관리
> - 서비스별 인가 헤더 자동 주입
> - 허용된 경로만 프록시 (오픈 프록시 방지)

향후 확장 가능: OAuth delegation, Policy Engine (OPA), API key per consumer, Multi-tenant

## 전체 아키텍처

```
Client
   ↓
FDS API (FastAPI)
   ├── Admin Router (/api/admin/) — 서비스 등록/관리
   ├── Proxy Router (/{sub_prefix}/{path:path}) — 동적 프록시
   ├── DB (SQLite → 향후 PostgreSQL)
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

## 작업 항목 (구현 순서)

1. [ ] DB 모델 설계 (SQLAlchemy + aiosqlite)
2. [ ] Admin API 완성 (서비스/URI CRUD)
3. [ ] Proxy 최소 기능 구현 (sub_prefix → DB 조회 → httpx 전달)
4. [ ] 인가 헤더 주입 (bearer, basic, api_key)
5. [ ] 보안 필터 적용 (허용 base_url 검증, SSRF 방지)
6. [ ] 샘플 데이터 시딩 (Confluence, Jira 초기 데이터)
7. [ ] 동작 검증 (Swagger UI + curl 테스트)

## 보안 고려사항 (필수)

### SSRF / 오픈 프록시 방지
- 허용된 base_url만 호출 (DB 등록 서비스만 허용)
- Host 검증 + IP 필터링 (내부망 접근 차단)

### 토큰 보안
- DB에 토큰 평문 저장 지양 → 최소 Fernet 암호화
- 운영 환경: Vault 연동 권장

### Rate Limit
- per-service / per-user rate limit 필요

### 인증 주체 확인 필요
- 현재: FDS → 단일 서비스 토큰으로 외부 호출
- 확인 필요: 사용자별 토큰 전달? SSO 위임? JWT 검증 후 대리 호출?

## 완료 판정 기준

| 기준 | 검증 방법 |
|---|---|
| DB 저장/조회 | Admin API로 서비스·URI CRUD 확인 |
| 프록시 정상 동작 | httpx 호출 성공 (외부 서비스 응답 반환) |
| 인가 헤더 자동 주입 | 외부 서비스에서 401 없이 응답 |
| CRUD 가능 | Swagger UI에서 Admin API 전체 테스트 |
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
| `app/routers/admin.py` | 관리 API 라우터 |

### 기타
| 파일 | 설명 |
|---|---|
| `requirements.txt` | 의존성 (sqlalchemy, aiosqlite, httpx 추가) |
| `fds.db` | SQLite 샘플 DB |

## 후속 작업

- 실제 Confluence/Jira 연동 테스트 (인증 토큰 필요)
- PostgreSQL 전환 + Redis 캐시 (service lookup)
- 요청/응답 로깅 + 감사 추적 (proxy_logs 테이블)
- Rate limit + Circuit breaker (tenacity)
- Timeout 설정 + Async connection pool 튜닝
