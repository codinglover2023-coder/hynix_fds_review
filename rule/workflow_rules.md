# 워크플로우 규칙 (CycleStack 모노레포)

최종 수정일: 2026-03-04
적용 범위: CycleStack 모노레포 전체 (Base Rules)
출처: `rule/achive/20260228_workflow_rules.md` → 모노레포 재설계 (`root_00001`)

---

## Rule 000: 규칙 재로딩 트리거
- 사용자가 `{prefix} rule000`을 호출하면 현재 `rule/` 문서를 다시 읽고 이후 작업에 즉시 반영한다.
- 우선 적용 순서:
  1. `rule/workflow_rules.md` (최상위 공통 — Base Rules)
  2. `{sub_project}/rule/*.md` (하위 프로젝트별 규칙)
- prefix별 rule 탐색 경로는 CLAUDE.md 디스패치 테이블로 결정한다.
- 충돌 시: **Base Rules(최상위) > Subproject Rules(하위)**

## Rule 001: 규칙 변경 정책
- 규칙은 고정 불변이 아니며 프로젝트 구조/운영 방식 변화에 따라 갱신한다.
- 규칙 간 충돌 시 "현재 저장소 코드와 디렉터리 구조"를 단일 사실 기준으로 사용한다.

---

## Rule 010: 작업 흐름
- 작업 문서는 `work-items_cl/` (Claude) 또는 `work-items_co/` (Codex)에서 관리한다.
- **옵션 C (혼합)** 적용:
  - 공통/크로스 프로젝트 작업 → 최상위 `work-items_cl/` (또는 `_co/`)
  - 프로젝트 특화 작업 → `{sub_project}/work-items_cl/` (또는 `_co/`)
- 4폴더 구조:
  - `todo/` — 진행 중 작업
  - `todo_issues/` — 진행 중 작업의 쟁점
  - `done/y{YYYY}/m{MM}/` — 완료된 작업 (연/월 보관)
  - `done_issues/y{YYYY}/m{MM}/` — 완료된 쟁점 (연/월 보관)
- 보관 시 연/월은 완료 처리 시점 기준이다.
- 크로스 작업 공간:
  - `work-items_cl_co/` — Claude↔Codex 공유 핸드오프 공간 (최상위만, Rule 9001 참조)

## Rule 020: 파일 네이밍 규칙
- `todo_idx` 형식: `{prefix}_{NNNNN}` (예: `root_00001`, `api_00001`)
- prefix는 디스패치 테이블과 동일: `root`, `api`, `web`, `cron`, `anal`, `gas`, `data`, `arch`
- 파일명: `{todo_idx}_{topic}.md` (예: `api_00001_some_task.md`)
- issue 파일: `{todo_idx}_{issue_idx}_{topic}.md` (예: `root_00001_01_design_review.md`)

## Rule 030: 실행 커뮤니케이션 규칙
- 작업 시작 시 아래 3가지를 명시한다:
  1. 목표
  2. 변경 대상 파일 + **소속 하위 프로젝트**
  3. 완료 기준(검증 포함)
- 작업 종료 시 아래 3가지를 남긴다:
  1. 변경 파일 목록
  2. 검증 결과
  3. 남은 리스크/후속 작업
- **크로스 프로젝트 변경 시 CPCR (Cross-Project Change Report) 필수**

### CPCR 트리거 (1개 이상 만족 시 필수)
1. `common_*` 또는 최상위 공통 디렉터리 변경
2. 2개 이상 sub_project에 영향을 주는 경로/계약 변경
3. `/api/*` ↔ `/web/*` 경로 호환성에 영향 가능 변경

### CPCR 6필드 포맷 (커밋 메시지 / PR 설명 / 작업 문서 공통)
```
[CPCR-Title] 한 줄 요약
Scope: affected sub_projects = {render_api, render_web, ...}
Change Type: {interface|behavior|data|ops|docs}
Risk: {low|mid|high} + 이유 1줄
Verification: 수행/확인한 체크 1~3개
Rollback: 되돌리는 방법 1줄(없으면 "N/A")
```

## Rule 040: 작업-이슈 연결 정책
- `todo/` 진행 중 쟁점이 생기면 `todo_issues/`에 issue 문서를 생성 또는 갱신한다.
- 이슈 문서 필수 섹션:
  1. 목적
  2. 현재 결정사항
  3. 남은 작업
  4. 다음 액션

---

