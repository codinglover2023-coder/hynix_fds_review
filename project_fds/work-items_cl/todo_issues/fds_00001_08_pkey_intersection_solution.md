# fds_00001 — pkey 교집합 강제: 해결 방법

todo_idx: fds_00001
issue_idx: 08
생성일: 2026-03-05
최종 갱신일: 2026-03-05
관련: fds_00001_07 (인가 교집합 설계)

---

## 해결해야 할 문제 요약

```
사용자 인가 pkey:    {PROJ-A, PROJ-B}
외부 서비스 토큰:    {PROJ-A ~ PROJ-Z}  (서비스 계정, 전체 접근)
────────────────────────────────
허용해야 할 범위:    {PROJ-A, PROJ-B}   (교집합)
차단해야 할 것:      PROJ-C ~ PROJ-Z 에 대한 모든 접근
```

프록시 특성상 요청/응답을 그대로 전달하므로, **어디에서 pkey를 검증할 것인가**가 핵심.

## 해결 방법 5가지

### 방법 1: 사전 검증 — 요청 경로/파라미터에서 pkey 추출 후 차단

**프록시 호출 전에** 요청에서 pkey를 추출하고, 인가 목록에 없으면 403.

```
요청 → pkey 추출 → 인가 목록에 있나? → NO → 403
                                    → YES → 프록시 호출
```

#### 구현

```python
# app/auth/pkey_extractor.py

class PkeyExtractor:
    """서비스별 요청에서 pkey를 추출하는 전략"""

    def extract_from_path(self, path: str) -> str | None:
        """URL 경로에서 pkey 추출"""
        raise NotImplementedError

    def extract_from_query(self, query_params: dict) -> str | None:
        """쿼리 파라미터에서 pkey 추출"""
        return None

    def extract_from_body(self, body: dict) -> str | None:
        """요청 body에서 pkey 추출"""
        return None


class JiraPkeyExtractor(PkeyExtractor):
    """Jira 요청에서 pkey 추출"""

    def extract_from_path(self, path: str) -> str | None:
        # /rest/api/2/issue/PROJ-A-123 → PROJ-A
        # /rest/api/2/project/PROJ-A   → PROJ-A
        import re

        # 이슈 키에서 pkey 추출: PROJ-A-123 → PROJ-A
        issue_match = re.search(r'/issue/([A-Z][A-Z0-9_]+-)\d+', path)
        if issue_match:
            return issue_match.group(1).rstrip('-')

        # 프로젝트 키 직접 접근
        project_match = re.search(r'/project/([A-Z][A-Z0-9_]+)', path)
        if project_match:
            return project_match.group(1)

        return None  # 추출 불가

    def extract_from_query(self, query_params: dict) -> str | None:
        # ?jql=project=PROJ-A → 단순 케이스만
        jql = query_params.get("jql", "")
        import re
        match = re.search(r'project\s*=\s*["\']?([A-Z][A-Z0-9_]+)', jql)
        return match.group(1) if match else None
```

#### 프록시 통합

```python
async def proxy_endpoint(sub_prefix, path, request, db):
    service = ...  # 기존 서비스 조회
    user = ...     # Keycloak JWT에서 사용자 추출 (Depends(get_current_user))

    # 1. 사용자 인가 pkey 목록 조회 (권한 API)
    allowed_pkeys = await get_user_allowed_pkeys(user["sub"], service.name)
    # 예: ["PROJ-A", "PROJ-B"]

    # 2. 요청에서 pkey 추출
    extractor = get_pkey_extractor(service.name)
    request_pkey = extractor.extract_from_path(path)

    if request_pkey is None:
        request_pkey = extractor.extract_from_query(dict(request.query_params))

    # 3. pkey 교집합 검증
    if request_pkey and request_pkey not in allowed_pkeys:
        raise HTTPException(403, f"Access denied: project {request_pkey}")

    # 4. pkey 추출 불가 시 정책 적용
    if request_pkey is None:
        # 정책: 차단 / 허용 후 응답 필터 / 서비스별 판단
        ...

    # 5. 프록시 호출 (기존 로직)
    ...
```

