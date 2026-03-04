# CycleStack — CLAUDE.md (최상위)

이 문서는 모노레포 전체의 협업 메모리이자 하위 프로젝트 위임 선언을 포함한다.

## Base Rules
- 공통 규칙: `rule/workflow_rules.md` (모노레포 전체 적용)
- 크로스 프로젝트 영향: `rule/ref/impact_matrix.md`
- 충돌 우선순위: **Base Rules(최상위) > Subproject Rules(하위)**

## 하위 프로젝트 위임 선언

각 하위 프로젝트는 독립 CLAUDE.md를 가지며, Base Rules를 강제 참조한다.

| prefix | 프로젝트 | CLAUDE.md | 역할 |
|---|---|---|---|
| `root` | hynix_fds_review (본 문서) | `CLAUDE.md` | 리뷰 프로젝트 공통 + 크로스 프로젝트 |
| `rule` | project_rule | `project_rule/CLAUDE.md` | 규칙 관리/정책 문서 |
| `fds` | project_fds | `project_fds/CLAUDE.md` | FDS 리뷰/분석 |

- Rule 호출: `{prefix} rule{NNN}` (예: `api rule101`, `root rule000`)
- 하위 프로젝트 Rule 호출: `{prefix} {sub_prefix} rule{NNN}` (예: `anal av rule101`)
- prefix 생략 시: 현재 VSCode에서 열린 프로젝트 기준 자동 판별

## 운영 원칙
1. 이 문서는 `rule/workflow_rules.md`의 대체가 아니다.
   - 규칙은 규칙대로 유지하고, 이 문서는 협업 메모리로만 사용한다.
2. 작업 시작 전 확인
   - Codex는 작업 시작 전에 `CLAUDE.md`를 먼저 확인한다.
   - 문서에 있는 합의사항이 있으면 우선 반영한다.
3. 작업 중 업데이트
   - 사용자와 새로운 합의가 생기면 즉시 본 문서에 추가한다.
   - 애매한 표현 대신 실행 가능한 문장으로 기록한다.

## 작업 공간 분리
| 디렉터리 | 담당 | 용도 |
|---|---|---|
| `work-items_co/` | Codex 중심 | 기존 rule(101~105 등) 기반 실행 |
| `work-items_cl/` | Claude 중심 | 분석/초안/별도 검토 문서 |
| `work-items_cl_co/` | Claude↔Codex 공유 | 핸드오프 스펙/리포트 교환 (최상위만, Rule 9001) |

## 현재 합의사항
1. `CLAUDE.md`는 소통 충돌 방지용 공용 메모리다.
2. 협업 관련 결정은 본 문서에 누적 관리한다.
3. rule 문서와 혼합하지 않고 역할을 분리한다.
4. 하위 프로젝트 CLAUDE.md는 독립 적용 + Base Rules 강제 참조.
5. 크로스 프로젝트 변경 시 Impact Matrix + CPCR + Required Checks 3요소 운영.
6. R&R 역할 분담:
   - 평가자: 사용자 (최종 승인/아키텍처 결정)
   - 커맨더: Claude(정), Codex(부) — Todo 설계, 검증, 규칙 운영
   - 엑터: Codex(정), Claude(부) — 코드 구현, 테스트
   - 노트북 검증은 Claude 자율 수행
   - 사용자 소통은 의사결정 항목 + 최종 결과만 최소화
   - 상세: `rule/workflow_rules.md` Rule 9000 참조

## 변경 이력
- 2026-02-25: 문서 깨짐 복구 및 공용 메모리 규칙 재정의.
- 2026-02-28: 위임 선언 + 디스패치 테이블 + Base Rules 정책 추가 (root_00002 rule102).
- 2026-03-02: anal 하위 프로젝트 위임 체계 추가. 하위 프로젝트 Rule 호출 형식 등록.
- 2026-03-04: project_rule 하위 프로젝트 추가. project_arch와 동일 규칙 적용.
- 2026-03-04: R&R 역할 분담 합의사항 추가 (Rule 9000). 노트북 검증 Claude 위임, 소통 최소화 원칙.
- 2026-03-04: hynix_fds_review 프로젝트 초기화. 하위 프로젝트를 rule, fds만 등록.
