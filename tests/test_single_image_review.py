import csv
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PIL import Image
from streamlit.testing.v1 import AppTest

from image_rating_app import storage
from image_rating_app.constants import (
    OPTION_SINGLE_IMAGE_REVIEW_LABEL,
    SINGLE_IMAGE_REVIEW_CHOICES,
    TEST_OPTION_SINGLE_IMAGE_REVIEW,
)


class SingleImageReviewTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.image_dir = Path(temporary.name) / "images"
        self.output_dir = Path(temporary.name) / "output"
        for folder in ("Awe", "Craving"):
            destination = self.image_dir / folder
            destination.mkdir(parents=True)
            for i in range(3):
                Image.new("RGB", (40, 30), (50 * i, 100, 80)).save(destination / f"sample_{i}.png")
        self.originals = {path: path.read_bytes() for path in self.image_dir.rglob("*.png")}
        for name, value in (("IMAGE_DIR", self.image_dir), ("OUTPUT_DIR", self.output_dir)):
            item = patch.object(storage, name, value)
            item.start()
            self.addCleanup(item.stop)
        self.app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
        self.app.run(timeout=20)
        self.app.text_input(key="draft_name").set_value("Single image test")
        self.app.selectbox(key="draft_image_folder").set_value("Awe")
        self.app.radio(key="draft_option").set_value(OPTION_SINGLE_IMAGE_REVIEW_LABEL).run()
        next(button for button in self.app.button if button.label == "Start").click().run()
        self.assertFalse(self.app.exception)

    def choose(self, index, choice):
        self.app.button(key=f"single_image_review_{index}_{choice}").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.session_state["current_index"], index + 1)

    def finish(self, at_end=False):
        self.app.button(key="finish_all_btn" if at_end else "finish_btn").click().run()
        self.app.button(key="confirm_finish_dialog").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.session_state["phase"], "finished")
        path = Path(self.app.session_state["saved_csv_path"])
        self.assertTrue(path.name.startswith("results_single_image_review_"))
        with path.open(encoding="utf-8-sig", newline="") as file:
            reader = csv.DictReader(file)
            self.assertEqual(reader.fieldnames, ["name", "test_option", "image_name", "image_path", "rating"])
            return list(reader)

    def test_all_choices_advance_and_export_with_folder_filter(self):
        self.assertEqual(self.app.session_state["test_option"], TEST_OPTION_SINGLE_IMAGE_REVIEW)
        self.assertEqual(len(self.app.session_state["images"]), 3)
        self.assertTrue(self.app.button(key="previous_btn").disabled)
        for index, (choice, label) in enumerate(SINGLE_IMAGE_REVIEW_CHOICES):
            self.choose(index, choice)
        rows = self.finish(at_end=True)
        self.assertEqual([row["rating"] for row in rows], [label for _, label in SINGLE_IMAGE_REVIEW_CHOICES])
        self.assertTrue(all(row["image_path"].startswith("Awe/") for row in rows))
        self.assertEqual({path: path.read_bytes() for path in self.originals}, self.originals)

    def test_previous_shows_saved_choice_and_replaces_it_before_early_finish(self):
        self.choose(0, "great")
        self.app.button(key="previous_btn").click().run()
        self.assertEqual(self.app.session_state["current_index"], 0)
        self.assertTrue(any(caption.value == "Saved rating: Great!" for caption in self.app.caption))
        self.assertEqual(self.app.button(key="single_image_review_0_great").proto.type, "primary")
        self.choose(0, "improve")
        self.choose(1, "delete")
        rows = self.finish()
        self.assertEqual(len(rows), 2)
        self.assertEqual([row["rating"] for row in rows], ["Good concept but needs improvement", "Delete"])

    def test_can_revise_the_last_image_after_reaching_the_end(self):
        for index in range(3):
            self.choose(index, "great")
        self.app.button(key="previous_btn").click().run()
        self.assertEqual(self.app.session_state["current_index"], 2)
        self.choose(2, "improve")
        rows = self.finish(at_end=True)
        self.assertEqual(rows[-1]["rating"], "Good concept but needs improvement")
        self.assertEqual(len(rows), 3)

    def test_finish_dialog_blocks_choices_and_cancel_preserves_progress(self):
        self.choose(0, "great")
        self.app.button(key="finish_btn").click().run()
        for choice, _ in SINGLE_IMAGE_REVIEW_CHOICES:
            self.assertTrue(self.app.button(key=f"single_image_review_1_{choice}").disabled)
        self.assertTrue(self.app.button(key="previous_btn").disabled)
        self.app.button(key="cancel_finish_dialog").click().run()
        self.assertEqual(len(self.app.session_state["ratings"]), 1)
        self.assertEqual(self.app.session_state["current_index"], 1)
        self.assertFalse(self.app.button(key="single_image_review_1_great").disabled)
        self.assertEqual(list(self.output_dir.glob("*.csv")), [])

    def test_finish_before_rating_exports_headers_only(self):
        self.assertEqual(self.finish(), [])


class SingleImageReviewExportTests(unittest.TestCase):
    def test_duplicate_names_in_different_folders_keep_distinct_ratings(self):
        state = SimpleNamespace(
            name="Test", test_option=TEST_OPTION_SINGLE_IMAGE_REVIEW,
            selected_emotions=[],
            images=["new_images/Awe/same.png", "new_images/Craving/same.png", "new_images/Craving/unseen.png"],
            ratings={"Awe/same.png": {"rating": "Great!"}, "Craving/same.png": {"rating": "Delete"}},
            get=lambda key, default=None: default,
        )
        with patch.object(storage, "st", SimpleNamespace(session_state=state)):
            result = storage.build_results_dataframe()
        self.assertEqual(result.image_name.tolist(), ["same.png", "same.png"])
        self.assertEqual(result.image_path.tolist(), ["Awe/same.png", "Craving/same.png"])
        self.assertEqual(result.rating.tolist(), ["Great!", "Delete"])


if __name__ == "__main__":
    unittest.main()
