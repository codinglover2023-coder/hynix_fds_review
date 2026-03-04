# root_00002_02: Validation and Output

대상 todo: `root_00002_sub_project_rule_delegation.md`

## 목적
- root_00002 완료 시 검증할 항목과 최종 산출물을 정의한다.

## 현재 결정사항

### 최종 산출물
1. 8개 하위 프로젝트 CLAUDE.md (common_data, render_api, render_web, render_cron, render_anal, project_gas, project_arch)
2. 최상위 CLAUDE.md — 위임 선언 + 디스패치 테이블 포함
3. 각 하위 프로젝트 `rule/workflow_rules.md` — Rule 101~105 이식본
4. root_00002 todo 문서 — 전체 체크박스 완료 상태

### 검증 체크리스트
- [ ] 8개 하위 프로젝트 모두 CLAUDE.md가 존재하는가
- [ ] 각 CLAUDE.md에 prefix, 작업 공간 경로, rule 참조가 포함되어 있는가
- [ ] 최상위 CLAUDE.md에 디스패치 테이블과 위임 선언이 있는가
- [ ] `project_arch/rule/workflow_rules.md` 패턴과 나머지 프로젝트 rule이 일관적인가
- [ ] 크로스 프로젝트 의존성 매트릭스가 문서화되어 있는가
- [ ] `{prefix} rule101 {todo_idx}` 호출이 올바른 경로로 디스패치되는가

### 검증 방법
1. CLAUDE.md 존재 확인: `find . -name "CLAUDE.md" -not -path "./.git/*"`
2. rule 파일 존재 확인: `find . -path "*/rule/workflow_rules.md"`
3. 디스패치 테스트: `arch rule101 arch_00001` 실행 → project_arch/work-items_cl/ 경로 확인

## 남은 작업
- [ ] 하위 프로젝트 CLAUDE.md 일괄 생성
- [ ] 하위 프로젝트 rule 이식
- [ ] 최상위 CLAUDE.md 갱신
- [ ] 검증 실행

## 다음 액션
1. `root rule102 root_00002` → CLAUDE.md 및 rule 일괄 생성
2. 검증 체크리스트 순회
3. `root rule105 root_00002` → 완료 처리
