"""Hyped API Router."""
from datasets import Features
from datasets.iterable_dataset import _batch_to_examples, _examples_to_batch
from fastapi import Response
from fastapi.routing import APIRoute, APIRouter
from hyped.common.pydantic import pydantic_model_from_features
from hyped.data.flow.flow import DataFlow, DataFlowExecutor


class HypedAPIRouter(APIRouter):
    """Hyped API Router serving a data pipe."""

    def __init__(self, flow: DataFlow, **kwargs) -> None:
        """Initialize the API Router.

        Arguments:
            flow (DataFlow):
                data flow to serve. Must be build.
            **kwargs (dict[str, Any]):
                keyword arguments passed to the base constructor. For more
                information check the FastAPIRouter documentation.
        """
        self.flow = flow
        # build pydantic request and response models from
        # the input and output features
        in_model = pydantic_model_from_features(
            self.flow.src_features.feature_
        )
        out_model = pydantic_model_from_features(
            self.flow.out_features.feature_
        )

        async def batch_apply_flow(
            examples: list[in_model],
        ) -> list[out_model]:
            """Apply the data flow to a batch of examples."""
            index = list(range(len(examples)))
            batch = _examples_to_batch([e.model_dump() for e in examples])
            # execute data flow
            executor = DataFlowExecutor(
                self.flow._graph, self.flow._out_features
            )
            batch = await executor.execute(batch, index=index, rank=0)

            return list(_batch_to_examples(batch))

        async def apply_flow(example: in_model) -> out_model:
            """Apply the data flow to an example."""
            return (await batch_apply_flow([example]))[0]

        super(HypedAPIRouter, self).__init__(
            routes=[
                APIRoute("/apply", apply_flow, methods=["POST"]),
                APIRoute("/batch", batch_apply_flow, methods=["POST"]),
            ]
            + list(kwargs.pop("routes", [])),
            **kwargs,
        )
