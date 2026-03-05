# fds_00001 — 인가 교집합 설계: 사용자 pkey 권한 × 외부 API 토큰 권한

todo_idx: fds_00001
issue_idx: 07
생성일: 2026-03-05
최종 갱신일: 2026-03-05
관련: fds_00001_06 (응답 통합 포맷)

---

## 아키텍처 변경 사항

### 기존 MVP 구조

```
Client → FDS API (X-ADMIN-KEY) → External Service (서비스 토큰)
         관리 라우터: /api/admin/*
```

- 인증: `X-ADMIN-KEY` 헤더 (단일 관리 키)
- 관리: FastAPI admin 엔드포인트 (`/api/admin/*`) → **제거 예정, DB 직접 CRUD로 대체**
- 외부 서비스 토큰: `services.auth_value`에 저장

### 변경 구조

```
Client (Keycloak Access Token)
   ↓
FDS API
   ├── 인증(Authentication): Keycloak JWT 검증 (OIDC)
   ├── 인가(Authorization): 외부 권한 API로 pkey 권한 확인
   ├── 서비스 관리: DB CRUD 직접 (관리 라우터 제거)
   └── 프록시: 외부 서비스 호출 (외부 API 토큰)
         ↓
   External Service (Jira 등)
```

#### 핵심 변경 3가지

1. **관리 라우터 → DB CRUD로 대체**: `/api/admin/*` 엔드포인트 제거, 서비스/매핑 관리는 DB 직접 조작
2. **Keycloak OIDC 인증**: 사용자 인증을 Keycloak Access Token (JWT)으로 처리 (기존 X-ADMIN-KEY 대체)
3. **외부 권한 API 연동**: 인가(pkey 권한) 확인을 외부 API에 위임

## 토큰 구조

시스템에 **3종류의 토큰**이 존재:

```
┌─────────────────────────────────────────────────────────┐
│ ① Keycloak Access Token (JWT)                            │
│    - 주체: 사용자 (Client → FDS API)                     │
│    - 용도: "이 사용자가 누구인지" 식별 + 기본 역할 확인    │
│    - 발급: Keycloak (OIDC Authorization Code Flow)       │
│    - 포함 정보: sub, preferred_username, realm_access,   │
│      resource_access, email, groups 등                   │
│    - 검증: JWT 서명 검증 (Keycloak Public Key / JWKS)    │
│    - 헤더: Authorization: Bearer <keycloak_access_token> │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ ② 외부 권한 API 토큰 (Authorization API Token)           │
│    - 주체: FDS 서비스 → 권한 API                         │
│    - 용도: "이 사용자가 어떤 pkey에 접근 가능한지" 확인     │
│    - 발급: 별도 권한 관리 시스템 (FDS와 독립)              │
│    - 호출: FDS가 사용자 정보(sub/username)로 권한 API 질의 │
│    - 참고: Keycloak 토큰과는 별개의 독립된 토큰            │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│ ③ 외부 서비스 토큰 (External Service Token)               │
│    - 주체: FDS 서비스 → Jira/Confluence 등                │
│    - 용도: 외부 서비스 API 호출 인가                       │
│    - 발급: 외부 서비스 (서비스 계정)                       │
│    - 특징: 서비스 계정이므로 광범위한 접근 권한 보유         │
└─────────────────────────────────────────────────────────┘
```

### Keycloak 연동 상세

```
Keycloak Server
   │
   ├── Realm: fds (또는 기존 realm)
   ├── Client: fds-api (confidential)
   │     ├── Client ID: fds-api
   │     ├── Valid Redirect URIs: ...
   │     └── Client Roles: (필요 시)
   │
   ├── OIDC Endpoints:
   │     ├── Authorization: /realms/{realm}/protocol/openid-connect/auth
   │     ├── Token:         /realms/{realm}/protocol/openid-connect/token
   │     ├── JWKS:          /realms/{realm}/protocol/openid-connect/certs
   │     └── UserInfo:      /realms/{realm}/protocol/openid-connect/userinfo
   │
   └── FDS API 검증 방식:
         ├── JWT 서명 검증 (RS256, Keycloak Public Key)
         ├── iss (issuer) 확인
         ├── aud (audience) 확인 → fds-api
         └── exp (만료) 확인
```

#### FDS API의 Keycloak JWT 검증 구현

