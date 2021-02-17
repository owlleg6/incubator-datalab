#!/usr/bin/python3

# *****************************************************************************
#
# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at
# 
#   http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.
#
# ******************************************************************************

import logging
import os
import sys
import uuid
import subprocess
from datalab.actions_lib import *
from datalab.fab import *
from datalab.meta_lib import *


# Main function for provisioning notebook server
def run():
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'],
                                               os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] + "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)

    notebook_config = dict()
    notebook_config['uuid'] = str(uuid.uuid4())[:5]

    try:
        params = "--uuid {}".format(notebook_config['uuid'])
        subprocess.run("~/scripts/{}.py {}".format('common_prepare_notebook', params), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed preparing Notebook node.", str(err))
        sys.exit(1)

    try:
        params = "--uuid {}".format(notebook_config['uuid'])
        subprocess.run("~/scripts/{}.py {}".format('deeplearning_configure', params), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed configuring Notebook node.", str(err))
        sys.exit(1)


# Main function for terminating exploratory environment
def terminate():
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'], os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] + "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)
    try:
        subprocess.run("~/scripts/{}.py".format('common_terminate_notebook'), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed terminating Notebook node.", str(err))
        sys.exit(1)


# Main function for stopping notebook server
def stop():
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'], os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] +  "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)
    try:
        subprocess.run("~/scripts/{}.py".format('common_stop_notebook'), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed stopping Notebook node.", str(err))
        sys.exit(1)


# Main function for starting notebook server
def start():
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'], os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] +  "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)

    try:
        subprocess.run("~/scripts/{}.py".format('common_start_notebook'), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed starting Notebook node.", str(err))
        sys.exit(1)


# Main function for configuring notebook server after deploying DataEngine service
def configure():
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'],
                                               os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] + "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)

    try:
        if os.environ['conf_resource'] == 'dataengine':
            subprocess.run("~/scripts/{}.py".format('common_notebook_configure_dataengine'), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed configuring dataengine on Notebook node.", str(err))
        sys.exit(1)


# Main function for installing additional libraries for notebook
def install_libs():
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'],
                                               os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] + "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)

    try:
        subprocess.run("~/scripts/{}.py".format('notebook_install_libs'), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed installing additional libs for Notebook node.", str(err))
        sys.exit(1)


# Main function for get available libraries for notebook
def list_libs():
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'],
                                               os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] + "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)

    try:
        subprocess.run("~/scripts/{}.py".format('notebook_list_libs'), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed get available libraries for notebook node.", str(err))
        sys.exit(1)


# Main function for manage git credentials on notebook
def git_creds():
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'],
                                               os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] + "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)

    try:
        subprocess.run("~/scripts/{}.py".format('notebook_git_creds'), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed to manage git credentials for notebook node.", str(err))
        sys.exit(1)


# Main function for creating image from notebook
def create_image():
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'],
                                               os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] + "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)

    try:
        subprocess.run("~/scripts/{}.py".format('common_create_notebook_image'), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed to create image from notebook node.", str(err))
        sys.exit(1)


# Main function for deleting existing notebook image
def terminate_image():
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'],
                                               os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] + "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)

    try:
        subprocess.run("~/scripts/{}.py".format('common_terminate_notebook_image'), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed to create image from notebook node.", str(err))
        sys.exit(1)


# Main function for reconfiguring Spark for notebook
def reconfigure_spark():
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'],
                                               os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] + "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)

    try:
        subprocess.run("~/scripts/{}.py".format('notebook_reconfigure_spark'), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed to reconfigure Spark for Notebook node.", str(err))
        sys.exit(1)

# Main function for checking inactivity status
def check_inactivity():
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'],
                                               os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] + "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)

    try:
        subprocess.run("~/scripts/{}.py".format('notebook_inactivity_check'), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed to check inactivity status.", str(err))
        sys.exit(1)