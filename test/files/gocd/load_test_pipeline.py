#!/bin/env python
import os, sys
from bs4 import BeautifulSoup

def backup_cruise_config(config_file):
    """
    Takes a path and the cruise config file handle,
    and creates a backup.
    """
    config_backup_path = os.path.join(os.path.dirname(config_file.name), "cruise-config.xml.bak")
    with open(config_backup_path, "w") as config_backup_file:
        config_backup_file.seek(0)
        config_backup_file.write(config_file.read())
        config_backup_file.truncate()

def update_cruise_config(config_file, pipeline_file):
    """
    Takes the cruise-config.xml file handle and the pipeline
    file handle, and uses Beautiful Soup to insert the new pipeline,
    if it doesn't already exist.
    """
    config_file.seek(0)
    config_soup = BeautifulSoup(config_file.read(), "xml")
    pipeline_soup = BeautifulSoup(pipeline_file.read(), "xml")

    # Only add the automated-test group if it does not already exist
    try:
        pipeline_group = config_soup.select('pipelines[group="automated-test"]')[0]
    except IndexError:
        pipeline_group = config_soup.new_tag("pipelines", group="automated-test")
        config_soup.cruise.insert(2, pipeline_group)

    # Only insert the pipeline if another of the same name does not exist
    pipeline_name = pipeline_soup.pipeline['name']

    if not pipeline_group.select('pipeline[name="{0}"]'.format(pipeline_name)):
        config_soup.find('automated-test')
        pipeline_group.append(pipeline_soup.pipeline)

    return config_soup

def write_cruise_config(config_path, config):
    """
    Outputs the new configuration to the cruise-config.xml
    file.
    """
    with open(config_path, "w") as config_file:
        config_file.seek(0)
        config_file.write(config.prettify())
        config_file.truncate()

if __name__ == '__main__':

    # Get command line arguements
    assert (
        len(sys.argv) == 2
    ), f"Please provide the pipeline XML file to load (and no other arguments): {sys.argv[1:]}"

    pipeline_xml_file = sys.argv[1]

    # Determine file paths
    script_path = os.path.dirname(os.path.realpath(__file__))
    config_path = os.path.join(os.getenv("GOCD_CONFIG_PATH", "/tmp"), "cruise-config.xml")
    pipeline_path = os.path.join(script_path, pipeline_xml_file)

    with open(config_path, "r") as config_file:
        pipeline_file = open(pipeline_path, "r")

        # Backup config_xml file
        backup_cruise_config(config_file)

        # Parse the config and pipeline files, then create a new pipeline group and insert the pipeline
        updated_config = update_cruise_config(config_file, pipeline_file)

    pipeline_file.close()

    # Output the modified contents
    write_cruise_config(config_path, updated_config)

    exit(0)