```python
# app/auth/keycloak.py
from jose import jwt, JWTError
import httpx

class KeycloakAuth:
    def __init__(self, server_url: str, realm: str, client_id: str):
        self.server_url = server_url
        self.realm = realm
        self.client_id = client_id
        self.jwks_url = f"{server_url}/realms/{realm}/protocol/openid-connect/certs"
        self._jwks_cache: dict | None = None

    async def get_jwks(self) -> dict:
        if self._jwks_cache is None:
            async with httpx.AsyncClient() as client:
                resp = await client.get(self.jwks_url)
                self._jwks_cache = resp.json()
        return self._jwks_cache

    async def verify_token(self, token: str) -> dict:
        """Keycloak Access Token 검증 → 사용자 정보 반환"""
        jwks = await self.get_jwks()
        try:
            payload = jwt.decode(
                token,
                jwks,
                algorithms=["RS256"],
                audience=self.client_id,
                issuer=f"{self.server_url}/realms/{self.realm}",
            )
            return payload  # sub, preferred_username, realm_access 등
        except JWTError as e:
            raise HTTPException(401, f"Invalid token: {e}")
```

#### FastAPI Dependency

```python
# app/deps.py
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

bearer_scheme = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
) -> dict:
    """Keycloak JWT에서 사용자 정보 추출"""
    keycloak = get_keycloak_auth()  # 싱글턴 또는 app.state
    user = await keycloak.verify_token(credentials.credentials)
    return user

async def get_user_id(user: dict = Depends(get_current_user)) -> str:
    return user.get("sub") or user.get("preferred_username")
```

## 문제 정의: 권한 초과 접근 (Privilege Escalation via Proxy)

### 시나리오

```
사용자 인가 범위:  pkey = [PROJ-A, PROJ-B]       ← 권한 API 응답
외부 서비스 토큰:  pkey = [PROJ-A ~ PROJ-Z]       ← 서비스 계정 (전체 접근)

사용자 요청: GET /jira/rest/api/2/issue/PROJ-C-123
```

**현재 동작** (문제):
```
1. Keycloak JWT 검증 → OK (유효한 사용자, sub=user123)
2. 권한 API에 인가 확인 → 사용자 인가 pkey: [PROJ-A, PROJ-B]
3. 프록시: 외부 서비스 토큰으로 Jira 호출
   → 외부 토큰은 PROJ-C 접근 가능 → 200 OK, 데이터 반환
4. 사용자에게 PROJ-C 데이터 전달 ← ⚠️ 인가되지 않은 데이터 노출
```

**원인**:
- 외부 서비스 토큰(③)은 서비스 계정이라 **모든 프로젝트에 접근 가능**
- 사용자 인가(②)에서 허용된 pkey와 **교집합 검증을 하지 않음**
- FDS가 외부 서비스 토큰의 광범위한 권한을 사용자에게 그대로 중계

### 권한 교집합 원칙

```
사용자가 실제 접근 가능한 범위 = 사용자 인가 pkey ∩ 외부 토큰 접근 pkey

사용자 인가:    {PROJ-A, PROJ-B}
외부 토큰:     {PROJ-A, PROJ-B, PROJ-C, ..., PROJ-Z}
─────────────────────────────────
교집합 결과:    {PROJ-A, PROJ-B}  ← 이것만 허용해야 함
```

### 위협 모델

| 위협 | 설명 | 심각도 |
|---|---|---|
| **수평 권한 상승** | 인가된 pkey 외의 프로젝트 데이터 접근 | 높음 |
| **데이터 유출** | 접근 불가해야 할 프로젝트 이슈/문서 열람 | 높음 |
| **감사 실패** | 인가 로그에는 정상이지만 실제로는 초과 접근 | 중 |
| **규정 위반** | 정보 접근 통제 기준 미충족 | 높음 |

## 설계 요구사항

### 필수 요구사항

| 번호 | 요구사항 | 설명 |
|---|---|---|
| R-1 | **pkey 교집합 강제** | 사용자 인가 pkey 범위 밖의 요청은 FDS에서 차단 |
| R-2 | **요청 시점 검증** | 프록시 호출 전에 pkey 권한 확인 (사후 필터링 아님) |
| R-3 | **관리 라우터 제거** | 서비스/매핑 관리는 DB CRUD 직접 (API 엔드포인트 불필요) |
| R-4 | **토큰 분리** | Keycloak JWT ≠ 권한 API 토큰 ≠ 외부 서비스 토큰 (3종 독립) |

### 선택 요구사항 (Phase 2)

| 번호 | 요구사항 | 설명 |
|---|---|---|
| R-5 | 응답 필터링 | 목록 응답에서 인가 pkey에 해당하는 항목만 반환 |
| R-6 | 권한 캐시 | 매 요청마다 권한 API 호출 방지 (TTL 캐시) |
| R-7 | 감사 로깅 | pkey 접근 시도/성공/차단 로그 |

## 요청 흐름 (목표 설계)