## Rule 050: 문서 동기화 정책
- **하위 프로젝트별 `{sub_project}/docs/` 분산 관리** 원칙.
- 코드 변경이 API/운영에 영향을 주면 해당 프로젝트의 문서를 함께 갱신한다.
- 자동 생성/강제 동기화 **금지** — Rule 050은 **항목 존재 여부만 점검**.

### README.md 2-레벨 정책

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

---

## Rule 060: 런타임 안전 게이트
- 동작 변경이 있는 수정은 최소 1개 이상의 검증을 수행한다.
- **테스트 경로 분산 정책**:
  - `{sub_project}/tests/` — 기본 (unit, integration)
  - 최상위 `tests/` — 공통 계약/호환성 테스트만 허용 (contract/smoke)
- 검증을 수행하지 못한 경우 사유를 결과에 명시한다.

### 테스트 레벨 정의
| 레벨 | 위치 | 범위 |
|---|---|---|
| unit | `{sub_project}/tests/` | sub_project 내부 |
| integration | `{sub_project}/tests/` | sub_project 내부 (필요시) |
| contract/smoke | 최상위 `tests/` | 크로스 프로젝트 최소 세트 |

## Rule 070: API 변경 게이트
- FastAPI 라우터/스키마 변경 시 **다음 중 1개 이상 수행 기록 필수**:
  1. Flask mount 경로 스모크 테스트 (요청 2~3개)
  2. `/api/*` ↔ `/web/*` 라우팅 호환성 체크 (리다이렉트/프록시 규칙 확인)
  3. OpenAPI 스키마 diff (변경 영향 확인)
- 브레이킹 변경이면 `todo_issues/`에 마이그레이션 노트를 남긴다.

---

## Rule 080: Apps Script 브리지 게이트

### 1단계 (확정)
- 코드 경로: `project_gas/src/`
- 계약 경로: `project_gas/docs/contracts/` (FastAPI↔GAS payload 스펙)
- `project_gas/` 변경 시 대응 FastAPI 경로와 페이로드 계약을 함께 점검한다.

### 2단계 (구조 확정 후 적용 — 별도 todo)
- FastAPI endpoint별 payload contract 문서 생성 (요청/응답 JSON 예시 포함)
- contract 변경 시 CPCR (Rule 030) 강제

---

## Rule 090: Config/Schema 게이트
- `common_data/config.py` 변경 시 `.env.template` 키 동기화 필수.
- 환경 변수 추가/삭제: `.env.template` + `common_data/config.py` + `render.yaml`(또는 Render UI env) **3종 동기화 필수**.
- 필드 추가/삭제 시 영향 프로젝트를 Impact Matrix (`rule/ref/impact_matrix.md`)로 확인.

---

## Rule 095: 인코딩 정책
- 프로젝트의 모든 `.md` 파일은 `UTF-8 (BOM 없음) + LF`로 저장한다.
- 한글 깨짐이 발견되면 원문 복원 후 저장하고, 연관 문서까지 점검한다.
- **최상위 `.editorconfig`, `.gitattributes`로 모노레포 전체 적용.**
- 하위 프로젝트별 오버라이드 허용 (필요 시 `{sub_project}/.editorconfig` 가능).

## Rule 096: 인코딩 강제 장치
- 인코딩 규칙은 문서 선언만으로 끝내지 않고 저장소 설정으로 강제한다.
  1. `.editorconfig`로 `LF`, `UTF-8`, `final newline` 기본값을 적용한다.
  2. `.gitattributes`로 `.md`의 `eol=lf`를 고정한다.
- `.editorconfig`, `.gitattributes` 실물 파일은 별도 생성 (본 규칙은 정책 선언).

---

## 자동화 규칙 (Rule 101~112) — 위임 정책

자동화 규칙은 **하위 프로젝트별 `{sub_project}/rule/workflow_rules.md`**에서 정의한다.
최상위에서는 공통 구조와 크로스 프로젝트 자동화만 정의한다.

### 공통 구조

#### Rule 101~105: Todo Kickoff/Execution/Validation
- 호출: `{prefix} rule{NNN} {todo_idx}` (예: `api rule101 api_00001`)
- `todo_idx` 형식: `{prefix}_{NNNNN}`
- 경로: `work-items_cl/todo/`, `work-items_cl/todo_issues/`
- done 보관: `work-items_cl/done/y{YYYY}/m{MM}/`, `work-items_cl/done_issues/y{YYYY}/m{MM}/`
- 상세 동작은 각 프로젝트 rule 파일 참조 (참조 구현: `project_arch/rule/workflow_rules.md`)

