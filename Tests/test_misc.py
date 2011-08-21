# Copyright (c) 2011, Yubico AB
# All rights reserved.

import sys
import unittest
import pyhsm

import test_common

class TestUtil(test_common.YHSM_TestCase):

    def setUp(self):
        test_common.YHSM_TestCase.setUp(self)

    def test_using_disabled_keyhandle(self):
        """ Test using a disabled key handle. """
        if not self.hsm.version.have_keydisable():
            return None
        # HSM> < keyload - Load key data now using flags ffffffff. Press ESC to quit
        # 00002001 - stored ok
        # HSM> < keydis 2001
        try:
            res = self.hsm.aes_ecb_encrypt(0x2001, "klartext")
            self.fail("Expected YSM_FUNCTION_DISABLED, got %s" % (res))
        except pyhsm.exception.YHSM_CommandFailed, e:
            self.assertEquals(e.status, pyhsm.defines.YSM_FUNCTION_DISABLED)

    def test_keystore_unlock(self):
        """ Test locking and then unlocking keystore. """
        cleartext = "reference"
        res_before = self.hsm.aes_ecb_encrypt(0x2000, cleartext)
        # lock key store
        try:
            res = self.hsm.key_storage_unlock("A" * 8)
            self.fail("Expected YSM_MISMATCH/YSM_KEY_STORAGE_LOCKED, got %s" % (res))
        except pyhsm.exception.YHSM_CommandFailed, e:
            if self.hsm.version.have_key_store_decrypt():
                self.assertEquals(e.status, pyhsm.defines.YSM_MISMATCH)
            else:
                self.assertEquals(e.status, pyhsm.defines.YSM_KEY_STORAGE_LOCKED)
        # make sure we can't AES encrypt when keystore is locked
        try:
            res = self.hsm.aes_ecb_encrypt(0x2000, cleartext)
            self.fail("Expected YSM_KEY_STORAGE_LOCKED, got %s (before lock: %s)" \
                          % (res.encode("hex"), res_before.encode("hex")))
        except pyhsm.exception.YHSM_CommandFailed, e:
            self.assertEquals(e.status, pyhsm.defines.YSM_KEY_STORAGE_LOCKED)
        # unlock key store with correct passphrase
        self.assertTrue(self.hsm.key_storage_unlock(test_common.HsmPassphrase.decode("hex")))
        # make sure it is properly unlocked
        res_after = self.hsm.aes_ecb_encrypt(0x2000, cleartext)
        self.assertEquals(res_before, res_after)
