# fds_00001 — 외부 서비스 API 미지정 문제: 설계 한계와 접근 방법

todo_idx: fds_00001
issue_idx: 04
생성일: 2026-03-04
최종 갱신일: 2026-03-04

---

## 문제 정의

인가 통제 게이트웨이는 Confluence, Jira 등 **다양한 외부 서비스를 프록시**한다.
그런데 각 서비스의 API 구조는 **전부 다르고**, 게이트웨이 개발 시점에 **알 수 없다**.

```
Confluence:  /wiki/rest/api/content, /wiki/rest/api/space, /wiki/rest/api/search ...
Jira:        /rest/api/2/issue, /rest/api/2/project, /rest/api/2/search ...
Slack:       /api/chat.postMessage, /api/conversations.list ...
GitHub:      /repos/{owner}/{repo}/issues, /user/repos ...
```

- 서비스마다 URL 패턴, 파라미터, 인증 방식이 전부 다름
- 신규 서비스 추가 시 어떤 API 경로가 필요한지 사전 파악 불가
- 현재 설계(화이트리스트 prefix 매칭)는 **경로를 미리 등록해야 통과** → 모든 API 경로를 열거해야 하는가?

## 현재 설계의 한계

### 1. 화이트리스트 전수 등록 부담

현재 `uri_mappings` 테이블에 허용 경로를 **prefix 단위로 등록**:

```
# Confluence
path_pattern: /wiki/rest/api      → /wiki/rest/api/* 전부 허용

# Jira
path_pattern: /rest/api/2         → /rest/api/2/* 전부 허용
```

**문제**: 서비스를 추가할 때마다 해당 서비스의 API 경로 체계를 파악해서 등록해야 함.
- Confluence REST API는 `/wiki/rest/api/` 하위에 통일되어 있어 1건 등록으로 충분
- 하지만 API 경로가 분산된 서비스(예: Slack `/api/*`)는 여러 건 등록 필요할 수 있음

### 2. 경로 체계를 모르면 등록할 수 없음

- 신규 외부 서비스의 API 문서를 확인하지 않으면 path_pattern 결정 불가
- 운영자가 외부 서비스 API 구조에 대한 지식 필요

### 3. 과도한 prefix는 보안 약화

```
# 너무 넓은 prefix → 의도하지 않은 경로도 허용
path_pattern: /           → 서비스 전체 오픈 (화이트리스트 무력화)

# 적절한 prefix
path_pattern: /wiki/rest/api   → REST API 영역만 허용
```

넓은 prefix로 등록하면 편하지만, 관리 콘솔·내부 경로까지 노출될 수 있음.

### 4. prefix 매칭의 표현력 한계

현재 `_matches_prefix` 로직:
```python
# path가 pattern으로 시작하면 허용
path == prefix or path.startswith(f"{prefix}/")
```

표현 불가능한 경우:
- 특정 경로만 제외 (예: `/rest/api/2/*` 허용하되 `/rest/api/2/admin` 차단)
- 경로 파라미터 패턴 (예: `/repos/{owner}/{repo}/issues` 형태)
- HTTP 메서드별 제어 (GET은 허용, DELETE는 차단)

## 접근 방법 5가지

### 방법 1: 대분류 prefix 등록 (현재 방식 유지)

서비스의 **API 루트 prefix를 1~3건 등록**하고, 하위 경로는 전부 허용.

```
Confluence: /wiki/rest/api
Jira:       /rest/api/2
Slack:      /api
```

| 장점 | 한계 |
|---|---|
| 구현 완료, 즉시 사용 가능 | 서비스 API 루트 경로는 파악 필요 |
| 등록 건수 최소화 (서비스당 1~3건) | 하위 경로 세밀 제어 불가 |
| 대부분의 REST API는 공통 prefix 존재 | 경로가 분산된 서비스에 부적합 |

**적합한 서비스**: Atlassian, GitHub, GitLab 등 REST API 경로가 통일된 서비스

### 방법 2: 서비스 레벨 전체 허용 모드

서비스 등록 시 `allow_all_paths` 옵션 추가. 활성화 시 uri_mappings 검사 생략.

