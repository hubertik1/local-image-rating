import csv
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

from PIL import Image
from streamlit.testing.v1 import AppTest

from image_rating_app import storage


class CategoryGroupingTests(unittest.TestCase):
    def test_leftovers_never_borrow_images_from_another_category(self):
        images = [Path("new_images") / folder / f"{i}.png"
                  for folder in ("Awe", "Craving") for i in range(2)]
        groups = storage.build_random_image_groups(images)
        self.assertEqual([len(group) for group in groups], [2, 2])
        self.assertTrue(all(len({p.parent for p in group}) == 1 for group in groups))
        self.assertCountEqual([p for group in groups for p in group], images)

    def test_every_image_is_used_once_without_changing_input(self):
        images = [Path("new_images") / folder / f"{i}.png"
                  for folder, count in (("Awe", 4), ("Craving", 5)) for i in range(count)]
        original = images.copy()
        groups = storage.build_random_image_groups(images)
        self.assertEqual([len(group) for group in groups], [3, 1, 3, 2])
        self.assertTrue(all(len({p.parent for p in group}) == 1 for group in groups))
        self.assertCountEqual([p for group in groups for p in group], images)
        self.assertEqual(images, original)

    def test_nested_folders_with_the_same_name_are_distinct(self):
        images = [Path("new_images") / path for path in (
            "root.png", "Awe/example.png", "Awe/detail/one.png", "Craving/detail/two.png"
        )]
        folders = storage.group_images_by_folder(images)
        self.assertEqual(list(folders), [".", "Awe", "Awe/detail", "Craving/detail"])
        self.assertEqual(len(storage.build_random_image_groups(images)), 4)

    def test_empty_input_has_no_groups(self):
        self.assertEqual(storage.build_random_image_groups([]), [])


class CategoryPickerTests(unittest.TestCase):
    def setUp(self):
        temporary = TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.image_dir = Path(temporary.name) / "images"
        self.output_dir = Path(temporary.name) / "output"
        for folder, count in (("Amusement", 4), ("Awe", 2), ("Awe/detail", 1), (".", 1)):
            destination = self.image_dir / folder
            destination.mkdir(parents=True, exist_ok=True)
            for i in range(count):
                Image.new("RGB", (30, 20), (i * 40, 100, 70)).save(
                    destination / f"{folder.replace('/', '_')}_{i}.png"
                )
        for name, value in (("IMAGE_DIR", self.image_dir), ("OUTPUT_DIR", self.output_dir)):
            item = patch.object(storage, name, value)
            item.start()
            self.addCleanup(item.stop)
        self.app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app.py"))
        self.app.run(timeout=20)
        self.app.text_input(key="draft_name").set_value("Category test")

    def start(self):
        next(button for button in self.app.button if button.label == "Start").click().run()
        self.assertFalse(self.app.exception)

    def test_all_folders_counts_separate_leftovers_and_keeps_groups_separate(self):
        self.assertEqual(self.app.selectbox(key="draft_image_folder").value, None)
        self.app.radio(key="draft_option").set_value("Choose the best of 3").run()
        self.assertTrue(any("5 sets of up to 3" in info.value for info in self.app.info))
        self.start()
        groups = [[Path(p) for p in group] for group in self.app.session_state["image_groups"]]
        self.assertEqual(len(groups), 5)
        self.assertTrue(all(len({p.parent for p in group}) == 1 for group in groups))
        self.assertCountEqual([p for group in groups for p in group], storage.get_image_paths())

    def test_selected_folder_excludes_child_folders_and_exports_only_its_images(self):
        self.app.selectbox(key="draft_image_folder").set_value("Awe").run()
        self.app.radio(key="draft_option").set_value("Choose the best of 3").run()
        self.assertTrue(any("2 images" in info.value for info in self.app.info))
        self.start()
        self.assertEqual(len(self.app.session_state["image_groups"]), 1)
        images = [Path(p) for p in self.app.session_state["images"]]
        self.assertEqual(len(images), 2)
        self.assertTrue(all(p.parent == self.image_dir / "Awe" for p in images))
        self.assertTrue(any(caption.value == "Folder: Awe" for caption in self.app.caption))
        self.app.button(key="best_of_three_choice_0_0").click().run()
        self.app.button(key="finish_all_btn").click().run()
        self.app.button(key="confirm_finish_dialog").click().run()
        self.assertFalse(self.app.exception)
        with Path(self.app.session_state["saved_csv_path"]).open(encoding="utf-8-sig", newline="") as file:
            rows = list(csv.DictReader(file))
        self.assertCountEqual([row["image_name"] for row in rows], [p.name for p in images])
        self.assertEqual(sum(int(row["selected"]) for row in rows), 1)

    def test_folder_filter_also_applies_to_default_rating_mode(self):
        self.app.selectbox(key="draft_image_folder").set_value("Amusement").run()
        self.start()
        images = [Path(p) for p in self.app.session_state["images"]]
        self.assertEqual(len(images), 4)
        self.assertTrue(all(p.parent == self.image_dir / "Amusement" for p in images))


if __name__ == "__main__":
    unittest.main()
