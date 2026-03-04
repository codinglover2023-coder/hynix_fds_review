# 워크플로우 규칙 (프로젝트 초안)

최종 수정일: 2026-02-16  
적용 범위: `render_api_test`

## Rule 000: 규칙 재로딩 트리거
- 사용자가 `rule 000`을 호출하면 현재 `rule/` 문서를 다시 읽고 이후 작업에 즉시 반영한다.
- 우선 적용 순서:
1. `rule/workflow_rules.md` (프로젝트 규칙)
2. `rule/ref/workflow_rules.md` (레퍼런스, 보완용)

## Rule 001: 규칙 변경 정책
- 규칙은 고정 불변이 아니며 프로젝트 구조/운영 방식 변화에 따라 갱신한다.
- 규칙 간 충돌 시 "현재 저장소 코드와 디렉터리 구조"를 단일 사실 기준으로 사용한다.

## Rule 010: 작업 흐름
- 진행 중 작업은 `work-items/todo/`에서 관리한다.
- 완료된 작업은 `work-items/done/`으로 이동한다.
- 즉시 처리하기 어려운 쟁점은 `work-items/issues/`에 분리 기록한다.

## Rule 020: 파일 네이밍 규칙
- `work-items/todo/`: `<topic>.md` 또는 `<domain>/<topic>.md`
- `work-items/done/`: 완료 후 동일 파일명 유지
- `work-items/issues/`: `<topic>.md` (논의/결정/블로커 중심)
- 숫자 prefix(`001_...`)는 선택이며, 현재 저장소 관례를 우선한다.

## Rule 030: 실행 커뮤니케이션 규칙
- 작업 시작 시 아래 3가지를 명시한다.
1. 목표
2. 변경 대상 파일
3. 완료 기준(검증 포함)
- 작업 종료 시 아래 3가지를 남긴다.
1. 변경 파일 목록
2. 검증 결과
3. 남은 리스크/후속 작업

## Rule 040: 작업-이슈 연결 정책
- `work-items/todo/*.md` 진행 중 쟁점이 생기면 `work-items/issues/*.md`를 생성 또는 갱신한다.
- 이슈 문서는 최소 아래 섹션을 유지한다.
1. 배경
2. 결정 필요 사항
3. 옵션 비교
4. 결론

## Rule 050: 문서 동기화 정책
- 코드 변경이 API/운영에 영향을 주면 문서를 함께 갱신한다.
- 우선 갱신 대상:
1. `README.md` (실행/환경변수/엔드포인트 개요)
2. `docs/` 하위 운영 문서
3. `google_apps_script/doc/` (Apps Script 연동 변경 시)

## Rule 060: 런타임 안전 게이트
- 동작 변경이 있는 수정은 최소 1개 이상의 검증을 수행한다.
1. 단위 테스트 (`tests/`)
2. 수동 스모크 체크 (`/health`, 핵심 라우터)
3. 설정 로딩 확인 (`CONFIG_SHEET_ID`, `SCHEDULE_SHEET_ID`)
- 검증을 수행하지 못한 경우 사유를 결과에 명시한다.

## Rule 070: API 변경 게이트
- FastAPI 라우터/스키마 변경 시 아래를 확인한다.
1. `main.py` 라우터 등록 영향
2. 요청/응답 모델 영향
3. 기존 경로 호환성(브레이킹 여부)
- 브레이킹 변경이면 `work-items/issues/`에 마이그레이션 노트를 남긴다.

## Rule 080: Apps Script 브리지 게이트
- `google_apps_script/src/` 변경 시 대응 FastAPI 경로와 페이로드 계약을 함께 점검한다.
- 브리지 관련 문서는 최소 아래를 동기화한다.
1. `google_apps_script/doc/...`
2. `docs/apps_script_bridge.md` (또는 후속 재구성 경로)

## Rule 090: Config/Schema 게이트
- `config/config.csv`, `schema/schema.csv` 변경 시 필드 정의와 사용 지점을 함께 점검한다.
- 필드 추가/삭제 시 영향 라우터/서비스를 이슈 문서에 기록한다.

