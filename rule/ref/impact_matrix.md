# Impact Matrix — 크로스 프로젝트 영향 매트릭스

최종 수정일: 2026-03-02
출처: `root_00002` 섹션 4 (크로스 프로젝트 의존성 규칙)

---

## 사용 방법
1. 변경 대상 경로가 아래 테이블에 해당하면, `affected_projects`를 확인한다.
2. `affected_projects >= 2` 또는 `interface 변경`이면 **CPCR 6필드 포맷 필수**.
3. `required_checks`에 명시된 최소 검증을 수행하고, 작업 문서에 기록한다.

---

## Impact Matrix

| change_area | affected_projects | required_checks |
|---|---|---|
| `common_data/` (모델/설정) | render_api, render_web, render_cron, render_anal, project_gas | import 영향 프로젝트 목록을 작업 문서에 명시 |
| `common_data/config.py` (환경변수) | render_api, render_cron | `.env.template` 키 동기화 확인 |
| `common_data/pipeline/` | render_anal, render_api | pipeline 함수 시그니처 호환성 확인 |
| `render_web/` (라우팅/템플릿) | render_api | `/web/*` 요청 스모크 2~3개 + api 마운트 경로 확인 |
| `render_api/app/routes.py` (라우터) | render_web | Flask mount 스모크 + 라우팅 호환 + OpenAPI diff (1개↑) |
| `project_gas/` (payload) | render_api | payload 예시(JSON) + api 수신 파싱 경로 확인 |
| `project_gas/docs/contracts/` | render_api, project_gas | contract 변경 시 CPCR 강제 |
| Redis key `cyclestack:beat_schedule:active` | render_cron, render_api | key payload 스키마 변경 시 양쪽 코드 동기화 확인 |

---

## CPCR 연동 규칙
- 위 테이블에서 `affected_projects`가 **2개 이상**이면 CPCR 필수
- `interface` 변경 (API endpoint, payload schema, import 경로)이면 개수 무관 CPCR 필수
- CPCR 포맷: root_00001 섹션 4에서 확정한 6필드 포맷 사용

```
[CPCR-Title] 한 줄 요약
Scope: affected sub_projects = {render_api, render_web, ...}
Change Type: {interface|behavior|data|ops|docs}
Risk: {low|mid|high} + 이유 1줄
Verification: 수행/확인한 체크 1~3개
Rollback: 되돌리는 방법 1줄(없으면 "N/A")
```

---

## 갱신 규칙
- 새로운 크로스 프로젝트 의존성 발견 시 본 문서에 행 추가
- 의존성 제거 시 행 삭제 (이력은 git으로 관리)
