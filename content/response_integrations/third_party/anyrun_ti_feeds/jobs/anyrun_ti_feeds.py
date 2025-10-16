from __future__ import annotations

from soar_sdk.SiemplifyJob import SiemplifyJob
from soar_sdk.SiemplifyUtils import output_handler
from TIPCommon.extraction import extract_job_param

from ..core.data_table_manager import DataTableManager


@output_handler
def main():
    siemplify = SiemplifyJob()

    feed_fetch_depth = extract_job_param(siemplify, param_name="Feed Fetch Depth", input_type=int)

    data_tables = DataTableManager(siemplify)
    data_tables.update_taxii_indicators(feed_fetch_depth)


if __name__ == "__main__":
    # Connectors are run in iterations. The interval is configurable from the ConnectorsScreen UI.
    main()