```
Client
  │  ① Keycloak Access Token (Authorization: Bearer <jwt>)
  ▼
┌──────────────────────────────────────────────────────┐
│ FDS API                                               │
│                                                       │
│  1. 인증(Authentication)                              │
│     └─ Keycloak JWT 서명 검증 → sub/username 추출      │
│                                                       │
│  2. 인가(Authorization)                               │
│     └─ 외부 권한 API 호출 ──→ ② 권한 API 토큰          │
│        응답: 사용자 허용 pkey 목록                      │
│        예: ["PROJ-A", "PROJ-B"]                       │
│                                                       │
│  3. pkey 교집합 검증 ★ (핵심)                          │
│     └─ 요청 경로/파라미터에서 pkey 추출                 │
│     └─ pkey ∈ 사용자 허용 목록? → NO → 403 Forbidden   │
│                                                       │
│  4. 프록시                                            │
│     └─ 외부 서비스 호출 ──→ ③ 서비스 토큰              │
│        (인가 확인된 pkey만 도달)                        │
│                                                       │
│  5. 응답 반환                                         │
│     └─ (선택) 목록 응답 필터링                         │
└──────────────────────────────────────────────────────┘
```

## pkey 추출의 과제

교집합 검증을 하려면 **요청에서 pkey를 추출**해야 하는데, 이것이 핵심 난제:

### 경로에 pkey가 있는 경우

```
GET /jira/rest/api/2/issue/PROJ-A-123     → pkey = PROJ-A (추출 가능)
GET /jira/rest/api/2/project/PROJ-B       → pkey = PROJ-B (추출 가능)
```

### 경로에 pkey가 없는 경우

```
GET /jira/rest/api/2/search?jql=project=PROJ-C  → pkey는 쿼리 파라미터 안 JQL에 존재
POST /jira/rest/api/2/issue (body: {"fields": {"project": {"key": "PROJ-D"}}})
                                                 → pkey는 요청 body에 존재
GET /jira/rest/api/2/search?jql=assignee=me      → pkey 없음 (전체 프로젝트 검색)
```

### pkey 추출 가능성 매트릭스

| 위치 | 추출 난이도 | 예시 |
|---|---|---|
| URL 경로 | 낮음 | `/project/PROJ-A`, `/issue/PROJ-A-123` |
| 쿼리 파라미터 (단순) | 낮음 | `?project=PROJ-A` |
| 쿼리 파라미터 (JQL 등) | 높음 | `?jql=project=PROJ-A AND ...` |
| 요청 body | 중 | `{"fields": {"project": {"key": "PROJ-A"}}}` |
| 응답 body | 중 | 검색 결과에 여러 pkey 혼재 |
| 추출 불가 | - | 범용 검색, 대시보드 등 |

> 해결 방법은 별도 문서 `fds_00001_08_pkey_intersection_solution.md`에서 상세 분석

## 관리 라우터 대체 방안

### 현재: Admin API 엔드포인트

```python
# app/routers/admin.py — 제거 대상
router = APIRouter(prefix="/api/admin", dependencies=[Depends(verify_admin_key)])
# POST/GET/PUT/DELETE /services, /mappings
```

### 변경: DB 직접 관리

서비스/매핑 관리는 **운영자가 DB를 직접 조작**:

| 방식 | 도구 | 용도 |
|---|---|---|
| SQLite CLI | `sqlite3 fds.db` | 로컬 개발/테스트 |
| DB 관리 도구 | DBeaver, DataGrip 등 | 운영 환경 |
| 마이그레이션 스크립트 | Python/SQL 스크립트 | 배포 시 초기 데이터 |
| 시딩 스크립트 | `app/bootstrap.py` | 기본 데이터 자동 주입 |

### 영향 범위

| 파일 | 변경 |
|---|---|
| `app/routers/admin.py` | 삭제 |
| `app/routes.py` | admin router 등록 제거 |
| `app/deps.py` | `verify_admin_key` 제거 → `get_current_user` (Keycloak JWT 검증) 추가 |
| `app/crud/service.py` | 유지 (bootstrap, 내부 로직에서 사용) |
| `app/crud/mapping.py` | 유지 (프록시에서 사용) |
| `test_verify.py` | Admin API 테스트 제거, DB 직접 조작으로 변경 |

## 설계 결정 필요 항목

| 항목 | 질문 | 선택지 |
|---|---|---|
| D-1 | pkey 추출 방식 | 경로 기반 / 쿼리 파라미터 / body 파싱 / 응답 필터링 |
| D-2 | pkey 추출 불가 요청 처리 | 차단(기본 거부) / 허용 후 응답 필터링 / 서비스별 정책 |
| D-3 | 권한 API 호출 시점 | 매 요청 / 캐시(TTL) / 세션 시작 시 |
| D-4 | 권한 API 장애 시 | 요청 차단(fail-closed) / 캐시 fallback |
| D-5 | 목록 검색 응답 필터링 | FDS에서 필터 / 외부 API에 pkey 조건 주입 / 클라이언트 위임 |
| D-6 | admin 라우터 완전 삭제 시점 | 즉시 / DB 관리 도구 준비 후 |

## 다음 액션

1. 문제 해결 방법 상세: `fds_00001_08_pkey_intersection_solution.md`
2. 설계 결정 항목 D-1 ~ D-6 확정 후 구현 착수
