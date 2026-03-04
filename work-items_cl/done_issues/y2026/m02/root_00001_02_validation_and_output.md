# root_00001_02: Validation and Output

대상 todo: `root_00001_rule_system_redesign_for_monorepo.md`

## 목적
- root_00001 완료 시 검증할 항목과 최종 산출물을 정의한다.

## 현재 결정사항

### 최종 산출물
1. `rule/workflow_rules.md` — 모노레포 공통 규칙 (Rule 000~096) 최종본
2. `CLAUDE.md` — 하위 프로젝트 위임 선언 포함 갱신본
3. root_00001 todo 문서 — 전체 체크박스 완료 상태

### 검증 체크리스트
- [ ] `rule/workflow_rules.md`에 Rule 000~096 모두 포함되어 있는가
- [ ] 모든 경로가 실제 모노레포 구조와 일치하는가
  - `work-items_cl/`, `work-items_co/` (4폴더 구조)
  - `{sub_project}/docs/`
  - `{sub_project}/rule/`
  - `project_gas/src/` (기존 `google_apps_script/src/`)
- [ ] `CLAUDE.md`에 공용 메모리 + 위임 선언이 반영되어 있는가
- [ ] root_00001 todo의 모든 검토 항목(섹션 1~8)이 확정/결정 상태인가
- [ ] 기존 `rule/achive/20260228_workflow_rules.md`와 신규 규칙 간 누락 규칙이 없는가

### 검증 방법
1. `rule/workflow_rules.md` 작성 후 `root rule104` 실행 → 규칙 감사 보고서 생성
2. 경로 일치 검증 → 실제 디렉터리 존재 확인 (find/glob)
3. 누락 검증 → 기존 규칙 번호와 신규 규칙 번호 대조

## 남은 작업
- [ ] 미결정 항목 확정 후 `rule/workflow_rules.md` 최종 작성
- [ ] `CLAUDE.md` 갱신
- [ ] `root rule104` 실행하여 감사 통과 확인

## 다음 액션
1. `root rule102 root_00001` → 즉시 수행 가능 항목 처리
2. 미결정 항목 사용자 결정 후 최종 산출물 작성
3. `root rule104` → 규칙 감사
