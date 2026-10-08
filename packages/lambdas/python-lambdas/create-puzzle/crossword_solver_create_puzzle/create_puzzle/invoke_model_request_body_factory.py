import base64
import json


class InvokeModelRequestBodyFactory:
    def to_request_body(
        self,
        image_bytes: bytes,
        prompt_text: str,
    ) -> str:
        return json.dumps(
            {
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 4096,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": prompt_text,
                            },
                            {
                                "type": "image",
                                "source": {
                                    "type": "base64",
                                    "media_type": "image/jpeg",
                                    "data": base64.b64encode(image_bytes).decode("ascii"),
                                },
                            },
                        ],
                    }
                ],
            }
        )
