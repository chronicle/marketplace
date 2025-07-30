# tests/test_detect_hash_type.py

from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from integration_testing.common import create_entity
from integrations.third_party.functions.actions import DetectHashType
from TIPCommon.base.action import EntityTypesEnum

HASH_ENTITY = create_entity("d41d8cd98f00b204e9800998ecf8427e", type_=EntityTypesEnum.FILE_HASH)

@set_metadata(parameters={"Hashes": "d41d8cd98f00b204e9800998ecf8427e"}, entities=[HASH_ENTITY])
def test_detect_md5(action_output: MockActionOutput, sdk_session) -> None:
    DetectHashType.main()
    assert action_output.results.json_output == [{"Hash": "d41d8cd98f00b204e9800998ecf8427e", "HashType": "MD5"}]


@set_metadata(parameters={"Hashes": "da39a3ee5e6b4b0d3255bfef95601890afd80709"})
def test_detect_sha1():
    DetectHashType.hashes = ["da39a3ee5e6b4b0d3255bfef95601890afd80709"]  # SHA1
    output = DetectHashType.main()
    assert output.results.json_output == [{"Hash": "da39a3ee5e6b4b0d3255bfef95601890afd80709", "HashType": "SHA1"}]


@set_metadata(parameters={"Hashes": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"})
def test_detect_sha256():
    DetectHashType.hashes = ["e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"]  # SHA256
    output = DetectHashType.main()
    assert output.results.json_output == [{"Hash": "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855", "HashType": "SHA256"}]