## Rule 095: 인코딩 정책
- 프로젝트의 모든 `.md` 파일은 `UTF-8 (BOM 없음) + LF`로 저장한다.
- 한글 깨짐이 발견되면 원문 복원 후 저장하고, 연관 문서까지 점검한다.

## Rule 096: 인코딩 강제 장치
- 인코딩 규칙은 문서 선언만으로 끝내지 않고 저장소 설정으로 강제한다.
1. `.editorconfig`로 `LF`, `UTF-8`, `final newline` 기본값을 적용한다.
2. `.gitattributes`로 `.md`의 `eol=lf`를 고정한다.
3. `.githooks/pre-commit` + `communication/tooling/check_md_utf8.py`로 커밋 전 `.md`의 `UTF-8(BOM 없음)/LF`를 검사한다.
- 재사용 템플릿은 `communication/templates/`에서 관리한다.
- 팀 공통 적용 명령:
1. `git config core.hooksPath .githooks`


## Rule 101: Todo Kickoff Bundle (Generic)
- 사용자가 `rule 101 {todo_idx}`를 호출하면, `{todo_idx}` 대상 todo에 대해 아래 작업을 자동 수행한다.
1. `todo/{todo_idx}_*.md` 기준으로 Codex가 먼저 수행 가능한 작업 목록을 정리한다.
2. `issue/` 폴더에 `{todo_idx}_{issue_idx}_*.md` 패턴 문서를 자동 생성/업데이트한다.
- 기본 생성 문서 템플릿:
  - `issue/{todo_idx}_00_kickoff_scope.md`
  - `issue/{todo_idx}_01_pipeline_design.md`
  - `issue/{todo_idx}_02_validation_and_output.md`
- 각 문서 필수 섹션:
  - `목적`
  - `현재 결정사항`
  - `남은 작업`
  - `다음 액션`
- `todo_idx`가 생략되면 현재 활성 todo 파일 인덱스를 우선 사용하고, 없으면 사용자에게 인덱스를 요청한다.

## Rule 102: Todo Execution From Issue Docs
- 사용자가 `rule 102 {todo_idx}`를 호출하면, `{todo_idx}` 대상 todo를 아래 순서로 처리한다.
1. `todo/{todo_idx}_*.md`와 `issue/{todo_idx}_*.md` 문서를 모두 읽고 현재 기준으로 사용한다.
2. `issue/{todo_idx}_*.md`에 정리된 항목 중 Codex가 즉시 수행 가능한 작업을 실제로 수행한다.
3. 수행 결과를 반영해 `todo/{todo_idx}_*.md`를 업데이트한다.
- `todo` 문서 업데이트 규칙:
  - 완료된 항목은 완료 상태로 표시한다.
  - 미완료/의사결정 필요 항목은 `todo/999_*.md`에 추가하거나 갱신한다.
  - 다음 실행 액션을 1~3개로 명시한다.
- `todo_idx`가 생략되면 현재 활성 todo 파일 인덱스를 우선 사용하고, 없으면 사용자에게 인덱스를 요청한다.

## Rule 103: Todo 인덱스 검증용 Jupyter 노트북 생성 규칙
- 사용자가 `rule 103 {todo_idx}`를 입력하면 `{todo_idx}` 작업 검증용 Jupyter 노트북을 생성/갱신한다.
- 입력 옵션:
  - 기본: `rule 103 {todo_idx}`
  - 검증 완료 처리: `rule 103 {todo_idx} done`
1. 노트북 경로는 `notebooks/{todo_idx}/`로 고정한다.
2. 파일명 규칙은 `{todo_idx}_{valid_idx}_<slug>.ipynb`를 사용한다.
  - 이력 관리 파일명: `{todo_idx}_{valid_idx}_{yyyymmdd}_{run_idx}_<slug>.ipynb`
  - 예시: `0010_00_20260218_01_validation_setup.ipynb`
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
9. 경로 탐색 규칙(중요):
  - 절대경로 하드코딩 금지
  - 노트북 시작 경로 기준으로 상위 경로를 순회하며 프로젝트 루트를 찾는다.
  - 프로젝트 루트 판별 조건: `work-items`, `config`, `handoff` 폴더가 모두 존재
  - 표준 함수:
