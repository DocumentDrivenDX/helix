"""Regression coverage for design-stage operational projects and scaffold sections."""
from pathlib import Path

import pytest
import yaml

from documentor import cli, detect, generate, schemas, site
from documentor.lib import load_traits, plan


def table(root, name="tasks", target="users"):
    path = root / f"docs/helix/02-design/umf/tables/{name}.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump({"version": "1.0", "table_name": name,
        "primary_key": ["id"], "columns": [{"name": "id", "data_type": "uuid", "nullable": False}],
        "relationships": {"foreign_keys": [{"column": "id", "references_table": target,
                                               "references_column": "id"}]}}, sort_keys=False))
    return path


def test_hextra_links_record_and_generated_sections_idempotently(tmp_path):
    content = tmp_path / "content"
    for directory in ("record", "model"):
        (content / directory).mkdir(parents=True)
    home = content / "_index.md"
    home.write_text('---\nlayout: hextra-home\n---\n{{< cards >}}\n{{< /cards >}}\n')
    (tmp_path / "hugo.yaml").write_text('menu:\n  main:\n    - name: Docs\n      pageRef: /developer/\n')
    config = {"publish": {"site": {"record": True, "sections": [
        {"id": "schema", "title": "Data model", "generated": {"command": "true", "out": "model"}},
        {"id": "absent", "generated": {"command": "true"}}]}}}
    site.link_sections(config, tmp_path)
    first = (home.read_text(), (tmp_path / "hugo.yaml").read_text())
    site.link_sections(config, tmp_path)
    assert first == (home.read_text(), (tmp_path / "hugo.yaml").read_text())
    assert home.read_text().count('link="record/"') == 1
    assert home.read_text().count('link="model/"') == 1
    menu = yaml.safe_load(first[1])["menu"]["main"]
    assert [s["pageRef"] for s in menu] == ["/developer/", "/record/", "/model/"]
    assert "absent" not in first[1]


def test_umf_init_proposes_design_and_operational_profiles(tmp_path):
    table(tmp_path)
    (tmp_path / "docs/helix/vision.md").write_text('# Planned app\n')
    _, block = cli.proposal_text(tmp_path)
    pub = block["publish"]
    assert pub["traits"] == ["umf-tablespec"]
    assert pub["data_mode"] == "operational"
    assert "profile" not in pub
    assert "skip" not in pub  # Only the data audience is selected.
    pages = {p.key: p for p in plan(block, tmp_path)}
    assert "data/lineage" not in pages
    assert "data-architecture" not in str(pages["data/index"].entry)
    assert pages["data/tables"].generator == "umf-tables"


def test_code_and_pipeline_are_not_treated_as_design_only_oltp(tmp_path):
    table(tmp_path)
    (tmp_path / "docs/helix/vision.md").write_text('# App\n')
    (tmp_path / "app.ts").write_text('export const app = 1;')
    (tmp_path / "pipeline.yaml").write_text('name: ingestion\n')
    _, block = cli.proposal_text(tmp_path)
    assert "profile" not in block["publish"]
    assert "data_mode" not in block["publish"]


def test_umf_reference_browser_catalog_and_pipeline_coexistence(tmp_path):
    task = table(tmp_path)
    table(tmp_path, "users", "users")
    body, sources = generate.GENERATORS["umf-tables"](tmp_path, {})
    assert "uuid" in body and "Primary key: ['id']" in body
    assert "| id | users | id |" in body
    assert '```mermaid' in body and 't0 --> t1' in body
    assert task.relative_to(tmp_path).as_posix() in sources
    config = {"publish": {"traits": ["umf-tablespec", "tablespec-pipeline"], "audiences": ["data"]}}
    pages = {p.key: p for p in plan(config, tmp_path)}
    assert pages["data/tables"].work == "generated"
    assert pages["data/pipeline-tables"].tool == "tablespec guidebook"
    entries = schemas.discover(tmp_path, config)
    assert len(entries) == 2
    assert entries[0]["schemaFormat"] == "tablespec"
    assert all((tmp_path / e["path"]).is_file() for e in entries)
    assert entries[0]["sha256"]


def test_duplicate_table_names_fail_instead_of_overwriting(tmp_path):
    source = table(tmp_path)
    (source.parent / "duplicate.yaml").write_bytes(source.read_bytes())
    with pytest.raises(ValueError, match="duplicate UMF table"):
        generate.GENERATORS["umf-tables"](tmp_path, {})


def test_plain_docs_do_not_propose_a_software_profile(tmp_path):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/readme.md").write_text("# Reference material\n")
    _, block = cli.proposal_text(tmp_path)
    assert "profile" not in block["publish"]
    assert "developer" not in block["publish"]["audiences"]


def test_umf_publisher_copies_exact_sources_and_browser_mount(tmp_path, monkeypatch):
    import json

    source = table(tmp_path)
    browser = tmp_path / "browser-package"
    (browser / "assets").mkdir(parents=True)
    for name in ("index.js", "assets/index.html", "LICENSE-MIT", "LICENSE-APACHE",
                 "THIRD_PARTY_NOTICES.md", "provenance.json"):
        (browser / name).write_text("fixture")
    monkeypatch.setattr(schemas, "package", lambda root, config: browser)
    config = {"publish": {"traits": ["umf-tablespec"]}}
    content, static = tmp_path / "content", tmp_path / "static"
    assert schemas.publish(tmp_path, config, content, static) == 0
    catalog = json.loads((static / "schemas/catalog.json").read_text())
    entry = catalog["entries"][0]
    assert entry["schemaFormat"] == "tablespec"
    assert (static / "schemas" / entry["url"]).read_bytes() == source.read_bytes()
    assert "mountSchemaBrowser" in (static / "schemas/mount.js").read_text()
    assert "iframe" in (content / "schemas/_index.md").read_text()
    assert schemas.publish(tmp_path, config, content, static, check=True) == 0


