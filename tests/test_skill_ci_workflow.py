from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "skill-ci.yml"
VALIDATOR = ROOT / "scripts" / "validate_agent_skills.py"


class SkillCiWorkflowTest(unittest.TestCase):
    def test_workflow_validates_agent_skills_tree(self) -> None:
        workflow = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("'.agents/skills/**'", workflow)
        self.assertNotIn("'.apm/**'", workflow)
        self.assertNotIn(".apm/skills", workflow)
        self.assertNotIn("apm compile --validate", workflow)
        self.assertIn("'tests/**'", workflow)
        self.assertIn(
            "python3 scripts/validate_agent_skills.py .agents/skills",
            workflow,
        )

    def test_validator_accepts_checked_in_skills(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), str(ROOT / ".agents" / "skills")],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_validator_rejects_skill_without_description(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            skills_root = Path(tmp) / "skills"
            skill = skills_root / "broken-skill"
            skill.mkdir(parents=True)
            (skill / "SKILL.md").write_text(
                "---\nname: broken-skill\n---\n\nBody.\n",
                encoding="utf-8",
            )

            result = subprocess.run(
                [sys.executable, str(VALIDATOR), str(skills_root)],
                cwd=ROOT,
                check=False,
                capture_output=True,
                text=True,
            )

        self.assertNotEqual(0, result.returncode, result.stdout + result.stderr)
        self.assertIn(
            "Missing required SKILL.md frontmatter field: description",
            result.stderr,
        )


if __name__ == "__main__":
    unittest.main()