```python
from pathlib import Path

def find_project_root(start: Path) -> Path:
    cur = start.resolve()
    for cand in [cur, *cur.parents]:
        if (cand / 'work-items').exists() and (cand / 'config').exists() and (cand / 'handoff').exists():
            return cand
    raise FileNotFoundError('project root not found')
```
  - 현재 프로젝트 기준 예시:
    - 프로젝트 루트: `D:/y2026/render/render_api_test`
    - 상위 경로: `D:/y2026/render`
10. `rule 102 {todo_idx}` 수행 후에는 `rule 103 {todo_idx}`를 권장 실행한다.
11. `done` 입력 처리:
  - `rule 103 {todo_idx} done`은 검증 완료 상태 업데이트 용도다.
  - `todo -> done` 이동은 `rule 105` 절차를 따른다.
12. `todo_idx`가 생략되면 현재 활성 todo 인덱스를 우선 사용하고, 불명확하면 사용자에게 확인한다.


## Rule 104: Full Rule Audit Report
- 사용자가 `rule 104`를 호출하면, 현재 `rule/`에 정의된 규칙을 처음부터 끝까지 전체 점검한다.
1. 점검 대상:
  - 규칙 번호 중복/누락 여부
  - 규칙 간 충돌/모순 여부
  - 호출 형식(`rule 000`, `rule 101 {todo_idx}` 등) 일관성
  - 파일 경로/네이밍 규칙의 실제 사용 가능성
2. 점검 결과 문서를 아래 경로로 생성/갱신한다.
  - `rule/104_rule_audit_report.md`
3. 보고서 필수 섹션:
  - `점검 범위`
  - `발견 이슈`
  - `수정 권고안`
  - `최종 판정(OK/Needs Update)`
4. 이슈가 없으면 `발견 이슈: 없음`으로 명시한다.

## Rule 105: Validation Confirmation Update Pattern
- 사용자가 검증 완료를 확인하면(예: "검증 확인했어"), 대상 `todo/{todo_idx}_*.md`를 즉시 업데이트한다.
- 호출 옵션:
  - 기본: `rule 105 {todo_idx}`
  - 노트북 검증/잔존 점검 무시: `rule 105 {todo_idx} --skip-notebooks-check`
0. `rule 105 {todo_idx}`로 호출되면 done 처리 전에 잔존 파일 검토를 먼저 수행한다.
  - 검토 대상:
    - `todo/{todo_idx}_*.md`
    - `issue/{todo_idx}_*.md` (working issue)
    - `notebooks/{todo_idx}/` (working notebook)
  - 잔존 파일이 있으면 기존 done 정책(`issue/done/...`, `notebooks/done/...`, `done/...`)으로 재처리한다.
  - 이미 done 경로에 동일 파일이 있으면 최신본 기준으로 갱신하고, working 경로는 placeholder 또는 삭제로 정리한다.
1. 검증 완료 증빙을 `진행 결과` 또는 `완료 기준 대비 상태`에 기록한다.
2. 남은 작업을 1~3개로 요약해 채팅에서 즉시 보고한다.
3. 남은 작업이 의사결정/환경 제약이면 `todo/999_*.md`에 반영 또는 갱신한다.
4. 완료 기준이 전부 충족되면 done 처리 전에 `Resolved Issues` 섹션을 `todo/{todo_idx}_*.md`에 갱신한다.
  - 규칙: issue 본문 전체 복사 금지, `요약(1~3줄) + 링크`만 통합
5. issue 상태를 분리 관리한다.
  - `working issue`: `issue/` 루트에 유지
  - `done issue`: `issue/done/%Y%m%w/{todo_idx}/` 하위로 이동 보관
  - `%Y%m%w`는 처리 시점 날짜 포맷(예: `2026020`)
6. notebook 상태도 issue와 동일하게 분리 관리한다.
  - `working notebook`: `notebooks/{todo_idx}/`에 유지
  - `done notebook`: `notebooks/done/%Y%m%w/{todo_idx}/` 하위로 이동 보관
  - `%Y%m%w`는 issue 이동 시점과 동일 기준을 사용한다.
7. `todo` 문서, 해결된 issue, 관련 notebook 정리가 끝나면 사용자 확인 후 `todo -> done/` 이동한다.
- `--skip-notebooks-check`가 명시되면:
  - 0번 단계의 notebook 잔존 점검을 생략한다.
  - 6번 단계의 notebook 이동/정리도 생략한다.
  - 단, `todo`/`issue` 점검 및 `todo -> done` 처리 규칙은 그대로 유지한다.
