"""The project's theme comes from ux-builder tokens: one mapping to every renderer's roles."""
import json
from pathlib import Path
import tempfile
import unittest

from documentor import theme
from documentor.architecture import model as am


def tokens(root: Path) -> Path:
    """A local @ux-builder/tokens build: one theme, `brandy`, light and dark, with a logomark."""
    dist = root / "tokens"
    (dist / "resolved").mkdir(parents=True)
    (dist / "themes").mkdir()
    (dist / "fonts").mkdir()
    (dist / "brand" / "brandy").mkdir(parents=True)
    (dist / "manifest.json").write_text(json.dumps({"themes": [
        {"name": "brandy", "brand": "brandy", "default": "light", "appearances": ["dark", "light"]}]}))
    for appearance, ground, accent in (("light", "#FFFFFF", "#C4463F"), ("dark", "#1A1414", "#F2A69E")):
        (dist / "resolved" / f"brandy.{appearance}.json").write_text(json.dumps({"tokens": {
            "piq-color-ground": ground, "piq-color-accent": accent, "piq-color-text": "#312A29",
            "piq-color-surface-sunken": "#F7F6F7", "piq-font-body": "Quicksand, sans-serif"}}))
    (dist / "themes" / "brandy.css").write_text('[data-theme="brandy"]{--piq-color-accent:#C4463F}')
    (dist / "fonts" / "brandy.css").write_text('@font-face{src:url("./quicksand.woff2")}')
    (dist / "fonts" / "quicksand.woff2").write_bytes(b"font")
    (dist / "brand" / "brandy" / "mark.svg").write_text("<svg/>")
    return dist


def config(**settings) -> dict:
    return {"publish": {"theme": {"tokens": "tokens", **settings}}}


class ThemeTests(unittest.TestCase):
    def test_a_named_theme_maps_its_tokens_onto_the_drawing_roles(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tokens(root)
            chosen = theme.load(root, config(name="brandy"))
            self.assertEqual((chosen.name, chosen.appearances), ("brandy", ("dark", "light")))
            self.assertEqual(chosen.roles["accent"], "#C4463F")
            self.assertEqual(chosen.roles["sunken"], "#F7F6F7")
            self.assertEqual(chosen.roles["font"], "Quicksand, sans-serif")
            self.assertEqual(chosen.dark["ground"], "#1A1414")
            roles = theme.drawing_roles(chosen)
            self.assertEqual((roles["accent"], roles["accent_name"]), ("#C4463F", "red"))
            self.assertEqual(theme.drawing_roles(theme.load(root, config(name="brandy", appearance="dark")))["accent"], "#F2A69E")

    def test_an_unknown_theme_or_none_falls_back_to_the_packaged_plain_theme(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tokens(root)
            self.assertEqual(theme.load(root, config(name="nonesuch")).name, "plain")
            fallback = theme.load(root, {})
            self.assertEqual((fallback.name, fallback.dist), ("plain", theme.packaged()))
            self.assertIn("accent", fallback.roles)
            self.assertFalse(theme.declared({}))
            self.assertTrue(theme.declared(config(name="brandy")))

    def test_a_site_gets_the_css_its_fonts_and_the_brand_with_relative_urls_intact(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tokens(root)
            assets = theme.copy_assets(theme.load(root, config(name="brandy")), root / "site")
            self.assertEqual(assets["css"], ["themes/brandy.css", "fonts/brandy.css"])
            self.assertEqual(assets["favicon"], "brand/brandy/mark.svg")
            self.assertTrue((root / "site" / "fonts" / "quicksand.woff2").is_file())

    def test_a_deck_takes_the_colors_and_keeps_its_portable_typefaces(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tokens(root)
            base = {"typography": {"body": {"family": "Arial"}}, "palette": {"primary": "#3B6BA8", "secondary": "#C44B2F"}}
            merged = theme.deck_theme(theme.load(root, config(name="brandy")), base)
            self.assertEqual(merged["palette"]["primary"], "#C4463F")
            self.assertEqual(merged["palette"]["secondary"], "#C44B2F")
            self.assertEqual(merged["palette"]["dark"]["primary"], "#F2A69E")
            self.assertEqual(merged["typography"], base["typography"])

    def test_a_model_draws_in_the_project_theme_under_its_own_overrides(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            tokens(root)
            (root / ".helix.yml").write_text(
                "flows:\n  - id: helix\n    root: docs/helix/\npublish:\n  theme: {name: brandy, tokens: tokens}\n")
            path = root / "docs/helix/02-design/architecture-model.toml"
            path.parent.mkdir(parents=True)
            path.write_text('[system]\nid = "s"\nname = "S"\n[theme]\nground = "#000000"\n')
            drawn = am.load(path).theme
            self.assertEqual((drawn["accent"], drawn["ground"], drawn["id"]), ("#C4463F", "#000000", "brandy"))
            self.assertEqual(drawn["limited"], am.DEFAULT_THEME["limited"], "a role the theme lacks keeps its default")

    def test_color_names(self):
        self.assertEqual([theme.color_name(c) for c in ("#2F6F8F", "#2E8B57", "#FFFFFF", "#888888")],
                         ["blue", "green", "white", "gray"])


if __name__ == "__main__":
    unittest.main()