| 장점 | 한계 |
|---|---|
| 프록시 호출 전 차단 (가장 안전) | **서비스별 pkey 추출 로직 개발 필요** |
| 불필요한 외부 호출 방지 | 경로에 pkey가 없으면 추출 불가 |
| 명확한 403 응답 | JQL 등 복잡한 쿼리 파싱 한계 |

### 방법 2: 응답 필터링 — 프록시 응답에서 인가 외 pkey 데이터 제거

프록시는 그대로 호출하고, **응답에서 인가되지 않은 pkey 데이터를 필터링**.

```
요청 → 프록시 호출 → 응답 수신 → pkey 필터링 → 클라이언트 반환
```

#### 구현

```python
# app/auth/response_filter.py

class PkeyResponseFilter:
    """응답에서 인가된 pkey 데이터만 남기는 필터"""

    def filter_response(self, body: dict, allowed_pkeys: set[str]) -> dict:
        raise NotImplementedError


class JiraResponseFilter(PkeyResponseFilter):

    def filter_response(self, body: dict, allowed_pkeys: set[str]) -> dict:
        # 검색 결과 필터링
        if "issues" in body:
            original_count = len(body["issues"])
            body["issues"] = [
                issue for issue in body["issues"]
                if self._extract_pkey(issue) in allowed_pkeys
            ]
            body["total"] = len(body["issues"])  # 총 건수 보정
            body["_fds_filtered"] = original_count - len(body["issues"])
            return body

        # 단건 조회 필터링
        pkey = self._extract_pkey(body)
        if pkey and pkey not in allowed_pkeys:
            return None  # 403으로 변환

        return body

    def _extract_pkey(self, issue: dict) -> str | None:
        try:
            return issue["fields"]["project"]["key"]
        except (KeyError, TypeError):
            # issue key에서 추출: PROJ-A-123 → PROJ-A
            key = issue.get("key", "")
            parts = key.rsplit("-", 1)
            return parts[0] if len(parts) == 2 else None
```

#### 프록시 통합

```python
async def proxy_endpoint(sub_prefix, path, request, db):
    # ... 프록시 호출 ...

    allowed_pkeys = await get_user_allowed_pkeys(user.id, service.name)

    # JSON 응답이면 필터링
    if "application/json" in content_type:
        body = upstream_response.json()
        filter_ = get_response_filter(service.name)

        filtered = filter_.filter_response(body, set(allowed_pkeys))
        if filtered is None:
            raise HTTPException(403, "Access denied: unauthorized project")

        return JSONResponse(content=filtered, status_code=upstream_response.status_code)

    return Response(content=upstream_response.content, ...)
```

| 장점 | 한계 |
|---|---|
| pkey 추출 불가 요청도 대응 가능 | **인가 외 데이터가 일단 외부에서 전달됨** |
| 검색 결과 목록 필터링 가능 | 응답 파싱 오버헤드 |
| 사전 추출 로직보다 범용적 | 페이지네이션 깨짐 (total 보정 필요) |
| | 모든 서비스 응답 구조 파악 필요 |

### 방법 3: 쿼리 주입 — 외부 API 호출 시 pkey 조건 강제 삽입

프록시가 외부 서비스를 호출할 때, **pkey 필터 조건을 강제로 주입**.

```
요청 → pkey 조건 주입 → 프록시 호출 → 응답 반환
```

#### 구현 (Jira JQL 주입 예시)

