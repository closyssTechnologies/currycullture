import os
import ssl
import sys
import json
import xmlrpc.client
import urllib.request
import urllib.error

STAGING_URL = "https://closysstechnologies-currycullture-staging-41759947.dev.odoo.com"
DB_NAME = "closysstechnologies-currycullture-staging-41759947"
USERNAME = "parvinder.chopra@closyss.com"
PASSWORD = os.environ.get("ODOO_STAGING_PASSWORD", "1")

ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

class OdooStagingClient:
    def __init__(self, url=STAGING_URL, db=DB_NAME, user=USERNAME, password=PASSWORD):
        self.url = url.rstrip('/')
        self.db = db
        self.user = user
        self.password = password
        self.common = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/common", context=ssl_ctx)
        self.models = xmlrpc.client.ServerProxy(f"{self.url}/xmlrpc/2/object", context=ssl_ctx)
        self.uid = self.common.authenticate(self.db, self.user, self.password, {})
        if not self.uid:
            raise RuntimeError(f"Authentication failed for {self.user} on {self.db}")
        self.session_cookie = None
        self._auth_jsonrpc()

    def _auth_jsonrpc(self):
        auth_url = f"{self.url}/web/session/authenticate"
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {"db": self.db, "login": self.user, "password": self.password}
        }
        req = urllib.request.Request(
            auth_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req, context=ssl_ctx) as resp:
            headers = resp.info()
            for header, value in headers.items():
                if header.lower() == 'set-cookie' and 'session_id=' in value:
                    for part in value.split(';'):
                        part = part.strip()
                        if part.startswith('session_id='):
                            self.session_cookie = part
                            break

    def execute(self, model, method, *args, **kwargs):
        return self.models.execute_kw(self.db, self.uid, self.password, model, method, list(args), kwargs)

    def download_report_pdf(self, report_name, docids):
        report_url = f"{self.url}/report/pdf/{report_name}/{','.join(str(i) for i in docids)}"
        req = urllib.request.Request(report_url, headers={"Cookie": self.session_cookie or ""})
        try:
            with urllib.request.urlopen(req, context=ssl_ctx, timeout=30) as resp:
                content = resp.read()
                content_type = resp.headers.get("Content-Type", "")
                return content, content_type
        except Exception as e:
            return None, str(e)

if __name__ == "__main__":
    client = OdooStagingClient()
    print("Logged in successfully as UID:", client.uid)
    installed_modules = client.execute("ir.module.module", "search_read", [["state", "=", "installed"]], fields=["name", "author", "installed_version", "latest_version"])
    print(f"Total installed modules: {len(installed_modules)}")
    custom = [m for m in installed_modules if m.get("author") not in ["Odoo S.A.", "Odoo"]]
    print(f"Total custom modules: {len(custom)}")
    for m in custom:
        print(f"  - {m['name']}: {m['installed_version']}")
