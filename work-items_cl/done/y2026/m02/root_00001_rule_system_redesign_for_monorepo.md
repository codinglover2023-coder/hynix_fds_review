# root_00001: Rule 시스템 모노레포 재설계

상태: **완료** (2026-02-28)
생성일: 2026-02-28
출처: `rule/achive/20260228_workflow_rules.md` (단일 프로젝트용)

## 목적
- 기존 `render_api_test` 단일 프로젝트 규칙을 CycleStack 모노레포에 맞게 재설계
- 최상위 rule이 하위 프로젝트별 rule을 위임·실행할 수 있는 구조 확립

## 검토 항목

### 1. 규칙 계층 구조 설계 ✅ 결정 완료
- [x] 최상위 `rule/workflow_rules.md` → 모노레포 공통 규칙만 유지
- [x] 하위 프로젝트별 `{sub_project}/rule/workflow_rules.md` → **도입 확정**
  - 실물: `project_arch/rule/workflow_rules.md` (Rule 101~105 이식 완료)
  - root_00002 디스패치 테이블로 구조 확정
- [x] 규칙 우선순위: **최상위 rule > 하위 rule** (충돌 시 최상위 우선)

### 2. Rule 000~001 (메타 규칙) 변환 ✅ 결정 완료
- [x] Rule 000 재로딩: **모노레포 전체 rule 탐색 경로 확정**
  - `rule/workflow_rules.md` (최상위 공통)
  - `{sub_project}/rule/*.md` 순회 (하위 프로젝트별)
  - root_00002 디스패치 테이블에 의해 `{prefix} rule{NNN}` 명령으로 경로 결정
- [x] Rule 001 변경 정책: "현재 저장소 코드와 디렉터리 구조" 기준 유지 — **변경 불필요 확인**

### 3. Rule 010~020 (작업 흐름 / 파일 네이밍) 변환 ✅ 결정 완료
- [x] `work-items_cl/` 경로 → **옵션 C (혼합)** 확정
  - 공통/크로스 프로젝트 작업 → 최상위 `work-items_cl/`
  - 프로젝트 특화 작업 → `{sub_project}/work-items_cl/`
- [x] `work-items_co/` (Codex용) → **유지, 옵션 C 동일 적용** 확정
  - 공통/크로스 프로젝트 작업 → 최상위 `work-items_co/`
  - 프로젝트 특화 작업 → `{sub_project}/work-items_co/`

#### 확정된 디렉터리 구조
```
work-items_cl/  또는  work-items_co/  (동일 구조)
├── todo/                   # 진행 중 작업
├── todo_issues/            # 진행 중 작업의 쟁점
├── done/                   # 완료된 작업 (연/월 보관)
│   └── y2026/
│       └── m02/
└── done_issues/            # 완료된 쟁점 (연/월 보관)
    └── y2026/
        └── m02/
```

#### 전체 모노레포 적용
```
CycleStack/
├── work-items_cl/          # Claude 공통 (크로스 프로젝트)
│   ├── todo/
│   ├── todo_issues/
│   ├── done/y2026/m02/
│   └── done_issues/y2026/m02/
├── work-items_co/          # Codex 공통 (크로스 프로젝트)
│   ├── todo/
│   ├── todo_issues/
│   ├── done/y2026/m02/
│   └── done_issues/y2026/m02/
├── render_api/
│   ├── work-items_cl/      # (동일 하위 구조)
│   └── work-items_co/
├── render_web/
│   ├── work-items_cl/
│   └── work-items_co/
├── render_cron/
│   ├── work-items_cl/
│   └── work-items_co/
├── render_anal/
│   ├── work-items_cl/
│   └── work-items_co/
├── common_data/
│   ├── work-items_cl/
│   └── work-items_co/
├── project_gas/
│   ├── work-items_cl/
│   └── work-items_co/
└── project_arch/
    ├── work-items_cl/
    └── work-items_co/
```

#### 보관 규칙
- 완료된 작업: `todo/` → `done/y{YYYY}/m{MM}/`
- 완료된 쟁점: `todo_issues/` → `done_issues/y{YYYY}/m{MM}/`
- 연/월은 완료 처리 시점 기준


### 4. Rule 030 (실행 커뮤니케이션) 변환 ✅ 결정 완료
- [x] 변경 대상 파일에 "어느 하위 프로젝트" 소속인지 명시 규칙 추가
- [x] 크로스 프로젝트 변경 시 **CPCR (Cross-Project Change Report)** 필수

#### CPCR 트리거 (1개 이상 만족 시 필수)
1. `common_*` 또는 최상위 공통 디렉터리 변경
2. 2개 이상 sub_project에 영향을 주는 경로/계약 변경
3. `/api/*` ↔ `/web/*` 경로 호환성에 영향 가능 변경

