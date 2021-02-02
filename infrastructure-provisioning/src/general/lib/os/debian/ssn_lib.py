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

import crypt
import json
import os
import sys
import traceback
from datalab.common_lib import manage_pkg
from datalab.fab import *
from datalab.meta_lib import *
from fabric.api import *


def ensure_docker_daemon(datalab_path, os_user, region):
    try:
        if not exists(datalab_path + 'tmp/docker_daemon_ensured'):
            docker_version = os.environ['ssn_docker_version']
            conn.sudo('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -')
            conn.sudo('add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) \
                  stable"')
            manage_pkg('update', 'remote', '')
            conn.sudo('apt-cache policy docker-ce')
            manage_pkg('-y install', 'remote', 'docker-ce=5:{}~3-0~ubuntu-focal'.format(docker_version))
            conn.sudo('usermod -a -G docker ' + os_user)
            conn.sudo('update-rc.d docker defaults')
            conn.sudo('update-rc.d docker enable')
            conn.sudo('touch ' + datalab_path + 'tmp/docker_daemon_ensured')
        return True
    except:
        return False


def ensure_nginx(datalab_path):
    try:
        if not exists(datalab_path + 'tmp/nginx_ensured'):
            manage_pkg('-y install', 'remote', 'nginx')
            conn.sudo('service nginx restart')
            conn.sudo('update-rc.d nginx defaults')
            conn.sudo('update-rc.d nginx enable')
            conn.sudo('touch ' + datalab_path + 'tmp/nginx_ensured')
    except Exception as err:
        traceback.print_exc()
        print('Failed to ensure Nginx: ', str(err))
        sys.exit(1)


def ensure_jenkins(datalab_path):
    try:
        if not exists(datalab_path + 'tmp/jenkins_ensured'):
            conn.sudo('wget -q -O - https://pkg.jenkins.io/debian/jenkins-ci.org.key | apt-key add -')
            conn.sudo('echo deb http://pkg.jenkins.io/debian-stable binary/ > /etc/apt/sources.list.d/jenkins.list')
            manage_pkg('-y update', 'remote', '')
            manage_pkg('-y install', 'remote', 'jenkins')
            conn.sudo('touch ' + datalab_path + 'tmp/jenkins_ensured')
    except Exception as err:
        traceback.print_exc()
        print('Failed to ensure Jenkins: ', str(err))
        sys.exit(1)


def configure_jenkins(datalab_path, os_user, config, tag_resource_id):
    try:
        if not exists(datalab_path + 'tmp/jenkins_configured'):
            conn.sudo('echo \'JENKINS_ARGS="--prefix=/jenkins --httpPort=8070"\' >> /etc/default/jenkins')
            conn.sudo('rm -rf /var/lib/jenkins/*')
            conn.sudo('mkdir -p /var/lib/jenkins/jobs/')
            conn.sudo('chown -R ' + os_user + ':' + os_user + ' /var/lib/jenkins/')
            conn.put('/root/templates/jenkins_jobs/*', '/var/lib/jenkins/jobs/')
            conn.sudo(
                "find /var/lib/jenkins/jobs/ -type f | xargs sed -i \'s/OS_USR/{}/g; s/SBN/{}/g; s/CTUN/{}/g; s/SGI/{}/g; s/VPC/{}/g; s/SNI/{}/g; s/AKEY/{}/g\'".format(
                    os_user, config['service_base_name'], tag_resource_id, config['security_group_id'],
                    config['vpc_id'], config['subnet_id'], config['admin_key']))
            conn.sudo('chown -R jenkins:jenkins /var/lib/jenkins')
            conn.sudo('/etc/init.d/jenkins stop; sleep 5')
            conn.sudo('systemctl enable jenkins')
            conn.sudo('systemctl start jenkins')
            conn.sudo('touch ' + datalab_path + '/tmp/jenkins_configured')
            conn.sudo('echo "jenkins ALL = NOPASSWD:ALL" >> /etc/sudoers')
    except Exception as err:
        traceback.print_exc()
        print('Failed to configure Jenkins: ', str(err))
        sys.exit(1)


