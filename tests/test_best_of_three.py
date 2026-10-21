import csv
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import patch

from PIL import Image
from streamlit.testing.v1 import AppTest

from image_rating_app import storage
from image_rating_app.constants import TEST_OPTION_BEST_OF_THREE


class BestOfThreeExportTests(unittest.TestCase):
    def setUp(self):
        self.images = [Path("new_images") / f"image_{i}.png" for i in range(7)]
        self.groups = [self.images[:3], self.images[3:6], self.images[6:]]
        self.state = SimpleNamespace(
            name="Test", test_option=TEST_OPTION_BEST_OF_THREE,
            selected_emotions=[], images=[str(p) for p in self.images],
            ratings={}, get=lambda key, default=None: self.groups if key == "image_groups" else default,
        )
        self.mock_st = patch.object(storage, "st", SimpleNamespace(session_state=self.state))
        self.mock_st.start()
        self.addCleanup(self.mock_st.stop)

    def choose(self, group_index, image_index):
        image = self.groups[group_index][image_index]
        self.state.ratings[storage.get_selection_group_key(group_index)] = {
            "image_key": storage.get_image_key(image), "image_name": image.name,
        }

    def test_early_finish_omits_unreviewed_sets(self):
        self.choose(0, 1)
        result = storage.build_results_dataframe()
        self.assertEqual(result.image_name.tolist(), [p.name for p in self.groups[0]])
        self.assertEqual(result.selected.tolist(), [0, 1, 0])

    def test_zero_choices_exports_headers_without_false_rejections(self):
        result = storage.build_results_dataframe()
        self.assertTrue(result.empty)
        self.assertEqual(list(result.columns), ["name", "test_option", "image_name", "selected"])

    def test_completed_session_includes_last_one_image_set(self):
        self.choose(0, 0)
        self.choose(1, 2)
        self.choose(2, 0)
        result = storage.build_results_dataframe()
        self.assertEqual(result.image_name.tolist(), [p.name for p in self.images])
        self.assertEqual(result.selected.tolist(), [1, 0, 0, 0, 0, 1, 1])

    def test_revised_choice_replaces_previous_selection(self):
        self.choose(0, 0)
        self.choose(0, 2)
        self.assertEqual(storage.build_results_dataframe().selected.tolist(), [0, 0, 1])

    def test_only_actually_reviewed_sets_export_after_navigation(self):
        self.choose(2, 0)
        result = storage.build_results_dataframe()
        self.assertEqual(result.image_name.tolist(), [self.images[-1].name])
        self.assertEqual(result.selected.tolist(), [1])


class BestOfThreeFinishTests(unittest.TestCase):
    def setUp(self):
        self.temporary = TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.image_dir = self.root / "images"
        self.output_dir = self.root / "output"
        self.image_dir.mkdir()
        for index in range(7):
            Image.new("RGB", (30, 20), (index * 30, 40, 80)).save(self.image_dir / f"sample_{index}.png")
        self.patches = [
            patch.object(storage, "IMAGE_DIR", self.image_dir),
            patch.object(storage, "OUTPUT_DIR", self.output_dir),
        ]
        for item in self.patches:
            item.start()
            self.addCleanup(item.stop)
        self.app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
        self.app.run(timeout=20)
        self.app.text_input(key="draft_name").set_value("Finish test")
        self.app.radio(key="draft_option").set_value("Choose the best of 3").run()
        next(button for button in self.app.button if button.label == "Start").click().run()
        self.assertFalse(self.app.exception)

    def test_finish_saves_completed_choice_and_cancel_keeps_session(self):
        selected_name = Path(self.app.session_state["image_groups"][0][1]).name
        self.app.button(key="best_of_three_choice_0_1").click().run()
        self.assertEqual(self.app.session_state["current_index"], 1)
        self.app.button(key="finish_btn").click().run()
        self.assertFalse(self.app.exception)
        self.assertTrue(self.app.button(key="best_of_three_choice_1_0").disabled)
        self.app.button(key="cancel_finish_dialog").click().run()
        self.assertEqual(self.app.session_state["phase"], "rating")
        self.assertEqual(len(self.app.session_state["ratings"]), 1)
        self.assertEqual(list(self.output_dir.glob("*.csv")), [])
        self.app.button(key="finish_btn").click().run()
        self.app.button(key="confirm_finish_dialog").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.session_state["phase"], "finished")
        with Path(self.app.session_state["saved_csv_path"]).open(encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))
        self.assertEqual(len(rows), 3)
        self.assertEqual([r["image_name"] for r in rows if r["selected"] == "1"], [selected_name])

    def test_finish_is_available_before_first_choice(self):
        self.app.button(key="finish_btn").click().run()
        self.app.button(key="confirm_finish_dialog").click().run()
        self.assertFalse(self.app.exception)
        self.assertEqual(self.app.session_state["phase"], "finished")
        self.assertEqual(self.app.session_state["saved_rows"], 0)
        self.assertTrue(Path(self.app.session_state["saved_csv_path"]).is_file())


if __name__ == "__main__":
    unittest.main()
