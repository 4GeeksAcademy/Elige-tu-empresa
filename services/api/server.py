"""Standard-library HTTP server for the incident service and static backoffice."""

import json
import mimetypes
import re
import sqlite3
from contextlib import contextmanager
from dataclasses import fields, is_dataclass
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, unquote, urlsplit

from services.api.catalogs import catalogs, inventoryCatalogs
from services.api.database import createConnection, initializeDatabase
from services.api.incidents import (
    changeIncidentStatus,
    getIncidentDetails,
    getOpenIncidentCountsBySeverity,
    listIncidents,
    reassignIncidentArea,
    registerIncident,
)
from services.api.inventory import (
    BusinessRuleError,
    createItem,
    deleteItem,
    getItem,
    getReorderSignal,
    getStockReport,
    listItems,
    registerMovement,
    updateItem,
)
from services.api.models import formatUtcTimestamp


maximumRequestBytes = 1_048_576
incidentIdPattern = re.compile(r"^[0-9a-f]{8}-[0-9a-f]{4}-4[0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}$")
defaultStaticRoot = Path(__file__).resolve().parents[2] / "uis" / "backoffice"


@contextmanager
def _databaseConnection(databasePath: Path):
    connection = createConnection(databasePath)
    try:
        yield connection
    finally:
        connection.close()


class APIRequestError(Exception):
    def __init__(self, statusCode: int, message: str):
        super().__init__(message)
        self.statusCode = statusCode


class IncidentHTTPServer(ThreadingHTTPServer):
    daemon_threads = True
    allow_reuse_address = True

    def __init__(
        self,
        serverAddress: tuple[str, int],
        databasePath: str | Path,
        staticRoot: str | Path = defaultStaticRoot,
    ):
        self.databasePath = Path(databasePath)
        self.staticRoot = Path(staticRoot).resolve()
        self.databasePath.parent.mkdir(parents=True, exist_ok=True)
        connection = createConnection(self.databasePath)
        try:
            initializeDatabase(connection)
        finally:
            connection.close()
        super().__init__(serverAddress, IncidentRequestHandler)


