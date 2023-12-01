from typing import Any

from taskiq.serializers.json_serializer import JSONSerializer


class PatchedSerializer(JSONSerializer):
    """Patched serializer removes labels."""

    def dumpb(self, value: Any) -> bytes:
        """
        Dumps taskiq message to some broker message format.

        :param message: message to send.
        :return: Dumped message.
        """
        del value["labels"]
        return super().dumpb(value)
