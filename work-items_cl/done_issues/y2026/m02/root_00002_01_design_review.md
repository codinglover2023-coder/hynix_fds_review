# root_00002_01: Design Review

대상 todo: `root_00002_sub_project_rule_delegation.md`

## 목적
- 하위 프로젝트별 CLAUDE.md 및 rule 위임 구조의 설계를 검토한다.

## 현재 결정사항

### 하위 프로젝트별 CLAUDE.md 내용 설계

| 프로젝트 | CLAUDE.md 핵심 내용 | Rule 101~105 이식 |
|---|---|---|
| common_data | Impact Matrix 참조, config.py→.env.template 동기화, pipeline 호환 | ✅ 완료 |
| render_api | merge 게이트 (Flask 스모크/라우팅/OpenAPI), WSGIMiddleware 제약 | ✅ 완료 |
| render_web | api 마운트 충돌 확인, WebSocket/streaming 불가, 정적 파일 | ✅ 완료 |
| render_cron | 스케줄 정의 명시, render.yaml cron 일치, stdout 로그 | ✅ 완료 |
| render_anal | 노트북 네이밍, 초기화 셀, 출력 clear, pipeline import | ✅ 완료 |
| project_gas | 코드/계약 경로, payload→api 확인, contract→CPCR | ✅ 완료 |
| project_arch | 구조설계 문서, ADR, Rule 101~105 | ✅ 완료 |

### CLAUDE.md 계층 정책 ✅ 확정
- **기본**: 독립 적용 — 하위 프로젝트 단독 VSCode 시 `{sub_project}/CLAUDE.md`만 적용
- **Base Rules 강제**: 모든 하위 CLAUDE.md 상단에 Base Rules 참조 필수
- **충돌 우선순위**: Base Rules(최상위) > Subproject Rules(하위)
- **예외**: 실험/샌드박스 프로젝트만 Base Rules 일부 제외 허용 (제외 목록 명시)

### CLAUDE.md 표준 템플릿 (확정된 계층 정책 반영)
```markdown
# {project_name} — CLAUDE.md

## Base Rules
- 공통 규칙: `../rule/workflow_rules.md` 를 따른다.
- 충돌 시: Base Rules > 본 문서의 규칙
- 제외 항목: 없음

## 프로젝트 개요
- 역할: ...
- prefix: `{prefix}`

## Rule 참조
- 프로젝트 규칙: `{sub_project}/rule/workflow_rules.md`

## 작업 공간
- Claude: `work-items_cl/`
- Codex: `work-items_co/`

## 현재 합의사항
(프로젝트별 결정 누적)
```

### 크로스 프로젝트 의존성 운영 ✅ 확정
운영 방식: **Impact Matrix + CPCR + Required Checks** 3요소

#### Impact Matrix (정적 테이블) — `rule/ref/impact_matrix.md`

| 변경 대상 (change_area) | 영향받는 프로젝트 (affected_projects) | 필수 점검 (required_checks) |
|---|---|---|
| `common_data/` | render_api, render_web, render_cron, render_anal, project_gas | import 영향 프로젝트 목록 명시 |
| `common_data/pipeline/` | render_anal, render_api | pipeline 함수 시그니처 호환성 |
| `render_web/` (라우팅/템플릿) | render_api | `/web/*` 스모크 2~3개 + api 마운트 경로 확인 |
| `project_gas/` (payload) | render_api | payload 예시(JSON) + api 수신 파싱 경로 확인 |

#### CPCR 연동
- `affected_projects >= 2` 또는 `interface 변경` → CPCR 6필드 포맷 강제
- root_00001 섹션 4에서 확정한 포맷 그대로 사용

#### Required Checks (최소 체크리스트)
- `common_data` 변경: import 영향 프로젝트 목록을 작업 문서에 명시
- `render_web` 변경: `/web/*` 요청 스모크 2~3개 + api 마운트 경로 확인
- `project_gas` 변경: payload 예시(JSON) + api 수신 파싱 경로 확인 (테스트 또는 샘플 호출)

## 남은 작업
- [x] ~~CLAUDE.md 표준 템플릿 확정~~ → 계층 정책 반영 템플릿 확정
- [x] ~~크로스 프로젝트 의존성 점검 규칙 명문화~~ → Impact Matrix + CPCR + Required Checks 확정
- [x] ~~7개 프로젝트 CLAUDE.md 초안 작성~~ → `root rule102` 완료 (8개 모두)
- [ ] 각 프로젝트 rule/workflow_rules.md 이식 (Rule 101~105) — 별도 todo

## 다음 액션
1. **root_00002 주요 산출물 완성** — CLAUDE.md 8개 + impact_matrix.md
2. Rule 이식은 별도 todo로 추적
