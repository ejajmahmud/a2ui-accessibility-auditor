"""Tests for A2UI Accessibility Auditor."""
import unittest
from a2ui_accessibility_auditor.core import A2UIAccessibilityAuditor, contrast_ratio


class TestA2UIAccessibilityAuditor(unittest.TestCase):
    def setUp(self):
        self.auditor = A2UIAccessibilityAuditor()

    def test_wcag_contrast_math(self):
        self.assertAlmostEqual(contrast_ratio("#000000", "#FFFFFF"), 21.0, places=1)
        self.assertLess(contrast_ratio("#999999", "#AAAAAA"), 1.5)

    def test_accessible_tree_passes(self):
        res = self.auditor.audit([
            {"id": "b1", "component": "Button", "props": {"label": "Run", "fg": "#FFFFFF", "bg": "#0F172A"}},
            {"id": "img1", "component": "Image", "props": {"alt": "Chart"}},
        ])
        self.assertTrue(res["passed"])
        self.assertEqual(res["score"], 100)

    def test_flags_missing_label_and_low_contrast(self):
        res = self.auditor.audit([
            {"id": "b1", "component": "Button", "props": {"fg": "#CCCCCC", "bg": "#FFFFFF"}},
        ])
        self.assertFalse(res["passed"])
        rules = {f["rule"] for f in res["findings"]}
        self.assertIn("missing-label", rules)
        self.assertIn("wcag-contrast", rules)

    def test_flags_duplicate_node_id(self):
        res = self.auditor.audit([
            {"id": "dup", "component": "Text", "props": {"text": "A"}},
            {"id": "dup", "component": "Text", "props": {"text": "B"}},
        ])
        self.assertFalse(res["passed"])