- `todo_idx`가 명시되지 않으면 현재 활성 todo 인덱스를 우선 사용한다.

## Rule 106: Concept Notebook Monthly Backup
- 사용자가 `rule 106`을 호출하면 `notebooks/concept/` 하위 산출물을 월 단위 백업 경로로 이동한다.
- 호출 옵션:
  - 기본: `rule 106`
  - 월 지정: `rule 106 202602` (형식: `YYYYMM`)
1. 백업 루트 경로:
  - `notebooks/concept/backup/{YYYYMM}/`
2. 이동 대상:
  - `notebooks/concept/` 하위의 `.ipynb` 파일
  - 필요 시 `.md`, `.csv`, `.json` 등 concept 소통용 파일도 함께 이동 가능
3. 제외 대상:
  - `notebooks/concept/backup/` 하위 파일/폴더는 재이동하지 않는다.
4. 동작 규칙:
  - 대상 파일이 없으면 `no-op`으로 종료하고 상태만 보고한다.
  - 같은 파일명이 이미 백업 경로에 있으면 날짜/시간 suffix를 붙여 충돌을 회피한다.
5. 보고 규칙:
  - 이동 파일 수, 백업 경로, 충돌로 rename된 파일 목록을 채팅에 요약 보고한다.

## Rule 107: Pipeline Current Version Sync
- 사용자가 `rule 107`을 호출하면 `pipeline/` 하위 현재 구현 코드를 기준으로 "현재 버전 동기화" 작업을 수행한다.
- 호출 옵션:
  - 기본: `rule 107`
  - 특정 파이프라인만: `rule 107 <pipeline_name>`
1. 점검 대상:
  - `pipeline/*.py` 실행 엔트리/인자(`--help`) 정상 여부
  - 관련 `todo/*`, `issue/*` 문서의 구현/산출물 경로 불일치 여부
  - 대표 산출물(`data/processed/...`) 존재 여부(필요 시 최소 실행으로 갱신)
2. 동기화 작업:
  - 코드 기준으로 문서(`todo`, `issue`, 필요 시 `docs`)의 상태/경로/명령어를 최신화
  - 오래된 예시 경로나 구버전 명령어를 현재 코드 기준으로 교체
  - 변경된 항목을 "무엇이 왜 바뀌었는지" 요약해 채팅에 보고
3. 산출물 갱신 원칙:
  - 무거운 전체 실행 대신 샘플 실행(`--max-tickers`) 우선
  - 네트워크/환경 제약이 있으면 실행 대신 제약사항을 문서에 기록
4. 완료 보고:
  - 수정 파일 목록
  - 검증 결과(`--help`/샘플 실행/파일 존재 확인)
  - 남은 작업(있으면 1~3개)

## Rule 108: Pipeline Common Function Consolidation Todo
- 사용자가 `rule 108`을 호출하면 `pipeline/` 내 공통 함수 후보를 분석하고, `src/` 공통화 작업을 위한 신규 `todo` 문서를 생성/갱신한다.
- 호출 옵션:
  - 기본: `rule 108`
  - 대상 제한: `rule 108 <pipeline_name_or_prefix>`
1. 분석 대상:
  - `pipeline/*.py` 함수 정의
  - 중복/유사 함수(예: config 로딩, 숫자 파싱, 날짜/경로 처리, CSV IO, 로깅/출력 포맷)
2. 산출물(todo 신규 등록):
  - 기본 파일: `todo/108_pipeline_common_function_consolidation.md`
  - 이미 존재하면 최신 분석 결과로 갱신
3. todo 문서 필수 섹션:
  - `목적`
  - `공통화 후보 함수 목록`
  - `영향도(High/Medium/Low)`
  - `이관 대상 제안(src/common, src/pipelines)`
  - `단계별 작업 절차`
  - `완료 기준`
4. 작업 원칙:
  - 동작 변경 없이 리팩터링 우선(behavior-preserving)
  - 기존 `python pipeline/*.py` 실행 호환 유지(래퍼 또는 fallback 유지)
  - 공통화 후 `--help` 및 샘플 실행으로 회귀 확인
