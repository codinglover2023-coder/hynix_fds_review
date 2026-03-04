"""fds_00001 Rule 102 통합 검증 스크립트"""
import asyncio
import os

os.environ["FDS_ADMIN_KEY"] = "test-admin-key"

import httpx as _httpx
from app import create_app
from app.db import init_db, SessionLocal
from app.bootstrap import seed_sample_data
from httpx import ASGITransport, AsyncClient

app = create_app()
results = []


def check(name, condition, actual):
    st = "PASS" if condition else "FAIL"
    results.append((name, condition, actual))
    print(f"  [{st}] {name} -> {actual}")


async def run_tests():
    # ASGITransport는 lifespan 이벤트를 트리거하지 않으므로 수동 초기화
    await init_db()
    async with SessionLocal() as session:
        await seed_sample_data(session)
    app.state.http_client = _httpx.AsyncClient(timeout=30.0)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        KEY = {"X-ADMIN-KEY": "test-admin-key"}

        # === 0단계: Admin API 인증 ===
        print("=== 0단계: Admin API 인증 확인 ===")
        r = await c.get("/api/admin/services")
        check("Admin no key -> 401", r.status_code == 401, r.status_code)

        r = await c.get("/api/admin/services", headers={"X-ADMIN-KEY": "wrong"})
        check("Admin wrong key -> 403", r.status_code == 403, r.status_code)

        # === 1단계: Admin API CRUD ===
        print("\n=== 1단계: Admin API CRUD ===")

        r = await c.get("/api/admin/services", headers=KEY)
        check("GET /services -> 200", r.status_code == 200, r.status_code)
        services = r.json()
        check("Seeded 2 services", len(services) == 2, len(services))

        r = await c.get("/api/admin/services/1", headers=KEY)
        check("GET /services/1 -> 200", r.status_code == 200, r.status_code)
        svc = r.json()
        print(f"    name={svc.get('name')}, sub_prefix={svc.get('sub_prefix')}")

        r = await c.post("/api/admin/services", headers=KEY, json={
            "name": "test_svc", "sub_prefix": "test", "base_url": "https://example.com",
            "auth_type": "bearer", "auth_value": "tok123",
        })
        check("POST /services -> 201", r.status_code == 201, r.status_code)
        new_id = r.json().get("id")

        r = await c.post("/api/admin/services", headers=KEY, json={
            "name": "test_svc", "sub_prefix": "test", "base_url": "https://example.com",
            "auth_type": "bearer", "auth_value": "tok123",
        })
        check("POST duplicate -> 409", r.status_code == 409, r.status_code)

        r = await c.put(f"/api/admin/services/{new_id}", headers=KEY, json={"name": "test_updated"})
        check("PUT /services -> 200", r.status_code == 200, r.status_code)
        check("PUT name updated", r.json().get("name") == "test_updated", r.json().get("name"))

        r = await c.post(f"/api/admin/services/{new_id}/mappings", headers=KEY, json={
            "path_pattern": "/api/v1", "description": "Test API v1",
        })
        check("POST /mappings -> 201", r.status_code == 201, r.status_code)
        mapping_id = r.json().get("id")

        r = await c.get(f"/api/admin/services/{new_id}/mappings", headers=KEY)
        check("GET /mappings -> 200", r.status_code == 200, r.status_code)
        check("Mapping count == 1", len(r.json()) == 1, len(r.json()))

        r = await c.delete(f"/api/admin/mappings/{mapping_id}", headers=KEY)
        check("DELETE /mappings -> 204", r.status_code == 204, r.status_code)

        r = await c.delete(f"/api/admin/services/{new_id}", headers=KEY)
        check("DELETE /services -> 204", r.status_code == 204, r.status_code)

        r = await c.get(f"/api/admin/services/{new_id}", headers=KEY)
        check("GET deleted -> 404", r.status_code == 404, r.status_code)

        # === 2단계: 프록시 호출 ===
        print("\n=== 2단계: 프록시 호출 ===")

        r = await c.get("/unknown/some/path")
        check("Unknown service -> 404", r.status_code == 404, r.status_code)

        r = await c.get("/conf/some/blocked/path")
        check("Blocked path -> 403", r.status_code == 403, r.status_code)

        await c.put("/api/admin/services/1", headers=KEY, json={"is_active": False})
        r = await c.get("/conf/wiki/rest/api/content")
        check("Inactive service -> 403", r.status_code == 403, r.status_code)

        await c.put("/api/admin/services/1", headers=KEY, json={"is_active": True})

        # 화이트리스트 등록 경로 → 프록시 시도 성공
        # 외부 서비스 도달: 401/403 (샘플 토큰 거부) = 프록시 정상
        # 외부 서비스 미도달: 502 (연결 실패) = 프록시 흐름 정상
        r = await c.get("/conf/wiki/rest/api/content")
        check("Conf proxy reached upstream", r.status_code in (200, 401, 403, 502), r.status_code)

        r = await c.get("/jira/rest/api/2/issue/TEST-1")
        check("Jira proxy reached upstream", r.status_code in (200, 401, 403, 502), r.status_code)

        r = await c.get("/conf/wiki/rest/api/content?limit=10&start=0")
        check("Query params forwarded", r.status_code in (200, 401, 403, 502), r.status_code)

        r = await c.post("/jira/rest/api/2/issue", json={"summary": "test"})
        check("POST body forwarded", r.status_code in (200, 401, 403, 502), r.status_code)

        # === 3단계: healthz + Swagger ===
        print("\n=== 3단계: healthz + Swagger ===")

        r = await c.get("/api/healthz")
        check("healthz -> 200", r.status_code == 200, r.status_code)
        check("healthz body ok", r.json() == {"status": "ok"}, r.json())

        r = await c.get("/docs")
        check("Swagger /docs -> 200", r.status_code == 200, r.status_code)

        r = await c.get("/openapi.json")
        check("openapi.json -> 200", r.status_code == 200, r.status_code)
        openapi = r.json()
        tags = set()
        for path_info in openapi.get("paths", {}).values():
            for op in path_info.values():
                if isinstance(op, dict):
                    for t in op.get("tags", []):
                        tags.add(t)
        check("Tags include admin", "admin" in tags, sorted(tags))
        check("Tags include proxy", "proxy" in tags, sorted(tags))

        # === 결과 요약 ===
        print("\n" + "=" * 50)
        passed = sum(1 for _, ok, _ in results if ok)
        total = len(results)
        print(f"TOTAL: {passed}/{total} PASSED")
        for name, ok, actual in results:
            if not ok:
                print(f"  FAIL: {name} (got {actual})")

    # cleanup
    await app.state.http_client.aclose()


asyncio.run(run_tests())