#### Rule 103: Jupyter 노트북 생성
- 프로젝트별 `{sub_project}/notebooks/` 유지
- `find_project_root()` 판별: `work-items_cl` 또는 `work-items_co` 폴더 존재 여부
- **노트북 초기화 셀 필수** (첫 번째 코드 셀):
```python
from pathlib import Path
from dotenv import load_dotenv

def find_project_root(start: Path) -> Path:
    cur = start.resolve()
    for cand in [cur, *cur.parents]:
        if (cand / 'work-items_cl').exists() or (cand / 'work-items_co').exists():
            return cand
    raise FileNotFoundError('project root not found')

ROOT = find_project_root(Path.cwd())
load_dotenv(ROOT / '.env', override=True)
```

#### Rule 106~108: Pipeline 관련
- 파이프라인 코드: `common_data/pipeline/`
- 모든 하위 프로젝트가 `common_data.pipeline`을 import해서 사용

### 크로스 프로젝트 자동화

#### Rule 109: Endpoint Handoff Package Export (root rule)
- 하위 프로젝트 간 handoff 가능
- 각 프로젝트별 handoff 경로: `{sub_project}/handoff/`
- **root rule이 크로스 프로젝트 handoff를 제어**
- 호출 형식: `root rule109 {source_prefix} {target_prefix} {endpoint_idx}`
  - 예: `root rule109 anal api 00001`
- root rule 수행 사항:
  1. source handoff 패키지 검증 (manifest, summary 존재 확인)
  2. target 프로젝트 handoff 경로로 복사
  3. target 프로젝트 work-items에 이관 기록 생성

#### Rule 110~112: Handoff Documentation/Review/Archive
- 상세 절차는 원본 rule 참조 (`rule/achive/20260228_workflow_rules.md`)
- 모노레포 경로 재매핑: `work-items/` → `work-items_cl/`, `pipeline/` → `common_data/pipeline/`

---

## 운영 규칙 (Rule 200~) — 조회/리포트

#### Rule 200: Todo 현황 대시보드

- 사용자가 `{prefix} rule200`을 호출하면, 해당 프로젝트의 전체 작업 현황을 요약 테이블로 출력한다.
- 호출 형식:
  - `{prefix} rule200` — 해당 프로젝트 todo 전체 요약
  - `root rule200` — 모노레포 전체 (모든 하위 프로젝트 포함)
  - `{prefix} {sub_prefix} rule200` — 하위 프로젝트 (예: `anal av rule200`)

1. 탐색 대상:
   - `work-items_cl/todo/*.md` — 진행 중 작업
   - `work-items_cl/done/y{YYYY}/m{MM}/*.md` — 완료 작업 (최근 1개월)
   - `work-items_cl/todo_issues/*.md` — 진행 중 이슈 (건수만)
2. 출력 형식:

   **진행 중:**
   ```
   | todo_idx | 제목 | 상태 | 관련 | issue |
   |----------|------|------|------|-------|
   | api_00006 | Stocklist Sheet Init | kickoff | anal_av_00005, cron_00008 | 0건 |
   ```

   **최근 완료 (1개월):**
   ```
   | todo_idx | 제목 | 완료일 |
   |----------|------|--------|
   | cron_00004 | Render Deploy | 2026-03-02 |
   ```

3. 각 todo 파일에서 추출하는 정보:
   - `todo_idx`: 파일 헤더의 `todo_idx` 필드
   - `제목`: 파일 첫 번째 `# TODO:` 또는 `# ` 헤딩
   - `상태`: 헤더의 `상태` 필드
   - `관련`: 헤더의 `관련` 필드 (다른 todo_idx 참조)
   - `issue 건수`: `todo_issues/{todo_idx}_*.md` 파일 수
4. `root rule200` 호출 시:
   - 모든 하위 프로젝트를 CLAUDE.md 디스패치 테이블 기준으로 순회
   - 프로젝트별 그룹으로 출력
   - 크로스 프로젝트 연동 관계도 함께 표시
5. 이 규칙은 **읽기 전용** — 파일 수정 없음. 현황 파악 목적만.

**`--save` 옵션:**