5. 보고 규칙:
  - 신규/갱신된 `todo` 파일 경로
  - 식별된 공통 함수 개수
  - 우선 이관 대상 1~3개

## Rule 109: Endpoint Handoff Package Export
- 사용자가 `rule 109 {endpoint_idx}`를 호출하면, `{endpoint_idx}` 작업을 다른 환경으로 이관하기 위한 패키지 복사를 수행한다.
- 목적:
  - `src`, `pipeline`, `issue`, `todo`, `done`, `notebooks`, `report`, 사전 `data`(예: `initial_ticker_list`, `sample` 기초정보)를 한 번에 취합
  - 예: `rule 109 006` 호출 시 `006`이 참조하는 선행 작업(`001~006`)까지 함께 수집
- 호출 옵션:
  - 기본: `rule 109 {endpoint_idx}`
  - 날짜 지정: `rule 109 {endpoint_idx} --date YYYYMMDD`
  - 대상 루트 지정: `rule 109 {endpoint_idx} --out handoff`
  - 데이터 최소/확장: `rule 109 {endpoint_idx} --data-profile minimal|standard|full` (기본 `full`)

1. 출력 경로 규칙:
  - 기본 출력 루트: `handoff/`
  - 최종 경로 패턴: `handoff/%Y%m%d/{endpoint_idx}/`
  - 예시: `handoff/20260216/006/`

2. 참조 작업 인덱스 수집 규칙:
  - 기본 포함: `{endpoint_idx}` 본인
  - 추가 포함: `{endpoint_idx}` 문서(`todo`, `issue`, `done`)에서 참조된 선행 작업 인덱스(`000~999`) 자동 추출
  - 추출 실패/애매한 경우:
    - 안전 기본값으로 `001..{endpoint_idx}` 범위를 포함
    - 채팅에 자동추정 근거를 보고

3. 복사 대상 범위:
  - 코드:
    - `src/**`
    - `pipeline/**`
  - 문서:
    - `todo/{idx}_*.md` (대상 인덱스 집합)
    - `done/{idx}_*.md` (대상 인덱스 집합)
    - `issue/{idx}_*.md`, `issue/done/**/{idx}/**`
  - 노트북:
    - `notebooks/{idx}/**`
    - `notebooks/done/**/{idx}/**`
  - 리포트:
    - `report/**` 중 대상 인덱스 실행에서 생성된 파일(문서 참조 경로 우선)
  - 데이터(사전/기초):
    - 공통: `data/processed/initial_ticker_list.csv`
    - sample 기초: `data/processed/sample/**`, `data/raw/sample/**` (profile 정책에 따라 축소 가능)

4. `--data-profile` 정책:
  - `minimal`:
    - 문서에서 직접 참조된 파일 + `initial_ticker_list.csv`만 포함
  - `standard` (기본):
    - `minimal` + `data/processed/sample/**` + 필수 로그/메타(`collection_*`, `now_collection_*`, `run_meta.json`)
  - `full`:
    - `standard` + `data/raw/sample/**` + 관련 `report/**` 전체

5. 복사 동작 규칙:
  - 원본 보존(복사만 수행, 이동/삭제 금지)
  - 상대 경로 구조를 패키지 내부에 그대로 유지
  - 동일 파일 충돌 시 최신 수정시간 기준으로 덮어쓰기
  - 누락 파일은 실패로 중단하지 않고 `missing_files.csv`에 기록 후 계속 진행

6. 매니페스트/검증 산출물:
  - `manifest.csv`: 복사 파일 목록(원본, 대상, 크기, 수정시각, sha256)
  - `missing_files.csv`: 참조되었으나 미존재한 파일 목록
  - `summary.md`: 수집 인덱스, 파일 수, 데이터 프로파일, 주의사항

7. 완료 보고 규칙:
  - 출력 폴더 경로
  - 포함된 작업 인덱스 목록(예: `001,002,003,004,005,006`)
  - 복사 파일 수 / 누락 파일 수
  - 재현 명령 1줄(`rule 109 {endpoint_idx} ...`)

