"""Django storage backend for Supabase Storage.

Uploads media (menu photos) to a public Supabase Storage bucket over its REST
API using the project's service-role key. No AWS/boto3 dependency, so the
serverless function stays small. Reads are served from the bucket's public URL.
"""

import mimetypes
import urllib.error
import urllib.request

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import Storage
from django.utils.deconstruct import deconstructible


@deconstructible
class SupabaseStorage(Storage):
    def __init__(self):
        self.base = settings.SUPABASE_URL.rstrip("/")          # https://<ref>.supabase.co
        self.bucket = settings.SUPABASE_BUCKET
        self.key = settings.SUPABASE_SERVICE_KEY

    # Object (authenticated) endpoint used for upload/delete.
    def _object_url(self, name):
        return f"{self.base}/storage/v1/object/{self.bucket}/{name}"

    # Overwrite instead of auto-renaming, so seeding is idempotent and image
    # paths stay stable.
    def get_available_name(self, name, max_length=None):
        return name

    def _save(self, name, content):
        content.seek(0)
        data = content.read()
        ctype = mimetypes.guess_type(name)[0] or "application/octet-stream"
        req = urllib.request.Request(
            self._object_url(name),
            data=data,
            method="POST",
            headers={
                "Authorization": f"Bearer {self.key}",
                "apikey": self.key,
                "Content-Type": ctype,
                "x-upsert": "true",
                "Cache-Control": "public, max-age=31536000",
            },
        )
        try:
            urllib.request.urlopen(req, timeout=30)
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", "replace")[:300]
            raise IOError(f"Supabase upload failed ({e.code}) for {name}: {body}")
        return name

    def _open(self, name, mode="rb"):
        data = urllib.request.urlopen(self.url(name), timeout=30).read()
        return ContentFile(data)

    def exists(self, name):
        req = urllib.request.Request(self.url(name), method="HEAD")
        try:
            urllib.request.urlopen(req, timeout=15)
            return True
        except Exception:
            return False

    def delete(self, name):
        req = urllib.request.Request(
            self._object_url(name),
            method="DELETE",
            headers={"Authorization": f"Bearer {self.key}", "apikey": self.key},
        )
        try:
            urllib.request.urlopen(req, timeout=15)
        except Exception:
            pass

    def size(self, name):
        return 0

    # Public read URL (bucket is public).
    def url(self, name):
        return f"{self.base}/storage/v1/object/public/{self.bucket}/{name}"
