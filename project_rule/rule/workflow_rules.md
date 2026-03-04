# project_rule 워크플로우 규칙

최종 수정일: 2026-03-04
적용 범위: `project_rule` (규칙 관리 프로젝트)
prefix: `rule`

---

## Rule 101: Todo Kickoff Bundle

- 사용자가 `rule rule101 {todo_idx}` 를 호출하면, `{todo_idx}` 대상 todo에 대해 아래 작업을 자동 수행한다.
- `todo_idx` 형식: `rule_{NNNNN}` (예: `rule_00001`)

1. `work-items_cl/todo/{todo_idx}_*.md` 기준으로 즉시 수행 가능한 작업 목록을 정리한다.
2. `work-items_cl/todo_issues/` 폴더에 `{todo_idx}_{issue_idx}_*.md` 패턴 문서를 자동 생성/업데이트한다.
- 기본 생성 문서 템플릿:
  - `todo_issues/{todo_idx}_00_kickoff_scope.md`
  - `todo_issues/{todo_idx}_01_design_review.md`
  - `todo_issues/{todo_idx}_02_validation_and_output.md`
- 각 문서 필수 섹션:
  - `목적`
  - `현재 결정사항`
  - `남은 작업`
  - `다음 액션`
- `todo_idx`가 생략되면 현재 활성 todo 파일 인덱스를 우선 사용하고, 없으면 사용자에게 인덱스를 요청한다.

---

## Rule 102: Todo Execution From Issue Docs

- 사용자가 `rule rule102 {todo_idx}` 를 호출하면, `{todo_idx}` 대상 todo를 아래 순서로 처리한다.

1. `work-items_cl/todo/{todo_idx}_*.md`와 `work-items_cl/todo_issues/{todo_idx}_*.md` 문서를 모두 읽고 현재 기준으로 사용한다.
2. `todo_issues/{todo_idx}_*.md`에 정리된 항목 중 즉시 수행 가능한 작업을 실제로 수행한다.
3. 수행 결과를 반영해 `work-items_cl/todo/{todo_idx}_*.md`를 업데이트한다.
- `todo` 문서 업데이트 규칙:
  - 완료된 항목은 완료 상태로 표시한다.
  - 미완료/의사결정 필요 항목은 `work-items_cl/todo/rule_99999_*.md`에 추가하거나 갱신한다.
  - 다음 실행 액션을 1~3개로 명시한다.
- `todo_idx`가 생략되면 현재 활성 todo 파일 인덱스를 우선 사용하고, 없으면 사용자에게 인덱스를 요청한다.

---

## Rule 103: Todo 인덱스 검증용 Jupyter 노트북 생성 규칙

- 사용자가 `rule rule103 {todo_idx}` 를 입력하면 `{todo_idx}` 작업 검증용 Jupyter 노트북을 생성/갱신한다.
- 입력 옵션:
  - 기본: `rule rule103 {todo_idx}`
  - 검증 완료 처리: `rule rule103 {todo_idx} done`

1. 노트북 경로는 `notebooks/{todo_idx}/`로 고정한다.
2. 파일명 규칙은 `{todo_idx}_{valid_idx}_<slug>.ipynb`를 사용한다.
  - 이력 관리 파일명: `{todo_idx}_{valid_idx}_{yyyymmdd}_{run_idx}_<slug>.ipynb`
  - 예시: `rule_00001_00_20260304_01_validation_setup.ipynb`
3. 기본 검증 노트북 세트:
  - `notebooks/{todo_idx}/{todo_idx}_00_validation_setup.ipynb`
  - `notebooks/{todo_idx}/{todo_idx}_01_run_checks.ipynb`
  - `notebooks/{todo_idx}/{todo_idx}_02_debug_notes.ipynb`
4. `valid_idx` 역할:
  - `00`: 실행 환경/입력 확인
  - `01`: 결과 검증
  - `02`: 디버그/이슈 메모
5. 노트북 생성 기본값은 `00_validation_setup` 1개로 시작하고, 필요 시 `01`, `02`를 확장한다.
6. 노트북 필수 내용:
  - 실행 명령/입력값
  - 결과 파일 로딩/검증 코드
  - 실패 케이스 재현 또는 방어 코드
7. `.ipynb`는 `UTF-8 (BOM 없음)`으로 저장한다.
8. 생성 직후 무결성 검사를 수행한다.
  - JSON 파싱 가능 여부
  - 필수 키(`cells`, `metadata`, `nbformat`, `nbformat_minor`) 존재 여부
  - `cells[*].source`가 list 형태인지 확인