def configure_nginx(config, datalab_path, hostname):
    try:
        random_file_part = id_generator(size=20)
        if not exists("/etc/nginx/conf.d/nginx_proxy.conf"):
            conn.sudo('useradd -r nginx')
            conn.sudo('rm -f /etc/nginx/conf.d/*')
            conn.put(config['nginx_template_dir'] + 'ssn_nginx.conf', '/tmp/nginx.conf')
            conn.put(config['nginx_template_dir'] + 'nginx_proxy.conf', '/tmp/nginx_proxy.conf')
            conn.sudo("sed -i 's|SSN_HOSTNAME|" + hostname + "|' /tmp/nginx_proxy.conf")
            conn.sudo('mv /tmp/nginx.conf ' + datalab_path + 'tmp/')
            conn.sudo('mv /tmp/nginx_proxy.conf ' + datalab_path + 'tmp/')
            conn.sudo('\cp ' + datalab_path + 'tmp/nginx.conf /etc/nginx/')
            conn.sudo('\cp ' + datalab_path + 'tmp/nginx_proxy.conf /etc/nginx/conf.d/')
            conn.sudo('mkdir -p /etc/nginx/locations')
            conn.sudo('rm -f /etc/nginx/sites-enabled/default')
    except Exception as err:
        traceback.print_exc()
        print('Failed to configure Nginx: ', str(err))
        sys.exit(1)

    try:
        if not exists("/etc/nginx/locations/proxy_location_jenkins.conf"):
            nginx_password = id_generator()
            template_file = config['nginx_template_dir'] + 'proxy_location_jenkins_template.conf'
            with open("/tmp/%s-tmpproxy_location_jenkins_template.conf" % random_file_part, 'w') as out:
                with open(template_file) as tpl:
                    for line in tpl:
                        out.write(line)
            conn.put("/tmp/%s-tmpproxy_location_jenkins_template.conf" % random_file_part,
                '/tmp/proxy_location_jenkins.conf')
            conn.sudo('mv /tmp/proxy_location_jenkins.conf ' + os.environ['ssn_datalab_path'] + 'tmp/')
            conn.sudo('\cp ' + os.environ['ssn_datalab_path'] + 'tmp/proxy_location_jenkins.conf /etc/nginx/locations/')
            conn.sudo("echo 'engineer:" + crypt.crypt(nginx_password, id_generator()) + "' > /etc/nginx/htpasswd")
            with open('jenkins_creds.txt', 'w+') as f:
                f.write("Jenkins credentials: engineer  / " + nginx_password)
    except:
        return False

    try:
        conn.sudo('service nginx reload')
        return True
    except:
        return False


def ensure_supervisor():
    try:
        if not exists(os.environ['ssn_datalab_path'] + 'tmp/superv_ensured'):
            manage_pkg('-y install', 'remote', 'supervisor')
            conn.sudo('update-rc.d supervisor defaults')
            conn.sudo('update-rc.d supervisor enable')
            conn.sudo('touch ' + os.environ['ssn_datalab_path'] + 'tmp/superv_ensured')
    except Exception as err:
        traceback.print_exc()
        print('Failed to install Supervisor: ', str(err))
        sys.exit(1)


def ensure_mongo():
    try:
        if not exists(os.environ['ssn_datalab_path'] + 'tmp/mongo_ensured'):
            conn.sudo('wget -qO - https://www.mongodb.org/static/pgp/server-4.4.asc | apt-key add -')
            conn.sudo('ver=`lsb_release -cs`; echo "deb [ arch=amd64,arm64 ] https://repo.mongodb.org/apt/ubuntu '
                 '$ver/mongodb-org/4.4 multiverse" | sudo tee /etc/apt/sources.list.d/mongodb-org-4.4.list; '
                 'apt update')
            manage_pkg('-y install', 'remote', 'mongodb-org')
            conn.sudo('systemctl enable mongod.service')
            conn.sudo('touch ' + os.environ['ssn_datalab_path'] + 'tmp/mongo_ensured')
    except Exception as err:
        traceback.print_exc()
        print('Failed to install MongoDB: ', str(err))
        sys.exit(1)


