from MythosEngine.gui.random_generator.controller_random_generator import (
    RandomGeneratorController,
)
from MythosEngine.gui.random_generator.view_random_generator import RandomGeneratorView


class DummyAI:
    def generate_random(self, prompt):
        return f"RANDOM:{prompt}"


def test_random_generator_empty_prompts(tk_root, config, storage):
    view = RandomGeneratorView(tk_root, config)
    ctrl = RandomGeneratorController(view, DummyAI(), storage, config)
    view.prompt_entry.delete(0, "end")
    ctrl.on_generate()
    assert "Please enter a prompt" in view.output_text.get("1.0", "end")


def test_random_generator_with_prompt(tk_root, config, storage):
    view = RandomGeneratorView(tk_root, config)
    ctrl = RandomGeneratorController(view, DummyAI(), storage, config)
    view.prompt_entry.delete(0, "end")
    view.prompt_entry.insert(0, "abc")
    ctrl.on_generate()
    assert "RANDOM:abc" == view.output_text.get("1.0", "end").strip()
