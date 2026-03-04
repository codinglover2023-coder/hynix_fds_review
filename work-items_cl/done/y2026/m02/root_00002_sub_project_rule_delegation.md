# root_00002: 하위 프로젝트별 Rule 위임 설계

상태: **완료** (2026-02-28)
생성일: 2026-02-28
선행: `root_00001_rule_system_redesign_for_monorepo.md`

## 목적
- 각 하위 프로젝트가 독립적으로 VSCode를 열어 개발할 때, 해당 프로젝트의 rule만 적용되도록 위임 구조 설계
- 최상위 rule과 하위 rule 간 충돌 없는 실행 보장

## 확정 사항

### Rule 호출 Prefix 디스패치 ✅ 결정 완료

호출 형식: `{prefix} rule{NNN}` (예: `api rule101`, `root rule000`)

| prefix | 대상 프로젝트 | 디렉터리 | work-items 경로 |
|---|---|---|---|
| `root` | 최상위 (크로스 프로젝트) | `./` | `work-items_cl/` |
| `api` | render_api | `render_api/` | `render_api/work-items_cl/` |
| `web` | render_web | `render_web/` | `render_web/work-items_cl/` |
| `cron` | render_cron | `render_cron/` | `render_cron/work-items_cl/` |
| `anal` | render_anal | `render_anal/` | `render_anal/work-items_cl/` |
| `gas` | project_gas | `project_gas/` | `project_gas/work-items_cl/` |
| `data` | common_data | `common_data/` | `common_data/work-items_cl/` |
| `arch` | project_arch | `project_arch/` | `project_arch/work-items_cl/` |

- prefix 생략 시: 현재 VSCode에서 열린 프로젝트 기준으로 자동 판별
- `_co` 경로도 동일 prefix로 디스패치 (Claude → `_cl`, Codex → `_co`)

---

## 검토 항목

### 1. 하위 프로젝트별 Rule 파일 구조 ✅ 결정 완료
- [x] 각 하위 프로젝트에 `CLAUDE.md` 배치 — **독립 적용 + Base Rules 강제 참조** 확정
  - 하위 프로젝트를 단독 VSCode로 열면 `{sub_project}/CLAUDE.md`**만** 적용
  - 모든 `{sub_project}/CLAUDE.md`는 상단에 **Base Rules 링크(또는 include 섹션)** 필수 포함
  - Base Rules = `CycleStack/rule/workflow_rules.md`
- [x] 충돌 정책: **Base Rules(최상위) > Subproject Rules(하위)**
- [x] 예외: 실험/샌드박스 성격 프로젝트만 "Base Rules 일부 제외" 허용
  - 제외 시 하위 CLAUDE.md에 제외 목록 명시 필수
- [x] 하위 프로젝트별 rule 적용 범위 — 디스패치 테이블 기준 매핑 확정

#### 확정된 CLAUDE.md 계층 구조
```
CycleStack/
├── CLAUDE.md                    # 최상위: 공통 규칙 + 하위 위임 선언
├── rule/workflow_rules.md       # Base Rules (모노레포 공통 규칙)
├── common_data/
│   └── CLAUDE.md                # 공유 패키지 규칙 (Base Rules 참조 필수)
├── render_api/
│   └── CLAUDE.md                # FastAPI 전용 규칙 (Base Rules 참조 필수)
├── render_web/
│   └── CLAUDE.md                # Flask 전용 규칙 (Base Rules 참조 필수)
├── render_cron/
│   └── CLAUDE.md                # 스케줄러 전용 규칙 (Base Rules 참조 필수)
├── render_anal/
│   └── CLAUDE.md                # Jupyter 전용 규칙 (Base Rules 참조 필수)
├── project_gas/
│   └── CLAUDE.md                # GAS 전용 규칙 (Base Rules 참조 필수)
└── project_arch/
    └── CLAUDE.md                # 구조설계 전용 규칙 (Base Rules 참조 필수)
```

#### 하위 CLAUDE.md 상단 필수 포맷
```markdown
# {sub_project} — CLAUDE.md

## Base Rules
- 공통 규칙: `../rule/workflow_rules.md` 를 따른다.
- 충돌 시: Base Rules > 본 문서의 규칙
- [제외 항목: 없음 | 또는 제외 목록 명시]
```

### 2. 하위 프로젝트별 Rule 내용 설계 ✅ CLAUDE.md 초안 작성 완료
- [x] **common_data**: Impact Matrix 참조, config.py 변경 시 .env.template 동기화, pipeline 호환성
- [x] **render_api**: merge 게이트 (Flask 스모크/라우팅 호환/OpenAPI diff), WSGIMiddleware 제약 인지
- [x] **render_web**: api 마운트 경로 충돌 확인, WebSocket/streaming 불가, 정적 파일 관리
- [x] **render_cron**: 스케줄 정의 명시, render.yaml cron 표현식 일치 확인, stdout 로그
- [x] **render_anal**: 노트북 네이밍, 초기화 셀 필수, 출력 clear 권장, pipeline import 영향
- [x] **project_gas**: 코드/계약 경로, payload 변경 시 api 확인, contract 변경 시 CPCR
- [x] **project_arch**: ADR 관리, Rule 101~105 참조 — Base Rules 포맷으로 갱신 완료

