#!/bin/bash
# Ajouter la methode de routing automatique a l'orchestrateur

cd /home/twister/TwisterLab

# Backup
cp agents/orchestrator/autonomous_orchestrator.py agents/orchestrator/autonomous_orchestrator.py.pre_routing

# Ajouter la methode process_ticket_workflow apres la methode initialize_agents
cat >> /tmp/new_method.py << 'EOF'

    async def process_ticket_workflow(self, ticket: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a ticket through the complete workflow:
        1. ClassifierAgent analyzes and routes
        2. ResolverAgent executes SOP if needed
        3. DesktopCommanderAgent runs commands if needed

        Args:
            ticket: Ticket data with title, description, etc

        Returns:
            Complete workflow results
        """
        logger.info(f"🎫 Processing ticket workflow: {ticket.get('ticket_id', 'Unknown')}")

        workflow_results = {
            "ticket_id": ticket.get("ticket_id"),
            "start_time": datetime.now().isoformat(),
            "steps": []
        }

        try:
            # Step 1: Classify ticket
            logger.info("Step 1/3: Classifying ticket...")
            classifier = self.agents.get("classifier")
            if not classifier:
                raise ValueError("ClassifierAgent not initialized")

            classification_result = await classifier.execute({
                "operation": "classify_ticket",
                "ticket": ticket
            })

            workflow_results["steps"].append({
                "step": "classification",
                "agent": "ClassifierAgent",
                "result": classification_result,
                "timestamp": datetime.now().isoformat()
            })

            if classification_result.get("status") != "success":
                raise ValueError(f"Classification failed: {classification_result.get('error')}")

            classification = classification_result.get("classification", {})
            routed_to = classification.get("routed_to_agent", "ResolverAgent")
            category = classification.get("category", "general")

            logger.info(f"✅ Classified as {category}, routing to {routed_to}")

            # Step 2: Execute resolver if routed
            if routed_to == "ResolverAgent":
                logger.info("Step 2/3: Executing ResolverAgent...")
                resolver = self.agents.get("resolver")
                if resolver:
                    # Map category to SOP
                    sop_map = {
                        "network": "network_troubleshoot",
                        "software": "software_install",
                        "performance": "disk_cleanup",
                        "security": "password_reset",
                        "database": "database_optimization"
                    }
                    sop_id = sop_map.get(category, "network_troubleshoot")

                    resolver_result = await resolver.execute({
                        "operation": "execute_sop",
                        "sop_id": sop_id,
                        "ticket": ticket
                    })

                    workflow_results["steps"].append({
                        "step": "resolution",
                        "agent": "ResolverAgent",
                        "sop_executed": sop_id,
                        "result": resolver_result,
                        "timestamp": datetime.now().isoformat()
                    })

                    logger.info(f"✅ ResolverAgent completed SOP: {sop_id}")

            # Step 3: Execute DesktopCommander if needed
            elif routed_to == "DesktopCommanderAgent":
                logger.info("Step 2/3: Executing DesktopCommanderAgent...")
                commander = self.agents.get("desktop_commander")
                if commander:
                    # Map category to command
                    command_map = {
                        "network": "ping 8.8.8.8 -c 4",
                        "hardware": "df -h && free -h"
                    }
                    command = command_map.get(category, "echo 'No specific command for this category'")

                    commander_result = await commander.execute({
                        "operation": "execute_command",
                        "command": command,
                        "ticket": ticket
                    })

                    workflow_results["steps"].append({
                        "step": "command_execution",
                        "agent": "DesktopCommanderAgent",
                        "command": command,
                        "result": commander_result,
                        "timestamp": datetime.now().isoformat()
                    })

                    logger.info(f"✅ DesktopCommanderAgent executed: {command}")

            workflow_results["status"] = "success"
            workflow_results["end_time"] = datetime.now().isoformat()

            logger.info(f"🎉 Ticket workflow completed successfully!")
            return workflow_results

        except Exception as e:
            logger.error(f"❌ Workflow failed: {e}", exc_info=True)
            workflow_results["status"] = "error"
            workflow_results["error"] = str(e)
            workflow_results["end_time"] = datetime.now().isoformat()
            return workflow_results
EOF

# Inserer la nouvelle methode apres initialize_agents
sed -i '/logger.info(f"✅ Initialized {len(self.agents)} autonomous agents")/a\
\    # Nouvelle methode ajoutee pour workflow automatique' agents/orchestrator/autonomous_orchestrator.py

# Ajouter le contenu de la methode
cat /tmp/new_method.py >> agents/orchestrator/autonomous_orchestrator.py

echo "Methode process_ticket_workflow ajoutee a l'orchestrateur"
echo ""
echo "Verification:"
grep -c "process_ticket_workflow" agents/orchestrator/autonomous_orchestrator.py
