import argparse
import importlib.util
import os
from pathlib import Path
import unittest


SCRIPT = Path(__file__).parents[1] / "scripts" / "drama_video.py"
SPEC = importlib.util.spec_from_file_location("drama_video", SCRIPT)
drama_video = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(drama_video)


class ModelPolicyTests(unittest.TestCase):
    def setUp(self):
        self.previous_base = os.environ.get("DRAMA_BASE_URL")
        self.previous_key = os.environ.get("DRAMA_API_KEY")
        self.previous_model = os.environ.pop("DRAMA_MODEL", None)
        self.previous_endpoint = os.environ.pop("DRAMA_ENDPOINT", None)
        os.environ["DRAMA_BASE_URL"] = "https://example.invalid"
        os.environ["DRAMA_API_KEY"] = "TOKEN"

    def tearDown(self):
        self._restore("DRAMA_BASE_URL", self.previous_base)
        self._restore("DRAMA_API_KEY", self.previous_key)
        self._restore("DRAMA_MODEL", self.previous_model)
        self._restore("DRAMA_ENDPOINT", self.previous_endpoint)

    @staticmethod
    def _restore(name, value):
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value

    @staticmethod
    def config(model, endpoint="auto"):
        return drama_video.config(argparse.Namespace(model=model, endpoint=endpoint))

    def test_seedance_20_0826_models_use_generations(self):
        for model in ("seedance-2.0-0826", "seedance-2.0-fast-0826"):
            with self.subTest(model=model):
                self.assertEqual(self.config(model)[3], "generations")

    def test_a_series_models_use_videos(self):
        for model in ("seedance2.0-A", "seedance2.0-Mini-A", "seedance2.5-A"):
            with self.subTest(model=model):
                self.assertEqual(self.config(model)[3], "videos")

    def test_seedance_20_without_0826_is_rejected(self):
        for model in ("seedance-2.0", "seedance-2.0-fast"):
            with self.subTest(model=model):
                with self.assertRaises(SystemExit):
                    self.config(model)

    def test_seedance_20_cannot_use_videos_endpoint(self):
        with self.assertRaises(SystemExit):
            self.config("seedance-2.0-fast-0826", "videos")

    def test_other_model_families_remain_available(self):
        self.assertEqual(self.config("seedance2.5")[3], "videos")
        self.assertTrue(drama_video.model_is_allowed("seedance2.5"))


if __name__ == "__main__":
    unittest.main()
