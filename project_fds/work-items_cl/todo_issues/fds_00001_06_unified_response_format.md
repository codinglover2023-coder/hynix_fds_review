# fds_00001 — 외부 서비스 응답 통합 포맷 검토

todo_idx: fds_00001
issue_idx: 06
생성일: 2026-03-04
최종 갱신일: 2026-03-04

---

## 배경

FDS 게이트웨이는 Confluence, Jira 등 다양한 외부 서비스를 프록시한다.
각 서비스의 **응답 포맷이 전부 다르다**.

현재 프록시는 upstream 응답을 **그대로 전달**(pass-through)하고 있어,
클라이언트가 서비스마다 다른 응답 구조를 각각 파싱해야 한다.

고객 요구: **FDS API에서 통합된 response 형태로 전달**해야 함.

## 문제 정의

### 현재 동작 (pass-through)

```python
# proxy.py — 현재
return Response(
    content=upstream_response.content,       # 그대로 전달
    status_code=upstream_response.status_code,
    headers=response_headers,
)
```

### 서비스별 응답 차이 예시

**Confluence** — 페이지 목록:
```json
{
  "results": [
    {"id": "12345", "type": "page", "title": "문서 제목", "status": "current"}
  ],
  "start": 0,
  "limit": 25,
  "size": 1,
  "_links": {"next": "/rest/api/content?start=25"}
}
```

**Jira** — 이슈 조회:
```json
{
  "id": "10001",
  "key": "PROJ-123",
  "fields": {
    "summary": "버그 수정",
    "status": {"name": "진행 중"},
    "assignee": {"displayName": "홍길동"}
  }
}
```

**Jira** — 이슈 검색:
```json
{
  "startAt": 0,
  "maxResults": 50,
  "total": 120,
  "issues": [...]
}
```

**GitHub** — 리포지토리 목록:
```json
[
  {"id": 1, "name": "repo-name", "full_name": "org/repo-name"}
]
```

| 차이점 | Confluence | Jira | GitHub |
|---|---|---|---|
| 목록 키 | `results` | `issues` | (배열 직접) |
| 페이지네이션 | `start/limit/size` | `startAt/maxResults/total` | `Link` 헤더 |
| 단건 구조 | `{id, title, type}` | `{key, fields: {...}}` | `{id, name}` |
| 에러 형식 | `{statusCode, message}` | `{errorMessages: [...]}` | `{message, documentation_url}` |

### 클라이언트 입장의 문제

```
현재: 클라이언트가 서비스별로 다른 파싱 로직 필요
  Confluence → results[].title
  Jira       → issues[].fields.summary
  GitHub     → [].name

원하는 것: 통합된 포맷으로 하나의 파싱 로직
  FDS 응답  → data[].title (어떤 서비스든 동일 구조)
```

## 통합 응답의 범위 결정

응답 통합의 깊이에 따라 접근 방법이 크게 달라진다.

### Level 1: 엔벨로프 래핑 (메타데이터 통합)

upstream 본문은 그대로 두되, **FDS 메타데이터로 감싸기**:

```json
{
  "service": "confluence",
  "status": 200,
  "timestamp": "2026-03-04T10:30:00Z",
  "upstream_url": "https://company.atlassian.net/wiki/rest/api/content",
  "data": {
    "results": [...],
    "start": 0,
    "limit": 25
  }
}
```

- upstream 응답 본문 = `data` 필드에 그대로 삽입
- 서비스명, 상태, 타임스탬프 등 FDS 메타데이터 추가
- **클라이언트**: `data` 안의 구조는 여전히 서비스마다 다름

### Level 2: 에러 포맷 통합

정상 응답은 pass-through, **에러 응답만 통합 포맷**:

```json
{
  "service": "jira",
  "status": 401,
  "error": {
    "code": "UPSTREAM_AUTH_FAILED",
    "message": "Unauthorized",
    "upstream_body": {"errorMessages": ["Login required"]}
  },
  "timestamp": "2026-03-04T10:30:00Z"
}
```

- 정상(2xx): pass-through 또는 Level 1 엔벨로프
- 에러(4xx/5xx): FDS 통합 에러 포맷으로 변환
- **클라이언트**: 에러 처리 로직 단일화 가능

### Level 3: 페이지네이션 통합