## Rule 110: Handoff Documentation Generator By Path And Target Mode
- 사용자가 `rule 110 {handoff_path} {handoff_target_mode}`를 호출하면, 지정한 handoff 패키지 경로를 기준으로 이관 문서를 생성/갱신한다.
- 입력 형식:
  - 기본: `rule 110 {handoff_path} {handoff_target_mode}`
  - 예시 1: `rule 110 handoff/20260216/006 fastapi`
  - 예시 2: `rule 110 20260216\\006 fastapi`
- `{handoff_target_mode}` 예시:
  - `fastapi`
  - 추후 확장 가능(`airflow`, `batch`, `worker` 등)

1. 목적:
  - `rule 109` 산출물(`handoff/%Y%m%d/{endpoint_idx}/`)을 대상 모드에 맞춘 실행/검증 문서로 변환한다.

2. handoff 경로 해석 규칙:
  - 표준 입력: `handoff/%Y%m%d/{endpoint_idx}`
  - 축약 입력 허용: `%Y%m%d/{endpoint_idx}` 또는 `%Y%m%d\\{endpoint_idx}`
  - 축약 입력 시 내부적으로 `handoff/%Y%m%d/{endpoint_idx}`로 정규화한다.
  - 경로가 존재하지 않으면 실패 처리하고 후보 경로(최신 날짜/인덱스)를 안내한다.

3. 입력 검증 규칙:
  - 필수 파일:
    - `manifest.csv`
    - `summary.md`
  - 선택 파일:
    - `missing_files.csv` (존재 시 리스크 반영)
  - 필수 파일이 없으면 문서 생성 실패로 처리한다.

4. 문서 생성 경로:
  - 기본 경로: `{handoff_path}/docs/`
  - 기본 파일명:
    - `handoff_%Y%m%d_{endpoint_idx}_{handoff_target_mode}.md`
  - 예시:
    - `handoff/20260216/006/docs/handoff_20260216_006_fastapi.md`

5. 문서 필수 섹션:
  - `목적`
  - `대상 모드({handoff_target_mode})`
  - `패키지 요약` (복사 파일 수, 누락 파일 수, 포함 인덱스)
  - `디렉터리 구조`
  - `실행 전 요구사항` (Python/venv/env/config)
  - `이관 절차` (복사/설정/실행 순서)
  - `검증 절차` (필수 커맨드와 기대 결과)
  - `리스크 및 제외 항목`
  - `원본 참조` (`manifest.csv`, `summary.md`, 관련 todo/issue 경로)

6. 모드별 템플릿 규칙:
  - `fastapi` 모드일 때 최소 포함:
    - API 서버 실행 기준(엔트리포인트/환경변수)
    - 백그라운드/스케줄 연동 포인트
    - `pipeline` 호출 계약(입력/출력 경로, resume 옵션)
  - 모드 템플릿이 미정이면 공통 템플릿으로 생성 후 `TODO(mode-specific)` 섹션에 보완 항목을 남긴다.

7. 생성 동작 규칙:
  - 기존 문서가 있으면 기본은 덮어쓰기, 필요 시 날짜/시간 suffix 버전 문서 추가 가능
  - `missing_files.csv`에 항목이 있으면 문서 `리스크` 섹션에 반드시 명시

8. 완료 보고 규칙:
  - 생성 문서 경로
  - 기준 handoff 패키지 경로(정규화 결과 포함)
  - 대상 모드
  - 문서에 반영된 핵심 리스크 1~3개




## Rule 111: 외부 Handoff 단계별 검토
- 다른 프로젝트에서 이관받은 내용을 현재 저장소에 어떻게 적용할지 검토할 때 사용한다.
- 입력 형식:
1. `rule 111 {handoff_path} {step}`
2. `rule 111 {handoff_path} {step} --mode fastapi`
- `--mode` 생략 시 기본값은 `fastapi`다.

### 1) 입력 검증
- `handoff_path`가 실제로 존재해야 한다.
- `handoff_path` 하위 필수 파일:
1. `summary.md`
2. `manifest.csv`
- 선택 파일:
1. `missing_files.csv`
- 필수 파일이 없으면 즉시 중단하고 누락 경로를 보고한다.

