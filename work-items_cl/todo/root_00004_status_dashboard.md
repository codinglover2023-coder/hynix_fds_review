# TODO: 모노레포 현황 대시보드 — 2026-03-03

- todo_idx: `root_00004`
- 작성일: 2026-03-03
- 상태: 스냅샷
- 생성 규칙: rule 200 --save

---

## 전체 현황 요약

| 프로젝트 | todo (활성) | done (최근 1개월) | issue (활성) |
|---|---|---|---|
| render_api | 6건 | 0건 | 18건 |
| render_cron | 1건 | 7건 | 3건 |
| render_anal/av | 1건 | 4건 | 3건 |
| project_arch (cl) | 4건 | 0건 | 0건 |
| project_arch (co) | 1건 | 0건 | 0건 |
| **합계** | **13건** | **11건** | **24건** |

---

## 프로젝트별 상세

### render_api

#### 진행 중

| todo_idx | 제목 | 상태 | 관련 | issue |
|---|---|---|---|---|
| `api_00001` | Schedule API | 구현 완료 (실연동 대기) | cron_00005 | 0건 |
| `api_00002` | Worker Beat Active API | 구현 완료 (실연동 대기) | cron_00007 | 0건 |
| `api_00003` | Neon PostgreSQL 연결 | 설계 대기 | api_00004, api_00005 | 3건 |
| `api_00004` | Neon 브랜치 전략 | 설계 대기 | api_00003, api_00005 | 3건 |
| `api_00005` | 투자 데이터 스키마 | 설계 대기 | api_00003 | 3건 |
| `api_00006` | Stocklist Sheet Init | kickoff | anal_av_00005, cron_00008 | 3건 |

#### 최근 완료 (1개월)

| todo_idx | 제목 | 완료일 |
|---|---|---|
| (없음) | | |

---

### render_cron

#### 진행 중

| todo_idx | 제목 | 상태 | 관련 | issue |
|---|---|---|---|---|
| `cron_00008` | Stocklist Flag Sync Task | kickoff (D-1~D-4 확정) | api_00006, anal_av_00005 | 3건 |

#### 최근 완료 (1개월)

| todo_idx | 제목 | 완료일 |
|---|---|---|
| `cron_00001` | Celery Migration Design | 2026-03-02 |
| `cron_00002` | Celery Code Implementation | 2026-03-02 |
| `cron_00003` | Local Test | 2026-03-02 |
| `cron_00004` | Render Deploy | 2026-03-02 |
| `cron_00005` | Dynamic Beat Schedule | 2026-03-03 |
| `cron_00006` | PG Execute SQL Kwarg | 2026-03-03 |
| `cron_00007` | Beat Status Publish | 2026-03-03 |

---

### render_anal/av_pipeline

#### 진행 중

| todo_idx | 제목 | 상태 | 관련 | issue |
|---|---|---|---|---|
| `anal_av_00005` | GSheet Flag Sync | rule101 완료 (rule102 대기) | api_00006, cron_00008 | 3건 |

#### 최근 완료 (1개월)

| todo_idx | 제목 | 완료일 |
|---|---|---|
| `anal_av_00001` | Schema Design | 2026-03 |
| `anal_av_00002` | Earnings Ingest | 2026-03 |
| `anal_av_00003` | Price Ingest | 2026-03 |
| `anal_av_00004` | Flag System | 2026-03 |

---

### project_arch

#### 진행 중 (cl)

| 파일명 | 제목 | 상태 |
|---|---|---|
| render_object_storage_review | Render Object Storage 검토 | 검토중 |
| backblaze_b2_backup_archive_review | Backblaze B2 백업/아카이브 검토 | 검토중 |
| render_redis_review | Render Redis 검토 | 검토중 |
| render_open_db_review | Render Open DB 검토 | 검토중 |

#### 진행 중 (co)

| 파일명 | 제목 | 상태 |
|---|---|---|
| render_object_storage_review | Render Object Storage 검토 | 검토중 |

> project_arch 검토 문서는 표준 todo_idx 체계 미사용. 리뷰 완료 시 별도 정리 필요.

---

## 완료 판정 로드맵

> 각 활성 todo가 done(rule 105)이 되기 위해 필요한 잔여 사항.
> C-1~C-4 판정 기준: Rule 201 참조.

---

### `api_00001` — Schedule API

**현재 상태**: 구현 완료 (실연동 검증 대기)

**C-1~C-4 판정**:

| 기준 | 결과 | 사유 |
|---|---|---|
| C-1 작업 항목 | **△** | 1건 미완료 (실연동 검증 — 사용자 수행 대기) |
| C-2 완료 판정 | N/A | 완료 판정 기준 섹션 없음 |
| C-3 의사결정 | **O** | |
| C-4 블로커 | **O** | |

