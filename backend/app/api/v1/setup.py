"""
Setup Wizard API Endpoints

Endpoints for Samba AD Domain Controller setup wizard.
"""

from fastapi import APIRouter, HTTPException
from typing import Dict
import logging

from app.schemas.setup import (
    DomainConfigSchema,
    PrerequisitesResponse,
    PrerequisiteCheck,
    ProvisionResponse,
    ProvisionStatus,
    VerificationResponse,
    VerificationTest,
    SetupStatusResponse
)
from app.services.samba.provision import SambaProvisionService
from app.services.samba.verification import SambaVerificationService

router = APIRouter()
logger = logging.getLogger(__name__)

# Initialize services
provision_service = SambaProvisionService()


@router.get("/setup/status", response_model=SetupStatusResponse)
async def get_setup_status():
    """
    Get current setup status
    Check if domain is already provisioned and get domain details
    """
    is_provisioned = await provision_service.is_domain_provisioned()

    domain_info = None
    if is_provisioned:
        # Try to get domain info from samba-tool
        domain_info = await provision_service.get_domain_info()

        # If samba-tool fails, at least get info from smb.conf
        if not domain_info:
            import os
            smb_conf_path = "/etc/samba/smb.conf"
            if os.path.exists(smb_conf_path):
                try:
                    with open(smb_conf_path, 'r') as f:
                        content = f.read()
                        domain_info = {"config_file": "exists", "raw_config": content[:500]}
                except Exception:
                    domain_info = {"status": "provisioned but details unavailable"}

    return SetupStatusResponse(
        is_provisioned=is_provisioned,
        domain_info=domain_info,
        last_provision_date=None  # TODO: Store this in database
    )


@router.post("/setup/check-prerequisites", response_model=PrerequisitesResponse)
async def check_prerequisites():
    """
    Check system prerequisites before starting setup
    Validates that all requirements are met
    """
    logger.info("Checking setup prerequisites")

    all_passed, checks_data = await provision_service.check_prerequisites()

    checks = [PrerequisiteCheck(**check) for check in checks_data]

    return PrerequisitesResponse(
        all_passed=all_passed,
        checks=checks
    )


@router.post("/setup/validate-config")
async def validate_config(config: DomainConfigSchema):
    """
    Validate domain configuration before provisioning
    Performs validation without actually provisioning
    """
    logger.info(f"Validating configuration for domain: {config.domain_name}")

    # Pydantic already validates, but we can add custom checks here
    validation_results = {
        "valid": True,
        "errors": [],
        "warnings": []
    }

    # Check if domain already provisioned
    if await provision_service.is_domain_provisioned():
        validation_results["warnings"].append(
            "A domain appears to be already provisioned. Proceeding will overwrite it."
        )

    # Check realm and domain consistency
    expected_realm = config.domain_name.upper()
    if config.realm != expected_realm:
        validation_results["warnings"].append(
            f"Realm '{config.realm}' does not match domain '{config.domain_name}'. "
            f"Consider using '{expected_realm}' as realm."
        )

    # Check DNS forwarder is reachable
    if config.dns_forwarder:
        import socket
        try:
            socket.create_connection((config.dns_forwarder, 53), timeout=2)
        except Exception:
            validation_results["warnings"].append(
                f"DNS forwarder {config.dns_forwarder} may not be reachable"
            )

    return validation_results


@router.post("/setup/provision", response_model=ProvisionResponse)
async def provision_domain(config: DomainConfigSchema):
    """
    Provision a new Samba AD domain
    This is the main provisioning endpoint
    """
    logger.info(f"Starting domain provision: {config.domain_name}")

    # Check if already provisioned
    if await provision_service.is_domain_provisioned():
        logger.warning("Domain already provisioned")
        raise HTTPException(
            status_code=400,
            detail="A domain is already provisioned. Please remove existing configuration first."
        )

    # Run provision
    status, message, output = await provision_service.provision_domain(config)

    return ProvisionResponse(
        status=status,
        message=message,
        output=output if status == ProvisionStatus.COMPLETED else None,
        error=output if status == ProvisionStatus.FAILED else None
    )


@router.post("/setup/verify", response_model=VerificationResponse)
async def verify_installation(config: DomainConfigSchema):
    """
    Run verification tests after provisioning
    Comprehensive tests to ensure everything is working
    """
    logger.info("Starting verification tests")

    # Initialize verification service
    verification_service = SambaVerificationService(
        domain_name=config.domain_name,
        realm=config.realm,
        admin_password=config.admin_password
    )

    # Run all tests
    tests = await verification_service.run_all_tests()

    # Calculate summary
    total = len(tests)
    passed = sum(1 for t in tests if t.status == "passed")
    failed = sum(1 for t in tests if t.status == "failed")
    skipped = sum(1 for t in tests if t.status == "skipped")

    # Determine overall status
    if failed == 0:
        overall_status = "passed"
        summary = f"All {total} tests passed successfully"
    elif passed > failed:
        overall_status = "partial"
        summary = f"{passed}/{total} tests passed, {failed} failed"
    else:
        overall_status = "failed"
        summary = f"{failed}/{total} tests failed"

    return VerificationResponse(
        overall_status=overall_status,
        total_tests=total,
        passed=passed,
        failed=failed,
        skipped=skipped,
        tests=tests,
        summary=summary
    )


@router.get("/setup/domain-info")
async def get_domain_info():
    """
    Get information about the current domain
    """
    if not await provision_service.is_domain_provisioned():
        raise HTTPException(status_code=404, detail="No domain provisioned")

    domain_info = await provision_service.get_domain_info()

    if not domain_info:
        raise HTTPException(status_code=500, detail="Could not retrieve domain information")

    return domain_info


@router.post("/setup/reset")
async def reset_domain():
    """
    Reset domain configuration by removing all Samba AD config
    WARNING: This is destructive! Creates backups before deletion.
    """
    logger.warning("Domain reset requested")

    # Check if domain exists
    if not await provision_service.is_domain_provisioned():
        raise HTTPException(
            status_code=404,
            detail="No domain found to reset"
        )

    # Perform reset
    success, message = await provision_service.reset_domain()

    if not success:
        raise HTTPException(
            status_code=500,
            detail=message
        )

    return {
        "success": True,
        "message": message
    }
