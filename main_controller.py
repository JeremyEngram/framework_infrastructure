import os
import importlib
import logging
import yaml
import argparse

# Load global configuration
def load_global_config(config_path):
    with open(config_path, 'r') as file:
        return yaml.safe_load(file)

# Set up logging
def setup_logging(log_config_path):
    logging.config.dictConfig(yaml.safe_load(open(log_config_path)))
    logger = logging.getLogger("CentralizedFramework")
    return logger

# Dynamically load and execute a module
def load_and_execute_module(module_name, logger):
    module_path = f"./modules/{module_name}"
    
    if not os.path.exists(module_path):
        logger.error(f"Module {module_name} not found.")
        return

    script_files = [f for f in os.listdir(module_path) if f.endswith(".py")]

    if not script_files:
        logger.warning(f"No scripts found in {module_path}.")
        return

    logger.info(f"Executing module {module_name}...")
    for script in script_files:
        script_path = os.path.join(module_path, script)
        try:
            spec = importlib.util.spec_from_file_location(script[:-3], script_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "run"):
                logger.info(f"Running script {script} in {module_name}")
                module.run()
            else:
                logger.warning(f"Script {script} in {module_name} does not have a 'run' function.")
        except Exception as e:
            logger.error(f"Error executing {script}: {e}")

# Main execution block
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Centralized Modular Framework")
    parser.add_argument("-m", "--module", help="Module to execute", required=True)
    args = parser.parse_args()

    config = load_global_config('./config/global_config.yaml')
    logger = setup_logging('./config/logging_config.yaml')

    load_and_execute_module(args.module, logger)
