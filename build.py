"""data/*.yaml と templates/ から静的サイトを dist/ に生成する。

    uv run build.py            # dist/ に出力
    uv run build.py -o out     # 出力先を指定
"""

import argparse
import datetime as dt
import shutil
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup

ROOT = Path(__file__).parent
LANGS = ("ja", "en")
CATEGORIES = ("paper", "book", "presentation", "misc")

UI = {
    "ja": {
        "nav_profile": "プロフィール",
        "nav_experience": "経歴",
        "nav_grants": "競争的資金",
        "nav_contributions": "社会貢献",
        "nav_publications": "研究業績",
        "keywords": "研究キーワード",
        "skills": "技術スキル",
        "profile": "プロフィール",
        "experience": "経歴",
        "education": "学歴",
        "grants": "競争的資金",
        "contributions": "社会貢献活動",
        "publications": "研究業績",
        "all": "すべて",
        "cat_paper": "論文",
        "cat_book": "著書",
        "cat_presentation": "講演",
        "cat_misc": "その他",
        "major_only": "主要業績のみ",
        "search": "キーワードで検索…",
        "no_match": "該当する業績はありません。",
        "theme": "表示テーマを切り替え",
        "updated": "最終更新",
        "other_lang": "English",
    },
    "en": {
        "nav_profile": "Profile",
        "nav_experience": "Experience",
        "nav_grants": "Grants",
        "nav_contributions": "Contributions",
        "nav_publications": "Publications",
        "keywords": "Research Keywords",
        "skills": "Technical Skills",
        "profile": "Profile",
        "experience": "Experience",
        "education": "Education",
        "grants": "Grants",
        "contributions": "Social Contributions",
        "publications": "Publications",
        "all": "All",
        "cat_paper": "Paper",
        "cat_book": "Book",
        "cat_presentation": "Talk",
        "cat_misc": "Misc",
        "major_only": "Major only",
        "search": "Search by keyword…",
        "no_match": "No matching publications found.",
        "theme": "Toggle color theme",
        "updated": "Last updated",
        "other_lang": "日本語",
    },
}


def load_yaml(name: str):
    with open(ROOT / "data" / name, encoding="utf-8") as f:
        return yaml.safe_load(f)


def validate(pubs: list[dict]) -> None:
    for i, p in enumerate(pubs):
        where = f"publications[{i}]"
        if p.get("category") not in CATEGORIES:
            raise SystemExit(f"{where}: category は {CATEGORIES} のいずれか: {p.get('category')!r}")
        for key in ("year", "ja", "en"):
            if key not in p:
                raise SystemExit(f"{where}: {key} がありません")


def group_by_year(pubs: list[dict]) -> list[tuple[int, list[dict]]]:
    """ファイル内の順序を保ったまま、年の降順でグループ化する。"""
    groups: dict[int, list[dict]] = {}
    for p in pubs:
        groups.setdefault(int(p["year"]), []).append(p)
    return sorted(groups.items(), key=lambda kv: kv[0], reverse=True)


def build(out: Path) -> None:
    profile = load_yaml("profile.yaml")
    pubs = load_yaml("publications.yaml")["publications"]
    validate(pubs)

    env = Environment(
        loader=FileSystemLoader(ROOT / "templates"),
        autoescape=True,
        undefined=StrictUndefined,
        trim_blocks=True,
        lstrip_blocks=True,
    )
    updated = dt.datetime.now(ZoneInfo("Asia/Tokyo")).date().isoformat()

    if out.exists():
        shutil.rmtree(out)
    shutil.copytree(ROOT / "assets", out / "assets")
    (out / ".nojekyll").touch()

    for lang in LANGS:
        def t(value, _lang=lang):
            """{ja:…, en:…} なら現在の言語の値を、それ以外はそのまま返す。"""
            return value[_lang] if isinstance(value, dict) else value

        def rich(value, _lang=lang):
            """<em> などの HTML を含みうるデータ文字列（信頼済み）を出力する。"""
            return Markup(t(value, _lang))

        page_dir = out if lang == "ja" else out / lang
        page_dir.mkdir(parents=True, exist_ok=True)
        html = env.get_template("index.html.j2").render(
            lang=lang,
            other_lang="en" if lang == "ja" else "ja",
            root="" if lang == "ja" else "../",
            other_href="en/" if lang == "ja" else "../",
            site_url=profile["site_url"],
            p=profile,
            pub_groups=group_by_year(pubs),
            pub_total=len(pubs),
            categories=CATEGORIES,
            ui=UI[lang],
            t=t,
            rich=rich,
            updated=updated,
        )
        (page_dir / "index.html").write_text(html, encoding="utf-8")

    print(f"built {out} ({len(pubs)} publications)")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--out", type=Path, default=ROOT / "dist")
    build(ap.parse_args().out)


if __name__ == "__main__":
    main()
