import time

from SiemplifyAction import SiemplifyAction
from SiemplifyUtils import unix_now, convert_unixtime_to_datetime, output_handler
from ScriptResult import EXECUTION_STATE_COMPLETED, EXECUTION_STATE_FAILED, EXECUTION_STATE_TIMEDOUT
from SiemplifyDataModel import EntityTypes

from TIPCommon.extraction import extract_configuration_param, extract_action_param

# Import Managers
from config import Config
from utils_manager import EntityValidator, GIBConnector


@output_handler
def main():
    
    # Google Chronicle base class initialization
    siemplify = SiemplifyAction()
    
    # Google Chronicle base class set up
    siemplify.script_name = Config.GC_PING
    
    # Get poller
    poller = GIBConnector(siemplify).init_action_poller()
    
    
    output_message = "Connection Established."
    connectivity_result = True
    status = EXECUTION_STATE_COMPLETED
    siemplify.LOGGER.info("----------------- Main - Started -----------------")

    try:
        result_json = poller.send_request(endpoint="user/granted_collections", params={"q": None})
        siemplify.LOGGER.info("Connection to API established, performing action {}".format(Config.GC_PING))
        
        siemplify.result.add_result_json(result_json)

    except Exception as e:
        output_message = "An error occurred when trying to connect to the API: {}".format(e)
        connectivity_result = False
        siemplify.LOGGER.error("Connection to API failed, performing action {}".format(Config.GC_PING))
        siemplify.LOGGER.exception(e)
        status = EXECUTION_STATE_FAILED

    siemplify.end(output_message, connectivity_result, status)


if __name__ == "__main__":
    main()
