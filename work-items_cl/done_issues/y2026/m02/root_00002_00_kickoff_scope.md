# root_00002_00: Kickoff Scope

대상 todo: `root_00002_sub_project_rule_delegation.md`

## 목적
- root_00002 작업 범위를 확정하고, 즉시 수행 가능한 항목과 의사결정 필요 항목을 분리한다.

## 현재 결정사항

### 확정 완료
1. **Prefix 디스패치 테이블** — 8개 prefix (root, api, web, cron, anal, gas, data, arch) 확정
2. **Rule 101~105** — `{prefix}_{NNNNN}` 네임스페이스, work-items_cl 경로 재매핑
3. **Rule 103** — 프로젝트별 notebooks/, .env 자동 로딩 초기화 셀
4. **Rule 106~108** — `common_data/pipeline/`
5. **Rule 109~112** — 크로스 프로젝트 handoff, root rule 제어

### 즉시 수행 가능한 작업
1. **섹션 1** — CLAUDE.md 배치:
   - 구조는 이미 설계됨 (8개 하위 프로젝트 각각 CLAUDE.md)
   - `project_arch/rule/workflow_rules.md`는 이미 실물 생성 완료
   - → 각 하위 프로젝트 CLAUDE.md 초안 작성 가능
2. **섹션 2** — Rule 내용 설계:
   - 7개 하위 프로젝트 × CLAUDE.md 초안 내용
   - `project_arch`는 Rule 101~105 이미 이식 완료 → 참조 템플릿으로 활용
   - → 나머지 프로젝트도 동일 패턴으로 이식 가능
3. **최상위 CLAUDE.md 갱신**:
   - 현재: 공용 메모리 문서만 있음
   - → 위임 선언 + 디스패치 테이블 추가 가능

### 의사결정 필요 항목
1. ~~**섹션 1** — CLAUDE.md 계층 관계~~ → ✅ **독립 적용 + Base Rules 강제 참조** 확정
   - 하위 프로젝트 단독 VSCode 실행 시 `{sub_project}/CLAUDE.md`만 적용
   - 모든 하위 CLAUDE.md 상단에 Base Rules (`rule/workflow_rules.md`) 링크 필수
   - 충돌 시: Base Rules > Subproject Rules
   - 예외: 실험/샌드박스만 Base Rules 일부 제외 허용 (제외 목록 명시)
2. ~~**섹션 4** — 크로스 프로젝트 의존성 규칙~~ → ✅ **Impact Matrix + CPCR + Required Checks 3요소** 확정
   - Impact Matrix: `rule/ref/impact_matrix.md` (정적 테이블)
   - CPCR 연동: affected_projects >= 2 또는 interface 변경 시 강제
   - Required Checks: common_data/web/gas 변경별 최소 체크리스트

## 남은 작업
- [x] ~~CLAUDE.md 계층 관계(상속/독립) 사용자 결정~~ → 독립 + Base Rules 강제 참조 확정
- [x] ~~크로스 프로젝트 의존성 규칙 세부 설계~~ → Impact Matrix + CPCR + Required Checks 확정
- [x] ~~8개 하위 프로젝트 CLAUDE.md 초안 작성~~ → `root rule102` 완료
- [x] ~~최상위 CLAUDE.md 위임 선언 추가~~ → `root rule102` 완료

## 다음 액션
1. **root_00002 완료 기준 충족** — 나머지 프로젝트 rule 이식은 별도 todo
2. `root rule105 root_00002` → 완료 처리 가능
