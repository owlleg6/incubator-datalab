/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *   http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing,
 * software distributed under the License is distributed on an
 * "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
 * KIND, either express or implied.  See the License for the
 * specific language governing permissions and limitations
 * under the License.
 */

package com.epam.datalab.module.aws;

import com.epam.datalab.core.AdapterBase.Mode;
import com.epam.datalab.module.ModuleName;
import org.junit.Test;

import static junit.framework.TestCase.assertEquals;

public class AdapterS3FileTest {

    @Test
    public void config() {
        AdapterS3File adapter = new AdapterS3File();
        adapter.setMode(Mode.READ);
        adapter.setWriteHeader(true);
        adapter.setBucket("bucket");
        adapter.setPath("path");
        adapter.setAccountId("accountId");
        adapter.setAccessKeyId("accessKeyId");
        adapter.setSecretAccessKey("secretAccessKey");

        assertEquals(ModuleName.ADAPTER_S3_FILE, adapter.getType());
        assertEquals(Mode.READ, adapter.getMode());
        assertEquals(true, adapter.isWriteHeader());
        assertEquals("bucket", adapter.getBucket());
        assertEquals("path", adapter.getPath());
        assertEquals("accountId", adapter.getAccountId());
        assertEquals("accessKeyId", adapter.getAccessKeyId());
        assertEquals("secretAccessKey", adapter.getSecretAccessKey());
    }
}
