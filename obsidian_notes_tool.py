import requests
import json
from typing import Callable, Any, List


class EventEmitter:
    def __init__(self, event_emitter: Callable[[dict], Any] = None):
        self.event_emitter = event_emitter

    async def emit_status(
        self, description="Unknown State", status="in_progress", done=False
    ):
        if self.event_emitter:
            await self.event_emitter(
                {
                    "type": "status",
                    "data": {
                        "status": status,
                        "description": description,
                        "done": done,
                    },
                }
            )

    async def emit_citations(self, documents: List[dict]):
        if self.event_emitter:
            for document in documents:
                await self.event_emitter(
                    {
                        "type": "citation",
                        "data": {
                            "document": [document["content"]],
                            "metadata": [{"source": document["filename"]}],
                            "source": {"name": document["filename"]},
                        },
                    }
                )


class Tools:
    def __init__(self):
        self.API_URL = "http://192.168.0.214:9000/api/weekly-notes" # Python Service API

    async def fetch_weekly_notes(
        self,
        __event_emitter__: Callable[[dict], Any] = None,
    ) -> str:
        """
        Fetches the weekly notes from the specified API endpoint, emits them as citations,
        and returns the encoded notes.
        :return: The encoded notes.
        """
        emitter = EventEmitter(__event_emitter__)

        await emitter.emit_status(
            description=f"Fetching weekly notes from API: {self.API_URL}"
        )

        try:
            response = requests.get(self.API_URL, timeout=30)
            response.raise_for_status()
            data = response.json()

            notes = data.get("notes", [])
            if not notes:
                await emitter.emit_status(
                    status="warning",
                    description="No notes found in the response.",
                    done=True,
                )
                return "No notes were fetched."

            # Emit each note as a citation
            await emitter.emit_citations(notes)

            # Create a success message
            success_message = f"Received {len(notes)} notes"

            await emitter.emit_status(
                status="complete",
                description=success_message,
                done=True,
            )

            return json.dumps(notes, ensure_ascii=False)

        except requests.exceptions.RequestException as e:
            await emitter.emit_status(
                status="error",
                description=f"Error fetching weekly notes: {str(e)}",
                done=True,
            )
            return f"Error fetching weekly notes: {str(e)}"