#### CPCR 6필드 포맷 (커밋 메시지 / PR 설명 / 작업 문서 공통)
```
[CPCR-Title] 한 줄 요약
Scope: affected sub_projects = {render_api, render_web, ...}
Change Type: {interface|behavior|data|ops|docs}
Risk: {low|mid|high} + 이유 1줄
Verification: 수행/확인한 체크 1~3개
Rollback: 되돌리는 방법 1줄(없으면 "N/A")
```

### 5. Rule 050 (문서 동기화) 변환 ✅ 결정 완료
- [x] `docs/` → **하위 프로젝트별 분산 관리** 확정
  - `{sub_project}/docs/` 기준으로 각 프로젝트가 자체 문서 관리
  - `google_apps_script/doc/` → `project_gas/docs/`
- [x] README.md → **2-레벨 정책** 확정

#### 최상위 `CycleStack/README.md` (인덱스 역할만)
- sub_project 목록
- 각 프로젝트 엔트리포인트 (실행/배포/cron)
- 공통 규칙 링크 (`rule/workflow_rules.md`)

#### 각 `{sub_project}/README.md` (최소 5항목 강제)
1. **Purpose** — 한 줄
2. **Entrypoint** — 실행 명령 또는 서비스
3. **Envs** — 필수 환경변수 표
4. **How to test** — 없으면 "N/A"
5. **Ownership/Contact** — 담당 규칙/문서 링크

#### 동기화 방식
- 자동 생성/강제 동기화 **금지**
- Rule 050에서 **항목 존재 여부만 점검**

### 6. Rule 060~070 (안전 게이트 / API 변경) 변환 ✅ 결정 완료
- [x] `tests/` 경로: **분산 기본 + 공통 contract 최소화** 확정
  - `{sub_project}/tests/` — 기본 (unit, integration)
  - 최상위 `tests/` — 공통 계약/호환성 테스트만 허용 (contract/smoke)
- [x] FastAPI 라우터 변경 시 **merge 게이트** 확정
  - 다음 중 1개 이상 수행 기록 필수:
    1. Flask mount 경로 스모크 테스트 (요청 2~3개)
    2. `/api/*` ↔ `/web/*` 라우팅 호환성 체크 (리다이렉트/프록시 규칙 확인)
    3. OpenAPI 스키마 diff (변경 영향 확인)
- [x] `/web/*` ↔ `/api/*` 크로스 경로 호환성 검사 규칙 — 위 게이트에 포함

#### 테스트 레벨 정의
| 레벨 | 위치 | 범위 |
|---|---|---|
| unit | `{sub_project}/tests/` | sub_project 내부 |
| integration | `{sub_project}/tests/` | sub_project 내부 (필요시) |
| contract/smoke | 최상위 `tests/` | 크로스 프로젝트 최소 세트 |

### 7. Rule 080 (Apps Script 브리지) 변환 ✅ 결정 완료 (2단계)
- [x] **1단계 (지금 확정)**:
  - 코드 경로: `project_gas/src/`
  - 계약 경로: `project_gas/docs/contracts/` (FastAPI↔GAS payload 스펙)
  - Rule 080은 "경로 변경 + 계약 위치"까지만 반영
- [ ] **2단계 (구조 확정 후 적용)**:
  - FastAPI endpoint별 payload contract 문서 생성 (요청/응답 JSON 예시 포함)
  - contract 변경 시 CPCR (섹션 4) 강제

### 8. Rule 095~096 (인코딩 정책) 변환 ✅ 결정 완료
- [x] 최상위 `.editorconfig`, `.gitattributes` → **모노레포 전체 적용 확정**
  - 참고: 실물 파일 미생성 — `rule/workflow_rules.md` 작성 시 정책 명시, 파일 생성은 별도
- [x] 하위 프로젝트별 오버라이드 → **허용** (필요 시 `{sub_project}/.editorconfig` 가능)

## 완료 기준
- [x] 모노레포용 Rule 000~096 초안 작성 완료 — `rule/workflow_rules.md` 생성
- [x] 하위 프로젝트 rule 위임 패턴 확정 — Rule 101~112 위임 정책 포함
- [x] CLAUDE.md에 새 구조 반영 — 디스패치 테이블 + Base Rules 정책

## 산출물
- `rule/workflow_rules.md` — 모노레포 Base Rules (Rule 000~096 + 101~112 위임)

## Resolved Issues
- `root_00001_00_kickoff_scope.md` — 작업 범위 확정, 즉시 수행/의사결정 분리 완료
- `root_00001_01_design_review.md` — Rule 000~096 전체 변환 매핑 확정, 설계 원칙 3개 확립
- `root_00001_02_validation_and_output.md` — 산출물 정의, 검증 체크리스트 작성

## 후속 작업 (별도 todo)
- Rule 080 2단계: payload contract 문서 생성 + CPCR 강제
- `.editorconfig`, `.gitattributes` 실물 파일 생성
