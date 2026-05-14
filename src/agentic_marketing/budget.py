"""Budget tracker following the estimate → reserve → reconcile pattern."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class TransactionType(str, Enum):
    ESTIMATE = "estimate"
    RESERVE = "reserve"
    RELEASE = "release"
    SPEND = "spend"
    RECONCILE = "reconcile"


@dataclass
class BudgetTransaction:
    tx_id: str
    channel: str
    stage: str
    tx_type: TransactionType
    amount_usd: float
    timestamp: str
    note: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "tx_id": self.tx_id,
            "channel": self.channel,
            "stage": self.stage,
            "tx_type": self.tx_type.value,
            "amount_usd": self.amount_usd,
            "timestamp": self.timestamp,
            "note": self.note,
        }


@dataclass
class ChannelBudget:
    channel: str
    allocated: float = 0.0
    reserved: float = 0.0
    spent: float = 0.0
    transactions: list[BudgetTransaction] = field(default_factory=list)

    @property
    def available(self) -> float:
        return self.allocated - self.reserved - self.spent


class BudgetTracker:
    """
    Tracks budget across estimate → reserve → reconcile lifecycle.

    Pattern:
      1. pre_execution_budget_check() — estimate + reserve
      2. track_stage_cost()            — log actual vs estimated per stage
      3. reserve_for_channel()        — reserve spend for paid channels
      4. reconcile_all()              — final reconciliation report
    """

    def __init__(
        self,
        total_budget_usd: float,
        allocation: dict[str, float] | None = None,
        enforcement: str = "warn",
        holdback_pct: float = 0.10,
    ) -> None:
        self.total_budget_usd = total_budget_usd
        self.enforcement = enforcement  # warn | cap | observe
        self.holdback_pct = holdback_pct
        self.holdback_amount = total_budget_usd * holdback_pct

        default_allocation = allocation or {
            "organic": 0.15,
            "paid": 0.80,
            "email": 0.05,
        }

        self.channels: dict[str, ChannelBudget] = {}
        for ch, pct in default_allocation.items():
            self.channels[ch] = ChannelBudget(channel=ch, allocated=total_budget_usd * pct)

        self.warnings: list[str] = []
        self._settled = False

    def pre_execution_budget_check(self, stage: str = "init") -> dict[str, Any]:
        """Reserve budget at start of execution; returns allocation report."""
        ts = datetime.now(timezone.utc).isoformat()
        report = {"total_budget": self.total_budget_usd, "allocated": {}, "reserve_holdback": self.holdback_amount}

        for ch, cb in self.channels.items():
            tx = BudgetTransaction(
                tx_id=f"tx-{uuid.uuid4().hex[:8]}",
                channel=ch,
                stage=stage,
                tx_type=TransactionType.RESERVE,
                amount_usd=cb.allocated,
                timestamp=ts,
                note="Initial allocation reserve",
            )
            cb.reserved = cb.allocated
            cb.transactions.append(tx)
            report["allocated"][ch] = cb.allocated

        return report

    def reserve_for_channel(self, channel: str, amount_usd: float, stage: str) -> BudgetTransaction:
        """Reserve a specific amount for a channel (e.g., ad spend)."""
        ts = datetime.now(timezone.utc).isoformat()
        cb = self.channels.get(channel)
        if not cb:
            raise ValueError(f"Unknown channel: {channel}")

        tx = BudgetTransaction(
            tx_id=f"tx-{uuid.uuid4().hex[:8]}",
            channel=channel,
            stage=stage,
            tx_type=TransactionType.RESERVE,
            amount_usd=amount_usd,
            timestamp=ts,
            note=f"Reserved for {stage}",
        )
        cb.reserved += amount_usd
        cb.transactions.append(tx)
        self._check_warnings(channel)
        return tx

    def release(self, channel: str, amount_usd: float, stage: str, note: str = "") -> BudgetTransaction:
        """Release a previously reserved amount (e.g., unused budget)."""
        ts = datetime.now(timezone.utc).isoformat()
        cb = self.channels.get(channel)
        if not cb:
            raise ValueError(f"Unknown channel: {channel}")

        release_amt = min(amount_usd, cb.reserved)
        tx = BudgetTransaction(
            tx_id=f"tx-{uuid.uuid4().hex[:8]}",
            channel=channel,
            stage=stage,
            tx_type=TransactionType.RELEASE,
            amount_usd=release_amt,
            timestamp=ts,
            note=note or f"Released after {stage}",
        )
        cb.reserved = max(0, cb.reserved - release_amt)
        cb.transactions.append(tx)
        return tx

    def spend(self, channel: str, amount_usd: float, stage: str, note: str = "") -> BudgetTransaction:
        """Record actual spend against a channel."""
        ts = datetime.now(timezone.utc).isoformat()
        cb = self.channels.get(channel)
        if not cb:
            raise ValueError(f"Unknown channel: {channel}")

        tx = BudgetTransaction(
            tx_id=f"tx-{uuid.uuid4().hex[:8]}",
            channel=channel,
            stage=stage,
            tx_type=TransactionType.SPEND,
            amount_usd=amount_usd,
            timestamp=ts,
            note=note or f"Spent during {stage}",
        )
        cb.spent += amount_usd
        cb.transactions.append(tx)
        self._check_warnings(channel)
        return tx

    def track_stage_cost(
        self, stage_name: str, channel: str, estimated: float, actual: float
    ) -> dict[str, Any]:
        """Log cost for a single stage, emit warning if exceeded."""
        ts = datetime.now(timezone.utc).isoformat()
        entry: dict[str, Any] = {
            "stage": stage_name,
            "channel": channel,
            "estimated": estimated,
            "actual": actual,
            "timestamp": ts,
        }

        if actual > estimated * 1.1:
            pct = ((actual / estimated) - 1) * 100
            warning = f"Stage {stage_name} exceeded estimate by {pct:.1f}% (${estimated:.2f} → ${actual:.2f})"
            self.warnings.append(warning)
            entry["warning"] = warning

            if self.enforcement == "cap" and actual > estimated * 1.5:
                raise PermissionError(f"Budget cap exceeded for stage {stage_name}: ${actual:.2f} > ${estimated * 1.5:.2f}")

        return entry

    def _check_warnings(self, channel: str) -> None:
        cb = self.channels[channel]
        if cb.reserved + cb.spent > cb.allocated * 1.05:
            self.warnings.append(f"Channel {channel} is approaching or over allocated budget: {cb.reserved + cb.spent:.2f} > {cb.allocated:.2f}")

    def reconcile_all(self) -> dict[str, Any]:
        """Final reconciliation report. Marks tracker as settled."""
        self._settled = True
        overspent_total = 0.0
        channel_reports = {}

        for ch, cb in self.channels.items():
            total_used = cb.reserved + cb.spent
            overspent = max(0, total_used - cb.allocated)
            if overspent > 0:
                overspent_total += overspent

            channel_reports[ch] = {
                "allocated": cb.allocated,
                "reserved": cb.reserved,
                "spent": cb.spent,
                "total_used": total_used,
                "available": cb.allocated - total_used,
                "overspent": overspent,
            }

        return {
            "execution_id": getattr(self, "_execution_id", None),
            "total_budget": self.total_budget_usd,
            "holdback": self.holdback_amount,
            "channels": channel_reports,
            "total_overspent": overspent_total,
            "settled": True,
            "warnings": self.warnings,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    def summary(self) -> dict[str, Any]:
        """Quick summary of current budget state."""
        return {
            ch: {
                "allocated": cb.allocated,
                "reserved": cb.reserved,
                "spent": cb.spent,
                "available": cb.available,
            }
            for ch, cb in self.channels.items()
        }

    def all_transactions(self) -> list[dict[str, Any]]:
        """Return flattened list of all transactions."""
        txs = []
        for cb in self.channels.values():
            txs.extend(tx.to_dict() for tx in cb.transactions)
        return sorted(txs, key=lambda t: t["timestamp"])