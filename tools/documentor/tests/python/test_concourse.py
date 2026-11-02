"""Concourse distribution integrity and opt-in site installation."""
import hashlib
import json
from pathlib import Path

import pytest
import yaml

from documentor.concourse import FILES, install


def distribution(root):
    package = root / "package/dist"
    package.mkdir(parents=True)
    files = {}
    for name in FILES:
        body = f"sample {name}".encode()
        (package / name).write_bytes(body)
        files[name] = hashlib.sha256(body).hexdigest()
    (package / "manifest.json").write_text(json.dumps({"version": "0.1.0", "files": files}))
    return {"publish": {"site": {"concourse": {"site": "guide", "enabled": True, "package": "package"}}}}


def test_install_is_opt_in(tmp_path):
    install(tmp_path, {}, tmp_path / "site")
    assert not (tmp_path / "site").exists()


def test_verified_install_keeps_existing_host_hook(tmp_path):
    config = distribution(tmp_path)
    site = tmp_path / "site"
    hook = site / "layouts/_partials/custom/footer.html"
    hook.parent.mkdir(parents=True)
    hook.write_text("host footer")
    install(tmp_path, config, site)
    assert hook.read_text() == "host footer"
    assert (site / "static/concourse/concourse.js").read_text() == "sample concourse.js"
    settings = yaml.safe_load((site / "config/_default/concourse.yaml").read_text())
    assert settings["params"]["concourse"] == {"enabled": True, "site": "guide", "api": "/__concourse/"}


def test_integrity_failure_writes_no_partial_assets(tmp_path):
    config = distribution(tmp_path)
    (tmp_path / "package/dist/concourse.css").write_text("tampered")
    with pytest.raises(ValueError, match="integrity mismatch"):
        install(tmp_path, config, tmp_path / "site")
    assert not (tmp_path / "site").exists()


def test_external_api_and_unknown_inventory_refuse(tmp_path):
    config = distribution(tmp_path)
    config["publish"]["site"]["concourse"]["api"] = "https://foreign.example/"
    with pytest.raises(ValueError, match="same-origin"):
        install(tmp_path, config, tmp_path / "site")


def test_direct_template_hook_does_not_create_duplicate_hook(tmp_path):
    config = distribution(tmp_path)
    base = tmp_path / "site/layouts/baseof.html"
    base.parent.mkdir(parents=True)
    base.write_text('{{ partial "concourse.html" . }}')
    install(tmp_path, config, tmp_path / "site")
    assert not (tmp_path / "site/layouts/_partials/custom/footer.html").exists()
