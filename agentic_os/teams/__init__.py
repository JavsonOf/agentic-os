"""Ready-made agent teams: one agent per department, each with five skills.

The skills live as ``SKILL.md`` files in ``teams/skills/`` (original texts written for Agentic OS: agents
here have no shell or file system, so ported Claude Code skills would not work as is). Installing a team
adds its skills to the skill registry and spawns its agent with them; the agent uses the OS default model.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any

from agentic_os.skills import Skill, parse_skill_md

if TYPE_CHECKING:
    from agentic_os.kernel import AgenticOS

SKILLS_DIR = Path(__file__).with_name("skills")

_ANSWER = " Odpowiadaj w języku użytkownika (domyślnie po polsku). Gdy brakuje danych, zapytaj zamiast zgadywać."


@dataclass(frozen=True)
class Team:
    id: str
    label: str
    description: str
    instructions: str
    skills: tuple[str, ...]


TEAMS: tuple[Team, ...] = (
    Team("mala-firma", "🏪 Mała firma", "Przepływy pieniężne, kampanie, podatki, wypłaty i windykacja faktur.",
         "Jesteś asystentem właściciela małej firmy: pilnujesz pieniędzy, terminów i papierów. Liczysz kalkulatorem, "
         "a nie na oko, i nie udzielasz porad podatkowych ani prawnych: przygotowujesz materiały dla księgowej.",
         ("cash-flow-snapshot", "run-campaign", "tax-prep", "plan-payroll", "invoice-chase")),
    Team("social-media", "📱 Social media", "Posty, własny styl pisania, haczyki, scenariusze rolek i profil.",
         "Jesteś ghostwriterem i strategiem social media. Piszesz krótko, konkretnie i stylem użytkownika, "
         "a jego styl i fakty o nim zapamiętujesz. Nie wymyślasz liczb ani historii, których nie podał.",
         ("post-writer", "voice-builder", "hook-generator", "reels-scripting", "profile-optimizer")),
    Team("programista", "💻 Programista", "Uporządkowana praca nad kodem, pamięć projektu, skille, serwery MCP i dokumentacja.",
         "Jesteś doświadczonym programistą. Najpierw rozumiesz problem i planujesz, potem piszesz testy i kod "
         "małymi krokami. Kod podajesz w blokach do skopiowania, bo nie masz dostępu do terminala ani plików. "
         "Nie wymyślasz API: gdy nie znasz aktualnej dokumentacji, mówisz to.",
         ("superpowers", "memory-keeper", "skill-creator", "mcp-builder", "docs-fetcher")),
    Team("projektant", "🎨 Projektant", "System UI/UX, marka, prototypy w HTML, front-end i krytyka designu.",
         "Jesteś projektantem produktu i front-endu z wyczuciem. Dbasz o hierarchię, czytelność, dostępność "
         "(kontrast WCAG AA) i spójność. Prototypy i kod podajesz w blokach do skopiowania.",
         ("ui-ux-pro-max", "brand-guidelines", "web-artifacts", "frontend-design", "taste")),
    Team("marketing", "📣 Marketing", "Copywriting, lead magnety, badanie klientów, konwersja i widoczność w wyszukiwarkach AI.",
         "Jesteś marketerem nastawionym na wyniki. Piszesz językiem korzyści, opierasz się na tym, co mówią "
         "klienci, a liczby liczysz kalkulatorem. Nie wymyślasz statystyk, opinii ani wyników: oznaczasz miejsca do uzupełnienia.",
         ("copywriting", "lead-magnets", "customer-research", "cro", "ai-seo")),
)


def team(team_id: str) -> Team:
    for t in TEAMS:
        if t.id == team_id:
            return t
    raise KeyError(team_id)


def load_skill(name: str) -> Skill:
    path = SKILLS_DIR / f"{name}.md"
    return parse_skill_md(path.read_text(encoding="utf-8"), name)


def install_team(system: AgenticOS, team_id: str) -> dict[str, Any]:
    """Add the team's skills (replacing older versions) and (re)create its agent with them."""
    t = team(team_id)
    for name in t.skills:
        system.skills.add(load_skill(name))
    system.spawn(t.id, t.instructions + _ANSWER, skills=list(t.skills))
    return {"team": t.id, "agent": t.id, "skills": list(t.skills)}


def public(system: AgenticOS) -> list[dict[str, Any]]:
    return [{**asdict(t), "skills": list(t.skills), "installed": t.id in system.agents} for t in TEAMS]


__all__ = ["SKILLS_DIR", "TEAMS", "Team", "install_team", "load_skill", "public", "team"]
