from pydantic import BaseModel

from .aws import AwsConfiguration
from .datadog import DataDogConfiguration
from .discord import DiscordConfiguration
from .logfire import LogfireConfiguration
from .newrelic import NewRelicConfiguration
from .opsgenie import OpsGenieConfiguration
from .pagerduty import PagerDutyConfiguration
from .slack import SlackConfiguration
from .symphony import SymphonyConfiguration

__all__ = ("PriorityConfiguration",)


class PriorityConfiguration(BaseModel):
    aws: AwsConfiguration | None = None
    datadog: DataDogConfiguration | None = None
    discord: DiscordConfiguration | None = None
    logfire: LogfireConfiguration | None = None
    newrelic: NewRelicConfiguration | None = None
    opsgenie: OpsGenieConfiguration | None = None
    pagerduty: PagerDutyConfiguration | None = None
    slack: SlackConfiguration | None = None
    symphony: SymphonyConfiguration | None = None
