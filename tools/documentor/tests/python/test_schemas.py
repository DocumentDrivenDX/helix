"""Schema publishing contracts: explicit discovery, provenance, bounds and freshness."""
import hashlib
import json
from pathlib import Path
from unittest.mock import patch

import pytest
import yaml

from documentor import schemas


@pytest.fixture
def project(tmp_path):
    root = tmp_path
    config = {"flows": [{"id": "helix", "root": "docs/helix"}]}
    model = root / "models/customer.json"
    model.parent.mkdir()
    model.write_text('{"umf":"0.10.0","modules":[{"id":"sales","elements":[{"id":"Customer"}]}]}\n')
    page = root / "docs/helix/02-design/customer.md"
    page.parent.mkdir(parents=True)
    ref = {"id": "customer", "version": "1.0.0", "title": "Customer", "path": "models/customer.json",
           "schemaFormat": "umf", "definition": ["sales", "Customer"]}
    page.write_text("---\n" + yaml.safe_dump({"ddx": {"schemas": [ref]}}) + "---\n# Customer\n")
    return root, config, page, ref


def write_ref(page, ref):
    page.write_text("---\n" + yaml.safe_dump({"ddx": {"schemas": [ref]}}) + "---\n# Customer\n")


def browser(root):
    path = root / "browser-package"
    (path / "assets").mkdir(parents=True)
    for name in ("index.js", "assets/index.html", "LICENSE-MIT", "LICENSE-APACHE",
                 "THIRD_PARTY_NOTICES.md", "provenance.json"):
        (path / name).write_text("fixture")
    return path


def test_catalog_preserves_bytes_and_records_all_owners(project):
    root, config, page, ref = project
    other = page.with_name("other.md")
    write_ref(other, ref)
    entries = schemas.discover(root, config)
    assert len(entries) == 1
    assert len(entries[0]["owners"]) == 2
    assert entries[0]["id"] == "customer@1.0.0"
    assert entries[0]["sha256"] == hashlib.sha256((root / ref["path"]).read_bytes()).hexdigest()


@pytest.mark.parametrize("change,match", [
    ({"path": "missing.json"}, "missing JSON/YAML"),
    ({"path": "../escape.json"}, "inside the repository"),
    ({"schemaFormat": "pretend"}, "unsupported schemaFormat"),
    ({"definition": ["sales", "Absent"]}, "does not exist"),
    ({"definition": "Customer"}, "moduleId"),
    ({"version": 1}, "nonempty string version"),
])
def test_invalid_reference_fails_before_publication(project, change, match):
    root, config, page, ref = project
    write_ref(page, ref | change)
    with pytest.raises(ValueError, match=match):
        schemas.discover(root, config)


def test_symlink_cannot_escape_repository(project, tmp_path):
    root, config, page, ref = project
    (root / "models/escape.json").symlink_to("/etc/passwd")
    write_ref(page, ref | {"path": "models/escape.json"})
    with pytest.raises(ValueError, match="inside the repository"):
        schemas.discover(root, config)


def test_conflicting_identity_fails_but_versions_can_coexist(project):
    root, config, page, ref = project
    other = page.with_name("other.md")
    write_ref(other, ref | {"title": "Different"})
    with pytest.raises(ValueError, match="conflicting schema identity"):
        schemas.discover(root, config)
    write_ref(other, ref | {"version": "2.0.0", "title": "Different"})
    assert len(schemas.discover(root, config)) == 2


def test_relative_link_keeps_schema_and_definition_under_mount_prefix(project):
    root, _, page, _ = project
    text = schemas.links(page, root, "/artifacts/contracts/customer/")
    assert '../../../schemas/explorer.html#schema=customer%401.0.0&amp;definition=%5B%22sales%22%2C%22Customer%22%5D' in text


def test_publish_check_detects_source_catalog_asset_and_inventory_drift(project):
    root, config, page, ref = project
    content, static = root / "content", root / "static"
    pkg = browser(root)
    with patch.object(schemas, "package", return_value=pkg):
        schemas.publish(root, config, content, static)
        manifest = (static / "schemas/manifest.json").read_bytes()
        catalog = json.loads((static / "schemas/catalog.json").read_text())
        assert catalog["entries"][0]["schemaFormat"] == "umf"
        assert "owners" not in catalog["entries"][0]
        source = static / "schemas" / catalog["entries"][0]["url"]
        assert source.read_bytes() == (root / ref["path"]).read_bytes()
        schemas.publish(root, config, content, static, check=True)
        schemas.publish(root, config, content, static)
        assert manifest == (static / "schemas/manifest.json").read_bytes()
        for path in (static / "schemas/catalog.json", static / "schemas/browser/index.js",
                     content / "schemas/_index.md"):
            previous = path.read_bytes() if path.exists() else None
            path.write_text("stale")
            with pytest.raises(ValueError, match="stale schema publication"):
                schemas.publish(root, config, content, static, check=True)
            path.write_bytes(previous) if previous is not None else path.unlink()
        (root / ref["path"]).write_text((root / ref["path"]).read_text() + " ")
        with pytest.raises(ValueError, match="stale schema publication"):
            schemas.publish(root, config, content, static, check=True)


