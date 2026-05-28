from typing import Literal
from urllib.parse import quote

from fastapi import APIRouter, Request, Response
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from app_distribution_server.build_info import (
    Platform,
)
from app_distribution_server.config import (
    get_absolute_url,
)
from app_distribution_server.storage import (
    get_app_file_presigned_url,
    get_upload_asserted_platform,
    load_app_file,
    load_build_info,
)

router = APIRouter(tags=["App files"])

templates = Jinja2Templates(directory="templates")


@router.get(
    "/get/{upload_id}/app.plist",
    response_class=HTMLResponse,
)
async def get_item_plist(
    request: Request,
    upload_id: str,
) -> HTMLResponse:
    get_upload_asserted_platform(
        upload_id,
        expected_platform=Platform.ios,
    )

    build_info = load_build_info(upload_id)

    return templates.TemplateResponse(
        request=request,
        name="plist.xml",
        media_type="application/xml",
        context={
            "ipa_file_url": get_absolute_url(f"/get/{upload_id}/{Platform.ios.app_file_name}"),
            "app_title": build_info.app_title,
            "bundle_id": build_info.bundle_id,
            "bundle_version": build_info.bundle_version,
        },
    )


@router.head(
    "/get/{upload_id}/app.{file_type}",
)
async def head_app_file(
    upload_id: str,
    file_type: Literal["ipa", "apk"],
) -> Response:
    """Быстрый HEAD: только метаданные из build_info, без обращения к S3.

    iOS OTA делает HEAD перед GET. Если ответить медленно или редиректом
    на presigned URL (S3 не разрешает HEAD по GET-подписи), iOS прервёт
    установку. Поэтому HEAD обслуживается локально и мгновенно.
    """
    expected_platform = Platform.ios if file_type == "ipa" else Platform.android
    get_upload_asserted_platform(upload_id, expected_platform=expected_platform)
    build_info = load_build_info(upload_id)

    return Response(
        status_code=200,
        media_type="application/octet-stream",
        headers={
            "Content-Length": str(build_info.file_size),
            "Accept-Ranges": "bytes",
        },
    )


@router.get(
    "/get/{upload_id}/app.{file_type}",
    response_class=HTMLResponse,
)
async def get_app_file(
    upload_id: str,
    file_type: Literal["ipa", "apk"],
) -> Response:
    expected_platform = Platform.ios if file_type == "ipa" else Platform.android
    get_upload_asserted_platform(upload_id, expected_platform=expected_platform)

    build_info = load_build_info(upload_id)

    # Если S3 — редиректим клиента прямо на presigned URL,
    # не пропуская файл через бэкенд.
    presigned_url = get_app_file_presigned_url(build_info)
    if presigned_url is not None:
        return RedirectResponse(url=presigned_url, status_code=302)

    # Локальный osfs / fallback — старое поведение с буфером в памяти.
    app_file_content = load_app_file(build_info)

    created_at_prefix = (
        build_info.created_at.strftime("%Y-%m-%d_%H-%M-%S") if build_info.created_at else ""
    )
    file_name = f"{build_info.app_title} {build_info.bundle_version}{created_at_prefix}"

    # Encode the filename for HTTP headers
    safe_filename = quote(file_name)
    content_disposition = f"attachment; filename*=UTF-8''{safe_filename}.{file_type}"

    return Response(
        content=app_file_content,
        media_type="application/octet-stream",
        headers={"Content-Disposition": content_disposition},
    )
