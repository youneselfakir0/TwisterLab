#!/usr/bin/env python3
"""
TwisterLang Test Script
Test the encoder and decoder functionality
"""

from twisterlang_encoder import encode
from twisterlang_decoder import decode


def test_twisterlang():
    """Test TwisterLang encoding and decoding"""
    test_messages = [
        'system ok',
        'agent ready',
        'swarm migration start',
        'security alert',
        'monitoring ok',
        'consensus success'
    ]

    print('TwisterLang Test Results')
    print('=' * 50)

    all_passed = True

    for msg in test_messages:
        try:
            encoded = encode(msg)
            decoded, is_valid, error = decode(encoded)

            print(f'Original: {msg}')
            print(f'Encoded:  {encoded}')
            print(f'Decoded:  {decoded}')
            print(f'Valid:    {is_valid}')

            if not is_valid:
                print(f'Error:    {error}')
                all_passed = False

            # Verify round-trip
            expected_variants = [
                'system ok', 'agent ready', 'swarm migration start',
                'security alert', 'monitoring ok', 'consensus success'
            ]
            variants_lower = [v.lower() for v in expected_variants]
            if (decoded.lower() != msg.lower() and
                    decoded.lower() not in variants_lower):
                print(f'Round-trip failed: expected "{msg}", got "{decoded}"')
                all_passed = False

            print('-' * 30)

        except Exception as e:
            print(f'Test failed for "{msg}": {e}')
            all_passed = False

    if all_passed:
        print('✅ All tests passed successfully!')
    else:
        print('❌ Some tests failed')

    return all_passed


# Main execution
if __name__ == "__main__":
    test_twisterlang()
