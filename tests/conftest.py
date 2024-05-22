from typing import Any

import pytest
from datasets import Features, Value
from datasets.iterable_dataset import _batch_to_examples, _examples_to_batch
from fastapi import FastAPI
from fastapi.testclient import TestClient
from hyped.data.flow import DataFlow
from hyped.data.flow.processors.ops.noop import NoOp

from hyped.serve.api import HypedAPI


@pytest.fixture
def features() -> Features:
    return Features({"x": Value("int32")})


@pytest.fixture
def flow(features: Features) -> DataFlow:
    # create flow and add noop processor
    flow = DataFlow(features)
    out = NoOp().call(x=flow.src_features.x)
    # build the flow
    return flow.build(collect=out)


@pytest.fixture
def api(flow: DataFlow) -> HypedAPI:
    return HypedAPI().serve_flow(flow)


@pytest.fixture
def client(api: FastAPI) -> TestClient:
    return TestClient(api)


@pytest.fixture(params=range(10))
def example(request) -> dict[str, Any]:
    return {"x": request.param}


@pytest.fixture
def out_example(flow: DataFlow, example: dict[str, Any]) -> dict[str, Any]:
    batch = _examples_to_batch([example])
    batch = flow.batch_process(batch, index=[0])
    return next(_batch_to_examples(batch))
