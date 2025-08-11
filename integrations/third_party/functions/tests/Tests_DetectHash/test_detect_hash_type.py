from __future__ import annotations
from integration_testing.platform.script_output import MockActionOutput
from integration_testing.set_meta import set_metadata
from integration_testing.common import create_entity
from integrations.third_party.functions.actions import DetectHashType
from TIPCommon.base.action import EntityTypesEnum, ExecutionState

MD5_HASH: str = "d41d8cd98f00b204e9800998ecf8427e"
SHA1_HASH: str = "da39a3ee5e6b4b0d3255bfef95601890afd80709"
SHA256_HASH: str = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

HASH_ENTITY = create_entity(MD5_HASH, type_=EntityTypesEnum.FILE_HASH)

pytest_plugins: tuple[str, ...] = ("integration_testing.conftest",)

class TestDetectHashType:

    @set_metadata(parameters={"Hashes": MD5_HASH}, entities=[HASH_ENTITY])
    def test_detect_md5(self, action_output: MockActionOutput) -> None:
        DetectHashType.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.json_output == [{"Hash": MD5_HASH, "HashType": "MD5"}]

    @set_metadata(parameters={"Hashes": SHA1_HASH})
    def test_detect_sha1(self, action_output: MockActionOutput) -> None:
        DetectHashType.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.json_output == [{"Hash": SHA1_HASH, "HashType": "SHA1"}]

    @set_metadata(parameters={"Hashes": SHA256_HASH})
    def test_detect_sha256(self, action_output: MockActionOutput) -> None:
        DetectHashType.main()
        assert action_output.results.execution_state is ExecutionState.COMPLETED
        assert action_output.results.json_output == [{"Hash": SHA256_HASH, "HashType": "SHA256"}]