- `{prefix} rule200 --save` 사용 시 화면 출력과 동시에 root todo md 문서를 생성한다.
- 저장 경로: `work-items_cl/todo/root_{NNNNN}_status_dashboard.md`
- idx는 기존 root todo(`work-items_cl/todo/root_*` + `work-items_cl/done/**/root_*`) 최대값 + 1로 자동 할당한다.
- 파일 내용:
  1. **전체 현황 요약** — 프로젝트별 todo/done/issue 건수 테이블
  2. **프로젝트별 상세** — 진행 중 + 최근 완료 테이블
  3. **완료 판정 로드맵** — 각 활성 todo에 대해:
     - C-1~C-4 판정 테이블 (Rule 201 기준 동일)
     - 잔여 `[ ]` 작업 항목 목록
     - Done 조건 요약 (1~2문장)
- 상태: `스냅샷` (작업 항목이 아닌 시점 기록)
- 매 실행 시 새 idx로 신규 파일 생성 (이력 보존)

#### Rule 201: Batch Done Sweep (Rule 200 → 판정 → Rule 105)

- 사용자가 `{prefix} rule201`을 호출하면, Rule 200으로 현황을 스캔한 뒤 done 대상을 식별하고 Rule 105를 일괄 실행한다.
- 호출 형식:
  - `{prefix} rule201` — 해당 프로젝트의 done 대상 스캔 + 처리
  - `root rule201` — 모노레포 전체 스캔 + 처리
  - `{prefix} {sub_prefix} rule201` — 하위 프로젝트 (예: `anal av rule201`)
  - `{prefix} rule201 --dry-run` — Phase 2 판정까지만 수행, Rule 105 실행 안 함

**Phase 1: 스캔 (Rule 200)**

1. Rule 200을 내부적으로 실행하여 전체 todo 목록을 수집한다.

**Phase 2: 완료 판정**

2. 각 todo 파일에서 아래 4가지 기준을 점검한다:

| # | 판정 기준 | 확인 방법 |
|---|---|---|
| C-1 | 작업 항목 완료 | `- [ ]` 가 0개이거나, 남은 것이 모두 명시적 보류(`보류`, `향후`, `Phase`) |
| C-2 | 완료 판정 기준 충족 | `완료 판정 기준` 섹션의 `- [ ]`가 0개이거나 명시적 보류 |
| C-3 | 의사결정 완결 | `의사결정 항목` 테이블에 `미결` 상태가 없음 |
| C-4 | 블로커 없음 | `블로커`, `선행 작업` 중 미완료 의존이 없음 |

3. 판정 결과를 3단계로 분류하여 출력한다:

   **Done 대상 (C-1~C-4 모두 충족):**
   ```
   | todo_idx | 제목 | C-1 | C-2 | C-3 | C-4 |
   |----------|------|-----|-----|-----|-----|
   | cron_00006 | PG 쿼리 유틸 | O | O | O | O |
   ```

   **거의 완료 (1~2개 미충족):**
   ```
   | todo_idx | 제목 | 미충족 | 사유 |
   |----------|------|--------|------|
   | api_00001 | Schedule API | C-2 | 실연동 검증 미수행 |
   ```

   **진행 중 (done 대상 아님):**
   ```
   | todo_idx | 제목 | 상태 |
   |----------|------|------|
   | api_00006 | Stocklist Init | kickoff |
   ```

**Phase 3: 사용자 확인 + Rule 105 실행**

4. Done 대상 목록을 사용자에게 제시하고 **승인을 요청**한다.
   - 사용자가 개별 선택 또는 전체 승인 가능
   - 거의 완료 항목도 사용자가 명시적으로 선택 가능 (강제 done)
5. 승인된 항목에 대해 **순차적으로** Rule 105를 실행한다.
   - 각 Rule 105 실행 후 결과를 즉시 보고
   - 실패 시 해당 항목 skip하고 다음 진행
6. 전체 처리 완료 후 최종 요약을 출력한다:
   ```
   Rule 201 처리 결과:
   | todo_idx | 결과 |
   |----------|------|
   | cron_00006 | done -> done/y2026/m03/ |
   | api_00001 | skip (사용자 미선택) |
   ```

**안전 장치:**
- Done 대상이 0건이면 "done 대상 없음" 메시지 출력 후 종료
- Rule 105 실행 전 **반드시 사용자 확인** 필요 (자동 실행 금지)
- `--dry-run` 옵션 사용 시 Phase 2 판정까지만 수행

---

## 내부 운영 정책 (Rule 9000~)

