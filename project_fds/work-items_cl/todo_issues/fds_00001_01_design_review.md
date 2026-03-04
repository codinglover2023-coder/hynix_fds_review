# fds_00001 — Design Review: 인가 통제 게이트웨이 API

todo_idx: fds_00001
issue_idx: 01
생성일: 2026-03-04

---

## 목적

인가 통제 게이트웨이 아키텍처 상세 설계 및 구현 방향 검토.

## MVP 한 줄 정의

> **인가 통제형 단일 토큰 프록시 게이트웨이 (화이트리스트 기반)**

## 아키텍처 개요

```
Client Request
    │
    ▼
┌──────────────────────────────────┐
│  FDS API (FastAPI)               │
│  /{sub_prefix}/{path:path}       │
│         │                        │
│    ┌────▼────┐                   │
│    │ DB 조회  │ sub_prefix →     │
│    │ service  │ services 테이블   │
│    │ + uri    │ uri_mappings     │
│    └────┬────┘                   │
│         │                        │
│    ┌────▼────────┐               │
│    │ 보안 필터    │ base_url 검증  │
│    │ (SSRF 방지) │ 경로 허용 확인  │
│    └────┬────────┘               │
│         │                        │
│    ┌────▼────┐                   │
│    │ 인가 헤더│ auth_type별 분기  │
│    │ 주입     │ bearer/basic/key │
│    └────┬────┘                   │
│         │                        │
│    ┌────▼──────┐                 │
│    │ httpx     │──────►  외부 서비스
│    │ forward   │◄──────  (Confluence/Jira)
│    └────┬──────┘                 │
│         │                        │
│    ┌────▼────┐                   │
│    │ 응답    │ status/headers/   │
│    │ 반환    │ body 그대로 전달   │
│    └─────────┘                   │
└──────────────────────────────────┘
```

## 디렉토리 구조

```
project_fds/app/
├── __init__.py          # create_app() 팩토리 + lifespan
├── db.py                # async engine + session
├── models.py            # SQLAlchemy 모델
├── schemas.py           # Pydantic 스키마
├── routes.py            # 라우터 등록
├── crud/                # service layer 분리
│   ├── __init__.py
│   ├── service.py       # services CRUD
│   └── mapping.py       # uri_mappings CRUD
└── routers/
    ├── __init__.py
    ├── sample.py        # 기존 샘플 (유지)
    ├── admin.py         # 관리 API
    └── proxy.py         # 프록시 라우터
```

> Proxy 로직과 Admin 로직 분리. CRUD는 crud/ 디렉토리로 별도 관리.

## 라우터 설계

### 1. 프록시 라우터 (`/{sub_prefix}/{path:path}`) — 루트 레벨

모든 HTTP 메서드 지원:
```python
@router.api_route(
    "/{sub_prefix}/{path:path}",
    methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
)
```

처리 흐름:
1. `sub_prefix` → DB에서 서비스 조회 (미등록 → 404)
2. 서비스 `is_active` 확인 (비활성 → 403)
3. `uri_mappings` 화이트리스트 prefix 매칭 (미등록 경로 → 403)
4. `base_url + "/" + path` 로 target URL 구성
5. 인가 헤더 주입 (FDS 단일 서비스 토큰)
6. httpx 비동기 호출 (query params, body, headers 전달, 30초 timeout)
7. 외부 서비스 응답 status/headers/body 그대로 반환

### 2. 관리 라우터 (`/api/admin/`)

| Method | Path | 설명 |
|---|---|---|
| `POST` | `/services` | 서비스 등록 |
| `GET` | `/services` | 서비스 목록 |
| `GET` | `/services/{id}` | 서비스 상세 |
| `PUT` | `/services/{id}` | 서비스 수정 |
| `DELETE` | `/services/{id}` | 서비스 삭제 |
| `POST` | `/services/{id}/mappings` | URI 매핑 등록 |
| `GET` | `/services/{id}/mappings` | URI 매핑 목록 |
| `DELETE` | `/mappings/{id}` | URI 매핑 삭제 |

## 인가 헤더 주입 상세

```python
def build_auth_header(service) -> dict:
    match service.auth_type:
        case "bearer":
            return {"Authorization": f"Bearer {service.auth_value}"}
        case "basic":
            return {"Authorization": f"Basic {service.auth_value}"}
        case "api_key":
            return {"X-API-Key": service.auth_value}
        case _:
            return {}
```

## httpx 호출 상세

```python
async with httpx.AsyncClient() as client:
    response = await client.request(
        method=request.method,
        url=target_url,
        headers=forwarded_headers,
        params=request.query_params,
        content=await request.body(),
        timeout=30.0,
    )
```

전달 항목:
- Query params 유지
- Request body 유지
- Status code 유지
- Response headers 유지 (hop-by-hop 제외)

## 보안 필터 설계

### MVP 적용
1. DB 등록 서비스만 프록시 허용 (미등록 → 404)
2. `is_active=False` 서비스 → 403
3. `uri_mappings` 화이트리스트 prefix 매칭 (미등록 경로 → 403)
4. Admin API: `X-ADMIN-KEY` 헤더 필수

### Phase 2
1. SSRF 방지: 내부 IP 대역 차단 (127.0.0.0/8, 10.0.0.0/8, 172.16.0.0/12, 192.168.0.0/16)
2. auth_value Fernet 암호화
3. Rate limit (per-service)
4. 요청/응답 로깅 (proxy_logs 테이블)

## 확정 결정사항 (2026-03-04)

| 항목 | 결정 |
|---|---|
| 인증 주체 | FDS 단일 서비스 토큰 |
| 프록시 경로 | `/{sub_prefix}/{path:path}` 루트 레벨 |
| 관리 경로 | `/api/admin/` 하위 |
| uri_mappings 역할 | 화이트리스트 (prefix 매칭, 경로 변환 없음) |
| 토큰 저장 | MVP: 평문 / Phase 2: Fernet |
| httpx timeout | 30초 고정 |
| Rate limit | MVP 제외 |
| Admin 인증 | `X-ADMIN-KEY` 헤더 |
| SQLite 파일 | `project_fds/fds.db` |
| httpx AsyncClient | lifespan에서 생성/해제 |
| CRUD 레이어 | `app/crud/` 디렉토리 분리 |

## 다음 액션

1. 구현 착수 (DB → Admin → Proxy → 인가 순서)
