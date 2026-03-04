# fds_00001 — 경로 파라미터 패턴 매칭 검토

todo_idx: fds_00001
issue_idx: 05
생성일: 2026-03-04
최종 갱신일: 2026-03-04
관련: fds_00001_04 (외부 서비스 API 미지정 문제)

---

## 배경

고객이 허용 경로를 **특정 패턴으로 지정**해 주시는데,
그 중에는 `/page/{page_id}/{action}` 처럼 **경로 파라미터가 포함된 패턴**이 존재한다.

현재 MVP의 prefix 매칭으로는 이 패턴을 **정확하게 표현할 수 없는** 경우가 있다.

## 문제 정의

### 고객 지정 패턴 예시

```
/page/{page_id}/{action}
/rest/api/2/issue/{issue_key}
/wiki/rest/api/content/{content_id}/child/{child_type}
/repos/{owner}/{repo}/pulls
```

### 실제 요청 예시

```
/page/12345/view              → page_id=12345, action=view
/page/67890/edit              → page_id=67890, action=edit
/rest/api/2/issue/PROJ-123    → issue_key=PROJ-123
/wiki/rest/api/content/98765/child/attachment
/repos/hynix/fds/pulls        → owner=hynix, repo=fds
```

### 현재 prefix 매칭의 동작

| 고객 지정 패턴 | prefix로 등록 | 매칭 결과 |
|---|---|---|
| `/page/{page_id}/{action}` | `/page` | `/page/*` 전부 허용 — 적절할 수 있음 |
| `/page/{page_id}/view` (view만 허용) | `/page` | `/page/123/edit`도 허용 — **과잉 허용** |
| `/rest/api/2/issue/{key}` | `/rest/api/2/issue` | 적절 (말단 파라미터) |
| `/{owner}/{repo}/pulls` | 등록 불가 | **첫 세그먼트부터 가변** — prefix 표현 불가 |
| `/content/{id}/child/{type}` | `/content` | `/content/123/admin`도 허용 — **과잉 허용** |

### 핵심 문제

prefix 매칭은 **"이 경로로 시작하면 전부 허용"** 이므로:
- 중간·끝에 있는 고정 세그먼트를 제약할 수 없음
- 세그먼트 깊이(depth)를 제한할 수 없음
- 특정 위치의 값을 제한할 수 없음 (예: action=view만)

```
고객 의도: /page/{page_id}/view 만 허용
prefix /page 등록 시:
  /page/123/view    ✓ 허용 (의도)
  /page/123/edit    ✓ 허용 (의도 아님)
  /page/123/delete  ✓ 허용 (의도 아님)
  /page/123/a/b/c   ✓ 허용 (의도 아님)
```

## 경로 파라미터 패턴 유형 분류

| 유형 | 패턴 예시 | 특징 | prefix 대응 |
|---|---|---|---|
| **A. 말단 파라미터** | `/issue/{key}` | 마지막 세그먼트만 가변 | O — `/issue` prefix 충분 |
| **B. 중간 파라미터 + 고정 꼬리** | `/page/{id}/view` | 가변 뒤에 고정값 | X — view 제약 불가 |
| **C. 선행 파라미터** | `/{owner}/{repo}/pulls` | 앞 세그먼트가 가변 | X — prefix 자체가 가변 |
| **D. 다중 파라미터 혼합** | `/content/{id}/child/{type}` | 고정-가변 교차 반복 | X — 중간 고정값 제약 불가 |

### 유형별 빈도 추정 (일반적인 REST API)

| 유형 | 빈도 | 대표 서비스 |
|---|---|---|
| A (말단) | **매우 높음** | 대부분의 REST API (`/resource/{id}`) |
| B (중간+꼬리) | 중간 | Confluence (`/content/{id}/child/{type}`), CMS 계열 |
| C (선행) | 낮음 | GitHub (`/{owner}/{repo}/...`), 멀티테넌트 |
| D (다중 혼합) | 낮음 | 복잡한 계층형 API |

> A 유형이 대다수이므로 **현재 prefix 매칭으로 실무 대부분 커버 가능**.
> B·C·D가 필요한 시점에 세그먼트 패턴 매칭을 도입하면 됨.

## 해결 방안: 세그먼트 패턴 매칭 (segment match_type)

### 핵심 아이디어

고객이 지정한 `{param}` 패턴을 **path_pattern에 그대로 저장**하고,
`{param}` 부분을 "슬래시가 아닌 문자 1개 이상"으로 매칭한다.

### 구현