```python
class JiraQueryInjector:

    def inject_pkey_filter(
        self, query_params: dict, allowed_pkeys: list[str]
    ) -> dict:
        pkey_condition = " OR ".join(f'project = "{pk}"' for pk in allowed_pkeys)
        pkey_jql = f"({pkey_condition})"

        original_jql = query_params.get("jql", "")
        if original_jql:
            # 기존 JQL에 AND로 pkey 조건 추가
            query_params["jql"] = f"({original_jql}) AND {pkey_jql}"
        else:
            query_params["jql"] = pkey_jql

        return query_params

# 사용 예:
# 원본: ?jql=assignee=me
# 주입: ?jql=(assignee=me) AND (project = "PROJ-A" OR project = "PROJ-B")
```

#### Confluence 예시

```python
class ConfluenceQueryInjector:

    def inject_pkey_filter(
        self, query_params: dict, allowed_pkeys: list[str]
    ) -> dict:
        # CQL에 space 조건 주입
        space_condition = " OR ".join(f'space = "{pk}"' for pk in allowed_pkeys)
        original_cql = query_params.get("cql", "")
        if original_cql:
            query_params["cql"] = f"({original_cql}) AND ({space_condition})"
        else:
            query_params["cql"] = f"({space_condition})"
        return query_params
```

| 장점 | 한계 |
|---|---|
| 외부 API 레벨에서 필터링 (가장 정확) | **서비스별 쿼리 문법 파악 필요** (JQL, CQL 등) |
| 불필요한 데이터 전송 없음 | 모든 API 엔드포인트에 적용 불가 |
| 페이지네이션 정상 동작 | 쿼리 언어 파싱/조작 복잡도 높음 |
| 응답 필터링 불필요 | 비-검색 API (단건 조회 등)에는 적용 불가 |

### 방법 4: pkey 스코프 테이블 — DB에 사용자별 허용 pkey 관리

권한 API 응답을 **FDS DB에 캐시**하고, 프록시 시 DB 조회로 교집합 검증.

```
[1회] 권한 API 호출 → 사용자별 pkey → FDS DB 저장 (user_pkey_scopes)
[매 요청] 요청 → DB에서 사용자 pkey 조회 → 교집합 검증 → 프록시
```

#### DB 모델

```python
class UserPkeyScope(Base):
    __tablename__ = "user_pkey_scopes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[str] = mapped_column(String(100), nullable=False, index=True)
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"), nullable=False)
    pkey: Mapped[str] = mapped_column(String(100), nullable=False)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        UniqueConstraint("user_id", "service_id", "pkey"),
    )
```

#### 동작 흐름

```python
async def get_user_allowed_pkeys(
    db: AsyncSession, user_id: str, service_id: int
) -> list[str]:
    # 1. DB 캐시 조회
    scopes = await db.execute(
        select(UserPkeyScope).where(
            UserPkeyScope.user_id == user_id,
            UserPkeyScope.service_id == service_id,
            UserPkeyScope.expires_at > datetime.utcnow(),
        )
    )
    cached = list(scopes.scalars().all())

    if cached:
        return [s.pkey for s in cached]

    # 2. 캐시 미스 → 권한 API 호출
    pkeys = await call_authorization_api(user_id, service_id)

    # 3. DB에 캐시 저장 (TTL)
    expires = datetime.utcnow() + timedelta(minutes=5)
    for pkey in pkeys:
        db.add(UserPkeyScope(
            user_id=user_id, service_id=service_id,
            pkey=pkey, expires_at=expires,
        ))
    await db.commit()

    return pkeys
```

| 장점 | 한계 |
|---|---|
| 권한 API 호출 횟수 최소화 (캐시) | DB 테이블 추가, TTL 관리 필요 |
| 빠른 조회 (DB index) | 권한 변경 시 캐시 무효화 필요 |
| 오프라인에서도 캐시로 동작 | 캐시 TTL 동안 권한 변경 미반영 |

### 방법 5: 하이브리드 — 사전 검증 + 응답 필터링 결합

**가장 권장하는 방법**. 사전 검증과 응답 필터링을 결합하여 이중 방어.

