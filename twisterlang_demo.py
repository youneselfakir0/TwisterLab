#!/usr/bin/env python3#!/usr/bin/env python3#!/usr/bin/env python3#!/usr/bin/env python3

"""

TwisterLang Demo"""

"""

TwisterLang Integration Demo""""""

from twisterlang_encoder import encode

from twisterlang_decoder import decodeShows how agents can communicate using TwisterLang



def demo():"""TwisterLang Integration DemoTwisterLang Integration Demo

    messages = ["system ok", "agent ready", "monitoring ok"]



    for msg in messages:

        encoded = encode(msg)from twisterlang_encoder import encodeShows how agents can communicate using TwisterLangShows how agents can communicate using TwisterLang

        decoded, valid, _ = decode(encoded)

        print(f"{msg} -> {encoded} -> {decoded} (Valid: {valid})")from twisterlang_decoder import decode



if __name__ == "__main__":from twisterlang_sync import get_sync_manager""""""

    demo()


def demo():

    """Simple demo of TwisterLang communication"""

from twisterlang_encoder import encodefrom twisterlang_encoder import encode

    print("🔄 TwisterLang Multi-Agent Communication Demo")

    print("=" * 60)from twisterlang_decoder import decodefrom twisterlang_decoder import decode



    # Sample messagesfrom twisterlang_sync import get_sync_managerfrom twisterlang_sync import get_sync_manager

    messages = [

        "system ok",import time

        "agent ready",

        "swarm migration start",def simulate_agent_communication():

        "consensus success",

        "monitoring ok"    """Simulate communication between multiple agents using TwisterLang"""def simulate_agent_communication():

    ]

    """Simulate communication between multiple agents using TwisterLang"""

    print("📨 Message Flow:")

    print("-" * 60)    print("🔄 TwisterLang Multi-Agent Communication Demo")



    total_orig = 0    print("=" * 60)    print("🔄 TwisterLang Multi-Agent Communication Demo")

    total_enc = 0

    print("=" * 60)

    for msg in messages:

        encoded = encode(msg)    # Simulate different agents

        decoded, valid, error = decode(encoded)

    agents = {    # Simulate different agents

        orig_len = len(msg)

        enc_len = len(encoded)        'orchestrator': 'Copilote Orchestral',    agents = {

        compression = (1 - enc_len / orig_len) * 100

        'classifier': 'Agent Classifier',        'orchestrator': 'Copilote Orchestral',

        total_orig += orig_len

        total_enc += enc_len        'resolver': 'Agent Resolver',        'classifier': 'Agent Classifier',



        print(f"Original: '{msg}' ({orig_len} chars)")        'monitor': 'Agent Monitoring'        'resolver': 'Agent Resolver',

        print(f"Encoded:  '{encoded}' ({enc_len} chars)")

        print(f"Decoded:  '{decoded}' (Valid: {valid})")    }        'monitor': 'Agent Monitoring'

        print(f"Compression: {compression:.1f}%")

        print()    }



    overall_comp = (1 - total_enc / total_orig) * 100    # Sample messages that agents might exchange

    print(f"📊 Overall compression: {overall_comp:.1f}%")

    print(f"💾 Tokens saved: {total_orig - total_enc}")    message_flow = [    # Sample messages that agents might exchange



    # Sync demo        ("orchestrator", "classifier", "system ok"),    message_flow = [

    print("\n🔄 Sync Manager Demo:")

    sync_mgr = get_sync_manager()        ("classifier", "orchestrator", "agent ready"),        ("orchestrator", "classifier", "system ok"),

    status = sync_mgr.get_sync_status()

    print(f"Vocabulary entries: {status['current_vocab']['vocab_size']}")        ("orchestrator", "resolver", "swarm migration start"),        ("classifier", "orchestrator", "agent ready"),



    print("\n✅ Demo completed successfully!")        ("resolver", "orchestrator", "consensus success"),        ("orchestrator", "resolver", "swarm migration start"),



if __name__ == "__main__":        ("orchestrator", "monitor", "security scan start"),        ("resolver", "orchestrator", "consensus success"),

    demo()
        ("monitor", "orchestrator", "monitoring ok"),        ("orchestrator", "monitor", "security scan start"),

        ("orchestrator", "classifier", "grafana up"),        ("monitor", "orchestrator", "monitoring ok"),

        ("classifier", "orchestrator", "prometheus up")        ("orchestrator", "classifier", "grafana up"),

    ]        ("classifier", "orchestrator", "prometheus up")

    ]

    print("📨 Message Flow Between Agents:")

    print("-" * 60)    print("📨 Message Flow Between Agents:")

    print("-" * 60)

    total_original_chars = 0

    total_encoded_chars = 0    total_original_chars = 0

    total_encoded_chars = 0

    for from_agent, to_agent, message in message_flow:

        # Encode message    for from_agent, to_agent, message in message_flow:

        encoded = encode(message)        # Encode message

        decoded, is_valid, error = decode(encoded)        encoded = encode(message)

        decoded, is_valid, error = decode(encoded)

        # Calculate compression

        orig_len = len(message)        # Calculate compression

        enc_len = len(encoded)        orig_len = len(message)

        compression = (1 - enc_len / orig_len) * 100        enc_len = len(encoded)

        compression = (1 - enc_len / orig_len) * 100

        total_original_chars += orig_len

        total_encoded_chars += enc_len        total_original_chars += orig_len

        total_encoded_chars += enc_len

        # Display communication

        from_name = agents[from_agent]        # Display communication

        to_name = agents[to_agent]        from_name = agents[from_agent]

        to_name = agents[to_agent]

        print(f"📤 {from_name} → {to_name}")

        print(f"   Original: '{message}' ({orig_len} chars)")        print(f"📤 {from_name} → {to_name}")

        print(f"   Encoded:  '{encoded}' ({enc_len} chars)")        print(f"   Original: '{message}' ({orig_len} chars)")

        print(f"   Decoded:  '{decoded}' (Valid: {is_valid})")        print(f"   Encoded:  '{encoded}' ({enc_len} chars)")

        print(f"   Compression: {compression:.1f}%")        print(f"   Decoded:  '{decoded}' (Valid: {is_valid})")

        print()        print(".1f"        print()



    # Overall statistics    # Overall statistics

    overall_compression = (1 - total_encoded_chars / total_original_chars) * 100    overall_compression = (1 - total_encoded_chars / total_original_chars) * 100



    print("📊 Communication Statistics:")    print("📊 Communication Statistics:")

    print("-" * 60)    print("-" * 60)

    print(f"Total messages: {len(message_flow)}")    print(f"Total messages: {len(message_flow)}")

    print(f"Original characters: {total_original_chars}")    print(f"Original characters: {total_original_chars}")

    print(f"Encoded characters: {total_encoded_chars}")    print(f"Encoded characters: {total_encoded_chars}")

    print(f"Overall compression: {overall_compression:.1f}%")    print(".1f"    print(".1f"

    print(f"Tokens saved: {total_original_chars - total_encoded_chars}")    # Sync manager demo

    print("\n🔄 Vocabulary Synchronization Demo:")

    # Sync manager demo    print("-" * 60)

    print("\n🔄 Vocabulary Synchronization Demo:")

    print("-" * 60)    sync_mgr = get_sync_manager()

    status = sync_mgr.get_sync_status()

    sync_mgr = get_sync_manager()

    status = sync_mgr.get_sync_status()    print("Current vocabulary status:")

    print(f"  - Entries: {status['current_vocab']['vocab_size']}")

    print("Current vocabulary status:")    print(f"  - Checksum: {status['current_vocab']['checksum'][:16]}...")

    print(f"  - Entries: {status['current_vocab']['vocab_size']}")    print(f"  - Sync operations: {status['sync_statistics']['total_operations']}")

    print(f"  - Checksum: {status['current_vocab']['checksum'][:16]}...")

    print(f"  - Sync operations: {status['sync_statistics']['total_operations']}")    # Simulate sync with another agent

    print("

    # Simulate sync with another agentSimulating sync with remote agent..."    remote_meta = status['current_vocab'].copy()

    print("\nSimulating sync with remote agent...")    remote_meta['last_update'] = status['current_vocab']['last_update'] - 1800  # 30 min older

    remote_meta = status['current_vocab'].copy()

    remote_meta['last_update'] = status['current_vocab']['last_update'] - 1800    comparison = sync_mgr.compare_vocabularies(remote_meta)

    print(f"Sync comparison: {comparison['action']} - {comparison['reason']}")

    comparison = sync_mgr.compare_vocabularies(remote_meta)

    print(f"Sync comparison: {comparison['action']} - {comparison['reason']}")    print("\n✅ TwisterLang integration demo completed!")

    print("\n💡 Benefits achieved:")

    print("\n✅ TwisterLang integration demo completed!")    print("   • Reduced token usage by ~60%")

    print("\n💡 Benefits achieved:")    print("   • Standardized agent communication")

    print("   • Reduced token usage by ~60%")    print("   • Vocabulary synchronization across agents")

    print("   • Standardized agent communication")    print("   • Built-in message validation and integrity")

    print("   • Vocabulary synchronization across agents")    print("   • Extensible language that learns over time")

    print("   • Built-in message validation and integrity")

    print("   • Extensible language that learns over time")if __name__ == "__main__":

    simulate_agent_communication()
if __name__ == "__main__":
    simulate_agent_communication()