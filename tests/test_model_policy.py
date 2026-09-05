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
        os.environ["DRAMA_BASE_URL"] = "https://example.invalid"
        os.environ["DRAMA_API_KEY"] = "TOKEN"

    def tearDown(self):
        self._restore("DRAMA_BASE_URL", self.previous_base)
        self._restore("DRAMA_API_KEY", self.previous_key)
        self._restore("DRAMA_MODEL", self.previous_model)

    @staticmethod
    def _restore(name, value):
        if value is None:
            os.environ.pop(name, None)
        else:
            os.environ[name] = value

    @staticmethod
    def config(model):
        return drama_video.config(argparse.Namespace(model=model))

    def test_supported_seedance_models_use_videos(self):
        for model in ("seedance2.0-A", "seedance2.0-Mini-A", "seedance2.5-A"):
            with self.subTest(model=model):
                self.assertEqual(self.config(model)[2], model)

    def test_non_a_series_models_are_rejected(self):
        for model in ("seedance2.0", "seedance2.0-fast"):
            with self.subTest(model=model):
                with self.assertRaises(SystemExit):
                    self.config(model)

    def test_only_seedance_models_are_allowed(self):
        for model in ("seedance2.0-A", "seedance2.0-fast-A", "seedance2.5-A"):
            with self.subTest(model=model):
                self.assertTrue(drama_video.model_is_allowed(model))
        for model in ("Drama-video-v2", "minimax-h3", "gpt-image-2"):
            with self.subTest(model=model):
                self.assertFalse(drama_video.model_is_allowed(model))

    def test_a_series_payload_uses_documented_public_fields(self):
        args = argparse.Namespace(
            prompt="hello", seconds=4, resolution="480p", aspect_ratio="16:9",
            references=[],
        )
        payload = drama_video.create_payload(args, "seedance2.5-A")
        self.assertEqual(payload, {
            "model": "seedance2.5-A",
            "prompt": "hello",
            "seconds": "4",
            "resolution": "480p",
            "aspect_ratio": "16:9",
        })

if __name__ == "__main__":
    unittest.main()
