import plistlib
import uuid

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.templating import Jinja2Templates

from app_distribution_server.config import (
    APP_TITLE,
    LOGO_URL,
    get_absolute_url,
)

router = APIRouter(tags=["iOS UDID"])

templates = Jinja2Templates(directory="templates")


@router.get(
    "/udid",
    response_class=HTMLResponse,
    summary="Render the page to get iOS device UDID",
)
async def render_udid_page(request: Request) -> HTMLResponse:
    enroll_url = get_absolute_url("/udid/enroll")

    return templates.TemplateResponse(
        request=request,
        name="udid-get.jinja.html",
        context={
            "page_title": f"Get iOS Device UDID - {APP_TITLE}",
            "enroll_url": enroll_url,
            "logo_url": LOGO_URL,
        },
    )


@router.get(
    "/udid/enroll",
    summary="Download mobileconfig profile to retrieve device UDID",
)
async def get_udid_mobileconfig(request: Request) -> Response:
    callback_url = get_absolute_url("/udid/callback")
    payload_uuid = str(uuid.uuid4()).upper()

    content = templates.get_template("udid.mobileconfig.xml").render(
        callback_url=callback_url,
        organization=APP_TITLE,
        display_name="Device UDID Enrollment",
        description="This profile will retrieve your device UDID. It will be automatically removed after installation.",
        payload_uuid=payload_uuid,
        payload_identifier=f"com.udid.profile.{payload_uuid}",
    )

    return Response(
        content=content,
        media_type="application/x-apple-aspen-config",
        headers={
            "Content-Disposition": 'attachment; filename="udid.mobileconfig"',
        },
    )


@router.post(
    "/udid/callback",
    summary="Callback endpoint that receives device information from iOS",
)
async def udid_callback(request: Request) -> Response:
    body = await request.body()

    try:
        device_info = plistlib.loads(body)
    except Exception:
        return RedirectResponse(
            url=get_absolute_url("/udid?error=invalid_response"),
            status_code=301,
        )

    udid = device_info.get("UDID", "")

    if not udid:
        return RedirectResponse(
            url=get_absolute_url("/udid?error=no_udid"),
            status_code=301,
        )

    result_url = get_absolute_url(f"/udid/result/{udid}")

    return RedirectResponse(
        url=result_url,
        status_code=301,
    )


@router.get(
    "/udid/result/{udid}",
    response_class=HTMLResponse,
    summary="Display the device UDID to the user",
)
async def render_udid_result(request: Request, udid: str) -> HTMLResponse:
    return templates.TemplateResponse(
        request=request,
        name="udid-result.jinja.html",
        context={
            "page_title": f"Your Device UDID - {APP_TITLE}",
            "udid": udid,
            "logo_url": LOGO_URL,
        },
    )
