from pathlib import Path

import boto3

from seeder.core import SeederManager
from seeder.service.minio_seeder import MinioSeeder

endpoint = "http://127.0.0.1:9000"
username = "admin"
password = "admin-password"

s3_client = boto3.client(
    "s3",
    endpoint_url=endpoint,
    aws_access_key_id=username,
    aws_secret_access_key=password,
)


def test_common_usage(datadir: Path):
    seeder_manager = SeederManager(seeders=[MinioSeeder(endpoint=endpoint, username=username, password=password)])
    seeder_manager.truncate()
    seeder_manager.seed(datadir / "data-1")

    assert _list_all_keys("demo-1") == ["a/b.txt", "c.txt"]
    assert _list_all_keys("demo-2") == ["d.txt"]
    assert _list_all_keys("demo-3") == []


def test_nested_folder(datadir: Path):
    seeder_manager = SeederManager(
        seeders=[
            MinioSeeder(
                endpoint=endpoint,
                username=username,
                password=password,
                get_folder_path=lambda folder, bucket: folder / "minio" / bucket,
            )
        ]
    )
    seeder_manager.truncate()
    seeder_manager.seed(datadir / "data-2")

    assert _list_all_keys("demo-1") == ["a/b/z.txt", "c.txt"]
    assert _list_all_keys("demo-2") == ["d.txt"]
    assert _list_all_keys("demo-3") == []


def _list_all_keys(bucket: str) -> list[str]:
    paginator = s3_client.get_paginator("list_objects_v2")

    outputs: list[str] = []
    for page in paginator.paginate(Bucket=bucket):
        if "Contents" in page:
            for k in [obj["Key"] for obj in page["Contents"]]:
                outputs.append(k)
    return sorted(outputs)