class IncidentRequestHandler(BaseHTTPRequestHandler):
    server: IncidentHTTPServer

    def do_GET(self) -> None:
        self._handleRequest("GET")

    def do_POST(self) -> None:
        self._handleRequest("POST")

    def do_PATCH(self) -> None:
        self._handleRequest("PATCH")

    def do_PUT(self) -> None:
        self._methodNotAllowed()

    def do_DELETE(self) -> None:
        self._handleRequest("DELETE")

    def _handleRequest(self, method: str) -> None:
        requestPath = urlsplit(self.path)
        if requestPath.path.startswith("/api/"):
            if method == "DELETE" and not requestPath.path.startswith("/api/inventory/"):
                self._methodNotAllowed()
                return
            try:
                self._dispatchAPI(method, requestPath.path, requestPath.query)
            except APIRequestError as error:
                self._sendJson(error.statusCode, {"error": str(error)})
            except (UnicodeDecodeError, json.JSONDecodeError, ValueError) as error:
                self._sendJson(400, {"error": str(error)})
            except BusinessRuleError as error:
                self._sendJson(409, {"error": str(error)})
            except LookupError as error:
                self._sendJson(404, {"error": str(error)})
            except sqlite3.Error:
                self.log_error("SQLite request failed")
                self._sendJson(500, {"error": "Internal server error"})
            return

        if method != "GET":
            self._methodNotAllowed()
            return
        self._serveStaticFile(requestPath.path)

    def _dispatchAPI(self, method: str, requestPath: str, query: str) -> None:
        if requestPath.startswith("/api/inventory/"):
            self._dispatchInventoryAPI(method, requestPath, query)
            return

        if method == "GET" and requestPath == "/api/catalogs":
            self._sendJson(200, catalogs)
            return

        if method == "GET" and requestPath == "/api/incidents":
            queryValues = parse_qs(query, keep_blank_values=True, strict_parsing=False)
            allowedFilters = {"statusId", "severityId", "responsibleAreaId"}
            if set(queryValues) - allowedFilters:
                raise APIRequestError(400, "Unsupported incident filter")
            filters = {}
            for fieldName, values in queryValues.items():
                if len(values) != 1:
                    raise APIRequestError(400, f"{fieldName} must be provided once")
                filters[fieldName] = values[0]
            with _databaseConnection(self.server.databasePath) as connection:
                incidents = listIncidents(connection, **filters)
            self._sendJson(200, incidents)
            return

        if method == "POST" and requestPath == "/api/incidents":
            payload = self._readJsonObject()
            expectedFields = {
                "channelId",
                "typeId",
                "severityId",
                "responsibleAreaId",
                "title",
                "description",
                "createdBy",
            }
            self._requirePayloadFields(payload, expectedFields)
            with _databaseConnection(self.server.databasePath) as connection:
                incident = registerIncident(connection, **payload)
            self._sendJson(201, incident)
            return

        if method == "GET" and requestPath == "/api/incidents/summary/by-severity":
            with _databaseConnection(self.server.databasePath) as connection:
                summary = getOpenIncidentCountsBySeverity(connection)
            self._sendJson(200, summary)
            return

        routeMatch = re.fullmatch(r"/api/incidents/([^/]+)", requestPath)
        if routeMatch and method == "GET":
            incidentId = routeMatch.group(1)
            self._requireIncidentId(incidentId)
            with _databaseConnection(self.server.databasePath) as connection:
                details = getIncidentDetails(connection, incidentId)
            self._sendJson(200, details)
            return

        statusMatch = re.fullmatch(r"/api/incidents/([^/]+)/status", requestPath)
        if statusMatch and method == "PATCH":
            incidentId = statusMatch.group(1)
            self._requireIncidentId(incidentId)
            payload = self._readJsonObject()
            self._requirePayloadFields(payload, {"statusId", "author"})
            with _databaseConnection(self.server.databasePath) as connection:
                incident = changeIncidentStatus(
                    connection,
                    incidentId,
                    payload["statusId"],
                    payload["author"],
                )
            self._sendJson(200, incident)
            return

        areaMatch = re.fullmatch(r"/api/incidents/([^/]+)/area", requestPath)
        if areaMatch and method == "PATCH":
            incidentId = areaMatch.group(1)
            self._requireIncidentId(incidentId)
            payload = self._readJsonObject()
            self._requirePayloadFields(payload, {"responsibleAreaId", "author"})
            with _databaseConnection(self.server.databasePath) as connection:
                incident = reassignIncidentArea(
                    connection,
                    incidentId,
                    payload["responsibleAreaId"],
                    payload["author"],
                )
            self._sendJson(200, incident)
            return

        raise APIRequestError(404, "API route not found")

    def _dispatchInventoryAPI(self, method: str, requestPath: str, query: str) -> None:
        if method == "GET" and requestPath == "/api/inventory/catalogs":
            self._sendJson(200, inventoryCatalogs)
            return

        if requestPath == "/api/inventory/items":
            if method == "GET":
                queryValues = parse_qs(query, keep_blank_values=True, strict_parsing=False)
                if set(queryValues) - {"locationId"}:
                    raise APIRequestError(400, "Unsupported inventory filter")
                if "locationId" in queryValues and len(queryValues["locationId"]) != 1:
                    raise APIRequestError(400, "locationId must be provided once")
                locationId = queryValues["locationId"][0] if "locationId" in queryValues else None
                with _databaseConnection(self.server.databasePath) as connection:
                    items = listItems(connection, locationId)
                self._sendJson(200, items)
                return
            if method == "POST":
                payload = self._readJsonObject()
                with _databaseConnection(self.server.databasePath) as connection:
                    item = createItem(connection, payload)
                self._sendJson(201, item)
                return

        itemMatch = re.fullmatch(r"/api/inventory/items/([^/]+)", requestPath)
        if itemMatch and method in {"GET", "PATCH", "DELETE"}:
            itemId = itemMatch.group(1)
            if incidentIdPattern.fullmatch(itemId) is None:
                raise APIRequestError(404, "Item not found")
            if method == "GET":
                with _databaseConnection(self.server.databasePath) as connection:
                    item = getItem(connection, itemId)
                self._sendJson(200, item)
                return
            if method == "PATCH":
                payload = self._readJsonObject()
                with _databaseConnection(self.server.databasePath) as connection:
                    item = updateItem(connection, itemId, payload)
                self._sendJson(200, item)
                return
            with _databaseConnection(self.server.databasePath) as connection:
                deleted = deleteItem(connection, itemId)
            self._sendJson(200, deleted)
            return

        itemActionMatch = re.fullmatch(r"/api/inventory/items/([^/]+)/(movements|report)", requestPath)
        if itemActionMatch and (
            (itemActionMatch.group(2) == "movements" and method == "POST")
            or (itemActionMatch.group(2) == "report" and method == "GET")
        ):
            itemId = itemActionMatch.group(1)
            if incidentIdPattern.fullmatch(itemId) is None:
                raise APIRequestError(404, "Item not found")
            if itemActionMatch.group(2) == "movements":
                payload = self._readJsonObject()
                with _databaseConnection(self.server.databasePath) as connection:
                    movement = registerMovement(connection, itemId, payload)
                self._sendJson(201, movement)
                return
            with _databaseConnection(self.server.databasePath) as connection:
                report = getStockReport(connection, itemId)
            self._sendJson(200, report)
            return

        reorderMatch = re.fullmatch(r"/api/inventory/locations/([^/]+)/reorder", requestPath)
        if reorderMatch and method == "GET":
            with _databaseConnection(self.server.databasePath) as connection:
                signal = getReorderSignal(connection, reorderMatch.group(1))
            self._sendJson(200, signal)
            return

        raise APIRequestError(404, "API route not found")

    def _readJsonObject(self) -> dict:
        contentType = self.headers.get("Content-Type", "")
        if contentType.partition(";")[0].strip().lower() != "application/json":
            raise APIRequestError(415, "Content-Type must be application/json")

        contentLength = self.headers.get("Content-Length")
        if contentLength is None:
            raise APIRequestError(411, "Content-Length is required")
        try:
            bodyLength = int(contentLength)
        except ValueError as error:
            raise APIRequestError(400, "Content-Length must be an integer") from error
        if bodyLength < 0:
            raise APIRequestError(400, "Content-Length must not be negative")
        if bodyLength > maximumRequestBytes:
            raise APIRequestError(413, "Request body is too large")

        rawBody = self.rfile.read(bodyLength)
        if len(rawBody) != bodyLength:
            raise APIRequestError(400, "Request body is incomplete")
        payload = json.loads(rawBody.decode("utf-8"))
        if not isinstance(payload, dict):
            raise APIRequestError(400, "JSON request body must be an object")
        return payload

    def _requirePayloadFields(self, payload: dict, expectedFields: set[str]) -> None:
        missingFields = expectedFields - payload.keys()
        unexpectedFields = payload.keys() - expectedFields
        if missingFields:
            raise APIRequestError(
                400,
                f"Missing required fields: {', '.join(sorted(missingFields))}",
            )
        if unexpectedFields:
            raise APIRequestError(
                400,
                f"Unsupported fields: {', '.join(sorted(unexpectedFields))}",
            )

    def _requireIncidentId(self, incidentId: str) -> None:
        if incidentIdPattern.fullmatch(incidentId) is None:
            raise APIRequestError(404, "Incident not found")

    def _serveStaticFile(self, requestPath: str) -> None:
        relativePath = unquote(requestPath).lstrip("/")
        if not relativePath:
            relativePath = "index.html"
        requestedFile = (self.server.staticRoot / relativePath).resolve()
        if not requestedFile.is_relative_to(self.server.staticRoot):
            self._sendJson(404, {"error": "File not found"})
            return
        if not requestedFile.is_file():
            self._sendJson(404, {"error": "File not found"})
            return

        contentType = mimetypes.guess_type(requestedFile.name)[0] or "application/octet-stream"
        if contentType.startswith("text/") or contentType in {
            "application/javascript",
            "application/json",
        }:
            contentType += "; charset=utf-8"
        content = requestedFile.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", contentType)
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def _methodNotAllowed(self) -> None:
        self.send_response(405)
        self.send_header("Allow", "GET, POST, PATCH")
        self.send_header("Content-Length", "0")
        self.end_headers()

    def _sendJson(self, statusCode: int, value: object) -> None:
        content = json.dumps(
            self._toJsonValue(value),
            ensure_ascii=False,
            separators=(",", ":"),
        ).encode("utf-8")
        self.send_response(statusCode)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.send_header("X-Content-Type-Options", "nosniff")
        self.end_headers()
        self.wfile.write(content)

    def _toJsonValue(self, value: object) -> object:
        if is_dataclass(value):
            return {
                item.name: self._toJsonValue(getattr(value, item.name))
                for item in fields(value)
            }
        if isinstance(value, datetime):
            return formatUtcTimestamp(value)
        if isinstance(value, dict):
            return {key: self._toJsonValue(item) for key, item in value.items()}
        if isinstance(value, (tuple, list)):
            return [self._toJsonValue(item) for item in value]
        return value

    def log_message(self, formatString: str, *arguments: object) -> None:
        print(f"{self.address_string()} - {formatString % arguments}")


def createServer(
    databasePath: str | Path,
    host: str = "127.0.0.1",
    port: int = 8000,
    staticRoot: str | Path = defaultStaticRoot,
) -> IncidentHTTPServer:
    """Create the local incident API and static backoffice HTTP server."""
    return IncidentHTTPServer((host, port), databasePath, staticRoot)


def main() -> None:
    server = createServer("data/incidents.sqlite")
    print(f"Brasaland incident manager listening on http://{server.server_address[0]}:{server.server_address[1]}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping incident manager.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