```
요청
  │
  ├─ pkey 추출 가능? ──YES──→ 사전 검증 (방법 1)
  │                            └─ 인가 목록에 없으면 → 403
  │
  └─ pkey 추출 불가? ──→ 프록시 호출
                          └─ 응답 필터링 (방법 2)
                               └─ 인가 외 pkey 데이터 제거
```

#### 구현

```python
async def proxy_endpoint(sub_prefix, path, request, db,
                         user = Depends(get_current_user)):  # Keycloak JWT
    service = ...

    # 1. 인가 pkey 조회 (캐시 포함)
    allowed_pkeys = await get_user_allowed_pkeys(db, user["sub"], service.id)

    # 2. 사전 검증: 요청에서 pkey 추출 시도
    extractor = get_pkey_extractor(service.name)
    request_pkey = extractor.extract(path, dict(request.query_params))

    if request_pkey and request_pkey not in allowed_pkeys:
        raise HTTPException(403, f"Access denied: project {request_pkey}")

    # 3. 프록시 호출
    upstream_response = await client.request(...)

    # 4. 응답 필터링: pkey 추출 불가했던 요청 또는 목록 응답
    if "application/json" in content_type:
        body = upstream_response.json()
        filter_ = get_response_filter(service.name)

        if filter_:
            filtered = filter_.filter_response(body, set(allowed_pkeys))
            if filtered is None:
                raise HTTPException(403, "Access denied")
            body = filtered

        return JSONResponse(content=body, status_code=upstream_response.status_code)

    return Response(...)
```

| 장점 | 한계 |
|---|---|
| **이중 방어**: 사전 차단 + 사후 필터 | 구현 복잡도 가장 높음 |
| pkey 추출 가능하면 사전 차단 (효율적) | 서비스별 extractor + filter 모두 필요 |
| pkey 추출 불가해도 응답에서 필터링 | 응답 구조 파악 필요 |
| 보안 가장 강력 | |

## 방법별 비교

| 기준 | 1. 사전 검증 | 2. 응답 필터 | 3. 쿼리 주입 | 4. DB 캐시 | 5. 하이브리드 |
|---|---|---|---|---|---|
| 보안 수준 | 높음 | 중 | 높음 | (보조) | **매우 높음** |
| pkey 추출 불가 대응 | 불가 | 가능 | 부분 | (보조) | **가능** |
| 목록 검색 대응 | 제한적 | 가능 | **최적** | (보조) | 가능 |
| 구현 비용 | 중 | 중 | 높음 | 낮음 | 높음 |
| 서비스별 개발 | extractor | filter | injector | 없음 | extractor+filter |
| 외부 호출 절감 | 사전 차단 | 없음 | 없음 | 캐시 | 사전 차단+캐시 |
| 페이지네이션 | 영향 없음 | 깨짐 가능 | 정상 | 영향 없음 | 부분 깨짐 |

## 권장 접근: 단계적 구현

### Phase 1: 사전 검증 + DB 캐시 (방법 1 + 4)

가장 핵심적인 **경로 기반 pkey 추출 + 사전 차단**부터 구현.

```
구현 범위:
  1. UserPkeyScope 테이블 + 권한 API 호출 + TTL 캐시 (방법 4)
  2. JiraPkeyExtractor: 경로에서 pkey 추출 (방법 1)
  3. proxy_endpoint에 pkey 검증 로직 추가
  4. pkey 추출 불가 시: 기본 허용 (로그만 남김) ← Phase 2에서 필터링 추가
```

이유:
- 경로 기반 pkey 추출은 **단건 조회(가장 빈번한 요청)** 커버
- 검색 API는 Phase 2에서 응답 필터링으로 대응
- DB 캐시로 권한 API 호출 최소화

### Phase 2: 응답 필터링 추가 (방법 5 완성)

