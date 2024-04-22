"""Hyped API."""
from datasets import Features
from datasets.iterable_dataset import _batch_to_examples, _examples_to_batch
from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute
from hyped.data.io.datasets.typed_json import pydantic_model_from_features
from hyped.data.pipe import DataPipe


class HypedAPI(FastAPI):
    """Hyped API serving a data pipe."""

    def __init__(self, pipe: DataPipe, features: Features, **kwargs) -> None:
        """Initialize the API.

        Arguments:
            pipe (DataPipe):
                data pipeline to serve
            features (Features):
                input features to be processed by the data pipe
            **kwargs (dict[str, Any]):
                keyword arguments passed to the base constructor. For more
                information check the FastAPI documentation.
        """
        self.pipe = pipe
        # prepare data pipe
        out_features = self.pipe.prepare(features)
        # build pydantic request and response models from
        # the input and output features
        in_model = pydantic_model_from_features(features)
        out_model = pydantic_model_from_features(out_features)

        async def batch_apply_pipe(
            examples: list[in_model],
        ) -> list[out_model]:
            """Apply the data pipeline to a batch of examples."""
            batch = _examples_to_batch([e.model_dump() for e in examples])
            batch = self.pipe.batch_process(batch, index=[0], rank=0)
            return list(_batch_to_examples(batch))

        async def apply_pipe(example: in_model) -> out_model:
            """Apply the data pipeline to an example."""
            return (await batch_apply_pipe([example]))[0]

        super(HypedAPI, self).__init__(
            title="HypedAPI",
            routes=[
                APIRoute("/health", self.health, methods=["GET"]),
                APIRoute("/ready", self.ready, methods=["GET"]),
                APIRoute("/apply", apply_pipe, methods=["POST"]),
                APIRoute("/batch", batch_apply_pipe, methods=["POST"]),
            ],
            **kwargs,
        )

    async def ready(self) -> Response:
        """Readiness check."""
        # check if pipeline is prepared
        if not self.pipe.is_prepared:
            return Response(content="pipe not prepared", status_code=503)
        # ready for usage
        return Response(content="ok", status_code=200)

    async def health(self) -> Response:
        """Health check."""
        return Response(content="ok", status_code=200)