def start_ss(keyfile, host_string, datalab_conf_dir, web_path,
             os_user, mongo_passwd, keystore_passwd, cloud_provider,
             service_base_name, tag_resource_id, billing_tag, account_id, billing_bucket,
             aws_job_enabled, datalab_path, billing_enabled, cloud_params,
             authentication_file, offer_number, currency,
             locale, region_info, ldap_login, tenant_id,
             application_id, hostname, data_lake_name, subscription_id,
             validate_permission_scope, datalab_id, usage_date, product,
             usage_type, usage, cost, resource_id, tags, billing_dataset_name, keycloak_client_id,
             keycloak_client_secret, keycloak_auth_server_url, report_path=''):
    try:
        if not exists(os.environ['ssn_datalab_path'] + 'tmp/ss_started'):
            java_path = conn.sudo("update-alternatives --query java | grep 'Value: ' | grep -o '/.*/jre'")
            supervisor_conf = '/etc/supervisor/conf.d/supervisor_svc.conf'
            local('sed -i "s|MONGO_PASSWORD|{}|g" /root/templates/ssn.yml'.format(mongo_passwd))
            local('sed -i "s|KEYSTORE_PASSWORD|{}|g" /root/templates/ssn.yml'.format(keystore_passwd))
            local('sed -i "s|CLOUD_PROVIDER|{}|g" /root/templates/ssn.yml'.format(cloud_provider))
            local('sed -i "s|\${JRE_HOME}|' + java_path + '|g" /root/templates/ssn.yml')
            conn.sudo('sed -i "s|KEYNAME|{}|g" {}/webapp/provisioning-service/conf/provisioning.yml'.
                 format(os.environ['conf_key_name'], datalab_path))
            conn.put('/root/templates/ssn.yml', '/tmp/ssn.yml')
            conn.sudo('mv /tmp/ssn.yml ' + os.environ['ssn_datalab_path'] + 'conf/')
            conn.put('/root/templates/proxy_location_webapp_template.conf', '/tmp/proxy_location_webapp_template.conf')
            conn.sudo('mv /tmp/proxy_location_webapp_template.conf ' + os.environ['ssn_datalab_path'] + 'tmp/')
            if cloud_provider == 'aws':
                conf_parameter_name = '--spring.config.location={0}billing_app.yml --conf '.format(datalab_conf_dir)
                with open('/root/templates/supervisor_svc.conf', 'r') as f:
                    text = f.read()
                text = text.replace('WEB_CONF', datalab_conf_dir).replace('OS_USR', os_user) \
                    .replace('CONF_PARAMETER_NAME', conf_parameter_name)
                with open('/root/templates/supervisor_svc.conf', 'w') as f:
                    f.write(text)
            elif cloud_provider == 'gcp' or cloud_provider == 'azure':
                conf_parameter_name = '--spring.config.location='
                with open('/root/templates/supervisor_svc.conf', 'r') as f:
                    text = f.read()
                text = text.replace('WEB_CONF', datalab_conf_dir).replace('OS_USR', os_user) \
                    .replace('CONF_PARAMETER_NAME', conf_parameter_name)
                with open('/root/templates/supervisor_svc.conf', 'w') as f:
                    f.write(text)
            conn.put('/root/templates/supervisor_svc.conf', '/tmp/supervisor_svc.conf')
            conn.sudo('mv /tmp/supervisor_svc.conf ' + os.environ['ssn_datalab_path'] + 'tmp/')
            conn.sudo('cp ' + os.environ['ssn_datalab_path'] +
                 'tmp/proxy_location_webapp_template.conf /etc/nginx/locations/proxy_location_webapp.conf')
            conn.sudo('cp ' + os.environ['ssn_datalab_path'] + 'tmp/supervisor_svc.conf {}'.format(supervisor_conf))
            conn.sudo('sed -i \'s=WEB_APP_DIR={}=\' {}'.format(web_path, supervisor_conf))
            try:
                conn.sudo('mkdir -p /var/log/application')
                conn.run('mkdir -p /tmp/yml_tmp/')
                for service in ['self-service', 'provisioning-service', 'billing']:
                    jar = conn.sudo('cd {0}{1}/lib/; find {1}*.jar -type f'.format(web_path, service))
                    conn.sudo('ln -s {0}{2}/lib/{1} {0}{2}/{2}.jar '.format(web_path, jar, service))
                    conn.sudo('cp {0}/webapp/{1}/conf/*.yml /tmp/yml_tmp/'.format(datalab_path, service))
                # Replacing Keycloak and cloud parameters
                for item in json.loads(cloud_params):
                    if "KEYCLOAK_" in item['key']:
                        conn.sudo('sed -i "s|{0}|{1}|g" /tmp/yml_tmp/self-service.yml'.format(
                            item['key'], item['value']))
                    conn.sudo('sed -i "s|{0}|{1}|g" /tmp/yml_tmp/provisioning.yml'.format(
                        item['key'], item['value']))
                conn.sudo('sed -i "s|SERVICE_BASE_NAME|{0}|g" /tmp/yml_tmp/self-service.yml'.format(service_base_name))
                conn.sudo('sed -i "s|OPERATION_SYSTEM|debian|g" /tmp/yml_tmp/self-service.yml')
                conn.sudo('sed -i "s|<SSN_INSTANCE_SIZE>|{0}|g" /tmp/yml_tmp/self-service.yml'.format(
                    os.environ['{0}_ssn_instance_size'.format(os.environ['conf_cloud_provider'])]))
                if cloud_provider == 'azure':
                    conn.sudo('sed -i "s|<LOGIN_USE_LDAP>|{0}|g" /tmp/yml_tmp/self-service.yml'.format(ldap_login))
                    conn.sudo('sed -i "s|<LOGIN_TENANT_ID>|{0}|g" /tmp/yml_tmp/self-service.yml'.format(tenant_id))
                    conn.sudo('sed -i "s|<LOGIN_APPLICATION_ID>|{0}|g" /tmp/yml_tmp/self-service.yml'.format(application_id))
                    conn.sudo('sed -i "s|<DATALAB_SUBSCRIPTION_ID>|{0}|g" /tmp/yml_tmp/self-service.yml'.format(
                        subscription_id))
                    conn.sudo('sed -i "s|<MANAGEMENT_API_AUTH_FILE>|{0}|g" /tmp/yml_tmp/self-service.yml'.format(
                        authentication_file))
                    conn.sudo('sed -i "s|<VALIDATE_PERMISSION_SCOPE>|{0}|g" /tmp/yml_tmp/self-service.yml'.format(
                        validate_permission_scope))
                    conn.sudo('sed -i "s|<LOGIN_APPLICATION_REDIRECT_URL>|{0}|g" /tmp/yml_tmp/self-service.yml'.format(
                        hostname))
                    conn.sudo('sed -i "s|<LOGIN_PAGE>|{0}|g" /tmp/yml_tmp/self-service.yml'.format(hostname))
                    # if os.environ['azure_datalake_enable'] == 'true':
                    #     permission_scope = 'subscriptions/{}/resourceGroups/{}/providers/Microsoft.DataLakeStore/accounts/{}/providers/Microsoft.Authorization/'.format(
                    #         subscription_id, service_base_name, data_lake_name)
                    # else:
                    #     permission_scope = 'subscriptions/{}/resourceGroups/{}/providers/Microsoft.Authorization/'.format(
                    #         subscription_id, service_base_name
                    #     )
                conn.sudo('mv /tmp/yml_tmp/* ' + datalab_conf_dir)
                conn.sudo('rmdir /tmp/yml_tmp/')
            except:
                append_result("Unable to upload webapp jars")
                sys.exit(1)
            if billing_enabled:
                local('scp -i {} /root/scripts/configure_billing.py {}:/tmp/configure_billing.py'.format(keyfile,
                                                                                                         host_string))
                params = '--cloud_provider {} ' \
                         '--infrastructure_tag {} ' \
                         '--tag_resource_id {} ' \
                         '--billing_tag {} ' \
                         '--account_id {} ' \
                         '--billing_bucket {} ' \
                         '--aws_job_enabled {} ' \
                         '--report_path "{}" ' \
                         '--mongo_password {} ' \
                         '--datalab_dir {} ' \
                         '--authentication_file "{}" ' \
                         '--offer_number {} ' \
                         '--currency {} ' \
                         '--locale {} ' \
                         '--region_info {} ' \
                         '--datalab_id {} ' \
                         '--usage_date {} ' \
                         '--product {} ' \
                         '--usage_type {} ' \
                         '--usage {} ' \
                         '--cost {} ' \
                         '--resource_id {} ' \
                         '--tags {} ' \
                         '--billing_dataset_name "{}" ' \
                         '--mongo_host localhost ' \
                         '--mongo_port 27017 ' \
                         '--service_base_name {} ' \
                         '--os_user {} ' \
                         '--keystore_password {} ' \
                         '--keycloak_client_id {} ' \
                         '--keycloak_client_secret {} ' \
                         '--keycloak_auth_server_url {} '.\
                            format(cloud_provider,
                                   service_base_name,
                                   tag_resource_id,
                                   billing_tag,
                                   account_id,
                                   billing_bucket,
                                   aws_job_enabled,
                                   report_path,
                                   mongo_passwd,
                                   datalab_path,
                                   authentication_file,
                                   offer_number,
                                   currency,
                                   locale,
                                   region_info,
                                   datalab_id,
                                   usage_date,
                                   product,
                                   usage_type,
                                   usage,
                                   cost,
                                   resource_id,
                                   tags,
                                   billing_dataset_name,
                                   service_base_name,
                                   os_user,
                                   keystore_passwd,
                                   keycloak_client_id,
                                   keycloak_client_secret,
                                   keycloak_auth_server_url)
                conn.sudo('python3 /tmp/configure_billing.py {}'.format(params))
            try:
                if os.environ['conf_stepcerts_enabled'] == 'true':
                    conn.sudo(
                        'openssl pkcs12 -export -in /etc/ssl/certs/datalab.crt -inkey /etc/ssl/certs/datalab.key -name ssn '
                        '-out ssn.p12 -password pass:{0}'.format(keystore_passwd))
                    conn.sudo('keytool -importkeystore -srckeystore ssn.p12 -srcstoretype PKCS12 -alias ssn -destkeystore '
                         '/home/{0}/keys/ssn.keystore.jks -deststorepass "{1}" -srcstorepass "{1}"'.format(
                        os_user, keystore_passwd))
                    conn.sudo('keytool -keystore /home/{0}/keys/ssn.keystore.jks -alias step-ca -import -file '
                         '/etc/ssl/certs/root_ca.crt  -deststorepass "{1}" -srcstorepass "{1}" -noprompt'.format(
                          os_user, keystore_passwd))
                    conn.sudo('keytool -importcert -trustcacerts -alias step-ca -file /etc/ssl/certs/root_ca.crt '
                         '-noprompt -storepass changeit -keystore {1}/lib/security/cacerts'.format(os_user, java_path))
                    conn.sudo('keytool -importcert -trustcacerts -alias ssn -file /etc/ssl/certs/datalab.crt -noprompt '
                         '-storepass changeit -keystore {0}/lib/security/cacerts'.format(java_path))
                else:
                    conn.sudo('keytool -genkeypair -alias ssn -keyalg RSA -validity 730 -storepass {1} -keypass {1} \
                         -keystore /home/{0}/keys/ssn.keystore.jks -keysize 2048 -dname "CN=localhost"'.format(
                        os_user, keystore_passwd))
                    conn.sudo('keytool -exportcert -alias ssn -storepass {1} -file /etc/ssl/certs/datalab.crt \
                         -keystore /home/{0}/keys/ssn.keystore.jks'.format(os_user, keystore_passwd))
                    conn.sudo('keytool -importcert -trustcacerts -alias ssn -file /etc/ssl/certs/datalab.crt -noprompt \
                         -storepass changeit -keystore {1}/lib/security/cacerts'.format(os_user, java_path))
            except:
                append_result("Unable to generate cert and copy to java keystore")
                sys.exit(1)
            conn.sudo('service supervisor start')
            conn.sudo('service nginx restart')
            conn.sudo('service supervisor restart')
            conn.sudo('touch ' + os.environ['ssn_datalab_path'] + 'tmp/ss_started')
    except Exception as err:
        traceback.print_exc()
        print('Failed to start Self-service: ', str(err))
        sys.exit(1)


def install_build_dep():
    try:
        if not exists('{}tmp/build_dep_ensured'.format(os.environ['ssn_datalab_path'])):
            maven_version = '3.5.4'
            manage_pkg('-y install', 'remote', 'openjdk-8-jdk git wget unzip')
            with cd('/opt/'):
                conn.sudo(
                    'wget http://mirrors.sonic.net/apache/maven/maven-{0}/{1}/binaries/apache-maven-{1}-bin.zip'.format(
                        maven_version.split('.')[0], maven_version))
                conn.sudo('unzip apache-maven-{}-bin.zip'.format(maven_version))
                conn.sudo('mv apache-maven-{} maven'.format(maven_version))
            conn.sudo('bash -c "curl --silent --location https://deb.nodesource.com/setup_12.x | bash -"')
            manage_pkg('-y install', 'remote', 'nodejs')
            conn.sudo('npm config set unsafe-perm=true')
            conn.sudo('touch {}tmp/build_dep_ensured'.format(os.environ['ssn_datalab_path']))
    except Exception as err:
        traceback.print_exc()
        print('Failed to install build dependencies for UI: ', str(err))
        sys.exit(1)
