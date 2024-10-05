import os
import importlib.util
import logging
import logging.handlers

# Define the directories for each category of scripts
SCRIPT_CATEGORIES = {
    "system": "./system_scripts",
    "user": "./user_scripts",
    "osint": "./osint_scripts",
    "forensics": "./forensics_scripts",
    "offensive": "./offensive_scripts",
    "logging": "./logging_scripts"
}

# Set up syslog logging
def setup_logging():
    logger = logging.getLogger("DynamicLoader")
    logger.setLevel(logging.INFO)
    
    # Define the syslog handler
    syslog_handler = logging.handlers.SysLogHandler(address='/dev/log')  # For Linux-based systems
    formatter = logging.Formatter('%(name)s: %(levelname)s: %(message)s')
    syslog_handler.setFormatter(formatter)
    
    logger.addHandler(syslog_handler)
    return logger

# Function to load and run scripts dynamically from a specific category
def load_and_run_scripts(category, logger):
    if category not in SCRIPT_CATEGORIES:
        logger.error(f"Unknown category: {category}")
        return

    script_dir = SCRIPT_CATEGORIES[category]
    
    # Check if the directory exists
    if not os.path.exists(script_dir):
        logger.error(f"Directory {script_dir} does not exist.")
        return

    logger.info(f"Loading scripts from category: {category}")
    
    # List all Python files in the script directory
    script_files = [f for f in os.listdir(script_dir) if f.endswith(".py")]
    
    # Iterate over each Python script
    for script_file in script_files:
        script_path = os.path.join(script_dir, script_file)
        
        # Dynamically import the script module
        module_name = script_file[:-3]  # Strip off the ".py"
        try:
            spec = importlib.util.spec_from_file_location(module_name, script_path)
            script_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(script_module)
            
            # Ensure the module has a 'run' function, then call it
            if hasattr(script_module, "run"):
                logger.info(f"Running script: {module_name} in {category}")
                try:
                    script_module.run()
                    logger.info(f"Successfully executed script: {module_name}")
                except Exception as e:
                    logger.error(f"Error running script {module_name}: {e}")
            else:
                logger.warning(f"Script {module_name} does not have a 'run()' function.")
        except Exception as e:
            logger.error(f"Error loading script {module_name}: {e}")

# Function to load and integrate an LLM dynamically if required
def integrate_llm(model_path, logger):
    logger.info(f"Loading LLM model from {model_path}...")
    # Example: Replace with actual LLM loading logic
    try:
        # Assuming you are using something like HuggingFace's Transformers or LMStudio API
        from transformers import AutoModelForCausalLM, AutoTokenizer
        
        # Load the model and tokenizer
        tokenizer = AutoTokenizer.from_pretrained(model_path)
        model = AutoModelForCausalLM.from_pretrained(model_path)
        logger.info("LLM loaded successfully.")
        return model, tokenizer
    except Exception as e:
        logger.error(f"Error loading LLM: {e}")
        return None, None

# Example of how you can run the loader
if __name__ == "__main__":
    # Set up logging to syslog
    logger = setup_logging()

    logger.info("Starting the dynamic script loader...")
    print("Available script categories:", ", ".join(SCRIPT_CATEGORIES.keys()))
    
    # Get user input for category selection
    category = input("Enter the category of scripts to run (e.g., system, user, osint): ").strip().lower()
    
    # Optionally ask if the user wants to integrate an LLM
    use_llm = input("Would you like to integrate a local large language model? (y/n): ").strip().lower() == 'y'
    if use_llm:
        model_path = input("Enter the path to the local LLM model: ").strip()
        model, tokenizer = integrate_llm(model_path, logger)
    
    # Run the scripts for the selected category
    load_and_run_scripts(category, logger)
    logger.info("Script execution completed.")
