#!/usr/bin/env python3
"""Test TwisterLab - Configuration Swarm & edgeserver"""

import subprocess
import sys


def run_cmd(cmd):
    """Exécute une commande et retourne le résultat"""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip(), result.returncode
    except Exception as e:
        return f"ERROR: {e}", 1


def test_swarm_status():
    """Test Docker Swarm actif"""
    output, code = run_cmd("docker info --format '{{.Swarm.LocalNodeState}}'")
    if code == 0 and "active" in output.lower():
        print("✅ Docker Swarm: ACTIF")
        return True
    else:
        print(f"❌ Docker Swarm: INACTIF ({output})")
        return False


def test_swarm_nodes():
    """Test nœuds Swarm"""
    output, code = run_cmd("docker node ls --format '{{.Hostname}}'")
    if code == 0:
        nodes = output.split("\n")
        edgeserver_found = any("edgeserver" in node for node in nodes)

        print(f"✅ Nœuds Swarm: {len(nodes)} nœud(s) détecté(s)")
        for node in nodes:
            marker = "🎯" if "edgeserver" in node else "  "
            print(f"   {marker} {node}")

        if edgeserver_found:
            print("   ✅ edgeserver.twisterlab.local trouvé")
            return True
        else:
            print("   ⚠️  edgeserver.twisterlab.local non trouvé")
            return False
    return False


def test_services_on_edgeserver():
    """Test services déployés sur edgeserver"""
    services = [
        "twisterlab-monitoring_grafana",
        "twisterlab-monitoring_prometheus",
        "twisterlab_prod_webui",
    ]

    results = {}
    for service in services:
        output, code = run_cmd(
            f"docker service ps {service} --filter 'desired-state=running' "
            f"--format '{{{{.Node}}}}|{{{{.CurrentState}}}}'"
        )

        if code == 0 and output:
            node, state = output.split("|")[0:2] if "|" in output else (output, "unknown")
            results[service] = {
                "node": node,
                "state": state,
                "on_edgeserver": "edgeserver" in node.lower(),
                "running": "running" in state.lower(),
            }
        else:
            results[service] = {
                "node": "N/A",
                "state": "N/A",
                "on_edgeserver": False,
                "running": False,
            }

    print("\n📊 SERVICES SUR EDGESERVER:")
    print("-" * 70)

    for service_name, info in results.items():
        short_name = service_name.replace("twisterlab-monitoring_", "").replace(
            "twisterlab_prod_", ""
        )

        if info["running"] and info["on_edgeserver"]:
            status = "✅"
        elif info["running"]:
            status = "⚠️"
        else:
            status = "❌"

        print(f"{status} {short_name:20} → {info['node']:30} [{info['state'][:20]}]")

    running_on_edge = sum(1 for i in results.values() if i["on_edgeserver"] and i["running"])
    return running_on_edge >= 2


def test_service_ports():
    """Test ports exposés par les services"""
    ports_to_check = {
        "Grafana (edgeserver)": "edgeserver.twisterlab.local:3000",
        "Prometheus (edgeserver)": "edgeserver.twisterlab.local:9090",
        "OpenWebUI (edgeserver)": "edgeserver.twisterlab.local:8083",
        "Traefik Dashboard": "edgeserver.twisterlab.local:8084",
    }

    print("\n🌐 PORTS ACCESSIBLES:")
    print("-" * 70)

    # Récupérer les services avec ports
    output, code = run_cmd("docker service ls --format '{{.Name}}|{{.Ports}}'")
    if code == 0:
        service_ports = dict(line.split("|") for line in output.split("\n") if "|" in line)

        for desc, endpoint in ports_to_check.items():
            # Extraire le port de l'endpoint
            port = endpoint.split(":")[1] if ":" in endpoint else "N/A"

            # Chercher dans les services
            found = False
            for svc_name, svc_ports in service_ports.items():
                if port in svc_ports and svc_ports:
                    print(f"✅ {desc:30} → http://{endpoint}")
                    found = True
                    break

            if not found and port != "N/A":
                print(f"⚠️  {desc:30} → Port {port} non publié")

    return True


def main():
    print("\n" + "=" * 70)
    print("🐳 TWISTERLAB - TEST DOCKER SWARM & EDGESERVER")
    print("=" * 70 + "\n")

    results = []

    # Tests
    print("🔍 INFRASTRUCTURE SWARM")
    print("-" * 70)
    results.append(test_swarm_status())
    results.append(test_swarm_nodes())
    print()

    results.append(test_services_on_edgeserver())
    print()

    results.append(test_service_ports())
    print()

    # Résumé
    success = sum(results)
    total = len(results)

    print("=" * 70)
    print(f"📊 RÉSULTAT: {success}/{total} tests réussis")
    print("=" * 70 + "\n")

    if success == total:
        print("🎉 CONFIGURATION SWARM PARFAITE\n")
        print("✅ Docker Swarm opérationnel")
        print("✅ edgeserver.twisterlab.local configuré")
        print("✅ Services déployés correctement")
        sys.exit(0)
    elif success >= total * 0.75:
        print("✅ CONFIGURATION SWARM FONCTIONNELLE\n")
        sys.exit(0)
    else:
        print("⚠️  CONFIGURATION SWARM PARTIELLE\n")
        sys.exit(1)


if __name__ == "__main__":
    main()