```python
import re

def _matches_segment_pattern(path: str, pattern: str) -> bool:
    """
    /page/{page_id}/{action} 패턴을 /page/123/view 에 매칭.
    {param} → 임의의 비-슬래시 문자열 1개 이상.
    고정 세그먼트는 정확히 일치해야 함.
    """
    path = _normalize_path(path)
    pattern = _normalize_path(pattern)

    # {param_name} → ([^/]+) 로 변환
    regex = re.sub(r'\{[^}]+\}', '([^/]+)', re.escape(pattern).replace(r'\{', '{').replace(r'\}', '}'))
    # re.escape 후 {, } 복원이 복잡하므로 단순화:
    regex = re.sub(r'\{[^}]+\}', '[^/]+', pattern)
    # 양쪽 슬래시 정규화 후 전체 매칭
    return bool(re.fullmatch(regex, path))
```

간결 버전:
```python
def _matches_segment_pattern(path: str, pattern: str) -> bool:
    path = _normalize_path(path)
    pattern = _normalize_path(pattern)
    regex = re.sub(r'\{[^}]+\}', '[^/]+', pattern)
    return bool(re.fullmatch(regex, path))
```

### 동작 검증

```
패턴: /page/{page_id}/{action}
  /page/123/view      → ✓ MATCH
  /page/456/edit      → ✓ MATCH
  /page/789           → ✗ NO MATCH (세그먼트 부족)
  /page/123/view/sub  → ✗ NO MATCH (세그먼트 초과)

패턴: /page/{page_id}/view
  /page/123/view      → ✓ MATCH
  /page/123/edit      → ✗ NO MATCH (action 제한 동작)
  /page/123/view/sub  → ✗ NO MATCH

패턴: /repos/{owner}/{repo}/pulls
  /repos/org/myrepo/pulls  → ✓ MATCH
  /repos/org/myrepo/issues → ✗ NO MATCH

패턴: /content/{id}/child/{type}
  /content/98765/child/attachment → ✓ MATCH
  /content/98765/admin            → ✗ NO MATCH
  /content/98765/child            → ✗ NO MATCH (세그먼트 부족)
```

### match_type 확장 설계

`uri_mappings` 테이블에 `match_type` 컬럼 추가:

```
uri_mappings 테이블:
  path_pattern   TEXT NOT NULL       -- 기존
  + match_type   TEXT DEFAULT 'prefix'  -- 추가: "prefix" | "segment" | "exact"
```

| match_type | path_pattern 예시 | 매칭 방식 |
|---|---|---|
| `prefix` (기본) | `/wiki/rest/api` | 현재 방식 — startswith |
| `segment` | `/page/{page_id}/{action}` | `{param}` → 세그먼트 매칭 (fullmatch) |
| `exact` | `/api/healthz` | 경로 완전 일치 |

### 매칭 로직 통합

```python
def _matches_path(path: str, pattern: str, match_type: str = "prefix") -> bool:
    if match_type == "exact":
        return _normalize_path(path) == _normalize_path(pattern)
    if match_type == "segment":
        return _matches_segment_pattern(path, pattern)
    # 기본: prefix (현재 동작 유지)
    return _matches_prefix(path, pattern)
```

`path_allowed_for_service` 변경:
```python
async def path_allowed_for_service(
    session: AsyncSession, service_id: int, request_path: str
) -> bool:
    mappings = await get_mappings_by_service_id(session, service_id)
    return any(
        _matches_path(request_path, m.path_pattern, m.match_type)
        for m in mappings if m.is_active
    )
```

## 고객 지정 패턴 → 등록 가이드

고객이 경로를 지정할 때 어떤 match_type으로 등록하면 되는지:

| 고객 지정 | path_pattern | match_type | 비고 |
|---|---|---|---|
| `/wiki/rest/api` 하위 전체 | `/wiki/rest/api` | `prefix` | 하위 전부 허용 |
| `/rest/api/2/issue/{key}` | `/rest/api/2/issue` | `prefix` | 말단 파라미터 → prefix 충분 |
| `/page/{page_id}/{action}` | `/page/{page_id}/{action}` | `segment` | 그대로 등록 |
| `/page/{page_id}/view` | `/page/{page_id}/view` | `segment` | action=view만 허용 |
| `/content/{id}/child/{type}` | `/content/{id}/child/{type}` | `segment` | 다중 파라미터 혼합 |
| `/repos/{owner}/{repo}/pulls` | `/repos/{owner}/{repo}/pulls` | `segment` | 선행 파라미터 |
| 정확히 `/api/healthz` 만 | `/api/healthz` | `exact` | 단일 경로 |

