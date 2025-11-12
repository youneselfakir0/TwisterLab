#!/bin/bash
# Script pour ajouter ClassifierAgent, ResolverAgent, DesktopCommanderAgent a l'orchestrateur

cd /home/twister/TwisterLab

# Ajouter les imports en haut du fichier
sed -i '/from agents.real.real_sync_agent import RealSyncAgent/a\
from agents.real.real_classifier_agent import RealClassifierAgent\
from agents.real.real_resolver_agent import RealResolverAgent\
from agents.real.real_desktop_commander_agent import RealDesktopCommanderAgent' agents/orchestrator/autonomous_orchestrator.py

# Modifier la methode initialize_agents pour ajouter les 3 nouveaux agents
sed -i 's/"sync": RealSyncAgent(),/"sync": RealSyncAgent(),\n            "classifier": RealClassifierAgent(),\n            "resolver": RealResolverAgent(),\n            "desktop_commander": RealDesktopCommanderAgent(),/' agents/orchestrator/autonomous_orchestrator.py

echo "Orchestrateur mis a jour avec 6 agents (monitoring, backup, sync, classifier, resolver, desktop_commander)"
echo ""
echo "Verification des imports:"
grep -E "(RealClassifierAgent|RealResolverAgent|RealDesktopCommanderAgent)" agents/orchestrator/autonomous_orchestrator.py
echo ""
echo "Verification des agents:"
grep -A 10 'self.agents = {' agents/orchestrator/autonomous_orchestrator.py | head -15
