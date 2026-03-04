# root_00003_00: Kickoff Scope

대상 todo: `root_00003_entrypoint_and_deployment_rules.md`

## 목적
- root_00003 작업 범위를 확정하고, 즉시 수행 가능한 항목과 의사결정 필요 항목을 분리한다.

## 현재 결정사항

### 전체 확정 완료
1. **섹션 1** (서비스 매핑): Render 2개 서비스 고정, entrypoint 확정 — ✅
2. **섹션 2** (마운트 규칙): 경로 규약 + 충돌 방지 게이트 + 재시작 정책 + WSGIMiddleware 제약 — ✅
3. **섹션 3** (환경 변수): .env.template SSOT + 3종 동기화 — ✅
4. **섹션 4** (의존성): 프로젝트별 requirements.txt — ✅
5. **섹션 5** (render.yaml): 3종 동기화 + 스모크 게이트 + Python 버전 절차 — ✅
6. **섹션 6** (로컬 개발): 루트 실행 표준 + PYTHONPATH 수동 금지 — ✅

### 의사결정 필요 항목
1. ~~**섹션 3 잔여** — Render↔.env 동기화~~ → ✅ **.env.template SSOT + 3종 동기화** 확정

## 남은 작업
- [x] ~~섹션 1~6 전체~~ → 사용자 결정 완료, todo 반영 완료
- [x] 검증 체크리스트 실행 (root_00003_02 참조) — 정적 분석 6항목 완료 (5 PASS + 1 CONDITIONAL PASS)

## 다음 액션
1. (선택) 로컬 스모크 테스트로 런타임 검증
2. `root rule105 root_00003` → 완료 처리