목록 응답의 **페이지네이션 구조를 통합**:

```json
{
  "service": "confluence",
  "status": 200,
  "data": [...],
  "pagination": {
    "offset": 0,
    "limit": 25,
    "total": 120,
    "has_next": true
  }
}
```

- 서비스별 페이지네이션 필드를 통합 구조로 변환
- 변환 규칙: 서비스별 매핑 필요 (Confluence: start→offset, Jira: startAt→offset)
- **클라이언트**: 페이지네이션 처리 단일화

### Level 4: 데이터 필드 매핑 (풀 변환)

응답 본문의 **필드를 통합 스키마로 변환**:

```json
{
  "service": "confluence",
  "status": 200,
  "data": [
    {"id": "12345", "title": "문서 제목", "type": "page", "url": "..."}
  ],
  "pagination": {"offset": 0, "limit": 25, "total": 120}
}
```

- 서비스별 필드를 FDS 통합 스키마로 매핑 (results[].title → data[].title)
- **서비스별 변환 어댑터** 필요
- **클라이언트**: 완전 통합된 구조

## 접근 방법별 상세

### 방법 1: FDS 엔벨로프 래핑 (Level 1)

모든 응답을 **공통 엔벨로프**로 감싸되, 본문은 건드리지 않음.

#### 엔벨로프 스키마

```python
class FdsResponse(BaseModel):
    service: str            # 서비스명 (confluence, jira)
    sub_prefix: str         # 라우팅 prefix (conf, jira)
    status: int             # upstream HTTP status code
    timestamp: str          # ISO 8601
    request_path: str       # 요청 경로
    data: Any               # upstream 응답 본문 (그대로)
```

#### 구현

```python
import json
from datetime import datetime, timezone

async def proxy_endpoint(sub_prefix, path, request, db):
    # ... 기존 인가/프록시 로직 동일 ...

    upstream_body = upstream_response.content
    content_type = upstream_response.headers.get("content-type", "")

    # JSON 응답이면 파싱하여 data에 삽입
    if "application/json" in content_type:
        try:
            data = upstream_response.json()
        except Exception:
            data = upstream_body.decode("utf-8", errors="replace")
    else:
        data = upstream_body.decode("utf-8", errors="replace")

    envelope = {
        "service": service.name,
        "sub_prefix": sub_prefix,
        "status": upstream_response.status_code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "request_path": f"/{path}",
        "data": data,
    }
    return JSONResponse(
        content=envelope,
        status_code=upstream_response.status_code,
    )
```

| 장점 | 한계 |
|---|---|
| 구현 단순 (~20줄 변경) | data 내부 구조는 여전히 서비스별 상이 |
| upstream 응답 손실 없음 | 클라이언트 파싱 부담 완전 해소 안 됨 |
| 메타데이터(서비스명, 시간) 추가 | 바이너리 응답(파일 다운로드) 처리 필요 |
| 모든 서비스에 범용 적용 가능 | |

### 방법 2: 에러 응답 통합 (Level 2)

정상(2xx) = Level 1 엔벨로프, 에러(4xx/5xx) = 통합 에러 포맷.

#### 에러 스키마

```python
class FdsErrorResponse(BaseModel):
    service: str
    status: int
    error: FdsError
    timestamp: str

class FdsError(BaseModel):
    code: str          # FDS 정의 에러 코드
    message: str       # 사람이 읽을 수 있는 메시지
    upstream_body: Any # 원본 에러 본문 (디버깅용)
```

#### 에러 코드 매핑

```python
def classify_upstream_error(status_code: int, service_name: str) -> str:
    if status_code == 401:
        return "UPSTREAM_AUTH_FAILED"
    if status_code == 403:
        return "UPSTREAM_FORBIDDEN"
    if status_code == 404:
        return "UPSTREAM_NOT_FOUND"
    if status_code == 429:
        return "UPSTREAM_RATE_LIMITED"
    if status_code >= 500:
        return "UPSTREAM_SERVER_ERROR"
    return "UPSTREAM_CLIENT_ERROR"
```

#### 구현

