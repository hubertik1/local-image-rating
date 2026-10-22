import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from PIL import Image
from streamlit.testing.v1 import AppTest

from image_rating_app import folder_browser, storage


class FolderBrowserTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.default = self.root / "default"
        self.external = self.root / "External images with spaces"
        self.empty = self.root / "empty"
        self.empty.mkdir()
        self.output = self.root / "output"
        self.default.mkdir()
        Image.new("RGB", (30, 20)).save(self.default / "default.png")
        for category, count in (("Awe", 4), ("Craving", 2)):
            destination = self.external / category
            destination.mkdir(parents=True)
            for index in range(1, count + 1):
                Image.new("RGB", (30, 20), (index * 40, 80, 90)).save(destination / f"sample_{index}.png")
        for name, value in (("IMAGE_DIR", self.default), ("OUTPUT_DIR", self.output)):
            item = patch.object(storage, name, value)
            item.start()
            self.addCleanup(item.stop)
        self.app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
        self.app.run(timeout=20)

    def open_browser(self):
        self.app.button(key="browse_computer").click().run()
        self.assertFalse(self.app.exception)

    def browse_to(self, path):
        self.app.text_input(key="folder_browser_address").set_value(str(path)).run()
        self.assertFalse(self.app.exception)

    def select_external(self):
        self.open_browser()
        self.browse_to(self.external)
        self.app.button(key="folder_browser_use").click().run()
        self.assertFalse(self.app.exception)

    def start(self, mode="Single-image review"):
        self.app.text_input(key="draft_name").set_value("External folder test")
        self.app.radio(key="draft_option").set_value(mode).run()
        next(button for button in self.app.button if button.label == "Start").click().run()
        self.assertFalse(self.app.exception)

    def test_browse_subfolders_parent_and_cancel_keep_source(self):
        self.open_browser()
        self.browse_to(self.external)
        self.app.selectbox(key="folder_browser_child").set_value("Awe").run()
        self.app.button(key="folder_browser_open").click().run()
        self.assertEqual(Path(self.app.session_state["folder_browser_current"]), self.external / "Awe")
        self.app.button(key="folder_browser_up").click().run()
        self.assertEqual(Path(self.app.session_state["folder_browser_current"]), self.external)
        self.app.button(key="folder_browser_cancel").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.session_state["source_image_root"], "")
        self.assertFalse(self.app.session_state["folder_browser_visible"])

    def test_external_category_review_exports_relative_paths(self):
        self.select_external()
        self.app.selectbox(key="draft_image_folder").set_value("Craving").run()
        self.start()
        self.assertEqual(len(self.app.session_state["images"]), 2)
        self.assertEqual(Path(self.app.session_state["image_root"]), self.external)
        self.app.button(key="single_image_review_0_great").click().run()
        self.app.button(key="finish_btn").click().run()
        self.app.button(key="confirm_finish_dialog").click().run()
        self.assertFalse(self.app.exception)
        with Path(self.app.session_state["saved_csv_path"]).open(encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["image_path"], "Craving/sample_1.png")
        next(button for button in self.app.button if button.label == "New session").click().run()
        self.assertEqual(Path(self.app.session_state["source_image_root"]), self.external)
        self.assertEqual(len(self.app.selectbox(key="draft_image_folder").options), 3)

    def test_external_best_of_three_keeps_categories_separate(self):
        self.select_external()
        self.start("Choose the best of 3")
        groups = self.app.session_state["image_groups"]
        self.assertEqual([len(group) for group in groups], [3, 1, 2])
        self.assertTrue(all(len({Path(path).parent for path in group}) == 1 for group in groups))
        self.assertTrue(any(caption.value == "Folder: Awe" for caption in self.app.caption))

    def test_external_triplets_keep_distinct_folder_keys(self):
        self.select_external()
        self.start("3-image quality rating")
        self.assertEqual(len(self.app.session_state["image_groups"]), 2)
        self.assertEqual([len(group) for group in self.app.session_state["image_groups"]], [3, 2])

    def test_default_folder_can_be_restored(self):
        self.select_external()
        self.app.button(key="use_default_folder").click().run()
        self.assertEqual(self.app.session_state["source_image_root"], "")
        self.assertTrue(any(caption.value == "1 images available" for caption in self.app.caption))

    def test_invalid_path_does_not_create_folder_or_allow_selection(self):
        self.open_browser()
        missing = self.root / "missing"
        self.browse_to(missing)
        self.assertTrue(self.app.error)
        self.assertTrue(self.app.button(key="folder_browser_use").disabled)
        self.assertFalse(missing.exists())
        self.browse_to(self.external)
        self.assertFalse(self.app.error)
        self.assertFalse(self.app.button(key="folder_browser_use").disabled)

    def test_empty_source_disables_start(self):
        self.open_browser()
        self.browse_to(self.empty)
        self.app.button(key="folder_browser_use").click().run()
        self.assertTrue(next(button for button in self.app.button if button.label == "Start").disabled)
        self.assertTrue(self.app.warning)

    def test_changing_setup_source_preserves_active_session_keys(self):
        self.select_external()
        self.start()
        self.app.button(key="single_image_review_0_great").click().run()
        self.app.button(key="back_to_setup_btn").click().run()
        self.app.button(key="use_default_folder").click().run()
        self.assertEqual(Path(self.app.session_state["image_root"]), self.external)
        self.assertIn("Awe/sample_1.png", self.app.session_state["ratings"])
        self.assertEqual(self.app.session_state["source_image_root"], "")

    def test_permission_error_is_reported_without_starting(self):
        with patch.object(storage.os, "walk", side_effect=PermissionError("Access denied")):
            self.app.run()
        self.assertTrue(any("Access denied" in error.value for error in self.app.error))
        self.assertTrue(next(button for button in self.app.button if button.label == "Start").disabled)

    def test_path_validation_rejects_files_and_accepts_quoted_folders(self):
        self.assertEqual(folder_browser.validate_folder(f'"{self.external}"'), self.external)
        with self.assertRaises(NotADirectoryError):
            folder_browser.validate_folder(str(self.default / "default.png"))


if __name__ == "__main__":
    unittest.main()
