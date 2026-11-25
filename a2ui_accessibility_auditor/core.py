"""Core WCAG 2.1 contrast and ARIA compliance auditor for A2UI surfaces."""
from typing import Any, Dict, List


def _hex_to_rgb(hex_color: str) -> tuple:
    h = hex_color.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"Invalid hex color: {hex_color}")
    return tuple(int(h[i:i + 2], 16) / 255.0 for i in (0, 2, 4))


def _linearize(channel: float) -> float:
    return channel / 12.92 if channel <= 0.03928 else ((channel + 0.055) / 1.055) ** 2.4


def relative_luminance(hex_color: str) -> float:
    r, g, b = (_linearize(c) for c in _hex_to_rgb(hex_color))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contrast_ratio(fg: str, bg: str) -> float:
    l1 = relative_luminance(fg)
    l2 = relative_luminance(bg)
    lighter, darker = max(l1, l2), min(l1, l2)
    return (lighter + 0.05) / (darker + 0.05)


class A2UIAccessibilityAuditor:
    """Audits A2UI component lists for WCAG AA contrast, labels, and keyboard focusability."""

    INTERACTIVE_COMPONENTS = {"Button", "TextField", "Select", "Checkbox", "Link"}

    def __init__(self, min_contrast: float = 4.5, pass_score: int = 85):
        self.min_contrast = min_contrast
        self.pass_score = pass_score

    def audit(self, components: List[Dict[str, Any]]) -> Dict[str, Any]:
        findings: List[Dict[str, str]] = []
        seen_ids = set()

        for idx, node in enumerate(components):
            nid = node.get("id", f"node-{idx}")
            comp = node.get("component", "Unknown")
            props = node.get("props", {})

            if nid in seen_ids:
                findings.append({"nodeId": nid, "severity": "error", "rule": "unique-id", "message": "Duplicate node id harms screen-reader focus"})
            seen_ids.add(nid)

            if comp in self.INTERACTIVE_COMPONENTS:
                label = str(props.get("ariaLabel") or props.get("label") or props.get("placeholder") or "").strip()
                if not label:
                    findings.append({"nodeId": nid, "severity": "error", "rule": "missing-label", "message": f"{comp} lacks accessible label or ariaLabel"})
                if props.get("tabIndex", 0) < -1:
                    findings.append({"nodeId": nid, "severity": "warning", "rule": "tab-order", "message": "Negative tabIndex below -1 breaks focus"})

            if comp == "Image" and not str(props.get("alt", "")).strip():
                findings.append({"nodeId": nid, "severity": "error", "rule": "img-alt", "message": "Image component missing alt text"})

            if "fg" in props and "bg" in props:
                ratio = contrast_ratio(props["fg"], props["bg"])
                req = 3.0 if props.get("largeText") else self.min_contrast
                if ratio < req:
                    findings.append({
                        "nodeId": nid,
                        "severity": "error",
                        "rule": "wcag-contrast",
                        "message": f"Contrast {ratio:.2f}:1 below WCAG AA {req}:1",
                    })

        penalty = sum(25 if f["severity"] == "error" else 10 for f in findings)
        score = max(0, 100 - penalty)
        return {
            "passed": score >= self.pass_score and not any(f["severity"] == "error" for f in findings),
            "score": score,
            "checkedNodes": len(components),
            "findings": findings,
        }
