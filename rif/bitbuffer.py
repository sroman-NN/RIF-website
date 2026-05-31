

class BitBuffer:
    """Buffer de bits optimizado utilizando bytearray interno."""

    __slots__ = ('_buffer', '_bit_length')

    def __init__(self, initial_bits: str = ""):
        self._buffer = bytearray()
        self._bit_length = 0
        if initial_bits:
            self.append_string(initial_bits)

    @property
    def bit_length(self) -> int:
        return self._bit_length

    def append_string(self, bits: str) -> None:
        """Añade bits a partir de un string de ceros y unos."""
        for bit in bits:
            self._append_one_bit(1 if bit == '1' else 0)

    def append_zeros(self, count: int) -> None:
        """Optimización para rellenar con ceros."""
        self.append_bits(0, count)

    def append_bits(self, value: int, width: int) -> None:
        """Añade 'width' bits al buffer a partir del 'value' entero."""
        if width <= 0:
            return

        value &= (1 << width) - 1

        while width > 0:
            bit_offset = self._bit_length % 8
            space_in_byte = 8 - bit_offset

            if width <= space_in_byte:
                shift = space_in_byte - width
                part = value << shift
                self._add_to_byte(part)
                self._bit_length += width
                break
            else:
                take_width = space_in_byte
                shift = width - take_width
                part = (value >> shift) & ((1 << take_width) - 1)
                self._add_to_byte(part)
                self._bit_length += take_width

                value &= (1 << shift) - 1
                width -= take_width

    def _add_to_byte(self, part: int) -> None:
        bit_offset = self._bit_length % 8
        if bit_offset == 0:
            self._buffer.append(part)
        else:
            self._buffer[-1] |= part

    def _append_one_bit(self, bit: int) -> None:
        bit_offset = self._bit_length % 8
        if bit_offset == 0:
            self._buffer.append(bit << 7)
        else:
            self._buffer[-1] |= (bit << (7 - bit_offset))
        self._bit_length += 1

    def to_bytes(self) -> bytes:
        """Devuelve los datos alineados a byte."""
        if self._bit_length % 8 != 0:
            raise ValueError(f"Longitud no alineada a byte: {self._bit_length}")
        return bytes(self._buffer)

    def to_string(self) -> str:
        """Devuelve la representación en string ('010101...') útil para debug."""
        res = []
        for b in self._buffer:
            res.append(f"{b:08b}")
        s = "".join(res)
        return s[:self._bit_length]

    def __len__(self) -> int:
        return self._bit_length
