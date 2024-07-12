import uuid
import base58

def uuid_to_base58(uuid_obj: uuid.UUID) -> str:
    binary_uuid = uuid_obj.bytes
    base58_uuid = base58.b58encode(binary_uuid).decode('utf-8')
    return base58_uuid

def base58_to_uuid(base58_str: str) -> uuid.UUID:
    binary_uuid = base58.b58decode(base58_str)
    uuid_obj = uuid.UUID(bytes=binary_uuid)
    return uuid_obj


if __name__ == "__main__":
    uuid_obj = uuid.uuid4()

    print(f"UUID: {uuid_obj}")
    base58_uuid = uuid_to_base58(uuid_obj)
    print(f"Base58 Encoded UUID: {base58_uuid}")

    decoded_uuid = base58_to_uuid(base58_uuid)
    print(f"Decoded UUID: {decoded_uuid}")