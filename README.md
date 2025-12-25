# Taskiq - FastStream

<p align="center">
    <a href="https://github.com/taskiq-python/taskiq-faststream/actions/workflows/test.yml" target="_blank">
        <img src="https://github.com/taskiq-python/taskiq-faststream/actions/workflows/test.yml/badge.svg" alt="Tests status"/>
    </a>
    <a href="https://pypi.org/project/taskiq-faststream/" target="_blank">
        <img src="https://img.shields.io/pypi/v/taskiq-faststream?label=pypi%20package" alt="Package version">
    </a>
    <a href="https://pepy.tech/project/taskiq-faststream" target="_blank">
        <img src="https://static.pepy.tech/personalized-badge/taskiq-faststream?period=month&units=international_system&left_color=grey&right_color=blue" alt="downloads"/>
    </a>
    <a href="https://pypi.org/project/taskiq-faststream" target="_blank">
        <img src="https://img.shields.io/pypi/pyversions/taskiq-faststream.svg" alt="Supported Python versions">
    </a>
    <a href="https://github.com/taskiq-python/taskiq-faststream/blob/master/LICENSE" target="_blank">
        <img alt="GitHub" src="https://img.shields.io/github/license/taskiq-python/taskiq-faststream?color=%23007ec6">
    </a>
</p>

---

The current package is just a wrapper for [**FastStream**](https://faststream.airt.ai/0.2/?utm_source=github&utm_medium=acquisition&utm_campaign=measure) objects to make them compatible with [**Taskiq**](https://taskiq-python.github.io/) library.

The main goal of it - provide **FastStream** with a great **Taskiq** tasks [scheduling](https://taskiq-python.github.io/guide/scheduling-tasks.html) feature.

## Installation

If you already have **FastStream** project to interact with your Message Broker, you can add scheduling to it by installing just a **taskiq-faststream**

```bash
pip install taskiq-faststream
```

If you starting with a clear project, you can specify **taskiq-faststream** broker by the following distributions:

```bash
pip install taskiq-faststream[rabbit]
# or
pip install taskiq-faststream[kafka]
# or
pip install taskiq-faststream[confluent]
# or
pip install taskiq-faststream[nats]
# or
pip install taskiq-faststream[redis]
```

For **OpenTelemetry** distributed tracing support:

```bash
pip install taskiq-faststream[otel]
```

## Usage

The package gives you two classes: `AppWrapper` and `BrokerWrapper`

These are just containers for the related **FastStream** objects to make them **taskiq**-compatible

To create scheduling tasks for your broker, just wrap it to `BrokerWrapper` and use it like a regular **taskiq** Broker.

```python
# regular FastStream code
from faststream.nats import NatsBroker

broker = NatsBroker()

@broker.subscriber("test-subject")
async def handler(msg: str):
    print(msg)

# taskiq-faststream scheduling
from taskiq.schedule_sources import LabelScheduleSource
from taskiq_faststream import BrokerWrapper, StreamScheduler

# wrap FastStream object
taskiq_broker = BrokerWrapper(broker)

# create periodic task
taskiq_broker.task(
    message="Hi!",
    # If you are using RabbitBroker, then you need to replace subject with queue.
    # If you are using KafkaBroker, then you need to replace subject with topic.
    subject="test-subject",
    schedule=[{
        "cron": "* * * * *",
    }],
)

# create scheduler object
scheduler = StreamScheduler(
    broker=taskiq_broker,
    sources=[LabelScheduleSource(taskiq_broker)],
)
```

To run the scheduler, just use the following command

```bash
taskiq scheduler module:scheduler
```

Also, you can wrap your **FastStream** application the same way (allows to use lifespan events and AsyncAPI documentation):

```python
# regular FastStream code
from faststream import FastStream
from faststream.nats import NatsBroker

broker = NatsBroker()
app = FastStream(broker)

@broker.subscriber("test-subject")
async def handler(msg: str):
    print(msg)

# wrap FastStream object
from taskiq_faststream import AppWrapper
taskiq_broker = AppWrapper(app)

# Code below omitted 👇
```

A little feature: instead of using a final `message` argument, you can set a message callback to collect information right before sending:

```python
async def collect_information_to_send():
    return "Message to send"

taskiq_broker.task(
    message=collect_information_to_send,
    ...,
)
```

Also, you can send a multiple message by one task call just using generator message callback with `yield`

```python
async def collect_information_to_send():
    """Sends 10 messages per task call."""
    for i in range(10):
        yield i

taskiq_broker.task(
    message=collect_information_to_send,
    ...,
)
```

## OpenTelemetry Support

**taskiq-faststream** supports taskiq's OpenTelemetry middleware. To enable it, pass `OpenTelemetryMiddleware` when creating the broker wrapper:

```python
from faststream.nats import NatsBroker
from taskiq_faststream import BrokerWrapper
from taskiq.middlewares.otel_middleware import OpenTelemetryMiddleware

broker = NatsBroker()

# Enable OpenTelemetry middleware
taskiq_broker = BrokerWrapper(broker, middlewares=[OpenTelemetryMiddleware()])
```

This will automatically add OpenTelemetry middleware to track task execution, providing insights into:
- Task execution spans
- Task dependencies and call chains
- Performance metrics
- Error tracking

Make sure to configure your OpenTelemetry exporter (e.g., Jaeger, Zipkin) according to your monitoring setup.

The same applies to `AppWrapper`:

```python
from faststream import FastStream
from taskiq_faststream import AppWrapper
from taskiq.middlewares.otel_middleware import OpenTelemetryMiddleware

app = FastStream(broker)

# Enable OpenTelemetry middleware
taskiq_broker = AppWrapper(app, middlewares=[OpenTelemetryMiddleware()])
```
