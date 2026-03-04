# root_00003: Entrypoint 및 배포 규칙 정의

상태: **완료** (2026-02-28)
생성일: 2026-02-28
선행: `root_00001_rule_system_redesign_for_monorepo.md` (병행 가능)

## 목적
- Render 배포 시 각 서비스의 entrypoint 규칙 정의
- 모노레포에서 단일 코드베이스 → 복수 Render 서비스 매핑 규칙 확립

## 검토 항목

### 1. Render 서비스 매핑 규칙 ✅ 결정 완료
- [x] Render 서비스 **2개 고정** 확정

| Render 서비스 | 타입 | Entrypoint | 하위 프로젝트 |
|---|---|---|---|
| cyclestack-api | Web Service | `uvicorn render_api.main:app --host 0.0.0.0 --port $PORT` | render_api + render_web |
| cyclestack-cron | Cron Job | `python -m render_cron.main` | render_cron |

- [x] `render_anal`은 Render 배포 대상 아님 (로컬 전용) — 규칙 명시
- [x] `project_gas`는 clasp 배포 — Render 무관, 별도 배포

### 2. FastAPI + Flask 마운트 규칙 ✅ 결정 완료
- [x] 경로 규약 확정:
  - `/api/*` = FastAPI (직접 처리)
  - `/web/*` = Flask (WSGIMiddleware 마운트)
  - `/` = FastAPI root (금지 또는 `/web/`로 리다이렉트 — 1개로 고정)
- [x] 새 라우트 추가 체크리스트 (필수):
  1. `/api/` 또는 `/web/` prefix 준수
  2. 동일 경로 중복 여부 확인 (특히 `/healthz`, `/` 등)
  3. `/api/healthz` + `/web/healthz` 스모크 통과
- [x] 재시작 정책 확정:
  - 운영(Render): Flask 변경도 FastAPI 서비스 재배포/재시작 필요 (단일 프로세스)
  - 로컬: `--reload`가 Flask 코드 변경도 자동 반영 (동일 프로세스)
- [x] WSGIMiddleware 제약 기록:
  - WebSocket은 Flask 측 지원 불가 (WSGI 한계)
  - streaming response 버퍼링 가능
  - 단일 프로세스 공유 → 장애/부하 상호 영향
  - 고성능/대용량 트래픽은 분리 서비스 고려 (향후 옵션)

### 3. 환경 변수 관리 규칙 ✅ 결정 완료
- [x] config, `.env` 모두 **최상위 프로젝트에서 단일 관리** 확정
- [x] `.env` 파일 분리 정책 확정:
  - `.env.template` — git 추적, 변수 키 + 설명만 기록 (값 없음)
  - `.env` — git 미추적 (`.gitignore`), 로컬 실제 값 관리
- [x] `common_data/config.py`에서 환경 변수 로딩 통합
- [x] Render↔.env 동기화 규칙 확정:
  - **키의 SSOT = `.env.template`** (유일한 기준)
  - 값의 SSOT: Render(운영) / `.env`(로컬) 분리
  - 새 키 추가/삭제: `.env.template` + `common_data/config.py` + `render.yaml`(또는 Render UI env) **3종 동기화 필수**
  - 배포 전 체크: "키 존재 여부"를 로컬 스모크 체크리스트에 포함

#### 확정된 구조
```
CycleStack/
├── .env.template       # git 추적 — 키 목록 + 설명 (SSOT)
├── .env                # git 미추적 — 로컬 실제 값
└── common_data/
    └── config.py       # 환경 변수 로딩 통합 (.env.template 키 기준)
```

### 4. 의존성 관리 규칙 ✅ 결정 완료
- [x] **entrypoint가 있는 프로젝트별 `requirements.txt` 관리** 확정
  - `render_api/requirements.txt` — FastAPI + Flask (Web Service용)
  - `render_cron/requirements.txt` — scheduler (Cron Job용)
- [x] `render_anal`은 `render_api/requirements.txt`를 공유 (별도 파일 없음)
- [x] 최상위 `requirements.txt`는 제거 또는 전체 통합용 참조로만 유지

#### 확정된 구조
```
CycleStack/
├── render_api/requirements.txt    # Render Web Service + render_anal 공용
└── render_cron/requirements.txt   # Render Cron Job
```

### 5. render.yaml Blueprint 관리 규칙 ✅ 결정 완료
- [x] `render.yaml` 변경 시 **3종 동기화 + 스모크** 필수 게이트:
  1. `buildCommand`/`startCommand`가 실제 entrypoint와 일치
  2. 서비스별 requirements 경로가 정확
  3. env 키 변경 시 `.env.template`과 동기화
- [x] 환경 변수 추가/삭제 규칙:
  - `.env.template` 수정 → `common_data/config.py` 반영 → `render.yaml`(또는 Render UI env) 반영 (3종 동기화)
- [x] Python 버전 업데이트 절차:
  1. 로컬에서 동일 버전으로 스모크 테스트 통과
  2. requirements 재빌드 (필요 시 핀)
  3. `render.yaml` runtime 버전 업데이트
  4. 배포 후 healthz 확인 (`/api/healthz`, `/web/healthz`)

### 6. 로컬 개발 실행 규칙 ✅ 결정 완료
- [x] 표준 실행 위치: **`CycleStack/` 루트** (고정)
- [x] 표준 명령 확정:
  - API: `uvicorn render_api.main:app --reload --port 8000`
  - CRON: `python -m render_cron.main`
- [x] 하위 프로젝트 단독 실행:
  - 원칙: 루트 기준 실행 권장 (경로/환경 일관성)
  - 예외: 하위 폴더 실행 필요 시 별도 안내 문서/스크립트로만 허용
- [x] `common_data` import 보장:
  - 루트 실행을 전제로 import 보장 (PYTHONPATH 수동 설정 금지)

## 완료 기준
- [x] 서비스별 entrypoint 규칙 확정
- [x] 환경 변수 관리 정책 확정
- [x] 로컬 개발 ↔ Render 배포 간 일관성 보장

## Resolved Issues
- `root_00003_00_kickoff_scope.md` — 섹션 1~6 범위 확정 + 검증 체크리스트 완료
- `root_00003_01_design_review.md` — 서비스 매핑/마운트/환경변수/render.yaml/로컬 개발 설계 확정
- `root_00003_02_validation_and_output.md` — 정적 검증 6항목 + 런타임 스모크 3개 endpoint 전부 PASS