### 3. Rule 101~112 (자동화 규칙) 모노레포 적용 가능성
- [x] Rule 101~105 (Todo Kickoff/Execution/Validation) — **부분 확정**
  - `work-items_cl/` 기준으로 경로 재매핑
  - `todo_idx` 네임스페이스: **prefix + 5자리 번호** 확정
    - 형식: `{prefix}_{NNNNN}` (예: `api_00001`, `web_00001`)
    - prefix는 디스패치 테이블과 동일: `root`, `api`, `web`, `cron`, `anal`, `gas`, `data`
    - 파일명 예시: `api_00001_some_task.md`
- [x] Rule 103 (Jupyter 검증 노트북) — **확정**
  - **프로젝트별 `{sub_project}/notebooks/` 유지**
  - `find_project_root()` 판별 조건 확정:
    - `work-items_cl` 또는 `work-items_co` 폴더 존재 여부로 판별
  - **노트북 초기화 셀 필수 포함** (`.env` 자동 로딩):
    - 모든 rule 103 생성 노트북의 첫 번째 코드 셀에 아래 표준 초기화 코드를 삽입
    - `.env` 변경 시 셀만 재실행하면 되므로 Jupyter 재시작 불필요
  - 표준 초기화 코드:
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
- [x] Rule 106~108 (Pipeline 관련) — **확정**
  - 기존 `pipeline/` → **`common_data/pipeline/`** 에 배치
  - 모든 하위 프로젝트가 `common_data.pipeline`을 import해서 사용
- [x] Rule 109~112 (Handoff/Archive) — **확정**
  - 하위 프로젝트 간 handoff **가능**
  - 각 프로젝트별 handoff 경로: `{sub_project}/handoff/`
  - **root rule이 크로스 프로젝트 handoff를 제어**
    - 예시 흐름: `anal/handoff/` → (root rule 이관) → `api/handoff/`
    - root rule 호출 형식: `root rule109 {source_prefix} {target_prefix} {endpoint_idx}`
    - 예: `root rule109 anal api 00001`
  - 이관 시 root rule이 수행하는 사항:
    1. source handoff 패키지 검증 (manifest, summary 존재 확인)
    2. target 프로젝트 handoff 경로로 복사
    3. target 프로젝트 work-items에 이관 기록 생성

### 4. 크로스 프로젝트 의존성 규칙 ✅ 결정 완료
운영 방식: **Impact Matrix + CPCR + 최소 검증 체크리스트** 3요소

- [x] **Impact Matrix (정적 테이블)** 확정
  - 위치: `rule/ref/impact_matrix.md`
  - 형식: `change_area → affected_projects → required_checks`
  - 최소 포함 항목:
    - `common_data/` 변경 → {api, web, cron, anal, gas} 중 해당 모듈 사용자
    - `render_web/` 라우팅/템플릿 변경 → api 마운트/프록시 영향 체크
    - `project_gas/` payload 변경 → api endpoint 계약 체크
- [x] **CPCR 연동** 확정
  - root_00001 섹션 4에서 확정한 CPCR 6필드 포맷 그대로 사용
  - 트리거: Impact Matrix에서 `affected_projects >= 2` 또는 `interface 변경` 시 CPCR 강제
- [x] **Required Checks (최소 체크리스트)** 확정
  - `common_data` 변경: import 영향 프로젝트 목록을 작업 문서에 명시
  - `render_web` 변경: `/web/*` 요청 스모크 2~3개 + api 마운트 경로 확인
  - `project_gas` 변경: payload 예시(JSON) + api 수신 파싱 경로 확인 (테스트 또는 샘플 호출)

## 완료 기준
- [x] 각 하위 프로젝트 CLAUDE.md 초안 작성 — 8개 모두 완료 (Base Rules 포맷)
- [x] 최상위 CLAUDE.md에 위임 선언 추가 — 디스패치 테이블 + Base Rules 정책
- [x] Rule 101~112 모노레포 적용 여부 확정 — 전부 확정
- [x] `rule/ref/impact_matrix.md` 실물 생성 — 완료

## 산출물
- `CLAUDE.md` — 최상위 (위임 선언 + 디스패치 테이블)
- `{sub_project}/CLAUDE.md` × 8개 — 프로젝트별 규칙 (Base Rules 참조)
- `rule/ref/impact_matrix.md` — 크로스 프로젝트 Impact Matrix

## Resolved Issues
- `root_00002_00_kickoff_scope.md` — CLAUDE.md 계층 관계 + 크로스 프로젝트 의존성 의사결정 완료
- `root_00002_01_design_review.md` — 7개 프로젝트 CLAUDE.md 내용 설계 + Impact Matrix + CPCR + Required Checks 확정
- `root_00002_02_validation_and_output.md` — 산출물 정의, 검증 체크리스트 작성

## 후속 작업 (별도 todo)
- 나머지 6개 하위 프로젝트 `rule/workflow_rules.md` 이식 (Rule 101~105)
