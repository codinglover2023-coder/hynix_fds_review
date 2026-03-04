# root_00001_01: Design Review

대상 todo: `root_00001_rule_system_redesign_for_monorepo.md`

## 목적
- 기존 Rule 000~096을 모노레포 구조에 맞게 변환하는 설계를 검토한다.

## 현재 결정사항

### Rule 변환 매핑 (기존 → 모노레포)

| 기존 Rule | 변환 방향 | 상태 |
|---|---|---|
| Rule 000 재로딩 | `rule/` + `{sub_project}/rule/*.md` 순회 + 디스패치 테이블 | ✅ 확정 |
| Rule 001 변경 정책 | 변경 불필요 | ✅ 확정 |
| Rule 010 작업 흐름 | work-items 옵션 C + 4폴더 + 연/월 보관 | ✅ 확정 |
| Rule 020 파일 네이밍 | `{prefix}_{NNNNN}_<topic>.md` | ✅ 확정 |
| Rule 030 커뮤니케이션 | 하위 프로젝트 소속 명시 + CPCR 6필드 포맷 | ✅ 확정 |
| Rule 040 작업-이슈 연결 | `todo_issues/` 로 경로 변경 | ✅ 확정 |
| Rule 050 문서 동기화 | `{sub_project}/docs/` 분산 + README 2-레벨 정책 | ✅ 확정 |
| Rule 060 런타임 게이트 | `{sub_project}/tests/` 분산 + 최상위 `tests/` contract만 | ✅ 확정 |
| Rule 070 API 변경 게이트 | Flask mount 스모크 + 라우팅 호환 + OpenAPI diff (1개↑ 필수) | ✅ 확정 |
| Rule 080 GAS 브리지 | `project_gas/src/` + `docs/contracts/` (2단계 처리) | ✅ 1단계 확정 |
| Rule 090 Config/Schema | `common_data/` 중심 | ✅ 확정 |
| Rule 095-096 인코딩 | 최상위 유지 + 하위 오버라이드 허용 | ✅ 확정 |

### 설계 원칙
1. 최상위 rule은 **공통 규칙만** 정의 (Rule 000~096)
2. 자동화 규칙 (Rule 101~112)은 **하위 프로젝트별 rule 파일**에서 정의
3. 크로스 프로젝트 자동화 (handoff 등)만 **root rule**에서 정의

## 남은 작업
- [x] ~~확정 가능 항목 (000, 001, 040, 090, 095-096) 일괄 확정~~ → `root rule102` 완료
- [x] ~~미결정 항목 (030, 060, 070) 사용자 결정~~ → 전부 확정 완료
- [x] `rule/workflow_rules.md` 최종 작성 — ✅ 완료

## 다음 액션
1. `root rule105 root_00001` → 완료 처리
2. Rule 080 2단계는 별도 todo로 추적