def test_last_reference_retirement_removes_old_public_schemas(project):
    root, config, page, _ = project
    content, static = root / "content", root / "static"
    with patch.object(schemas, "package", return_value=browser(root)):
        schemas.publish(root, config, content, static)
    page.unlink()
    with pytest.raises(ValueError, match="stale schema publication"):
        schemas.publish(root, config, content, static, check=True)
    schemas.publish(root, config, content, static)
    assert not (static / "schemas").exists()
    assert not (content / "schemas/_index.md").exists()


def test_no_refs_need_no_browser(project):
    root, config, page, _ = project
    page.unlink()
    with patch.object(schemas, "package", side_effect=AssertionError("not needed")):
        schemas.publish(root, config, root / "content", root / "static")


def test_browser_package_pin_and_integrity(project):
    root, config, _, _ = project
    with pytest.raises(ValueError, match="install it"):
        schemas.package(root, config)
    pkg = browser(root)
    config["publish"] = {"schemas": {"browser_package": "browser-package"}}
    meta = {"name": "@documentdrivendx/umf-schema-browser", "version": "wrong"}
    (pkg / "package.json").write_text(json.dumps(meta))
    with pytest.raises(ValueError, match="must be"):
        schemas.package(root, config)
    meta["version"] = schemas.BROWSER_VERSION
    (pkg / "package.json").write_text(json.dumps(meta))
    (pkg / "release-manifest.json").write_text(json.dumps({"version": 1, "sha256": {"index.js": "bad"}}))
    with pytest.raises(ValueError, match="integrity mismatch"):
        schemas.package(root, config)


@pytest.mark.parametrize("target", ["hugo", "static"])
def test_site_build_automatically_publishes_catalog_and_design_link(project, target):
    from documentor import site

    root, config, _, _ = project
    config["publish"] = {"site": {"target": target, "site_dir": "website", "record": True}}
    (root / ".helix.yml").write_text(yaml.safe_dump(config))
    output = root / "website"
    if target == "hugo":
        output.mkdir()
        (output / "hugo.yaml").write_text("baseURL: https://example.org/helix/\n")
    with patch.object(schemas, "package", return_value=browser(root)):
        assert site.build(root, output, False, "https://example.org/helix/") == 0
    assert (output / "static/schemas/catalog.json").is_file()
    assert (output / "content/schemas/_index.md").is_file()
    design = (output / "content/record/customer.md").read_text()
    assert "../../schemas/explorer.html#schema=customer%401.0.0" in design


@pytest.mark.parametrize("existing", ["assets", "index"])
def test_publisher_refuses_unowned_output_without_modifying_it(project, existing):
    root, config, _, _ = project
    content, static = root / "content", root / "static"
    path = static / "schemas/customer.json" if existing == "assets" else content / "schemas/_index.md"
    path.parent.mkdir(parents=True)
    path.write_text("project-owned")
    with patch.object(schemas, "package", return_value=browser(root)):
        with pytest.raises(ValueError, match="unowned schema"):
            schemas.publish(root, config, content, static)
    assert path.read_text() == "project-owned"
    assert not (static / "schemas/manifest.json").exists()


def test_no_references_leave_unowned_files_and_index_alone(project):
    root, config, page, _ = project
    page.unlink()
    content, static = root / "content", root / "static"
    for path in (content / "schemas/_index.md", static / "schemas/manifest.json", static / "schemas/mine.json"):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("mine")
    schemas.publish(root, config, content, static)
    schemas.publish(root, config, content, static, check=True)
    assert all(p.read_text() == "mine" for p in (content / "schemas/_index.md", static / "schemas/manifest.json", static / "schemas/mine.json"))


def test_owned_updates_and_retirement_preserve_additional_site_files(project):
    root, config, page, ref = project
    content, static = root / "content", root / "static"
    with patch.object(schemas, "package", return_value=browser(root)):
        schemas.publish(root, config, content, static)
        custom = static / "schemas/custom.json"
        custom.write_text("project-owned")
        write_ref(page, ref | {"title": "Updated"})
        schemas.publish(root, config, content, static)
        schemas.publish(root, config, content, static, check=True)
        assert custom.read_text() == "project-owned"
        page.unlink()
        schemas.publish(root, config, content, static)
        assert custom.read_text() == "project-owned"
        assert not (static / "schemas/manifest.json").exists()
        assert not (content / "schemas/_index.md").exists()


