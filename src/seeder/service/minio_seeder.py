import os
from pathlib import Path
from typing import Callable

import boto3

from seeder.core import Seeder


def _default_get_folder_path(folder: Path, bucket: str) -> Path:
    return folder / bucket


class MinioSeeder(Seeder):
    def __init__(
        self,
        endpoint: str,
        username: str,
        password: str,
        get_folder_path: Callable[[Path, str], Path] = _default_get_folder_path,
    ):
        self._client = boto3.client(
            "s3",
            endpoint_url=endpoint,
            aws_access_key_id=username,
            aws_secret_access_key=password,
        )
        self._buckets: list[str] = [info["Name"] for info in self._client.list_buckets()["Buckets"]]
        self._get_folder_path = get_folder_path

    def truncate(self) -> None:
        for bucket in self._buckets:
            self._delete_objects(bucket)

    def seed(self, folder: Path) -> None:
        for bucket in self._buckets:
            local_folder: Path = self._get_folder_path(folder, bucket)
            if not local_folder.exists():
                continue

            for root, dirs, filenames in os.walk(local_folder):
                for filename in filenames:
                    local_filepath = Path(root) / filename
                    key = str(local_filepath.relative_to(local_folder))
                    self._client.upload_file(str(local_filepath), bucket, key)

    def _delete_objects(self, bucket: str) -> None:
        paginator = self._client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket):
            if "Contents" in page:
                objects = [{"Key": obj["Key"]} for obj in page["Contents"]]
                self._client.delete_objects(Bucket=bucket, Delete={"Objects": objects})
