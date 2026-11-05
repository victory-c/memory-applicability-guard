"""Include the canonical skill helper in built distributions."""
from pathlib import Path
from setuptools import setup
from setuptools.command.build_py import build_py

class BuildPy(build_py):
    def run(self):
        super().run()
        target = Path(self.build_lib) / "memory_applicability_guard"
        target.mkdir(parents=True, exist_ok=True)
        self.copy_file("memory-applicability-guard/scripts/guard_decision.py", str(target / "_helper.py"))

setup(cmdclass={"build_py": BuildPy})