### 2) Step 사전
- `00`: package-fact-check
- `01`: structure-mapping
- `02`: runtime-prerequisites
- `03`: integration-design
- `04`: verification-plan
- `05`: risk-and-gap
- `06`: execution-decision
- 정의되지 않은 step 입력 시 중단하고 유효 step 목록을 반환한다.

### 3) 산출 경로 규칙
- 기본 루트: `work-items/issues/handoff_review/`
- 대상 폴더: `work-items/issues/handoff_review/{yyyymmdd}_{handoff_id}/rule_111/`
- step 문서명: `step_{step}_{slug}.md`
- `handoff_id`: `handoff_path` 마지막 토큰 (예: `006`)
- `slug`: Step 사전 이름 사용

### 4) Step 문서 필수 섹션
1. `Purpose`
2. `Input Package`
3. `Current Project Mapping`
4. `Findings`
5. `Apply Decision (Keep/Adapt/Drop)`
6. `Action Items`
7. `Open Questions`
8. `Source References`

### 5) Step별 분석 규칙
- Step `00` (package-fact-check)
1. `summary.md`에서 목적/범위/복사 수/누락 수/모드를 추출한다.
2. `manifest.csv`와 대조해 문서 주장과 실제 파일 구성이 일치하는지 확인한다.

- Step `01` (structure-mapping)
1. handoff 폴더 구조를 현재 저장소 경로(`app/`, `docs/`, `work-items/`, `google_apps_script/` 등)로 매핑한다.
2. 매핑 불가 경로와 신규 수용 경로를 명시한다.

- Step `02` (runtime-prerequisites)
1. 런타임/환경변수/의존성 요구사항을 식별한다.
2. 현재 프로젝트(`requirements.txt`, 설정 파일, env 계약)와 차이를 정리한다.

- Step `03` (integration-design)
1. FastAPI 계층(라우터/서비스/스케줄러/설정) 기준 통합 방안을 설계한다.
2. "동작 불변 리팩터링"과 "동작 변경 통합"을 분리해 제시한다.

- Step `04` (verification-plan)
1. 명령 단위 검증 절차와 기대 산출물을 정의한다.
2. 필요 시 API 스모크 체크와 데이터 산출물 검증을 포함한다.

- Step `05` (risk-and-gap)
1. 기술 리스크/운영 리스크/증빙 공백을 정리한다.
2. 각 리스크별 완화 액션과 담당 주체를 기록한다.

- Step `06` (execution-decision)
1. Go/No-Go와 단계적 롤아웃 권고안을 확정한다.
2. 우선순위 체크리스트(`P0`, `P1`, `P2`)를 작성한다.

### 6) 업데이트 정책
- 동일 step 문서가 이미 있으면 덮어쓰지 말고 최신 판단으로 갱신한다.
- 유효하지 않은 과거 가정은 명시적으로 제거한다.

### 7) 완료 보고 규칙
- step 문서 생성/갱신 후 아래를 채팅으로 보고한다.
1. 산출 파일 경로
2. 핵심 발견사항 최대 3개
3. 다음 권장 step 1개

### 8) Baseline Reference Rule (Required)
- `rule 111` 수행 시, 아래 기준 리뷰의 Decision Update를 기본 참조로 사용한다.
1. `work-items/issues/handoff_review/20260216_006/rule_111/step_00_package-fact-check.md`
2. `work-items/issues/handoff_review/20260216_006/rule_111/step_01_structure-mapping.md`
3. `work-items/issues/handoff_review/20260216_006/rule_111/step_02_runtime-prerequisites.md`
4. `work-items/issues/handoff_review/20260216_006/rule_111/step_03_integration-design.md`
5. `work-items/issues/handoff_review/20260216_006/rule_111/step_04_verification-plan.md`
6. `work-items/issues/handoff_review/20260216_006/rule_111/step_05_risk-and-gap.md`
7. `work-items/issues/handoff_review/20260216_006/rule_111/step_06_execution-decision.md`
- 적용 원칙:
1. 기존 결정과 충돌이 없으면 `Keep`로 계승한다.
2. 패키지 구조/요구사항 차이가 있으면 `Adapt`로 차이와 근거를 명시한다.
3. 기존 결정을 적용하지 않으면 `Drop` 사유를 step 문서에 명시한다.