def test_legacy_inventory_is_migrated_and_new_asset_collisions_are_refused(project):
    root, config, _, _ = project
    content, static = root / "content", root / "static"
    pkg = browser(root)
    with patch.object(schemas, "package", return_value=pkg):
        schemas.publish(root, config, content, static)
        path = static / "schemas/manifest.json"
        legacy = json.loads(path.read_text())
        del legacy["generator"]
        path.write_text(json.dumps(legacy))
        index = content / "schemas/_index.md"
        index.write_text(index.read_text().replace(schemas.INDEX_MARKER + "\n\n", ""))
        legacy["indexSha256"] = hashlib.sha256(index.read_bytes()).hexdigest()
        path.write_text(json.dumps(legacy))
        schemas.publish(root, config, content, static)
        assert json.loads(path.read_text())["generator"] == schemas.OWNER
        (pkg / "assets/extra.js").write_text("new generated asset")
        collision = static / "schemas/browser/assets/extra.js"
        collision.write_text("project asset")
        with pytest.raises(ValueError, match="unowned schema file"):
            schemas.publish(root, config, content, static)
        assert collision.read_text() == "project asset"


def test_retirement_refuses_modified_generated_files(project):
    root, config, page, _ = project
    content, static = root / "content", root / "static"
    with patch.object(schemas, "package", return_value=browser(root)):
        schemas.publish(root, config, content, static)
    custom = static / "schemas/browser/index.js"
    custom.write_text("hand edited")
    page.unlink()
    with pytest.raises(ValueError, match="refusing to delete modified"):
        schemas.publish(root, config, content, static)
    assert custom.read_text() == "hand edited"


def test_guide_only_schema_reference_is_published(project):
    root, config, page, ref = project
    guide = root / "docs/guide/developer/reference.md"
    guide.parent.mkdir(parents=True)
    write_ref(guide, ref)
    page.unlink()
    entries = schemas.discover(root, config)
    assert entries[0]["owners"] == ["docs/guide/developer/reference.md"]
    content, static = root / "content", root / "static"
    with patch.object(schemas, "package", return_value=browser(root)):
        schemas.publish(root, config, content, static)
        schemas.publish(root, config, content, static, check=True)
    assert json.loads((static / "schemas/catalog.json").read_text())["entries"][0]["id"] == "customer@1.0.0"


@pytest.mark.parametrize("target", ["static", "hextra"])
def test_schema_cli_uses_selected_target_despite_unrelated_hugo_site(project, target):
    from documentor import site

    root, config, _, _ = project
    config["publish"] = {"site": {"target": target}}
    (root / "docs/hugo.toml").write_text('baseURL = "https://unrelated.example/"\n')
    (root / ".helix.yml").write_text(yaml.safe_dump(config))
    with patch.object(schemas, "package", return_value=browser(root)):
        assert schemas.main(["--root", str(root)]) == 0
        assert schemas.main(["--root", str(root), "--check"]) == 0
    content, static = site.schema_output_dirs(root, config)
    assert (content / "schemas/_index.md").is_file()
    assert (static / "schemas/catalog.json").is_file()
    assert not (root / "docs/static").exists()


@pytest.mark.parametrize("target", ["hugo", "static", "hextra"])
@pytest.mark.parametrize("bad", ["reference", "frontmatter", "schema"])
def test_site_returns_actionable_errors_instead_of_traceback(project, target, bad, capsys):
    from documentor import site

    root, config, page, ref = project
    output = root / "website"
    output.mkdir()
    (output / "hugo.yaml").write_text("baseURL: https://example.org/\n")
    config["publish"] = {"site": {"target": target, "site_dir": "website", "record": True}}
    (root / ".helix.yml").write_text(yaml.safe_dump(config))
    if bad == "reference":
        write_ref(page, ref | {"path": "missing.json"})
    elif bad == "frontmatter":
        page.write_text("---\nddx: [unterminated\n---\n# Invalid\n")
    else:
        (root / ref["path"]).write_text("{invalid-json")
    assert site.build(root, output, False, None) == 1
    error = capsys.readouterr().err
    assert "documentor site:" in error and "customer.md" in error
    assert "Traceback" not in error


def test_record_cli_reports_schema_errors(project, capsys):
    from documentor import record

    root, config, page, _ = project
    (root / ".helix.yml").write_text(yaml.safe_dump(config))
    page.write_text("---\nddx: [unterminated\n---\n# Invalid\n")
    assert record.main(["--root", str(root)]) == 1
    assert "invalid schema-reference frontmatter" in capsys.readouterr().err


def test_generated_asset_symlinks_cannot_overwrite_unrelated_files(project):
    root, config, _, _ = project
    content, static = root / "content", root / "static"
    with patch.object(schemas, "package", return_value=browser(root)):
        schemas.publish(root, config, content, static)
        custom = static / "schemas/custom.txt"
        custom.write_text("mine")
        asset = static / "schemas/browser/index.js"
        asset.unlink()
        asset.symlink_to(custom)
        with pytest.raises(ValueError, match="symlinked schema output"):
            schemas.publish(root, config, content, static)
        assert custom.read_text() == "mine"


def test_guide_reference_discovery_honors_custom_output_directory(project):
    root, config, page, ref = project
    guide = root / ".guide/developer/model.md"
    guide.parent.mkdir(parents=True)
    write_ref(guide, ref)
    page.unlink()
    config["publish"] = {"out": ".guide", "audiences": ["developer"]}
    assert schemas.discover(root, config)[0]["owners"] == [".guide/developer/model.md"]