### Rule 9000: R&R (역할 분담) 정책

#### 역할 정의

| 역할 | 담당 | 설명 |
|------|------|------|
| **평가자(Evaluator)** | 사용자 | 최종 승인/검증. 아키텍처 결정, Done 승인 |
| **커맨더(Commander)** | 사용자(요청) → Claude(정) → Codex(부) | 작업 설계, Todo 문서 작성, 전략 수립, 범위 분석 |
| **엑터(Actor)** | Codex(정) → Claude(부) | 코드 구현, 테스트 작성, 리팩토링 |

#### 역할별 책임 범위

**커맨더 책임 (Claude 정):**
- Todo/Issue 문서 작성 및 갱신
- Kickoff 분석 (Rule 101)
- 코드 리뷰 및 검증
- CPCR 작성
- Done 판정 (Rule 201) 실행
- 현황 대시보드 (Rule 200) 운영
- 크로스 프로젝트 영향 분석

**엑터 책임 (Codex 정):**
- 코드 구현 (신규 기능, 버그 수정)
- 테스트 작성 및 실행
- 리팩토링
- 구현 결과물에 대한 1차 검증

**평가자 책임 (사용자):**
- 작업 요청 및 우선순위 결정
- 아키텍처/설계 의사결정 승인
- Done 최종 승인 (Rule 105/201)
- 크로스 프로젝트 변경 승인

#### 자동화 정책
- 커맨더(Claude)는 자동화 수준이 **높음**인 작업은 사용자 확인 없이 수행 가능
- 자동화 수준이 **낮음**인 작업(아키텍처 결정 등)은 반드시 평가자 승인 필요
- 엑터(Codex)의 구현 결과는 커맨더(Claude)가 1차 검증 후 평가자에게 보고
- **노트북 검증(Rule 103)은 Claude가 자율 수행** — 생성, 실행 확인, 무결성 검사까지 자동

#### 소통 최소화 원칙
- 사용자에게 보고하는 내용은 **의사결정이 필요한 항목**과 **최종 결과**만
- Todo/Issue 문서는 내부 추적용 — 사용자 소통용 요약은 별도로 최소화
- 중간 과정, 상세 분석, 검증 로그는 문서에 기록하되 사용자에게 직접 전달하지 않음

#### 정렬 루프
작업은 아래 순환 구조를 따른다:
1. **감지**: 사용자가 방향/요구사항 제시
2. **번역**: Claude(커맨더)가 Todo 문서로 구조화
3. **실행**: Codex(엑터)가 구현
4. **해석**: Claude(커맨더)가 결과 검증 및 피드백
5. **재번역**: Done 이력을 바탕으로 다음 작업에 패턴 반영

### Rule 9001: 핸드오프 공간 (work-items_cl_co/) 운영 정책

#### 용도
- Claude(커맨더)↔Codex(엑터) 간 실행 스펙과 결과를 교환하는 공유 공간.
- 기존 `work-items_cl/`(Claude 단독), `work-items_co/`(Codex 단독)와 분리 운영.

#### 폴더 구조
```
work-items_cl_co/
├── handoff/                    # Claude→Codex 실행 스펙
├── report/                     # Codex→Claude 실행 결과
└── archive/y{YYYY}/m{MM}/     # 완료 건 보관
```

#### 파일 네이밍
- 핸드오프: `handoff/{todo_idx}_spec.md`
- 리포트: `report/{todo_idx}_result.md`
- Rule 020 네이밍 규칙 준수

#### 운영 흐름
1. 커맨더(Claude)가 `handoff/{todo_idx}_spec.md`에 실행 스펙 작성
2. 엑터(Codex)가 구현 후 `report/{todo_idx}_result.md`에 결과 작성
3. 커맨더가 report 검증 후 사용자에게 최종 결과만 보고
4. Done 처리 시 handoff + report 쌍을 `archive/y{YYYY}/m{MM}/`로 이동

#### 적용 범위
- 최상위 `work-items_cl_co/`만 운영 (하위 프로젝트별 생성은 향후 필요 시 허용)

---

## 참조
- 크로스 프로젝트 Impact Matrix: `rule/ref/impact_matrix.md`
- 하위 프로젝트 위임: `CLAUDE.md` 디스패치 테이블
- 원본 (단일 프로젝트): `rule/achive/20260228_workflow_rules.md`
- 참조 구현 (project_arch): `project_arch/rule/workflow_rules.md`