```
추가 구현:
  1. JiraResponseFilter: 검색 결과에서 인가 외 pkey 제거
  2. pkey 추출 불가 요청에 응답 필터 적용
  3. 쿼리 주입 (선택): JQL에 pkey 조건 강제 삽입
```

### Phase 3: 고도화

```
  1. 서비스별 extractor/filter 확장 (Confluence 등)
  2. 감사 로깅 (pkey 접근 시도/차단)
  3. 캐시 무효화 API (권한 변경 시)
```

## 서비스별 pkey 개념 매핑

"pkey"는 서비스마다 다른 이름으로 존재:

| 서비스 | pkey 에 해당하는 개념 | 예시 | 경로 내 위치 |
|---|---|---|---|
| **Jira** | Project Key | `PROJ-A` | `/issue/PROJ-A-123` → `PROJ-A` |
| **Confluence** | Space Key | `DEV` | `/space/DEV`, `?spaceKey=DEV` |
| **GitHub** | `owner/repo` | `hynix/fds` | `/repos/hynix/fds/...` |
| **GitLab** | Project ID/Path | `123` or `group/project` | `/projects/123/...` |

`services` 테이블에 **pkey 메타데이터** 추가 검토:

```
services 테이블 확장:
  + pkey_field_name: TEXT  -- "project_key", "space_key" 등
  + pkey_extraction_rule: TEXT  -- 추출 규칙 (정규식 또는 패턴)
```

## 경계 케이스 (Edge Cases)

### 1. pkey가 여러 개인 요청

```
JQL: project IN (PROJ-A, PROJ-B, PROJ-C)
```
- PROJ-A, PROJ-B는 인가됨, PROJ-C는 미인가
- **처리**: 인가된 pkey만 남기고 JQL 재작성? → 복잡도 매우 높음
- **대안**: 응답 필터링으로 PROJ-C 관련 이슈만 제거

### 2. pkey가 간접 참조인 요청

```
GET /jira/rest/api/2/issue/PROJ-A-123/comment
```
- 경로에 pkey가 있음 (PROJ-A) → 사전 검증 가능

```
GET /jira/rest/api/2/myself
```
- pkey 없음 → 사용자 프로필 조회, 프로젝트 무관 → 허용

### 3. 생성(POST) 요청

```
POST /jira/rest/api/2/issue
Body: {"fields": {"project": {"key": "PROJ-C"}, "summary": "..."}}
```
- pkey가 body에 존재 → body 파싱으로 추출 필요
- 인가 외 프로젝트에 이슈 생성 차단

### 4. 권한 API 장애

```
권한 API 500 에러 → 사용자 pkey 목록 조회 실패
```
- **Fail-closed (권장)**: 차단 + 503 Service Unavailable
- Fail-open: 캐시 fallback → 만료된 캐시라도 사용 (보안 위험)

## 구현 영향도 (Phase 1 기준)

| 파일 | 변경 내용 | 규모 |
|---|---|---|
| `app/models.py` | `UserPkeyScope` 모델 추가 | ~15줄 |
| 신규: `app/auth/pkey_extractor.py` | pkey 추출기 (Jira 우선) | ~40줄 |
| 신규: `app/auth/authorization.py` | 권한 API 호출 + 캐시 | ~50줄 |
| `app/routers/proxy.py` | pkey 검증 로직 추가 | ~20줄 |
| 신규: `app/auth/keycloak.py` | Keycloak JWT 검증 (JWKS) | ~40줄 |
| `app/deps.py` | `verify_admin_key` 제거 → `get_current_user` (Keycloak JWT) | ~20줄 |
| `app/routers/admin.py` | 삭제 (DB 직접 CRUD로 대체) | -110줄 |
| `app/routes.py` | admin router 등록 제거 | ~2줄 |

## 다음 액션

1. 설계 결정 항목 확인 (D-1 ~ D-6, fds_00001_07 참조)
2. Phase 1 구현 착수: pkey 사전 검증 + DB 캐시 + admin 라우터 제거