```python
# services 테이블에 컬럼 추가
allow_all_paths: bool = False

# proxy 로직 변경
if service.allow_all_paths:
    pass  # 경로 검사 생략
else:
    allowed = await path_allowed_for_service(db, service.id, path)
    if not allowed:
        raise HTTPException(403)
```

| 장점 | 한계 |
|---|---|
| API 경로 몰라도 즉시 연동 가능 | 경로 레벨 접근 제어 포기 |
| 신규 서비스 온보딩 최소 비용 | 내부 관리 경로까지 노출 위험 |
| 운영자 API 지식 불필요 | 보안 감사 시 지적 가능 |

**적합한 경우**: 내부망에서만 사용, 보안 요구사항 낮은 환경, 빠른 PoC

### 방법 3: 패턴 매칭 확장 (와일드카드 + 정규식)

`path_pattern`에 와일드카드·정규식 지원 추가:

```
# 와일드카드
/rest/api/*/issue          → /rest/api/2/issue, /rest/api/3/issue
/repos/*/*/pulls           → /repos/org/repo/pulls

# 정규식
^/rest/api/\d+/.*$         → 버전 번호가 있는 API 전체
^/wiki/rest/api/(?!admin)  → admin 제외 허용
```

```python
import re

def _matches_pattern(path: str, pattern: str) -> bool:
    if pattern.startswith("^"):  # 정규식 모드
        return bool(re.match(pattern, path))
    # 와일드카드 → 정규식 변환
    regex = pattern.replace("*", "[^/]+").replace("**", ".*")
    return bool(re.match(f"^{regex}$", path))
```

| 장점 | 한계 |
|---|---|
| 세밀한 경로 제어 가능 | 패턴 작성에 API 지식 여전히 필요 |
| 특정 경로 제외 표현 가능 | 정규식 오류 시 의도치 않은 허용/차단 |
| 버전 번호 등 가변 경로 대응 | 관리 복잡도 증가 |

**적합한 경우**: 보안 정책이 엄격하고 경로별 세밀한 제어가 필요한 환경

> 경로 파라미터(`{param}`) 패턴 매칭은 별도 문서에서 상세 분석:
> `fds_00001_05_path_parameter_pattern.md`

### 방법 4: 거부 목록(Deny-list) 방식

화이트리스트 대신 **블랙리스트** 방식. 기본 허용, 위험 경로만 차단.

```
# deny_mappings 테이블
Confluence: /wiki/admin, /wiki/rest/api/admin
Jira:       /rest/api/2/configuration, /rest/api/2/serverInfo
공통:       /admin, /management, /actuator
```

```python
# 로직 반전
if service.access_mode == "deny_list":
    denied = await path_denied_for_service(db, service.id, path)
    if denied:
        raise HTTPException(403)
    # 나머지는 전부 허용
```

| 장점 | 한계 |
|---|---|
| API 경로 전수 파악 불필요 | 차단해야 할 경로를 빠뜨릴 위험 |
| 신규 서비스 온보딩 빠름 | 보안 기본 원칙(기본 거부) 위반 |
| 위험 경로만 관리하면 됨 | 외부 서비스 업데이트로 새 위험 경로 추가 시 즉시 대응 필요 |

**적합한 경우**: 내부 사용 전용, 신뢰할 수 있는 외부 서비스만 대상

### 방법 5: 하이브리드 (서비스별 정책 선택)

서비스마다 **접근 제어 모드를 선택**할 수 있도록 설계:

```python
class AccessMode(str, Enum):
    ALLOW_LIST = "allow_list"   # 화이트리스트 (현재 기본)
    DENY_LIST = "deny_list"     # 블랙리스트
    ALLOW_ALL = "allow_all"     # 전체 허용
```

```python
# services 테이블에 access_mode 컬럼 추가
# proxy 로직
match service.access_mode:
    case "allow_all":
        pass  # 검사 없이 통과
    case "deny_list":
        if await path_denied_for_service(db, service.id, path):
            raise HTTPException(403)
    case "allow_list" | _:
        if not await path_allowed_for_service(db, service.id, path):
            raise HTTPException(403)
```

