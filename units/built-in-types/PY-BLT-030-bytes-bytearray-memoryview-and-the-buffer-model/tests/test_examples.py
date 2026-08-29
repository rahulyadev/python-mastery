"""Deterministic checks for the PY-BLT-030 learning artifacts."""

from __future__ import annotations

from array import array
from pathlib import Path
import sys
import unittest


UNIT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(UNIT_ROOT / "examples"))
sys.path.insert(
    0,
    str(
        UNIT_ROOT
        / "experiments"
        / "EXP-01-aliasing-metadata-and-view-lifetime"
    ),
)

import binary_protocol  # noqa: E402
import buffer_alias_probe  # noqa: E402
import buffer_operations  # noqa: E402


class BinaryProtocolTests(unittest.TestCase):
    def test_utf8_round_trip_keeps_code_point_and_byte_lengths_distinct(self) -> None:
        encoded = binary_protocol.encode_text_frame("A\u00e9")
        decoded = binary_protocol.decode_text_frame(encoded)

        self.assertEqual(encoded, b"\x01\x00\x03A\xc3\xa9")
        self.assertEqual(len("A\u00e9"), 2)
        self.assertEqual(decoded.payload_size, 3)
        self.assertEqual(decoded.text, "A\u00e9")

    def test_empty_payload_is_valid(self) -> None:
        encoded = binary_protocol.encode_text_frame("")

        self.assertEqual(encoded, b"\x01\x00\x00")
        self.assertEqual(
            binary_protocol.decode_text_frame(encoded),
            binary_protocol.TextFrame(version=1, text="", payload_size=0),
        )

    def test_decoder_accepts_distinct_buffer_exporters(self) -> None:
        encoded = binary_protocol.encode_text_frame("ok")

        for exporter in (
            encoded,
            bytearray(encoded),
            memoryview(encoded),
            array("B", encoded),
        ):
            with self.subTest(exporter=type(exporter).__name__):
                self.assertEqual(
                    binary_protocol.decode_text_frame(exporter).text,
                    "ok",
                )

    def test_text_is_not_silently_accepted_as_binary_data(self) -> None:
        with self.assertRaisesRegex(TypeError, "buffer protocol"):
            binary_protocol.decode_text_frame("\x01\x00\x00")

    def test_encoder_requires_text_and_bounds_encoded_size(self) -> None:
        with self.assertRaisesRegex(TypeError, "text must be str"):
            binary_protocol.encode_text_frame(b"text")  # type: ignore[arg-type]
        with self.assertRaisesRegex(binary_protocol.FrameError, "exceeds"):
            binary_protocol.encode_text_frame("x" * 65_536)

    def test_short_header_is_rejected(self) -> None:
        with self.assertRaisesRegex(binary_protocol.FrameError, "shorter"):
            binary_protocol.decode_text_frame(b"\x01\x00")

    def test_declared_length_must_match_the_complete_frame(self) -> None:
        for malformed in (b"\x01\x00\x02x", b"\x01\x00\x01xy"):
            with self.subTest(malformed=malformed), self.assertRaisesRegex(
                binary_protocol.FrameError,
                "length mismatch",
            ):
                binary_protocol.decode_text_frame(malformed)

    def test_version_and_utf8_contracts_are_enforced(self) -> None:
        with self.assertRaisesRegex(binary_protocol.FrameError, "version"):
            binary_protocol.decode_text_frame(b"\x02\x00\x00")
        with self.assertRaisesRegex(binary_protocol.FrameError, "valid UTF-8"):
            binary_protocol.decode_text_frame(b"\x01\x00\x01\xff")

    def test_non_contiguous_view_is_rejected_explicitly(self) -> None:
        frame = binary_protocol.encode_text_frame("hello")
        strided = memoryview(frame)[::2]
        try:
            with self.assertRaisesRegex(binary_protocol.FrameError, "C-contiguous"):
                binary_protocol.decode_text_frame(strided)
        finally:
            strided.release()


