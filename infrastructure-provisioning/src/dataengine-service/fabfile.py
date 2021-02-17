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
from fabric import *


def run():
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'],
                                               os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] + "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.INFO,
                        filename=local_log_filepath)
    dataengine_service_config = dict()
    dataengine_service_config['uuid'] = str(uuid.uuid4())[:5]
    try:
        subprocess.run("~/scripts/{}.py --uuid {}".format('dataengine-service_prepare', dataengine_service_config['uuid']), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed preparing Data Engine service.", str(err))
        sys.exit(1)

    try:
        subprocess.run("~/scripts/{}.py --uuid {}".format('dataengine-service_configure', dataengine_service_config['uuid']), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed configuring Data Engine service.", str(err))
        sys.exit(1)


# Main function for installing additional libraries for Dataengine
def install_libs():
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'],
                                               os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] + "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)

    try:
        subprocess.run("~/scripts/{}.py".format('dataengine-service_install_libs'), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed installing additional libs for DataEngine service.", str(err))
        sys.exit(1)


# Main function for get available libraries for Data Engine
def list_libs():
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'],
                                               os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] + "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)

    try:
        subprocess.run("~/scripts/{}.py".format('dataengine-service_list_libs'), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed get available libraries for Data Engine service.", str(err))
        sys.exit(1)


def terminate():
    local_log_filename = "{}_{}_{}.log".format(os.environ['conf_resource'], os.environ['edge_user_name'], os.environ['request_id'])
    local_log_filepath = "/logs/" + os.environ['conf_resource'] +  "/" + local_log_filename
    logging.basicConfig(format='%(levelname)-8s [%(asctime)s]  %(message)s',
                        level=logging.DEBUG,
                        filename=local_log_filepath)

    try:
        subprocess.run("~/scripts/{}.py".format('dataengine-service_terminate'), shell=True, check=True)
    except Exception as err:
        traceback.print_exc()
        append_result("Failed configuring Notebook node.", str(err))
        sys.exit(1)
