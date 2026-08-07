"""Tests for product polish infrastructure (no AI engine changes)."""

import pytest
from backend.services.file_security import validate_upload, verify_signed_url, generate_signed_download_url
from backend.services.auth_service import ROLE_PERMISSIONS


def test_validate_upload_rejects_bad_extension():
    ok, msg = validate_upload("resume.exe", b"content")
    assert not ok
    assert "not allowed" in msg.lower()


def test_validate_upload_accepts_pdf():
    ok, _ = validate_upload("resume.pdf", b"%PDF-1.4 test content")
    assert ok


def test_validate_upload_rejects_empty():
    ok, msg = validate_upload("resume.pdf", b"")
    assert not ok
    assert "empty" in msg.lower()


def test_signed_url_roundtrip():
    url = generate_signed_download_url("resumes/job1/file.pdf", "user-123")
    assert "sig=" in url
    # Parse query params manually
    from urllib.parse import urlparse, parse_qs
    qs = parse_qs(urlparse(url).query)
    assert verify_signed_url(
        qs["path"][0], qs["uid"][0], int(qs["expires"][0]), qs["sig"][0]
    )


def test_rbac_roles_defined():
    assert "admin" in ROLE_PERMISSIONS
    assert "recruiter" in ROLE_PERMISSIONS
    assert "screening:read" in ROLE_PERMISSIONS["recruiter"]


def test_jd_quality_engine():
    from ai.engines.jd_quality import analyze_jd_quality
    result = analyze_jd_quality("Short jd", {})
    assert "overall_score" in result
    assert "grade" in result


def test_compare_ranking_runs_structure():
  import asyncio
  from unittest.mock import AsyncMock, MagicMock, patch

  run_a = MagicMock()
  run_a.id = "a"
  run_a.rankings_snapshot = [
      {"candidate_id": "c1", "candidate_name": "Alice", "rank": 1, "final_score": 0.9},
  ]
  run_b = MagicMock()
  run_b.id = "b"
  run_b.rankings_snapshot = [
      {"candidate_id": "c1", "candidate_name": "Alice", "rank": 2, "final_score": 0.8},
  ]

  async def _run():
      from backend.services import ranking_service
      mock_result = MagicMock()
      mock_result.scalar_one_or_none = MagicMock(side_effect=[run_a, run_b])
      mock_db = AsyncMock()
      mock_db.execute = AsyncMock(return_value=mock_result)
      mock_ctx = AsyncMock()
      mock_ctx.__aenter__ = AsyncMock(return_value=mock_db)
      mock_ctx.__aexit__ = AsyncMock(return_value=None)
      with patch.object(ranking_service, "AsyncSessionLocal", return_value=mock_ctx):
          return await ranking_service.compare_ranking_runs("a", "b")

  result = asyncio.get_event_loop().run_until_complete(_run())
  assert "rank_changes" in result
  assert "summary" in result
