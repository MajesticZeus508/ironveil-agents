"""Provider-specific selection of optional middleware, without dependency patches."""


def provider_middleware(middleware, model_id, cache_type):
    # sling-agent 0.1.0.dev6 sends an OpenAI-only prompt_cache_key for every
    # ChatOpenAI transport, even when it fronts Vertex/Gemini. Omit the optional
    # cache component at construction; preserve every other component and order.
    if "gemini" in model_id.lower():
        return [item for item in middleware if not isinstance(item, cache_type)]
    return middleware