def test_pages_template_has_scoped_deploy_and_valid_build_command():
    from documentor.lib import catalog

    # BaseLoader retains GitHub's `on` key rather than YAML 1.1's boolean key.
    workflow = yaml.load((catalog() / "ci/github-pages.yml").read_text(), Loader=yaml.BaseLoader)
    assert "push" in workflow["on"]
    assert workflow["jobs"]["deploy"]["needs"] == "build"
    assert workflow["jobs"]["deploy"]["permissions"] == {"pages": "write", "id-token": "write"}
    steps = workflow["jobs"]["build"]["steps"]
    build = next(s for s in steps if "documentor build" in s.get("run", ""))
    assert build["run"] == 'uvx --from "$DOCUMENTOR" documentor build --root .'
    assert "HUGO_BASEURL" in build["env"]
    assert "REPLACE_WITH_UMF_RELEASE" in workflow["env"]["DOCUMENTOR"]
    preflight = next(s for s in steps if s.get("name") == "Verify selected documentor release")
    assert "documentor schemas --help" in preflight["run"]


def test_design_only_developer_proposal_has_effective_skips_without_unused_profile(tmp_path):
    path = tmp_path / "docs/helix/01-frame/vision.md"
    path.parent.mkdir(parents=True)
    path.write_text("# Planned software\n")
    _, block = cli.proposal_text(tmp_path)
    assert "profile" not in block["publish"]
    assert block["publish"]["audiences"] == ["developer"]
    assert set(block["publish"]["skip"]) == {"developer/walkthrough", "developer/developer-guide"}
    assert not {"developer/walkthrough", "developer/developer-guide"} & {p.key for p in plan(block, tmp_path)}


def test_local_pipeline_override_without_delegate_does_not_crash_planning(tmp_path):
    traits = tmp_path / ".helix/traits"
    traits.mkdir(parents=True)
    (traits / "tablespec-pipeline.yml").write_text("id: tablespec-pipeline\ntitle: Custom pipeline\n")
    config = {"publish": {"traits_dir": ".helix/traits",
                         "traits": ["umf-tablespec", "tablespec-pipeline"], "audiences": ["data"]}}
    pages = {p.key: p for p in plan(config, tmp_path)}
    assert pages["data/tables"].generator == "umf-tables"
    assert "data/pipeline-tables" not in pages


def test_discovery_ignores_large_non_table_yaml_and_external_symlinks(tmp_path):
    from documentor.umf_tables import tables

    source = table(tmp_path)
    (tmp_path / "pnpm-lock.yaml").write_text("lockfileVersion: 9\n#" + "x" * 4_100_000)
    (tmp_path / "outside.yaml").symlink_to("/etc/passwd")
    assert [path for path, _ in tables(tmp_path)] == [source.relative_to(tmp_path).as_posix()]
    source.write_text(source.read_text() + "\n#" + "x" * 4_100_000)
    with pytest.raises(ValueError, match="UMF table exceeds browser"):
        tables(tmp_path)


@pytest.mark.parametrize("release,tool_status,expected", [
    ("REPLACE_WITH_UMF_RELEASE", 0, 1),
    ("v0.19.1", 2, 2),
    ("qualified-release", 0, 0),
])
def test_pages_preflight_rejects_placeholder_and_tools_without_schema_support(tmp_path, release, tool_status, expected):
    import os
    import subprocess
    from documentor.lib import catalog

    workflow = yaml.load((catalog() / "ci/github-pages.yml").read_text(), Loader=yaml.BaseLoader)
    step = next(s for s in workflow["jobs"]["build"]["steps"]
                if s.get("name") == "Verify selected documentor release")
    tool = tmp_path / "uvx"
    tool.write_text(f"#!/bin/sh\nexit {tool_status}\n")
    tool.chmod(0o755)
    result = subprocess.run(["/bin/sh", "-c", step["run"]], env=dict(os.environ,
        PATH=str(tmp_path) + os.pathsep + os.environ["PATH"], DOCUMENTOR=release), capture_output=True, text=True)
    assert result.returncode == expected
    if release == "REPLACE_WITH_UMF_RELEASE":
        assert "Set DOCUMENTOR to a released tag" in result.stderr


@pytest.mark.parametrize("hextra", [False, True])
def test_umf_and_pipeline_references_survive_site_rendering(tmp_path, hextra):
    table(tmp_path)
    config = {"publish": {"traits": ["umf-tablespec", "tablespec-pipeline"], "audiences": ["data"]}}
    body, _ = generate.GENERATORS["umf-tables"](tmp_path, config)
    page = tmp_path / "docs/guide/data/tables.md"
    page.parent.mkdir(parents=True)
    page.write_text("<!-- helix:publish audience=data page=tables kind=reference generated=umf-tables -->\n" + body)
    output = tmp_path / "website"
    site.emit_hugo(tmp_path, config, output, "guide", hextra)
    content = output / "content/guide/data"
    assert "uuid" in (content / "tables.md").read_text()
    assert "tablespec guidebook" not in (content / "tables.md").read_text()
    assert "tablespec guidebook" in (content / "pipeline-tables.md").read_text()