9. **노트북 초기화 셀 필수 포함** (첫 번째 코드 셀):
  - 절대경로 하드코딩 금지
  - `.env` 자동 로딩으로 Jupyter 재시작 없이 환경변수 반영
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
10. `rule rule102 {todo_idx}` 수행 후에는 `rule rule103 {todo_idx}`를 권장 실행한다.
11. `done` 입력 처리:
  - `rule rule103 {todo_idx} done`은 검증 완료 상태 업데이트 용도다.
  - `todo -> done` 이동은 `rule rule105` 절차를 따른다.
12. `todo_idx`가 생략되면 현재 활성 todo 인덱스를 우선 사용하고, 불명확하면 사용자에게 확인한다.

---

## Rule 104: Full Rule Audit Report

- 사용자가 `rule rule104`를 호출하면, 현재 `project_rule/rule/`에 정의된 규칙을 전체 점검한다.

1. 점검 대상:
  - 규칙 번호 중복/누락 여부
  - 규칙 간 충돌/모순 여부
  - 호출 형식(`rule rule101 {todo_idx}` 등) 일관성
  - 파일 경로/네이밍 규칙의 실제 사용 가능성
2. 점검 결과 문서를 아래 경로로 생성/갱신한다.
  - `project_rule/rule/104_rule_audit_report.md`
3. 보고서 필수 섹션:
  - `점검 범위`
  - `발견 이슈`
  - `수정 권고안`
  - `최종 판정(OK/Needs Update)`
4. 이슈가 없으면 `발견 이슈: 없음`으로 명시한다.

---

## Rule 105: Validation Confirmation Update Pattern

- 사용자가 검증 완료를 확인하면, 대상 `work-items_cl/todo/{todo_idx}_*.md`를 즉시 업데이트한다.
- 호출 옵션:
  - 기본: `rule rule105 {todo_idx}`
  - 노트북 검증/잔존 점검 무시: `rule rule105 {todo_idx} --skip-notebooks-check`

0. `rule rule105 {todo_idx}`로 호출되면 done 처리 전에 잔존 파일 검토를 먼저 수행한다.
  - 검토 대상:
    - `work-items_cl/todo/{todo_idx}_*.md`
    - `work-items_cl/todo_issues/{todo_idx}_*.md` (working issue)
    - `notebooks/{todo_idx}/` (working notebook)
  - 잔존 파일이 있으면 done 정책에 따라 재처리한다.
1. 검증 완료 증빙을 `진행 결과` 또는 `완료 기준 대비 상태`에 기록한다.
2. 남은 작업을 1~3개로 요약해 채팅에서 즉시 보고한다.
3. 남은 작업이 의사결정/환경 제약이면 `work-items_cl/todo/rule_99999_*.md`에 반영 또는 갱신한다.
4. 완료 기준이 전부 충족되면 done 처리 전에 `Resolved Issues` 섹션을 `work-items_cl/todo/{todo_idx}_*.md`에 갱신한다.
  - 규칙: issue 본문 전체 복사 금지, `요약(1~3줄) + 링크`만 통합
5. issue 상태를 분리 관리한다.
  - `working issue`: `work-items_cl/todo_issues/`에 유지
  - `done issue`: `work-items_cl/done_issues/y{YYYY}/m{MM}/` 하위로 이동 보관
6. notebook 상태도 issue와 동일하게 분리 관리한다.
  - `working notebook`: `notebooks/{todo_idx}/`에 유지
  - `done notebook`: `notebooks/done/y{YYYY}/m{MM}/{todo_idx}/` 하위로 이동 보관
7. `todo` 문서, 해결된 issue, 관련 notebook 정리가 끝나면 사용자 확인 후 이동한다.
  - `work-items_cl/todo/` -> `work-items_cl/done/y{YYYY}/m{MM}/`
- `--skip-notebooks-check`가 명시되면:
  - 0번 단계의 notebook 잔존 점검을 생략한다.
  - 6번 단계의 notebook 이동/정리도 생략한다.
  - 단, `todo`/`issue` 점검 및 `todo -> done` 처리 규칙은 그대로 유지한다.
- `todo_idx`가 명시되지 않으면 현재 활성 todo 인덱스를 우선 사용한다.