**잔여 작업**:

- [ ] 실연동 검증 — `POST /api/schedule/init` → Google Sheets 워크시트 생성 확인 (사용자 수행)

**Done 조건**: 사용자가 실연동 검증 완료 확인 시 즉시 done 가능.

---

### `api_00002` — Worker Beat Active API

**현재 상태**: 구현 완료 (실연동 검증 대기 — cron_00007 Redis 발행 필요)

**C-1~C-4 판정**:

| 기준 | 결과 | 사유 |
|---|---|---|
| C-1 작업 항목 | **X** | 2건 미완료 (환경변수 확인 + cron_00007 실연동 검증) |
| C-2 완료 판정 | N/A | 완료 판정 기준 섹션 없음 |
| C-3 의사결정 | **O** | |
| C-4 블로커 | **X** | `cron_00007` 실연동 검증 필요 (코드는 done, 배포 검증 대기) |

**잔여 작업**:

- [ ] `CELERY_BROKER_URL` 환경변수 API 측에서 접근 가능 확인 (배포 시)
- [ ] `cron_00007` Redis 발행 구현 후 실연동 검증

**Done 조건**: Render 배포 후 `cron_00007` Redis 발행 → `GET /schedule/active` 정상 응답 확인.

---

### `api_00003` — Neon PostgreSQL + FastAPI 연결 설정

**현재 상태**: 설계 대기

**C-1~C-4 판정**:

| 기준 | 결과 | 사유 |
|---|---|---|
| C-1 작업 항목 | **X** | 0/7 완료 |
| C-2 완료 판정 | N/A | |
| C-3 의사결정 | **O** | |
| C-4 블로커 | **O** | 선행 작업 없음 |

**잔여 작업**:

- [ ] Neon CLI 초기화 (`npx neonctl@latest --force-auth init --agent claude`)
- [ ] Neon 프로젝트 생성 + 브랜치 확인
- [ ] `requirements.txt`에 `sqlalchemy[asyncio]`, `asyncpg` 추가
- [ ] `app/db/engine.py` 생성 — 엔진 + 세션 팩토리
- [ ] `app/__init__.py` lifespan에 `engine.dispose()` 추가
- [ ] Render 환경변수 `DATABASE_URL` 설정
- [ ] 연결 스모크 테스트 (서버 부팅 + DB 핑)

**Done 조건**: Neon 프로젝트 생성 → SQLAlchemy async 엔진 연결 → 스모크 테스트 성공.

---

### `api_00004` — Neon 브랜치 전략 + Render 환경 매핑

**현재 상태**: 설계 대기

**C-1~C-4 판정**:

| 기준 | 결과 | 사유 |
|---|---|---|
| C-1 작업 항목 | **X** | 0/5 완료 |
| C-2 완료 판정 | N/A | |
| C-3 의사결정 | **O** | |
| C-4 블로커 | **X** | `api_00003` (Neon 연결) 선행 필요 |

**잔여 작업**:

- [ ] Neon 프로젝트에서 `main`, `dev` 브랜치 확인/생성
- [ ] Render 환경변수 `DATABASE_URL` 설정 (prod → main)
- [ ] 로컬 `.env`에 dev 브랜치 연결 문자열 설정
- [ ] Alembic 초기화 여부 결정
- [ ] staging 브랜치 생성 시점 결정 (당장 불필요할 수 있음)

**Done 조건**: `api_00003` 완료 후 → Neon main/dev 브랜치 생성 → Render/로컬 환경변수 매핑.

---

### `api_00005` — 투자 데이터 전용 스키마 설계

**현재 상태**: 설계 대기

**C-1~C-4 판정**:

| 기준 | 결과 | 사유 |
|---|---|---|
| C-1 작업 항목 | **X** | 0/5 완료 |
| C-2 완료 판정 | N/A | |
| C-3 의사결정 | **O** | |
| C-4 블로커 | **X** | `api_00003` (Neon 연결) 선행 필요 |

**잔여 작업**:

- [ ] 스키마 최종 확정 (테이블 구조, 필드)
- [ ] SQLAlchemy ORM 모델 파일 생성 (`app/db/models.py`)
- [ ] Alembic 초기 마이그레이션 생성
- [ ] dev 브랜치에 스키마 적용
- [ ] CRUD API 엔드포인트 설계 (별도 todo)

**Done 조건**: `api_00003` 완료 → 스키마 확정 → dev 브랜치에 마이그레이션 적용 → CRUD 설계.

---

### `api_00006` — Stocklist Google Sheets 워크시트 Init

**현재 상태**: kickoff

**C-1~C-4 판정**:

