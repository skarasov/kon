"""/model command - listing and switching models."""

from __future__ import annotations

from ...config import get_config
from ...llm import Model, get_all_models
from ..chat import ChatLog
from ..floating_list import ListItem
from ..selection_mode import SelectionMode
from ..widgets import InfoBar
from .base import CommandSupport


def _parse_hidden_entries(entries: list[str]) -> tuple[set[str], set[tuple[str, str]]]:
    """Split hidden-model entries into provider names and (provider, model) combos."""
    hidden_providers: set[str] = set()
    hidden_combos: set[tuple[str, str]] = set()
    for entry in entries:
        if ":" in entry:
            provider, _, model_id = entry.partition(":")
            provider, model_id = provider.strip(), model_id.strip()
            if provider and model_id:
                hidden_combos.add((provider, model_id))
        else:
            entry = entry.strip()
            if entry:
                hidden_providers.add(entry)
    return hidden_providers, hidden_combos


def _is_model_hidden(
    model: Model, hidden_providers: set[str], hidden_combos: set[tuple[str, str]]
) -> bool:
    return model.provider in hidden_providers or (model.provider, model.id) in hidden_combos


class ModelCommands(CommandSupport):
    def _handle_model_command(self, args: str) -> None:
        hidden_providers, hidden_combos = _parse_hidden_entries(get_config().ui.hidden_models)
        models = get_all_models()
        # Filter out hidden models, but always keep the currently active model
        # so its selection state is visible in the picker.
        if hidden_providers or hidden_combos:
            models = [
                m
                for m in models
                if not _is_model_hidden(m, hidden_providers, hidden_combos)
                or (m.id == self._runtime.model and m.provider == self._runtime.model_provider)
            ]
        if not models:
            self.notify("No models configured", title="Models", timeout=3, severity="warning")
            return

        models.sort(key=lambda m: (m.provider, m.id))

        items: list[ListItem] = []
        for m in models:
            parts = [m.provider]
            if not m.supports_images:
                parts.append("[no-vision]")
            caption = " ".join(parts)
            label = (
                f"{m.id} ✓"
                if m.id == self._runtime.model and m.provider == self._runtime.model_provider
                else m.id
            )
            items.append(ListItem(value=m, label=label, description=caption))

        self._show_selection_picker(items, SelectionMode.MODEL)

    def _select_model(self, model) -> None:
        chat = self.query_one("#chat-log", ChatLog)
        info_bar = self.query_one("#info-bar", InfoBar)

        try:
            self._runtime.switch_model(model)
        except ValueError as e:
            chat.add_info_message(str(e), error=True)
            return
        self._sync_runtime_state()

        info_bar.set_model(model.id, model.provider)

        chat.add_info_message(f"Model changed to {model.id} ({model.provider})")