```python
async def proxy_endpoint(sub_prefix, path, request, db):
    # ... 프록시 로직 ...

    timestamp = datetime.now(timezone.utc).isoformat()

    if upstream_response.status_code >= 400:
        # 에러 → 통합 포맷
        try:
            upstream_body = upstream_response.json()
        except Exception:
            upstream_body = upstream_response.text

        return JSONResponse(
            status_code=upstream_response.status_code,
            content={
                "service": service.name,
                "status": upstream_response.status_code,
                "error": {
                    "code": classify_upstream_error(upstream_response.status_code, service.name),
                    "message": _extract_error_message(upstream_body, service.name),
                    "upstream_body": upstream_body,
                },
                "timestamp": timestamp,
            },
        )

    # 정상 → 엔벨로프
    return JSONResponse(
        status_code=upstream_response.status_code,
        content={
            "service": service.name,
            "status": upstream_response.status_code,
            "timestamp": timestamp,
            "data": upstream_response.json(),
        },
    )
```

#### 서비스별 에러 메시지 추출

```python
def _extract_error_message(body: Any, service_name: str) -> str:
    """서비스별 에러 본문에서 사람이 읽을 수 있는 메시지 추출"""
    if isinstance(body, dict):
        # Confluence: {"statusCode": 401, "message": "..."}
        if "message" in body:
            return body["message"]
        # Jira: {"errorMessages": ["...", "..."]}
        if "errorMessages" in body:
            return "; ".join(body["errorMessages"])
        # GitHub: {"message": "...", "documentation_url": "..."}
        if "message" in body:
            return body["message"]
    if isinstance(body, str):
        return body
    return "Unknown error"
```

| 장점 | 한계 |
|---|---|
| 에러 처리 로직 클라이언트에서 단일화 | 정상 응답은 여전히 서비스별 상이 |
| FDS 에러 코드로 에러 유형 분류 | 서비스별 에러 메시지 추출 규칙 유지보수 |
| 원본 에러 본문도 포함 (디버깅) | |

### 방법 3: 서비스별 어댑터 (Level 3~4)

서비스마다 **변환 어댑터**를 두고, 응답을 FDS 통합 스키마로 변환.

#### 아키텍처

```
Upstream 응답
     ↓
 어댑터 선택 (service.name → adapter)
     ↓
 변환 로직 (서비스별 필드 매핑)
     ↓
 FDS 통합 응답
```

#### 어댑터 구조

```python
# app/adapters/base.py
class ResponseAdapter:
    def transform(self, upstream_body: dict, path: str, method: str) -> dict:
        """upstream 응답을 FDS 통합 포맷으로 변환"""
        raise NotImplementedError

    def transform_pagination(self, upstream_body: dict) -> dict | None:
        """페이지네이션 정보 추출 (있으면)"""
        return None

# app/adapters/confluence.py
class ConfluenceAdapter(ResponseAdapter):
    def transform(self, body, path, method):
        if "results" in body:
            return {
                "items": [
                    {"id": r["id"], "title": r["title"], "type": r.get("type")}
                    for r in body["results"]
                ],
            }
        return body  # 변환 규칙 없으면 그대로

    def transform_pagination(self, body):
        if "start" in body and "limit" in body:
            return {
                "offset": body["start"],
                "limit": body["limit"],
                "total": body.get("size"),
                "has_next": body.get("_links", {}).get("next") is not None,
            }
        return None

# app/adapters/jira.py
class JiraAdapter(ResponseAdapter):
    def transform(self, body, path, method):
        if "issues" in body:
            return {
                "items": [
                    {"id": i["id"], "title": i["fields"]["summary"], "key": i["key"]}
                    for i in body["issues"]
                ],
            }
        if "key" in body and "fields" in body:
            return {
                "id": body["id"],
                "title": body["fields"]["summary"],
                "key": body["key"],
                "status": body["fields"].get("status", {}).get("name"),
            }
        return body

    def transform_pagination(self, body):
        if "startAt" in body:
            return {
                "offset": body["startAt"],
                "limit": body["maxResults"],
                "total": body.get("total"),
                "has_next": body["startAt"] + body["maxResults"] < body.get("total", 0),
            }
        return None
```

#### 어댑터 레지스트리