| 장점 | 한계 |
|---|---|
| 서비스 특성에 맞는 정책 적용 | 구현 복잡도 증가 |
| API 구조 아는 서비스 → 화이트리스트 | 운영자가 정책 선택 판단 필요 |
| API 구조 모르는 서비스 → 전체 허용 또는 거부 목록 | 정책 혼재 시 관리 부담 |
| 점진적 보안 강화 가능 | Admin API 확장 필요 |

**적합한 경우**: 다양한 보안 수준의 서비스를 혼합 운영하는 환경

## 방법별 비교 매트릭스

| 기준 | 1. 대분류 prefix | 2. 전체 허용 | 3. 정규식 | 4. 거부 목록 | 5. 하이브리드 |
|---|---|---|---|---|---|
| API 사전 지식 필요도 | 중 | 없음 | 높음 | 낮음 | 선택 |
| 보안 수준 | 중 | 낮음 | 높음 | 낮음 | 선택 |
| 온보딩 속도 | 중 | 빠름 | 느림 | 빠름 | 빠름 |
| 구현 복잡도 | 낮음 (완료) | 낮음 | 중 | 중 | 중~높음 |
| 운영 부담 | 낮음 | 낮음 | 높음 | 중 | 중 |
| 확장성 | 중 | 낮음 | 높음 | 중 | 높음 |

## 현실적 권장 방향

### MVP (현재) → 유지

현재 **방법 1(대분류 prefix)** 으로 충분. 이유:
- Confluence, Jira 등 Atlassian 서비스는 API 루트 경로가 명확
- 서비스당 1~2건 등록으로 대부분 커버
- 이미 28/28 검증 완료

### Phase 2 → 방법 5 (하이브리드) 권장

```
services 테이블 확장:
  + access_mode: "allow_list" | "deny_list" | "allow_all"  (기본: allow_list)

uri_mappings 테이블 확장:
  + match_type: "prefix" | "regex"  (기본: prefix)
  + rule_type: "allow" | "deny"     (기본: allow)
```

이유:
1. **신규 서비스 온보딩 속도**: API 구조 모를 때 `allow_all`로 빠르게 연동, 이후 화이트리스트로 전환
2. **서비스별 최적 정책**: 보안 민감 서비스는 화이트리스트, 내부 도구는 전체 허용
3. **점진적 보안 강화**: `allow_all` → `deny_list` → `allow_list` 단계적 전환 가능
4. **하위 호환**: 기존 `allow_list` 방식 그대로 유지

### 운영 프로세스 제안

```
1. 신규 서비스 등록
   ├── API 구조 파악됨 → access_mode: allow_list + prefix 등록
   ├── API 구조 미파악 → access_mode: allow_all (임시)
   │   └── 이후 API 사용 패턴 로깅(proxy_logs) → 화이트리스트 전환
   └── 위험 경로만 파악됨 → access_mode: deny_list + 차단 경로 등록
```

## 근본적 한계 (해결 불가)

아래 항목들은 설계 방식과 무관하게 존재하는 **본질적 한계**:

| 한계 | 설명 |
|---|---|
| **외부 API 변경 추적 불가** | 외부 서비스가 API 경로를 변경·추가해도 게이트웨이가 알 수 없음 |
| **API 의미 파악 불가** | 경로만으로 해당 API가 읽기/쓰기/삭제인지 판단 불가 |
| **요청/응답 검증 불가** | 프록시는 body를 그대로 전달 — 페이로드 수준 검증 없음 |
| **권한 범위 불일치** | 게이트웨이 인가 ≠ 외부 서비스 인가 (토큰 권한 초과/부족 가능) |
| **서비스 간 의존성** | Confluence에서 Jira 링크 조회 등 서비스 간 연쇄 호출은 제어 불가 |

> 이 한계들은 프록시 게이트웨이의 본질적 특성이며, 완전한 해결은 **API Management Platform**(Kong, Apigee 등) 수준의 시스템이 필요.

## 다음 액션

1. MVP는 현재 방식(대분류 prefix) 유지 — 추가 구현 불필요
2. Phase 2 설계 시 `access_mode` 컬럼 추가 검토
3. `proxy_logs` 구현 시 API 사용 패턴 분석 → 화이트리스트 자동 추천 기능 검토
