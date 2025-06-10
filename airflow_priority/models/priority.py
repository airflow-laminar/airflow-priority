from typing import Optional

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
    aws: Optional[AwsConfiguration] = None
    datadog: Optional[DataDogConfiguration] = None
    discord: Optional[DiscordConfiguration] = None
    logfire: Optional[LogfireConfiguration] = None
    newrelic: Optional[NewRelicConfiguration] = None
    opsgenie: Optional[OpsGenieConfiguration] = None
    pagerduty: Optional[PagerDutyConfiguration] = None
    slack: Optional[SlackConfiguration] = None
    symphony: Optional[SymphonyConfiguration] = None
