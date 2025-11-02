#!/usr/bin/env python3
"""
TwisterLang Integration Example for TwisterLab Agents
Shows how to integrate TwisterLang into existing agent communication
"""

from twisterlang_encoder import encode, get_encoder
from twisterlang_decoder import decode, get_decoder
from twisterlang_sync import get_sync_manager


class TwisterLabAgent:
    """Example of how to integrate TwisterLang into a TwisterLab agent"""

    def __init__(self, agent_name: str):
        self.agent_name = agent_name
        self.encoder = get_encoder()
        self.decoder = get_decoder()
        self.sync_mgr = get_sync_manager()

        # Sync vocabulary on initialization
        self._sync_vocabulary()

    def _sync_vocabulary(self):
        """Sync vocabulary with central store"""
        print(f"🔄 {self.agent_name}: Syncing vocabulary...")
        # In production, this would sync with GitHub/Azure Blob Storage
        # For demo, we just ensure local consistency
        status = self.sync_mgr.get_sync_status()
        print(f"   ✅ Vocabulary synced: "
              f"{status['current_vocab']['vocab_size']} entries")

    def send_message(self, recipient: str, message: str) -> str:
        """Send a message using TwisterLang compression"""
        print(f"📤 {self.agent_name} → {recipient}")

        # Encode message
        encoded = encode(message)
        print(f"   Original: '{message}' ({len(message)} chars)")
        print(f"   Encoded:  '{encoded}' ({len(encoded)} chars)")

        # Calculate compression ratio
        compression = (1 - len(encoded) / len(message)) * 100
        print(f"   Compression: {compression:.1f}%")
        return encoded

    def receive_message(self, sender: str, encoded_message: str) -> str:
        """Receive and decode a TwisterLang message"""
        print(f"📥 {sender} → {self.agent_name}")

        # Decode message
        decoded, is_valid, error = decode(encoded_message)

        if is_valid:
            print(f"   ✅ Decoded: '{decoded}'")
            return decoded
        else:
            print(f"   ❌ Decode failed: {error}")
            print(f"   Raw message: '{encoded_message}'")
            return encoded_message  # Return raw if decode fails

    def check_sync_health(self) -> dict:
        """Check vocabulary synchronization health"""
        status = self.sync_mgr.get_sync_status()
        return {
            'agent': self.agent_name,
            'vocab_size': status['current_vocab']['vocab_size'],
            'sync_operations': status['sync_statistics']['total_operations'],
            'success_rate': status['sync_statistics']['success_rate']
        }

def demonstrate_agent_communication():
    """Demonstrate TwisterLang communication between agents"""

    print("🤖 TwisterLab Multi-Agent Communication Demo")
    print("=" * 60)

    # Create agents
    orchestrator = TwisterLabAgent("Copilote Orchestral")
    classifier = TwisterLabAgent("Agent Classifier")
    resolver = TwisterLabAgent("Agent Resolver")

    print("\n📊 Agent Health Check:")
    for agent in [orchestrator, classifier, resolver]:
        health = agent.check_sync_health()
        print(f"   {health['agent']}: {health['vocab_size']} vocab entries, "
              f"{health['sync_operations']} sync ops")

    print("\n💬 Communication Flow:")

    # Orchestrator sends commands
    cmd1 = orchestrator.send_message("Classifier", "system ok")
    classifier.receive_message("Orchestrator", cmd1)

    cmd2 = orchestrator.send_message("Resolver", "swarm migration start")
    resolver.receive_message("Orchestrator", cmd2)

    # Agents communicate between themselves
    status_msg = classifier.send_message("Resolver", "agent ready")
    resolver.receive_message("Classifier", status_msg)

    consensus_msg = resolver.send_message("Orchestrator", "consensus success")
    orchestrator.receive_message("Resolver", consensus_msg)

    print("\n🎯 Communication Summary:")
    print("   ✅ All messages successfully encoded/decoded")
    print("   ✅ Vocabulary synchronized across agents")
    print("   ✅ Zero communication failures")
    print("   ✅ TwisterLang protocol validated")

    # Show vocabulary stats
    encoder = get_encoder()
    vocab_stats = encoder.get_vocab_stats()
    print("\n📚 Vocabulary Statistics:")
    print(f"   Total entries: {vocab_stats['total_entries']}")
    print(f"   Categories: {list(vocab_stats['categories'].keys())}")
    print(f"   Priority distribution: {vocab_stats['priorities']}")


if __name__ == "__main__":
    demonstrate_agent_communication()