| 기준 | 결과 | 사유 |
|---|---|---|
| C-1 작업 항목 | **X** | 0/8 완료 |
| C-2 완료 판정 | **X** | 0/6 완료 |
| C-3 의사결정 | **O** | anal_av_00005에서 D-1~D-6 전체 확정됨 |
| C-4 블로커 | **O** | 선행 없음 (기존 sheets 인프라 활용) |

**잔여 작업**:

- [ ] `sheets/stocklist_loader.py` 구현 (워크시트 읽기 + list[dict] 반환)
- [ ] `routers/stocklist.py` 구현 (`POST /stocklist/init` — config/init 패턴)
- [ ] `app/__init__.py`에 stocklist 라우터 등록
- [ ] `.env.template`에 `STOCKLIST_WORKSHEET` 추가
- [ ] init 실행 → 워크시트 생성 확인
- [ ] `GET /stocklist/`, `POST /stocklist/reload` 추가
- [ ] `POST /stocklist/sync` 구현 (Sheet → DB flag 동기화 + dry_run 지원)
- [ ] `cron_00008` 태스크에서 sync 엔드포인트 호출 확인

**Done 조건**: rule102 구현 → init/reload/sync 엔드포인트 동작 → cron_00008 연동 확인.

---

### `cron_00008` — Stocklist → Flag 자동 동기화 Celery 태스크

**현재 상태**: kickoff (D-1~D-4 확정)

**C-1~C-4 판정**:

| 기준 | 결과 | 사유 |
|---|---|---|
| C-1 작업 항목 | **X** | 0/7 완료 |
| C-2 완료 판정 | **X** | 0/5 완료 |
| C-3 의사결정 | **O** | D-1~D-4 전체 확정 |
| C-4 블로커 | **X** | `api_00006` (sync 엔드포인트), `anal_av_00005` Phase 1~2 선행 |

**잔여 작업**:

- [ ] `tasks/stocklist_sync.py` 구현
- [ ] `celeryconfig.py` include에 모듈 추가
- [ ] `_schedules` 워크시트에 태스크 등록
- [ ] render_api에 `POST /stocklist/sync` 엔드포인트 추가 (api_00006 확장)
- [ ] 로컬 테스트 (celery worker 실행 → 태스크 호출)
- [ ] Render 배포 확인

**Done 조건**: `api_00006` sync 엔드포인트 완료 → 태스크 구현 → _schedules 등록 → 배포 검증.

---

### `anal_av_00005` — Google Sheets → Flag 동기화

**현재 상태**: rule101 완료 (D-1~D-6 전체 확정, rule102 대기)

**C-1~C-4 판정**:

| 기준 | 결과 | 사유 |
|---|---|---|
| C-1 작업 항목 | **X** | 6/14 완료 (D-1~D-6 확정, 코드 미착수) |
| C-2 완료 판정 | **X** | 0/7 완료 |
| C-3 의사결정 | **O** | D-1~D-6 전체 확정 |
| C-4 블로커 | **△** | `api_00006` init 엔드포인트 선행 권장 (워크시트 존재 필요) |

**잔여 작업**:

- [ ] gspread 의존성 추가 (av_pipeline)
- [ ] `holding` flag seed 추가 (flag_def)
- [ ] `sheet_reader.py` 구현
- [ ] `sheet_flag_sync.py` 구현 (dry-run 포함)
- [ ] `config.py` 상수 추가
- [ ] stock 자동 등록 + symbol validation 로직
- [ ] Phase 1: Jupyter notebook 검증
- [ ] Phase 2: CLI runner 승격 (`--dry-run` / `--apply`)

**Done 조건**: sheet_reader + sheet_flag_sync 구현 → Phase 1 Jupyter 검증 → Phase 2 CLI 안정화. Phase 3(cron_00008)은 별도.

---

## 의존 체인

```
api_00003 ──→ api_00004
         └──→ api_00005

api_00006 ──→ anal_av_00005 (Phase 1~2)
         └──→ cron_00008 (Phase 3)

cron_00005 (done) ──→ cron_00007 (done) ──→ api_00002 (실연동 대기)

api_00001 ── 독립 (실연동 대기)
```

## 즉시 착수 가능 작업

| 우선순위 | todo_idx | 작업 | 비고 |
|---|---|---|---|
| 1 | `api_00001` | 실연동 검증 (사용자 수행) | done 직전 |
| 2 | `api_00006` | rule102 구현 (stocklist init) | 블로커 없음 |
| 3 | `anal_av_00005` | rule102 구현 (sheet_reader + sync) | api_00006 병행 가능 |
| 4 | `api_00003` | Neon CLI 초기화 + 연결 설정 | 블로커 없음 |

---

## 변경 이력

- 2026-03-03: rule 200 --save로 자동 생성 (root rule201 batch sweep 직후)
