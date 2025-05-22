from taskiq.kicker import AsyncKicker, _FuncParams, _ReturnType


class LabelRespectKicker(AsyncKicker[_FuncParams, _ReturnType]):
    """Patched kicker doesn't cast labels to str."""
