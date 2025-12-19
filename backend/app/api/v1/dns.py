"""DNS management API endpoints"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import logging

from app.schemas.dns import (
    DNSZoneListResponse,
    DNSRecordListResponse,
    DNSRecordCreate,
    DNSRecordDelete,
    DNSRecord
)
from app.services.samba.dns import dns_service
from app.api.dependencies.auth import get_current_admin_user
from app.schemas.auth import User

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/dns/zones", response_model=DNSZoneListResponse)
async def list_zones(current_user: User = Depends(get_current_admin_user)):
    """
    List all DNS zones

    Requires admin privileges.
    """
    try:
        zones = dns_service.list_zones()
        return DNSZoneListResponse(
            zones=zones,
            total=len(zones)
        )
    except Exception as e:
        logger.error(f"Error listing DNS zones: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list DNS zones: {str(e)}"
        )


@router.get("/dns/zones/{zone}/records", response_model=DNSRecordListResponse)
async def list_records(
    zone: str,
    current_user: User = Depends(get_current_admin_user)
):
    """
    List all DNS records in a zone

    Requires admin privileges.
    """
    try:
        records = dns_service.list_records(zone)
        return DNSRecordListResponse(
            records=records,
            total=len(records),
            zone=zone
        )
    except Exception as e:
        logger.error(f"Error listing DNS records for zone {zone}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list DNS records: {str(e)}"
        )


@router.post("/dns/records", response_model=DNSRecord, status_code=status.HTTP_201_CREATED)
async def add_record(
    record_data: DNSRecordCreate,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Add a DNS record

    Requires admin privileges.
    """
    try:
        logger.info(f"Admin {current_user.username} adding DNS record: {record_data.name}.{record_data.zone} {record_data.type} {record_data.data}")

        success = dns_service.add_record(
            zone=record_data.zone,
            name=record_data.name,
            record_type=record_data.type,
            data=record_data.data,
            admin_password=record_data.admin_password
        )

        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to add DNS record"
            )

        # Return the created record
        return DNSRecord(
            zone=record_data.zone,
            name=record_data.name,
            type=record_data.type,
            data=record_data.data
        )

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error adding DNS record: {error_msg}")

        # Parse common error messages
        if "already exists" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="DNS record already exists"
            )
        elif "invalid" in error_msg.lower() and "credentials" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid administrator credentials"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add DNS record: {error_msg}"
        )


@router.delete("/dns/records", status_code=status.HTTP_204_NO_CONTENT)
async def delete_record(
    record_data: DNSRecordDelete,
    current_user: User = Depends(get_current_admin_user)
):
    """
    Delete a DNS record

    Requires admin privileges.
    """
    try:
        logger.info(f"Admin {current_user.username} deleting DNS record: {record_data.name}.{record_data.zone} {record_data.type} {record_data.data}")

        dns_service.delete_record(
            zone=record_data.zone,
            name=record_data.name,
            record_type=record_data.type,
            data=record_data.data,
            admin_password=record_data.admin_password
        )

        return None

    except HTTPException:
        raise
    except Exception as e:
        error_msg = str(e)
        logger.error(f"Error deleting DNS record: {error_msg}")

        if "not found" in error_msg.lower() or "does not exist" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="DNS record not found"
            )
        elif "invalid" in error_msg.lower() and "credentials" in error_msg.lower():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid administrator credentials"
            )

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to delete DNS record: {error_msg}"
        )