```python
# app/adapters/__init__.py
from .confluence import ConfluenceAdapter
from .jira import JiraAdapter

_ADAPTERS: dict[str, ResponseAdapter] = {
    "confluence": ConfluenceAdapter(),
    "jira": JiraAdapter(),
}

class PassthroughAdapter(ResponseAdapter):
    def transform(self, body, path, method):
        return body  # 변환 없이 그대로

_DEFAULT = PassthroughAdapter()

def get_adapter(service_name: str) -> ResponseAdapter:
    return _ADAPTERS.get(service_name, _DEFAULT)
```

#### 프록시 통합

```python
from ..adapters import get_adapter

async def proxy_endpoint(sub_prefix, path, request, db):
    # ... 기존 프록시 로직 ...

    adapter = get_adapter(service.name)
    upstream_body = upstream_response.json()

    transformed = adapter.transform(upstream_body, path, request.method)
    pagination = adapter.transform_pagination(upstream_body)

    envelope = {
        "service": service.name,
        "status": upstream_response.status_code,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "data": transformed,
    }
    if pagination:
        envelope["pagination"] = pagination

    return JSONResponse(content=envelope, status_code=upstream_response.status_code)
```

| 장점 | 한계 |
|---|---|
| 클라이언트 파싱 완전 단일화 | **서비스마다 어댑터 개발 필요** |
| 페이지네이션 통합 가능 | 서비스 API 변경 시 어댑터 수정 필요 |
| 필드 매핑으로 불필요 데이터 제거 가능 | 모든 API 응답 구조를 사전 파악해야 함 |
| 신규 서비스 = PassthroughAdapter 기본 적용 | 어댑터 없는 서비스는 통합 안 됨 |

### 방법 4: 변환 규칙 DB 관리 (설정 기반)

어댑터를 코드가 아닌 **DB에 저장된 변환 규칙**으로 관리.

#### 변환 규칙 테이블

```
response_transforms 테이블:
  id              INTEGER PK
  service_id      INTEGER FK
  path_pattern    TEXT         -- 적용 대상 경로 패턴
  list_key        TEXT         -- 목록 데이터 키 (results, issues, null=루트배열)
  pagination_map  JSON         -- {"offset": "start", "limit": "limit", "total": "size"}
  field_map       JSON         -- {"id": "id", "title": "title", "type": "type"}
  is_active       BOOLEAN
```

#### 예시 데이터

```json
// Confluence 목록 변환 규칙
{
  "service_id": 1,
  "path_pattern": "/wiki/rest/api/content",
  "list_key": "results",
  "pagination_map": {"offset": "start", "limit": "limit", "total": "size"},
  "field_map": {"id": "id", "title": "title", "type": "type"}
}

// Jira 검색 변환 규칙
{
  "service_id": 2,
  "path_pattern": "/rest/api/2/search",
  "list_key": "issues",
  "pagination_map": {"offset": "startAt", "limit": "maxResults", "total": "total"},
  "field_map": {"id": "id", "title": "fields.summary", "key": "key"}
}
```

#### 런타임 변환 엔진

```python
def apply_transform(body: dict, rule: dict) -> dict:
    result = {}
    list_key = rule.get("list_key")

    # 목록 추출
    if list_key:
        items = body.get(list_key, [])
    elif isinstance(body, list):
        items = body
    else:
        items = None

    # 필드 매핑
    if items is not None and rule.get("field_map"):
        field_map = rule["field_map"]
        result["items"] = [
            {target: _get_nested(item, source) for target, source in field_map.items()}
            for item in items
        ]
    else:
        result = body  # 매핑 없으면 그대로

    return result

def _get_nested(obj: dict, dotted_key: str):
    """fields.summary → obj["fields"]["summary"]"""
    for key in dotted_key.split("."):
        if isinstance(obj, dict):
            obj = obj.get(key)
        else:
            return None
    return obj
```

| 장점 | 한계 |
|---|---|
| 코드 배포 없이 변환 규칙 추가/수정 가능 | 변환 엔진 구현 복잡도 높음 |
| Admin API로 런타임 규칙 관리 | 복잡한 변환 표현에 한계 (조건 분기 등) |
| 서비스 추가 시 DB에 규칙만 등록 | 중첩 구조(fields.status.name) 접근 로직 필요 |
| 변환 없는 경로는 pass-through | 디버깅 어려움 (왜 이렇게 변환됐지?) |

## 방법별 비교