## Rule 112: Pipeline Archive + API Example Governance
- 목적: 파이프라인 산출물(csv/txt 등)을 Drive에 아카이브하고, handoff API 예제를 `md/py/ipynb` 형태로 관리한다.
- 기준 리뷰 경로: `work-items/issues/handoff_review/{review_key}`

### 1) 입력 형식
1. `rule 112 {handoff_review_path} {step}`
2. `rule 112 {handoff_review_path} {step} --mode fastapi`
3. `rule 112 {handoff_review_path} {step} --archive-date YYYYMMDD`
- `handoff_review_path` 예시: `work-items/issues/handoff_review/20260216_006`
- `review_key`: `handoff_review_path`의 마지막 토큰 (예: `20260216_006`)
- `--mode` 기본값: `fastapi`
- `--archive-date` 생략 시 실행일(`YYYYMMDD`) 사용

### 2) Step 사전
- `00`: output-inventory
- `01`: drive-archive-design
- `02`: export-manifest-and-metadata
- `03`: api-example-spec
- `04`: example-assets-generation
- `05`: api-change-impact-sync
- `06`: verification-and-smoke
- `07`: operation-and-retention-decision

### 3) 산출 경로
- 리뷰 문서 루트: `{handoff_review_path}/rule_112/`
- step 문서명: `step_{step}_{slug}.md`
- API 예제 루트: `{handoff_review_path}/examples/`
- 예제 파일:
1. `request_examples.md`
2. `request_examples.py`
3. `request_examples.ipynb`
- 로컬 임시 export 루트: `var/pipeline_exports/{review_key}/{archive_date}/`

### 4) Drive 아카이브 정책 (확정)
1. 업로드 방식은 API 기반으로 설계한다.
2. 목표 URI:
- `/apps-script/spreadsheet`
- `/apps-script/folder`
- `/apps-script/folder/list`
3. 일반 파일 업로드 API가 아직 없으므로 API 관리 작업은 아래 TODO에서 진행한다.
- `work-items/todo/0001_rule112_api_upload_management.md`
4. API 업로드가 준비될 때까지는 `common` 패키지 기반 Python 직접 업로드를 사용한다.
5. 공통 패키지 작업은 아래 TODO에서 관리한다.
- `work-items/todo/0002_rule112_common_drive_upload_package.md`
6. raw 파일은 원본 그대로 업로드한다(재인코딩/재압축 금지).

### 5) 보존 정책 (확정)
1. 보존 기간 및 삭제 승인 절차는 현재 수동 운영으로 고정한다.
2. timer + Drive 삭제 API가 준비되면 재설계한다.

### 6) API Spec Version 정책 (확정)
1. FastAPI 코드(또는 settings)에 `API_SPEC_VERSION`을 둔다.
2. Rule 112 실행 시 `manifest.json`에 `api_spec_version`을 자동 기록한다.
3. 1인 개발 기준 버전 증가 규칙:
- breaking 변경(필수 필드/응답 구조/경로 변경): MAJOR 증가
- non-breaking 변경(필드 추가/선택값 확장): MINOR 증가
- 문서/예제 오타 수준: PATCH 증가 또는 유지

### 7) 노트북 출력 정책 (확정)
1. 예제 노트북은 실행 결과를 포함해 저장한다.
2. 전체 원문 응답이 아닌 요약만 저장한다.
3. 요약 필수 항목:
- `status`
- 핵심 필드
- 실행 시간
4. 대용량 데이터와 민감 정보는 제외한다.

### 8) 동기화 규칙
- API 스펙이 변경되면 동일 변경 세트에서 아래를 함께 갱신한다.
1. `{handoff_review_path}/examples/request_examples.md`
2. `{handoff_review_path}/examples/request_examples.py`
3. `{handoff_review_path}/examples/request_examples.ipynb`
4. `{handoff_review_path}/rule_112/step_03_*.md`
5. `{handoff_review_path}/rule_112/step_05_*.md`
6. `{handoff_review_path}/rule_112/step_06_*.md`

### 9) 완료 보고
- step 갱신 후 아래를 보고한다.
1. 산출 파일 경로
2. Drive 아카이브 경로
3. examples 갱신 여부(`md/py/ipynb`)
4. 다음 권장 step
