"""Request schemas for admin-managed static data (sample types + devices)."""

from __future__ import annotations

from pydantic import BaseModel


class Device(BaseModel):
    title: str
    code: str


class SampleTypeCreate(BaseModel):
    sampleType: str
    sampleCollectionDeviceName: list[Device] = []


class SampleTypeUpdate(BaseModel):
    sampleType: str | None = None
    sampleCollectionDeviceName: list[Device] | None = None