| 기준 | 1. 엔벨로프 | 2. 에러 통합 | 3. 어댑터 | 4. DB 규칙 |
|---|---|---|---|---|
| 클라이언트 단일화 | 부분 (메타만) | 에러만 | 완전 | 완전 |
| 구현 비용 | 매우 낮음 | 낮음 | 중~높음 | 높음 |
| 서비스 추가 비용 | 없음 | 없음 | 어댑터 개발 | 규칙 등록 |
| API 지식 필요도 | 없음 | 낮음 | 높음 | 높음 |
| 유지보수 부담 | 낮음 | 낮음 | 중 | 중 |
| upstream 변경 대응 | 자동 (pass-through) | 에러만 수정 | 어댑터 수정 | 규칙 수정 |

## 권장 방향: 단계적 적용

### Phase 1 (MVP 확장): Level 1 + Level 2

```
모든 응답 → FDS 엔벨로프 래핑
에러 응답 → 통합 에러 포맷

{
  "service": "confluence",
  "status": 200,
  "timestamp": "...",
  "data": { ... upstream 본문 그대로 ... }
}

or (에러 시)

{
  "service": "jira",
  "status": 401,
  "error": {
    "code": "UPSTREAM_AUTH_FAILED",
    "message": "Login required",
    "upstream_body": { ... }
  },
  "timestamp": "..."
}
```

**이유**:
1. 구현 비용 최소 (~30줄)
2. 클라이언트에 서비스 식별자 + 타임스탬프 제공
3. 에러 처리 로직 단일화 (가장 즉각적인 효과)
4. upstream 응답 손실 없음 (data에 원본 보존)
5. 서비스 추가 시 추가 작업 없음

### Phase 2: 필요 시 어댑터 점진 추가

```
고객이 통합 포맷을 요청하는 서비스만 어댑터 추가
어댑터 없는 서비스 → PassthroughAdapter (data에 원본 그대로)
```

**판단 기준**: 클라이언트가 2개 이상 서비스의 동일 유형 데이터를 통합 처리해야 할 때

### Pass-through 모드 유지 옵션

기존 pass-through 동작이 필요한 경우를 위해 **모드 전환** 지원:

```
# 쿼리 파라미터로 전환
GET /conf/wiki/rest/api/content?_fds_raw=true  → pass-through (현재 동작)
GET /conf/wiki/rest/api/content                → FDS 엔벨로프

# 또는 헤더로 전환
X-FDS-Response: raw          → pass-through
X-FDS-Response: envelope     → 엔벨로프 (기본)
```

## 주의사항

### 1. 바이너리 응답

파일 다운로드 등 JSON이 아닌 응답은 엔벨로프 래핑 불가 → **pass-through 유지**:

```python
content_type = upstream_response.headers.get("content-type", "")
if "application/json" not in content_type:
    # 바이너리/HTML 등 → 그대로 전달
    return Response(
        content=upstream_response.content,
        status_code=upstream_response.status_code,
        headers=response_headers,
    )
```

### 2. 대용량 응답

큰 JSON 응답을 파싱 → 재직렬화하면 메모리·성능 오버헤드:
- 1MB 이상 응답 → pass-through 고려
- 스트리밍 응답 → 엔벨로프 불가

### 3. upstream 응답 구조 변경

외부 서비스 API 업데이트로 응답 구조가 바뀌면:
- Level 1~2: 영향 없음 (본문 그대로 전달)
- Level 3~4: 어댑터/규칙 수정 필요

## 구현 영향도 (Phase 1 기준)

| 파일 | 변경 내용 | 규모 |
|---|---|---|
| `app/routers/proxy.py` | 엔벨로프 래핑 + 에러 포맷 분기 | ~30줄 |
| `app/schemas.py` | FdsResponse, FdsErrorResponse 스키마 추가 | ~15줄 |
| 신규: `app/response.py` | 에러 코드 매핑 + 에러 메시지 추출 함수 | ~30줄 |
| `test_verify.py` | 응답 구조 변경에 따른 테스트 수정 | 기존 테스트 조정 |

## 다음 액션

1. 고객과 통합 응답 포맷 범위 확인 (Level 1~2로 충분한지, Level 3~4 필요한지)
2. Phase 1(엔벨로프 + 에러 통합) 우선 구현 검토
3. 바이너리 응답 처리 정책 확정
