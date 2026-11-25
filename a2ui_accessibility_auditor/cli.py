"""CLI for A2UI Accessibility Auditor."""
import argparse
import json
from .core import A2UIAccessibilityAuditor


def main():
    parser = argparse.ArgumentParser(description="A2UI Accessibility Auditor CLI")
    parser.add_argument("--demo", action="store_true", help="Run sample A2UI accessibility audit")
    args = parser.parse_args()

    auditor = A2UIAccessibilityAuditor()
    sample = [
        {"id": "btn-save", "component": "Button", "props": {"label": "Save", "fg": "#FFFFFF", "bg": "#1E3A8A"}},
        {"id": "hero", "component": "Image", "props": {"alt": "Architecture diagram"}},
    ]
    print(json.dumps(auditor.audit(sample), indent=2))


if __name__ == "__main__":
    main()