**판단 기준**: 고객 패턴에 `{...}`가 있고, 그 뒤에 고정 세그먼트가 있으면 → `segment`

## match_type 자동 판별 (선택적 편의 기능)

운영자가 match_type을 직접 지정하지 않아도 패턴에서 자동 추론하는 방안:

```python
def infer_match_type(pattern: str) -> str:
    if '{' in pattern and '}' in pattern:
        return "segment"
    if '*' not in pattern and not pattern.endswith('/'):
        # 슬래시 없는 단일 경로 → exact 후보 (운영자 판단)
        pass
    return "prefix"
```

> Admin API에서 `match_type` 미지정 시 자동 추론 가능.
> 단, 명시적 지정을 권장 (의도 명확화).

## 한계 및 주의사항

### 1. 세그먼트 깊이 고정

segment 매칭은 **패턴의 세그먼트 수와 정확히 일치**해야 함:
```
패턴: /page/{id}/{action}  → 3세그먼트 고정
  /page/123/view        → ✓ (3세그먼트)
  /page/123/view/detail → ✗ (4세그먼트 — 불일치)
```

하위 경로까지 허용하려면 패턴 2건 등록 필요:
```
/page/{id}/{action}           (segment) — 3세그먼트
/page/{id}/{action}/{sub}     (segment) — 4세그먼트
```

또는 prefix와 병행:
```
/page/{id}/view    (segment) — view action만, 정확히 3세그먼트
/page/{id}/edit    (segment) — edit action만
```

### 2. 파라미터 값 제약 없음

`{action}`에 **어떤 값이든** 들어올 수 있음:
```
패턴: /page/{page_id}/{action}
  /page/123/view          → ✓
  /page/123/../../etc/pwd → ✓ (path traversal 문자도 통과)
```

**대응**: 프록시 단에서 path traversal 검사 추가 (Phase 2 보안):
```python
if '..' in path:
    raise HTTPException(400, "Invalid path")
```

### 3. 정규식보다 표현력 제한

segment 패턴은 **단순 placeholder만 지원**:
- `{param}` → 슬래시 제외 아무 문자
- 숫자만 허용 (`{id:\d+}`) 같은 타입 제약 없음
- 선택적 세그먼트 (`/page/{id}(/view)?`) 불가

더 복잡한 제약이 필요하면 → regex match_type 사용 (fds_00001_04 방법 3 참조)

### 4. 성능

| match_type | 매칭 비용 |
|---|---|
| prefix | O(1) — 문자열 startswith |
| exact | O(1) — 문자열 비교 |
| segment | O(n) — 정규식 컴파일 + 매칭 (n = 매핑 수) |

> 매핑 수가 수백 건 이하면 성능 문제 없음.
> 대량 매핑 시 정규식 사전 컴파일(캐시)로 최적화 가능.

## 구현 영향도 (변경 범위)

| 파일 | 변경 내용 | 규모 |
|---|---|---|
| `app/models.py` | UriMapping에 `match_type` 컬럼 추가 | 1줄 |
| `app/schemas.py` | UriMappingCreate/Out에 `match_type` 필드 추가 | 2줄 |
| `app/crud/mapping.py` | `_matches_segment_pattern` 함수 + `_matches_path` 분기 | ~15줄 |
| `app/routers/admin.py` | 변경 없음 (스키마가 자동 반영) | 0 |
| DB 마이그레이션 | `ALTER TABLE uri_mappings ADD match_type TEXT DEFAULT 'prefix'` | 1줄 |

**총 변경량**: ~20줄 — 소규모 변경

## MVP vs Phase 2 판단

| 관점 | 평가 |
|---|---|
| **지금 당장 필요한가?** | 고객 지정 패턴 중 A 유형(말단 파라미터)이 대부분이면 → MVP prefix로 충분 |
| **B·C·D 유형이 있는가?** | 있으면 → segment 매칭 즉시 구현 검토 |
| **구현 비용** | ~20줄, 기존 로직 변경 최소 → Phase 2 초기 또는 필요 시 즉시 추가 가능 |
| **기존 호환** | match_type 기본값 `prefix` → 기존 매핑 동작 변경 없음 |

## 다음 액션

1. 고객 지정 경로 패턴 중 B·C·D 유형 존재 여부 확인
2. 존재 시 → `match_type` + `_matches_segment_pattern` 구현 (소규모)
3. 미존재 시 → MVP prefix 유지, Phase 2에서 확장