class BufferOperationTests(unittest.TestCase):
    def test_metadata_distinguishes_readonly_and_element_width(self) -> None:
        immutable = buffer_operations.describe_buffer(b"abc")
        mutable = buffer_operations.describe_buffer(bytearray(b"abc"))
        words = buffer_operations.describe_buffer(array("H", [1, 2, 3]))

        self.assertTrue(immutable.readonly)
        self.assertFalse(mutable.readonly)
        self.assertEqual(immutable.itemsize, 1)
        self.assertEqual(words.itemsize, array("H").itemsize)
        self.assertEqual(words.nbytes, 3 * words.itemsize)

    def test_bytearray_slice_copies_but_memoryview_slice_aliases(self) -> None:
        exporter = bytearray(b"abcdef")
        copied = exporter[1:4]
        view = memoryview(exporter)[1:4]
        try:
            view[0] = ord("X")
            exporter[2] = ord("Y")

            self.assertEqual(exporter, bytearray(b"aXYdef"))
            self.assertEqual(copied, bytearray(b"bcd"))
            self.assertEqual(view.tobytes(), b"XYd")
        finally:
            view.release()

    def test_readonly_view_is_a_permission_not_a_snapshot(self) -> None:
        exporter = bytearray(b"abc")
        writable = memoryview(exporter)
        readonly = writable.toreadonly()
        try:
            writable[0] = ord("z")
            self.assertEqual(readonly.tobytes(), b"zbc")
            with self.assertRaises(TypeError):
                readonly[0] = ord("x")
        finally:
            readonly.release()
            writable.release()

    def test_resize_is_blocked_until_the_view_is_released(self) -> None:
        exporter = bytearray(b"abc")
        view = memoryview(exporter)

        with self.assertRaises(BufferError):
            exporter.append(0)
        view.release()
        exporter.append(0)

        self.assertEqual(exporter, bytearray(b"abc\x00"))
        with self.assertRaises(ValueError):
            view[0]

    def test_overwrite_window_mutates_without_resizing(self) -> None:
        exporter = bytearray(b"HEADsecretTAIL")

        buffer_operations.overwrite_window(exporter, 4, b"******")

        self.assertEqual(exporter, bytearray(b"HEAD******TAIL"))
        self.assertEqual(len(exporter), 14)

    def test_overwrite_validates_permissions_shape_and_bounds(self) -> None:
        with self.assertRaisesRegex(TypeError, "writable"):
            buffer_operations.overwrite_window(b"abc", 0, b"x")
        with self.assertRaisesRegex(TypeError, "plain integer"):
            buffer_operations.overwrite_window(bytearray(b"abc"), True, b"x")
        with self.assertRaisesRegex(TypeError, "replacement must be bytes"):
            buffer_operations.overwrite_window(
                bytearray(b"abc"),
                0,
                bytearray(b"x"),  # type: ignore[arg-type]
            )
        with self.assertRaisesRegex(ValueError, "out of bounds"):
            buffer_operations.overwrite_window(bytearray(b"abc"), 2, b"xy")

    def test_checksum_accepts_multiple_contiguous_exporters(self) -> None:
        expected = (1 + 2 + 255) % 256

        self.assertEqual(buffer_operations.checksum_octets(b"\x01\x02\xff"), expected)
        self.assertEqual(
            buffer_operations.checksum_octets(array("B", [1, 2, 255])),
            expected,
        )

    def test_non_contiguous_input_is_rejected_by_octet_consumer(self) -> None:
        view = memoryview(b"abcdef")[::2]
        try:
            with self.assertRaisesRegex(ValueError, "C-contiguous"):
                buffer_operations.checksum_octets(view)
        finally:
            view.release()


class ExperimentTests(unittest.TestCase):
    def test_probe_separates_copy_from_alias_and_tracks_lifetime(self) -> None:
        result = buffer_alias_probe.run_experiment()

        self.assertEqual(result.copied_slice, "02030405")
        self.assertEqual(result.copy_after_view_write, "02030405")
        self.assertEqual(result.exporter_after_view_write, "0001aa0304050607")
        self.assertEqual(result.view_after_direct_write, "aabb0405")
        self.assertEqual(result.readonly_after_direct_write, "aabb0405")
        self.assertEqual(result.resize_while_exported, "BufferError")
        self.assertEqual(result.access_after_release, "ValueError")
        self.assertEqual((result.resized_length, result.resized_tail), (9, 255))

    def test_probe_exposes_shape_strides_and_contiguity(self) -> None:
        result = buffer_alias_probe.run_experiment()

        self.assertIn("shape=(2, 4)", result.matrix_metadata)
        self.assertIn("strides=(4, 1)", result.matrix_metadata)
        self.assertEqual(result.matrix_element, 6)
        self.assertEqual(result.strided_bytes, "00020406")
        self.assertIn("strides=(2,)", result.strided_metadata)
        self.assertIn("c_contiguous=False", result.strided_metadata)

    def test_probe_report_is_stable(self) -> None:
        report = buffer_alias_probe.format_report(buffer_alias_probe.run_experiment())

        self.assertEqual(len(report.splitlines()), 9)
        self.assertIn("resize-while-exported: BufferError", report)
        self.assertIn("access-after-release: ValueError", report)
        self.assertIn("element[1,2]=6", report)


if __name__ == "__main__":
    unittest.main()
