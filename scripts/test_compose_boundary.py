import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "boundary", Path(__file__).with_name("check-compose-boundary.py")
)
boundary = importlib.util.module_from_spec(spec)
spec.loader.exec_module(boundary)


class LocalBoundaryTests(unittest.TestCase):
    def test_ipv4_and_ipv6_loopback_are_allowed(self):
        self.assertEqual(
            boundary.boundary_errors(
                {
                    "services": {
                        "api": {"ports": [{"host_ip": "127.0.0.1"}, {"host_ip": "::1"}]}
                    }
                }
            ),
            [],
        )

    def test_unpublished_internal_services_are_allowed(self):
        self.assertEqual(boundary.boundary_errors({"services": {"database": {}}}), [])

    def test_wildcard_implicit_and_lan_bindings_are_rejected(self):
        for address in [None, "", "0.0.0.0", "::", "192.168.1.10"]:
            with self.subTest(address=address):
                self.assertTrue(
                    boundary.boundary_errors(
                        {"services": {"api": {"ports": [{"host_ip": address}]}}}
                    )
                )

    def test_shared_network_namespace_bypass_is_rejected(self):
        for mode in ["host", "container:external-host-network", "service:external"]:
            with self.subTest(mode=mode):
                self.assertTrue(
                    boundary.boundary_errors(
                        {"services": {"api": {"network_mode": mode}}}
                    )
                )


if __name__ == "__main__":
    unittest.main()
