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

    def test_legacy_seedance_20_0826_models_use_generations(self):
        for model in ("seedance-2.0-0826", "seedance-2.0-fast-0826"):
            with self.subTest(model=model):
                self.assertEqual(self.config(model)[3], "generations")

    def test_a_series_models_use_videos(self):
        for model in ("seedance2.0-A", "seedance2.0-Mini-A", "seedance2.5-A"):
            with self.subTest(model=model):
                self.assertEqual(self.config(model)[3], "videos")

    def test_legacy_seedance_20_cannot_use_videos_endpoint(self):
        with self.assertRaises(SystemExit):
            self.config("seedance-2.0-fast-0826", "videos")

    def test_a_series_cannot_use_generations_endpoint(self):
        with self.assertRaises(SystemExit):
            self.config("seedance2.5-A", "generations")

    def test_only_seedance_models_are_allowed(self):
        for model in ("seedance2.5", "seedance2.0-A", "seedance2.0-fast-A"):
            with self.subTest(model=model):
                self.assertTrue(drama_video.model_is_allowed(model))
        for model in ("Drama-video-v2", "minimax-h3", "gpt-image-2"):
            with self.subTest(model=model):
                self.assertFalse(drama_video.model_is_allowed(model))

    def test_a_series_rejects_undocumented_fields(self):
        args = argparse.Namespace(
            prompt="hello", seconds=4, resolution="480p", aspect_ratio="16:9",
            references=[], generate_audio=True, seed=7, negative_prompt="no text",
        )
        with self.assertRaises(SystemExit):
            drama_video.create_payload(args, "seedance2.5-A", "videos")

    def test_a_series_payload_uses_documented_public_fields(self):
        args = argparse.Namespace(
            prompt="hello", seconds=4, resolution="480p", aspect_ratio="16:9",
            references=[], generate_audio=False, seed=None, negative_prompt=None,
        )
        payload = drama_video.create_payload(args, "seedance2.5-A", "videos")
        self.assertEqual(payload, {
            "model": "seedance2.5-A",
            "prompt": "hello",
            "seconds": "4",
            "resolution": "480p",
            "aspect_ratio": "16:9",
        })

    def test_legacy_payload_keeps_legacy_fields(self):
        args = argparse.Namespace(
            prompt="hello", seconds=4, resolution="480p", aspect_ratio="16:9",
            references=[], generate_audio=True, seed=7, negative_prompt="no text",
        )
        payload = drama_video.create_payload(args, "seedance-2.0-0826", "generations")
        self.assertEqual(payload["seconds"], 4)
        self.assertEqual(payload["task_mode"], "text")
        self.assertTrue(payload["generate_audio"])
        self.assertEqual(payload["seed"], 7)
        self.assertEqual(payload["negative_prompt"], "no text")


if __name__ == "__main__":
    unittest.main()
