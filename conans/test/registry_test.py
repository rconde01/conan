import unittest
import os
from conans.test.utils.test_files import temp_folder
from conans.client.remote_registry import RemoteRegistry
from conans.model.ref import ConanFileReference
from conans.errors import ConanException
from conans.test.tools import TestBufferConanOutput
from conans.util.files import save


class RegistryTest(unittest.TestCase):

    def retro_compatibility_test(self):
        f = os.path.join(temp_folder(), "aux_file")
        save(f, """conan.io https://server.conan.io
""")  # Without SSL parameter
        registry = RemoteRegistry(f, TestBufferConanOutput())
        self.assertEqual(registry.remotes, [("conan.io", "https://server.conan.io", True)])

    def add_remove_update_test(self):
        f = os.path.join(temp_folder(), "aux_file")
        registry = RemoteRegistry(f, TestBufferConanOutput())

        # Add
        registry.add("local", "http://localhost:9300")
        self.assertEqual(registry.remotes, [("conan.io", "https://server.conan.io", True),
                                            ("local", "http://localhost:9300", True)])
        # Add
        registry.add("new", "new_url", False)
        self.assertEqual(registry.remotes, [("conan.io", "https://server.conan.io", True),
                                            ("local", "http://localhost:9300", True),
                                            ("new", "new_url", False)])
        with self.assertRaises(ConanException):
            registry.add("new", "new_url")
        # Update
        registry.update("new", "other_url")
        self.assertEqual(registry.remotes, [("conan.io", "https://server.conan.io", True),
                                            ("local", "http://localhost:9300", True),
                                            ("new", "other_url", True)])
        with self.assertRaises(ConanException):
            registry.update("new2", "new_url")

        registry.update("new", "other_url", False)
        self.assertEqual(registry.remotes, [("conan.io", "https://server.conan.io", True),
                                            ("local", "http://localhost:9300", True),
                                            ("new", "other_url", False)])

        # Remove
        registry.remove("local")
        self.assertEqual(registry.remotes, [("conan.io", "https://server.conan.io", True),
                                            ("new", "other_url", False)])
        with self.assertRaises(ConanException):
            registry.remove("new2")

    def refs_test(self):
        f = os.path.join(temp_folder(), "aux_file")
        registry = RemoteRegistry(f, TestBufferConanOutput())
        ref = ConanFileReference.loads("MyLib/0.1@lasote/stable")

        remotes = registry.remotes
        registry.set_ref(ref, remotes[0])
        remote = registry.get_ref(ref)
        self.assertEqual(remote, remotes[0])

        registry.set_ref(ref, remotes[0])
        remote = registry.get_ref(ref)
        self.assertEqual(remote, remotes[0])
